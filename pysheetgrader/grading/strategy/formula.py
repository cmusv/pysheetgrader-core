from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.formula_parser import parse_formula
from sympy import simplify


class NaiveFormulaStrategy(BaseStrategy):
    """
    Naively compare whether the formula between key and submission is the same when they're simplified.
    """

    def grade(self):
        key_sheet = self.key_document.formula_wb[self.sheet_name]
        sub_sheet = self.sub_document.formula_wb[self.sheet_name]

        cell_cord = self.grading_rubric.cell_cord

        try:
            key_formula = parse_formula(key_sheet[cell_cord].value)
            sub_formula = parse_formula(sub_sheet[cell_cord].value)
            is_similar = simplify(key_formula - sub_formula) == 0
            return self.grading_rubric.score if is_similar else 0
        except Exception as exc:
            print(f"Failed to compare formulas. Error:")
            print(exc)
            return 0
