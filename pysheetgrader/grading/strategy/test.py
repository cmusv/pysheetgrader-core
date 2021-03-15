from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.grading.test_case import GradingTestCase
from pysheetgrader.formula_parser import parse_formula
from pysheetgrader.formula_parser import encode_cell_reference
from pysheetgrader.custom_excel_formula import get_excel_formula_lambdas


class TestRunStrategy(BaseStrategy):
    """
    Runs all available test for the corresponding rubric.
    """

    def grade(self):
        report = self.create_initial_report()
        html_args = {'test_cases': [], 'all_test_pass': False}
        # Retrieving sheets
        try:
            sub_sheet = self.sub_document.formula_wb[self.sheet_name]
        except Exception as exc:
            report.append_line(f"{self.report_line_prefix}{exc}")
            return report

        # Grading cells
        cell_coord = self.grading_rubric.cell_coord
        sub_raw_formula = sub_sheet[cell_coord].value

        # Test runs
        if not self.report_line_prefix:
            self.report_line_prefix = ""

        all_test_pass = True
        for test_case in self.grading_rubric.test_cases:
            test_case_html_args = {'success': False, 'error': '', 'name': test_case.name}
            result_suffix = "PASS"
            try:
                result_match, result, lower_range, upper_range = self.test_run_match(test_case, sub_raw_formula)
                if not result_match:
                    all_test_pass = False
                    result_suffix = f"FAIL\n{self.report_line_prefix}Expected result between {lower_range} " \
                                    f"and {upper_range}, got {result} instead"
                    test_case_html_args['error'] = result_suffix
                else:
                    test_case_html_args['success'] = True
            except Exception as exc:
                # TODO: Add more profound exception error message later.
                all_test_pass = False
                result_suffix = f"FAIL\n{self.report_line_prefix}Exception found: Failed to process {sub_raw_formula}"
                test_case_html_args['error'] = result_suffix

            if not self.grading_rubric.hidden:
                report.append_line(f"{self.report_line_prefix}- {test_case.name}: {result_suffix}")
            html_args['test_cases'].append(test_case_html_args)

        if all_test_pass:
            report.submission_score = self.grading_rubric.score
        html_args['all_test_pass'] = all_test_pass

        report.report_html_args = html_args
        return report

    def test_run_match(self, test_case: GradingTestCase, sub_raw_formula: str):
        """
        Runs the passed test case against the passed formula.
        Will return tuple of (Boolean, calculated value, expected lower range, expected upper range).
            The Boolean will inform if the test run matches the expected values or not.
        :param test_case: GradingTestCase instance.
        :param sub_raw_formula: String of the raw formula.
        :return: Tuple of (Boolean, Float, Float, Float).
        """

        raw_inputs = test_case.inputs

        # Lowercase the inputs and the custom functions, because Sympy supports simple functions out-of-the box
        #   e.g. sqrt, sin
        lowercased_formula = sub_raw_formula.lower()
        encoded_inputs = {encode_cell_reference(cell_coord).lower(): raw_inputs[cell_coord]
                          for cell_coord in raw_inputs}
        local_dict = get_excel_formula_lambdas()
        local_dict.update(encoded_inputs)

        result = parse_formula(lowercased_formula, local_dict=local_dict)
        expected_lower_range = test_case.expected_output
        expected_upper_range = test_case.expected_output

        if test_case.output_delta:
            expected_lower_range -= test_case.output_delta
            expected_upper_range += test_case.output_delta

        result_match = expected_lower_range <= result <= expected_upper_range

        return result_match, result, expected_lower_range, expected_upper_range
