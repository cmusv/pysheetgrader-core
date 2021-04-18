from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.grading.test_case import GradingTestCase
from pysheetgrader.formula_parser import parse_formula
from pysheetgrader.formula_parser import encode_cell_reference
from pysheetgrader.formula_parser import transform_excel_formula_to_sympy
from pysheetgrader.custom_excel_formula import get_excel_formula_lambdas
import re
# import numpy as np


class TestRunStrategy(BaseStrategy):
    """
    Runs all available test for the corresponding rubric.
    """

    def grade(self):
        report = self.create_initial_report()
        html_args = {'test_cases': [], 'all_test_pass': False}

        # Retrieving sheets
        _, sub_sheet = self.try_get_key_and_sub(report)
        if sub_sheet is None:
            return report

        # Grading cells
        cell_coord = self.grading_rubric.cell_coord
        sub_raw_formula = sub_sheet[cell_coord].value

        # Test runs
        if not self.report_line_prefix:
            self.report_line_prefix = ""

        all_test_pass = True
        #print("self.grading_rubric.test_cases: ", self.grading_rubric.test_cases)
        feedback = None
        for test_case in self.grading_rubric.test_cases:
            expected_output = test_case.expected_output
            print("test case fail msg: ", test_case.failmsg)
            temp2 = str(expected_output)
            # print("temp2: ", temp2)
            temp = temp2.split('.')
            # print("temp: ", temp)
            significant = len(temp[-1])
            test_case_html_args = {'success': False, 'error': '', 'name': test_case.name}
            result_suffix = "PASS"
            try:
                result_match, result, lower_range, upper_range = self.test_run_match(test_case, sub_raw_formula)
                actual_result = round(result, -significant)
                if not result_match:
                    all_test_pass = False
                    result_suffix = f"FAIL\n{self.report_line_prefix}Expected result between {lower_range} " \
                                    f"and {upper_range}, got {result} instead"
                    test_case_html_args['error'] = result_suffix
                    # print("*****feedback inside test **********: ", test_case.failmsg)
                    # print("I am here")
                    # print("sheet name: ", self.sheet_name)
                    # print(type(self.sub_document))
                    # print(type(self.sheet_name))
                    # print(type(test_case.failmsg))
                    # actual_str = str(actual_result)[:(significant+1)]
                    # print("expected: ", temp2)
                    # print("actual slice: ", actual_str)
                    fail_template = test_case.failmsg.replace("$actual", str(int(actual_result)))
                    fail_template = fail_template.replace("$expected", str(expected_output))
                    feedback = self.failure_message_testcase(self.sub_document, self.sheet_name, fail_template)# if test_case.failmsg else ""
                    # print("test case failed!")
                    
                    print("feedback for failed test: ", feedback)
                    #report.append_line(f"feedback: {feedback}")
                    #print("feedback: ", feedback)
                else:
                    test_case_html_args['success'] = True
            except Exception as exc:
                # TODO: Add more profound exception error message later.
                all_test_pass = False
                result_suffix = f"FAIL\n{self.report_line_prefix}Exception found: Failed to process {sub_raw_formula}"
                test_case_html_args['error'] = result_suffix

            if not self.grading_rubric.hidden:
                report.append_line(f"{self.report_line_prefix}- {test_case.name}: {result_suffix}")
                if feedback is not None:
                    report.append_line(f"{self.report_line_prefix}- {test_case.name} feedback: {feedback}")

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

        lowercased_formula = transform_excel_formula_to_sympy(sub_raw_formula)
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

    #@staticmethod
    def failure_message_testcase(self, document, sheet_name, fail_msg_template: str):
        """
        Render generic failure message with failure message template. For example, if template is
            "This cell should have used standard deviation, which was $B3 according to your calculation."

        The rendered failure message can be
            "This cell should have used standard deviation, which was 15 according to your calculation."

        :param document: Document instance.
        :param sheet_name: String value of the sheet name.
        :param fail_msg_template: String value of the failure message template.
        :return: String value of rendered failure message.
        """
        # print("Inside failure message testcases ")
        # print("sheet name: ", sheet_name)
        # print("fail template: ", fail_msg_template)
        pattern = re.compile(r"(\$)([A-Z]+\d+)")
        # pattern2 = re.compile(r"(\$)([a-z]+)")
        referred_cells = []
        for match in re.finditer(pattern, fail_msg_template):
            cell_coord = match.group(2)  # second group is whatever after $
            # print("cell_coord: ", cell_coord)
            referred_cells.append(document.computed_value_wb[sheet_name][cell_coord])
        return re.sub(pattern, '{}', fail_msg_template).format(*[c.value for c in referred_cells])
