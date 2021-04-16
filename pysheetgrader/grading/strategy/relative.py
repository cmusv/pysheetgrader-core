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
        raise NotImplementedError("relative rubric has been deprecated, please use relative_f instead")

    def is_key_sub_match(self, key_sheet, key_value, sub_value):
        """
        Does the key value match the submission value? This function also consider
        the alt_cells and delta, if they are presented in the rubric

        :param key_sheet: the key sheet
        :param key_value: the evaluated key value for the cell
        :param sub_value: the evaluated submission value for the cell
        :return:
        """
        match = False
        if self.value_matches(key_value, sub_value):
            match = True

        for alt_coord in self.grading_rubric.alt_cells:
            if self.value_matches(key_sheet[alt_coord].value, sub_value):
                match = True

        return match

    def get_formula_value(self, sub_sheet, key_raw_formula: str):
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
