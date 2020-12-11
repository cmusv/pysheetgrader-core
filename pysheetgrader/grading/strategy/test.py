from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.grading.report import GradingReport
from pysheetgrader.formula_parser import parse_formula
from pysheetgrader.formula_parser import encode_cell_reference
from sympy import parse_expr

class TestRunStrategy(BaseStrategy):
    """
    Runs all available test for the corresponding rubric.
    """

    def grade(self):
        key_sheet = self.key_document.formula_wb[self.sheet_name]
        sub_sheet = self.sub_document.formula_wb[self.sheet_name]
        cell_coord = self.grading_rubric.cell_coord

        report = GradingReport()
        report.max_possible_score = self.grading_rubric.score

        sub_raw_formula = sub_sheet[cell_coord].value

        all_test_pass = True
        for test_case in self.grading_rubric.test_cases:
            if not self.test_run_match(test_case, sub_raw_formula):
                all_test_pass = False
                report.append_line(f"- {test_case.name} [FAIL]")
            else:
                report.append_line(f"- {test_case.name} [PASS]")

        if all_test_pass:
            report.submission_score = self.grading_rubric.score

        return report

    def test_run_match(self, test_case, sub_raw_formula):
        # TODO: Add implementation here.
        pass

