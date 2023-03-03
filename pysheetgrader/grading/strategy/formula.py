from pysheetgrader.grading.strategy.base import BaseStrategy
from sympy import simplify


class NaiveFormulaStrategy(BaseStrategy):
    """
    Naively compare whether the formula between key and submission is the same when they're simplified.
    This instance will check the alternative cells in the key if the submission formula didn't match the key formula
        in the main cell.
    """

    def get_submitted_value(self):
        sub_cell_value = self.sub_sheet_raw[self.cell_coord].value
        return self.parse_formula(sub_cell_value, local_dict=self.custom_formulas)

    def check_correct(self, sub_cell_value, key_cell_value):
        return simplify(key_cell_value - sub_cell_value) == 0

    def get_key_value(self, key_coord):
        key_cell_value = self.key_sheet_raw[key_coord].value
        return self.parse_formula(key_cell_value, local_dict=self.custom_formulas)
