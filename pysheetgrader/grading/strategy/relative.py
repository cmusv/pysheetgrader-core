from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.formula_parser import parse_formula_inputs, parse_formula, \
    encode_cell_reference, transform_excel_formula_to_sympy
from pysheetgrader.custom_excel_formula import get_excel_formula_lambdas


class RelativeStrategy(BaseStrategy):
    """
    Relatively compares the evaluation of key's formula using submission cells values, with the actual value of that
    cell in the submission.

    For example:

    (A1Key.xlsx) A1 contains =IF(A2 = "ok", B2, C2)

    (A1Submission.xlsx)
    A1 contains 13
    A2 contains "not_ok"
    B2 contains 13
    C2 contains 14

    However, A1 is suppose to be 14 according to the relative formula.

    Thus, A1 doesn't pass.
    """

    def grade(self):
        report = self.create_initial_report()

        # Retrieving both key and submission document
        key_sheet, sub_sheet = self.try_get_key_and_sub(report)

        # Grading cells
        cell_coord = self.grading_rubric.cell_coord
        key_raw_formula = key_sheet[cell_coord].value

        # compare submission value and relative evaluation value
        sub_value = sub_sheet[cell_coord].value
        key_value = self.get_relative_value(sub_sheet, key_raw_formula)
        if self.value_matches(key_value, sub_value):
            report.submission_score += self.grading_rubric.score

        return report

    def get_relative_value(self, sub_sheet, key_raw_formula: str):
        """
        Evaluate the relative value from student's submission cells, using the formula from the Key cell.

        :param sub_sheet: the student's submission sheet
        :param key_raw_formula: the String value of the relative formula from the Key.
        :return:
        """
        lowercased_formula = transform_excel_formula_to_sympy(key_raw_formula)

        # extract input coordinates
        input_coords = parse_formula_inputs(key_raw_formula, encoded=False)

        encoded_inputs = {encode_cell_reference(coord): sub_sheet[coord].value for coord in input_coords}
        local_dict = get_excel_formula_lambdas()
        local_dict.update(encoded_inputs)

        result = parse_formula(lowercased_formula, local_dict)
        return result
