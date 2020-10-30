from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.grading.report import GradingReport
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

        key_cell_value = key_sheet[cell_cord].value
        sub_cell_value = sub_sheet[cell_cord].value

        report = GradingReport()
        report.max_possible_score = self.grading_rubric.score

        try:
            key_formula = parse_formula(key_cell_value)
            sub_formula = parse_formula(sub_cell_value)
            is_similar = simplify(key_formula - sub_formula) == 0

            if is_similar:
                report.submission_score = self.grading_rubric.score

            print(f"[NaiveFormulaStrategy] GradingReport of grading: {report}")
            return report
        except Exception as exc:
            report.report_lines.append(f"Failed to compare formulas, key: {key_cell_value}, "
                                       f"submission: {sub_cell_value}. Error:")
            report.report_lines.append(f"{exc}")
            return report
