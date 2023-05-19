from pysheetgrader.grading.rubric import GradingRubric
from pysheetgrader.grading.report import GradingReport, GradingReportType
from pysheetgrader.document import Document
from pysheetgrader.formula_parser import (
    parse_formula_inputs, 
    parse_formula, 
    encode_cell_reference, 
    transform_excel_formula_to_sympy, 
    parse_from_excel
)
from pysheetgrader.custom_excel_formula import get_excel_formula_lambdas
from traceback import print_exc
import re
from openpyxl.utils import get_column_letter, column_index_from_string
from itertools import chain

class BaseStrategy:
    """
    Base class of other grading strategies.
    """
    COL_MATCH = r"\$[a-zA-Z]+\d+"
    '''
    very dumbly matches column + digit
    '''
    COL_MATCH_RAW = r"(?<![\w:])\b[A-Z]+\d+\b(?!\s*[\(:][^()]*[\):]|\s*:\w+\d+\b)" # thanks chatgpt
    '''
    given this pattern: B4+D5+C2+(B5:D4)+MAX(C5:C9) 
    write a regular expression that only matches B4, D5, and C2
    (to account for array concats)

    This regex pattern will match cell references that are not inside range references or function calls. 
    The negative lookbehind assertion will ensure that the match is not preceded by a word character or a colon. 
    The negative lookahead assertion will ensure that the match is not followed by a range reference or a colon followed by a cell reference.

    1. `(?<![\w:])` - negative lookbehind assertion that ensures that the match is not preceded by a word character or a colon.
    2. `\b` - word boundary that matches the start or end of a word.
    3. `[A-Z]+` - character class that matches one or more uppercase letters.
    4. `\d+` - matches one or more digits.
    5. `\b` - another word boundary that matches the end of the word.
    6. `(?!\s*[\(:][^()]*[\):]|\s*:\w+\d+\b)` - negative lookahead assertion that ensures that the match is not followed by a range reference or a colon followed by a cell reference.
    7. `[\(:][^()]*[\):]` - matches a range reference, such as `C5:B10`, enclosed in parentheses or brackets.
    8. `:\w+\d+\b` - matches a colon followed by a cell reference, such as `C5`, at the end of a word.

    Putting it all together, the regex pattern matches a cell reference that is not inside a range reference or function call and is not preceded by a word character or a colon.
    '''

    CONCAT_MATCH = r"\b[A-Z]+\d+:[A-Z]+\d+\b(?!\s*\([^()]*\))" # this basically just matches concats with a :
    '''
    1. `\b` - word boundary that matches the start or end of a word.
    2. `[A-Z]+` - character class that matches one or more uppercase letters.
    3. `\d+` - matches one or more digits.
    4. `:` - matches a colon.
    5. `[A-Z]+` - character class that matches one or more uppercase letters.
    6. `\d+` - matches one or more digits.
    7. `\b` - another word boundary that matches the end of the word.
    8. `(?!\s*\([^()]*\))` - negative lookahead assertion that ensures that the match is not inside a function call.
    9. `\s*` - matches zero or more whitespace characters.
    10. `\(` - matches an opening parenthesis.
    11. `[^()]*` - matches zero or more characters that are not parentheses.
    12. `\)` - matches a closing parenthesis.

    Putting it all together, the regex pattern matches a range reference that is not inside a function call. 
    It matches a cell reference followed by a colon and another cell reference, enclosed in word boundaries, 
    and ensures that there are no opening and closing parentheses with any number of characters in between them immediately after the match.
    '''

    def __init__(self, key_document: Document, sub_document: Document, sheet_name, grading_rubric: GradingRubric,correct_cells,
                 report_line_prefix: str = ""):
        """
        Initializer of this class.
        :param key_document: Document instance that used as a key.
        :param sub_document: Document instance that will be graded as a submission.
        :param sheet_name: String value of the sheet that will be graded.
        :param grading_rubric: GradingRubric instance.
        :param report_line_prefix: Prefix of the report line returned by this instance's `grade()`.
            Defaults to an empty string.
        """
        self.key_document = key_document
        self.sub_document = sub_document
        self.sheet_name = sheet_name
        self.grading_rubric = grading_rubric
        self.report_line_prefix = report_line_prefix
        self.correct_cells = correct_cells

        ### setup 
        self.report = self.create_initial_report()
        self.cell_coord = self.grading_rubric.cell_coord
        self.key_sheet_compute, self.sub_sheet_compute = self.try_get_key_and_sub(computed=True)
        self.key_sheet_raw, self.sub_sheet_raw = self.try_get_key_and_sub(computed=False)        
        self.custom_formulas = get_excel_formula_lambdas()
        self.parse_formula = parse_formula
        self.parse_from_excel = parse_from_excel
        self.re = re

    def get_submitted_value(self):
        '''
        template pattern: this is how to get the submitted value
        '''
        raise NotImplementedError()

    def get_key_value(self, key_coord):
        '''
        template pattern: this is how to get the key value
        '''
        raise NotImplementedError()
    
    def check_correct(self, sub_cell_value, key_cell_value, key_coord):
        '''
        template pattern: this is how to check if the value is correct
        '''
        raise NotImplementedError()
    
    def additional_fail_check(self):
        return False
    
    def get_key_coord_set(self):
        return self.grading_rubric.get_all_cell_coord()
    
    def grade(self):
        '''
        loop through all cell cords
        setup report, validate inputs, parse formulas
        iterate through cells and compare to proper formula
            as soon as we get a correct answer, stop and sum
        
        if we must, subtract at the end
        '''
        try:
            ### validate
            if not self.key_sheet_raw or self.additional_fail_check():
                return self.report

            ### grab the submitted value
            sub_cell_value = self.get_submitted_value()
    
            ### loop thru all keys, including alt cells
            for key_coord in self.get_key_coord_set():
                
                ### get proper answer
                key_cell_value = self.get_key_value(key_coord)
                
                ### compare to submitted
                is_correct = self.check_correct(sub_cell_value, key_cell_value, key_coord)
                
                if is_correct and self.prereq_check():
                    ### here is where we can add weird logic for different grading natures
                    self.report.submission_score += self.get_correct_score(self.grading_rubric.grading_nature, self.grading_rubric.score)

                    #### mark as correct
                    self.grading_rubric.is_correct = True

                    break
            
            ### subtract if necessary
            if  self.grading_rubric.grading_nature == 'negative' and not self.grading_rubric.is_correct:

                self.report.submission_score += self.grading_rubric.score
        
            return self.report

        except Exception as exc:
            self.report.append_line(f"{self.report_line_prefix}Error: {exc}")
            self.report.report_html_args['error'] = f"Error: {exc}"

            if self.grading_rubric.log_mode:
                print_exc()

            return self.report

    def create_initial_report(self):
        """
        Returns initial GradingReport instance with max_possible_score assigned to this instance's rubric score.
        :return: GradingReport instance.
        """
        report: GradingReport = GradingReport(GradingReportType.RUBRIC)
        if self.grading_rubric.grading_nature == 'positive':
            report.max_possible_score += self.grading_rubric.score
        return report

    def get_key_sheet(self, computed=True):
        """
        Retrieve the key sheet from the key document, according to `sheet_name`
        :return: the key sheet
        """
        return self.key_document.formula_wb[self.sheet_name] if not computed \
            else self.key_document.computed_value_wb[self.sheet_name]

    def get_sub_sheet(self, computed=True):
        """
        Retrieve the submission sheet from the submission document, according to `sheet_name`
        :return: the submission sheet
        """
        return self.sub_document.formula_wb[self.sheet_name] if not computed \
            else self.sub_document.computed_value_wb[self.sheet_name]

    def try_get_key_and_sub(self, computed=True):
        """
        Attempt to load both key and submission sheet according to `sheet_name`. Log any exception if occurs to report.
        :param computed: Should return the sheet with computed cells rather than formula strings
        :param report: the report to log any exception
        :return: the key sheet and submission sheet, None if execption occurs
        """
        try:
            key_sheet = self.get_key_sheet(computed)
            sub_sheet = self.get_sub_sheet(computed)
        except Exception as exc:
            self.report.append_line(f"{self.report_line_prefix}{exc}")
            self.report.report_html_args['error'] = exc
            return None, None
        return key_sheet, sub_sheet

    def value_matches(self, key_value, sub_value):
        """
        Returns boolean whether the passed `sub_value` match the `key_value`. If both of them are numeric and there's
        a `constant_delta` in current rubric, it will check if `sub_value` is in the range of `constant_delta`.

        :param key_value: Any value.
        :param sub_value: Any value.
        :return: True if they match, False otherwise.
        """

        # Best case: both are equals by default
        if key_value == sub_value:
            return True

        # If both of them are numbers, and there's no constant delta
        # Directly return False.
        if self.grading_rubric.constant_delta is None:
            return False

        delta = self.grading_rubric.constant_delta

        try:
            key_float = float(key_value)
            sub_float = float(sub_value)
            return (key_float - delta) <= sub_float <= (key_float + delta)
        except Exception as e: # basically always fails
            # TODO: Check if we should log an error here.
            return False

    def prereq_check(self):
        """
        Checks if the pre-requistes mentioned are correct or not the
        :param cell_coord: current correct cell coordinate to be added to correct cells list
        :return: True if the pre-requistes
        """
        if self.grading_rubric.prereq_cells is None or len(self.grading_rubric.prereq_cells) == 0:
            return True

        if len(self.correct_cells)>0:
            prereq_check = all(item in self.correct_cells for item in self.grading_rubric.prereq_cells)
        else:
            prereq_check = False

        if len(self.grading_rubric.prereq_cells) == 1:
            prereq_string = 'Cell '+' '.join(self.grading_rubric.prereq_cells)
        else:
            prereq_string = 'Cells '+', '.join(self.grading_rubric.prereq_cells)
        if not prereq_check:
            self.report.append_line(f"{self.report_line_prefix} "+ prereq_string + " must be correct before this cell can be graded!")
            self.report.report_html_args['feedback'] = f" "+ prereq_string + " must be correct before this cell can be graded!"

        return prereq_check

    @staticmethod
    def get_correct_score(grading_nature, score):
        '''
        gonna need to test this function
        '''
        if grading_nature == 'positive':
            return score
        elif grading_nature == 'negative':
            return  0
        else:
            raise NotImplementedError(f'Bad grading nature: {grading_nature}')

    def get_formula_value(self, sub_sheet, key_raw_formula: str, parse_xl=False):
        """
        Evaluate the relative value from student's submission cells, using the formula from the Key cell.

        :param sub_sheet: the student's submission sheet
        :param key_raw_formula: the String value of the relative formula from the Key.
        :return:
        """
        if parse_xl:
            r = self.get_formula_value_xl(sub_sheet, key_raw_formula)

        else:
            lowercased_formula = transform_excel_formula_to_sympy(key_raw_formula)
            
            # extract input coordinates
            input_coords = parse_formula_inputs(key_raw_formula, encoded=False)
            encoded_inputs = {encode_cell_reference(coord): sub_sheet[coord].value for coord in input_coords}
            local_dict = get_excel_formula_lambdas()
            local_dict.update(encoded_inputs)

            result = parse_formula(lowercased_formula, local_dict)
            local_dict.clear()
            r = result
        
        return r

    def get_formula_value_xl(self, sub_sheet, key_raw_formula: str) -> str:
        all_cols = self.re.findall(self.COL_MATCH_RAW, key_raw_formula)
        all_concats = self.re.findall(self.CONCAT_MATCH, key_raw_formula)

        tgt_kwargs = {
            col_match.upper(): sub_sheet[col_match.upper()].value or 0
            for col_match in all_cols
        }

        for concat in all_concats:
            # e.g.
            # concat = 'A1:B1' 
            # split -> [ 'A1', 'B1' ]
            # regex sub parsing -> [ ('A', 1), ('B', 1) ] 
            # column index from string -> [ (1, 1), (2, 1) ]
            # chain + unpack -> [ 1, 1, 2, 1 ]

            bounds = concat.split(':') 
            first_col, first_num, last_col, last_num = list(
                chain(
                    *[
                        ( 
                            column_index_from_string(self.re.sub(r"[^A-Za-z]", "", bound).upper()), 
                            int(self.re.sub(r"[^0-9]", "", bound))
                        )
                        for bound in bounds
                    ]
                )
            )
            
            tgt_kwargs[concat] = [    
                sub_sheet[f'{get_column_letter(col_idx)}{num}'.upper()].value 
                
                for col_idx in range(
                    first_col, 
                    last_col + 1
                ) 
                for num in range(
                    first_num, 
                    last_num + 1
                )
            ]

        return parse_from_excel(key_raw_formula, **tgt_kwargs)
