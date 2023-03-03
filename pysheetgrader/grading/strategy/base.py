from pysheetgrader.grading.rubric import GradingRubric
from pysheetgrader.grading.report import GradingReport, GradingReportType
from pysheetgrader.document import Document


class BaseStrategy:
    """
    Base class of other grading strategies.
    """
    COMPUTE_RESULT = True

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

    def get_submitted_value(self, sub_sheet, cell_coord):
        '''
        template pattern: this is how to get the submitted value
        '''
        raise NotImplementedError()

    def get_key_value(self, sub_sheet, cell_coord):
        '''
        template pattern: this is how to get the key value
        '''
        raise NotImplementedError()
    
    def check_correct(self, key_sheet, key_coord):
        '''
        template pattern: this is how to check if the value is correct
        '''
        raise NotImplementedError()
 
    def grade(self):
        '''
        loop through all cell cords
        setup report, validate inputs, parse formulas
        iterate through cells and compare to proper formula
            as soon as we get a correct answer, stop and sum
        
        if we must, subtract at the end
        '''
        ### setup 
        report = self.create_initial_report()
        cell_coord = self.grading_rubric.cell_coord
        key_sheet, sub_sheet = self.try_get_key_and_sub(report, computed=self.COMPUTE_RESULT)
        
        ### validate
        if key_sheet is None:
            return report

        ### grab the submitted value
        sub_cell_value = self.get_submitted_value(sub_sheet, cell_coord)
 
        ### loop thru all keys, including alt cells
        for key_coord in self.grading_rubric.get_all_cell_coord():
            
            ### get proper answer
            key_cell_value = self.get_key_value(key_sheet, key_coord)
            
            ### compare to submitted
            is_correct = self.check_correct(sub_cell_value, key_cell_value)
            
            if is_correct and self.prereq_check(cell_coord, report):
                ### here is where we can add weird logic for different grading natures
                report.submission_score += self.get_correct_score(self.grading_rubric.grading_nature, self.grading_rubric.score)

                #### mark as correct
                self.grading_rubric.is_correct = True
                break
        
        ### subtract if necessary
        if  self.grading_rubric.grading_nature == 'negative' and not self.grading_rubric.is_correct:
            report.submission_score += self.grading_rubric.score
    
        return report

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

    def  try_get_key_and_sub(self, report, computed=True):
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
            report.append_line(f"{self.report_line_prefix}{exc}")
            report.report_html_args['error'] = exc
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
        except Exception: # basically always fails
            print('error')
            # TODO: Check if we should log an error here.
            return False

    def prereq_check(self, cell_coord, report):
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
            report.append_line(f"{self.report_line_prefix} "+ prereq_string + " must be correct before this cell can be graded!")
            report.report_html_args['feedback'] = f" "+ prereq_string + " must be correct before this cell can be graded!"
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