from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.grading.test_case import GradingTestCase
from pysheetgrader.grading.rubric import GradingRubric
from pysheetgrader.grading.report import GradingReport
from pysheetgrader.formula_parser import parse_formula
from pysheetgrader.formula_parser import encode_cell_reference
from pysheetgrader.document import Document
from sympy import parse_expr


class TestRunStrategy(BaseStrategy):
    """
    Runs all available test for the corresponding rubric.
    """

    def __init__(self, key_document: Document, sub_document: Document, sheet_name,
                 grading_rubric: GradingRubric,  report_line_prefix: str = ""):
        self.report_line_prefix = report_line_prefix
        super().__init__(key_document, sub_document, sheet_name,  grading_rubric)

    def grade(self):
        sub_sheet = self.sub_document.formula_wb[self.sheet_name]
        cell_coord = self.grading_rubric.cell_coord

        report = GradingReport()
        report.max_possible_score = self.grading_rubric.score

        sub_raw_formula = sub_sheet[cell_coord].value

        # Test runs
        if not self.report_line_prefix:
            self.report_line_prefix = ""

        all_test_pass = True
        for test_case in self.grading_rubric.test_cases:
            result_suffix = "PASS"
            try:
                if not self.test_run_match(test_case, sub_raw_formula):
                    all_test_pass = False
                    result_suffix = "FAIL"
            except Exception as exc:
                # TODO: Add more profound exception error message later.
                all_test_pass = False
                result_suffix = f"FAIL\n{self.report_line_prefix}Exception found: {exc}"

            report.append_line(f"{self.report_line_prefix}- {test_case.name}: {result_suffix}")

        if all_test_pass:
            report.submission_score = self.grading_rubric.score

        return report

    def test_run_match(self, test_case: GradingTestCase, sub_raw_formula: str):

        raw_inputs = test_case.inputs
        encoded_inputs = {encode_cell_reference(cell_coord): raw_inputs[cell_coord] for cell_coord in raw_inputs}
        # TODO: Add  option to prevent expansion of cells here
        encoded_formula = parse_formula(sub_raw_formula)

        result = parse_expr(encoded_formula, local_dict=encoded_inputs)

        if test_case.output_delta:
            delta = test_case.output_delta
            expected_output = test_case.expected_output
            return (expected_output - delta) <= result <= (expected_output + delta)
        else:
            return result == test_case.expected_output
