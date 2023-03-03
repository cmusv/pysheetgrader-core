from pysheetgrader.custom_excel_formula import get_excel_formula_lambdas
from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.formula_parser import parse_formula
from sympy import simplify


class NaiveFormulaStrategy(BaseStrategy):
    """
    Naively compare whether the formula between key and submission is the same when they're simplified.
    This instance will check the alternative cells in the key if the submission formula didn't match the key formula
        in the main cell.
    """
    COMPUTE_RESULT = False

    def get_submitted_value(self, sub_sheet, cell_coord):
        custom_formulas = get_excel_formula_lambdas()
        sub_cell_value = sub_sheet[cell_coord].value
        return parse_formula(sub_cell_value, local_dict=custom_formulas)

    def check_correct(self, sub_cell_value, key_cell_value):
        return simplify(key_cell_value - sub_cell_value) == 0

    def get_key_value(self, key_sheet, key_coord):
        custom_formulas = get_excel_formula_lambdas()
        key_cell_value = key_sheet[key_coord].value
        return parse_formula(key_cell_value, local_dict=custom_formulas)
