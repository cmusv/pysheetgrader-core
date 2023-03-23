from pysheetgrader.grading.strategy.base import BaseStrategy

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
    def get_submitted_value(self):
        return self.sub_sheet_compute[self.cell_coord].value

    def check_correct(self, sub_cell_value, key_cell_value, key_coord):
        return self.is_key_sub_match(self.key_sheet_compute, key_cell_value, sub_cell_value)

    def get_key_value(self, key_coord):
        return self.get_formula_value(self.sub_sheet_compute, self.key_sheet_raw[key_coord].value)

    def is_key_sub_match(self, key_sheet, key_value, sub_value):
        """
        Does the key value match the submission value? This function also consider
        the alt_cells and delta, if they are presented in the rubric

        :param key_sheet: the key sheet
        :param key_value: the evaluated key value for the cell
        :param sub_value: the evaluated submission value for the cell
        :return:
        """
         # TODO: REFACTOR
        match = False
        if self.value_matches(key_value, sub_value):
            match = True

        for alt_coord in self.grading_rubric.alt_cells:
            if self.value_matches(key_sheet[alt_coord].value, sub_value):
                match = True

        return match
