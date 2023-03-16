from pysheetgrader.sheet import Sheet

from pysheetgrader.grading.rubric import GradingRubric
from pysheetgrader.grading.rubric import GradingRubricType
from pysheetgrader.grading.report import GradingReport
from pysheetgrader.grading.report import GradingReportType
from pysheetgrader.grading.strategy.constant import ConstantStrategy
from pysheetgrader.grading.strategy.formula import NaiveFormulaStrategy
from pysheetgrader.grading.strategy.soft import SoftFormulaStrategy
from pysheetgrader.grading.strategy.test import TestRunStrategy
from pysheetgrader.grading.strategy.relative import RelativeStrategy
from pysheetgrader.grading.strategy.relative_f import RelativeFormulaStrategy
from pysheetgrader.grading.strategy.check2 import CheckStrategy

import re
import os

class Grader:
    """
    Responsible to grade submission Document instances against the key Document.
    """

    def __init__(self, key_document, is_testmode, is_debug):
        """
        Initializer of this instance.

        :param key_document: Document instance of a valid key.
        :param is_testmode: Boolean to indicate that autograder is running in test mode.
        :exception ValueError: Raises a ValueError if the passed `key_document` is not a valid key.
        """
        # Sanity check
        if not key_document or not key_document.is_valid_key():
            raise ValueError(f"The document passed is not a valid key. Path: {key_document.path}")

        # Attributes
        self.key_document = key_document
        self.grading_sheets = key_document.get_grading_sheets()
        self.correct_cells = []
        self.is_testmode = is_testmode
        self.is_debug = is_debug

    def grade(self, document):
        """
        Grade the passed `document` against this instance's key document.
        :param document: Document instance.
        :return: GradingReport instance of the grade.
        """
        report = GradingReport(GradingReportType.ASSIGNMENT)
        report.report_html_args = {'name': os.path.basename(document.path), 'sheets': []}
        report.append_line(f"========== START GRADING PROCESS ==========")

        for sheet in self.grading_sheets:
            report += self.grade_sheet(document, sheet)

        report.report_html_args['submission_score'] = report.submission_score
        report.report_html_args['max_possible_score'] = report.max_possible_score
        report.report_html_args['is_testmode'] = self.is_testmode
        if self.is_testmode:
            report.report_html_args['total_tests'] = report.total_tests
            report.report_html_args['passing_tests'] = report.passing_tests
        report.append_line(f"\nFinal score: {report.submission_score} / {report.max_possible_score}")
        return report

    def grade_sheet(self, document, sheet: Sheet):
        """
        Grade the passed `sheet_name` of the passed `document` against this instance's key document.

        :param document: Document instance.
        :param sheet: The Sheet object that represents the sheet to be graded
        :return: GradingReport instance of the grade for the sheet.
        """
        report = GradingReport(GradingReportType.SHEET)
        report.report_html_args = {'name': sheet.name, 'rubrics': [], 'minimum_work_reached': True,
                                   'minimum_work': sheet.minimum_work,
                                   'minimum_work_feedback': sheet.feedback,
                                   'submission_score': 0,
                                   'max_possible_score': 0}
        report.append_line(f"\n {'Running Tests' if self.is_testmode else 'Grading'} for sheet: {sheet.name}")
        rubrics = GradingRubric.create_rubrics_for_sheet(self.key_document, sheet, self.is_debug)
        for r in rubrics:
            sub_score = report.submission_score
            report += self.grade_sheet_by_rubric(document, sheet, r)
            if self.is_testmode:
                sheet.total_tests += 1
                if r.is_test_pass:
                    sheet.passing_tests += 1
            if r.is_correct:
                self.correct_cells.append(r.cell_coord)
            if r.killer and not r.is_correct:
                report.submission_score = 0
                if r.hidden:
                    report.append_line(f"This tab didn't pass its prerequisites! - Please contact the professor")
                    break
                else:
                    report.append_line(f"Cell {r.cell_coord} must be correct before this tab can be graded!")
                    break
        self.correct_cells = []
        if report.submission_score < sheet.minimum_work:
            # If the students don't give an assignment a real try,
            # we don't want to give any feedback or provide a grade.
            report.submission_score = 0.0
            report.report_lines = report.report_lines[:1]
            report.report_html_args['minimum_work_reached'] = False
            report.append_line(f"Minimum work ({sheet.minimum_work}) not reached: {sheet.feedback}")

        report.append_line(f"Score for {sheet.name} sheet: "
                           f"{report.submission_score} / {report.max_possible_score}")

        report.report_html_args['submission_score'] = report.submission_score
        report.report_html_args['max_possible_score'] = report.max_possible_score
        if self.is_testmode:
            report.total_tests = sheet.total_tests
            report.passing_tests = sheet.passing_tests
            report.report_html_args['total_tests'] = sheet.total_tests
            report.report_html_args['passing_tests'] = sheet.passing_tests
        return report

    def grade_sheet_by_rubric(self, document, sheet: Sheet, rubric):
        """
        Grades the `sheet_name` of the passed `document` using the passed `rubric`.

        :param document: Document instance.
        :param sheet: The Sheet object that represents the sheet to be graded
        :param rubric: GradingRubric instance.
        :return: GradingReport instance of the grade of the document's sheet.
        """
        report = GradingReport(GradingReportType.RUBRIC)

        html_args = {
            'id': rubric.cell_id,
            'cell': rubric.cell_coord,
            'hidden': rubric.hidden,
            'description': rubric.description,
            'test_params': rubric.test_params
        }
        if rubric.rubric_type == GradingRubricType.CONSTANT:
            if not rubric.hidden:
                report.append_line(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, constant value comparison")
            report += ConstantStrategy(self.key_document, document, sheet.name, rubric, self.correct_cells).grade()
            html_args['rubric_type'] = "Value check" if rubric.grading_nature == 'positive' else "Value check (penalty)"
        elif rubric.rubric_type == GradingRubricType.FORMULA:
            if not rubric.hidden:
                report.append_line(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, formula comparison")
            report += NaiveFormulaStrategy(self.key_document, document, sheet.name, rubric, self.correct_cells,
                                           report_line_prefix="\t").grade()
            html_args['rubric_type'] = "Formula check" if rubric.grading_nature == 'positive' else "Formula check (penalty)"
        elif rubric.rubric_type == GradingRubricType.SOFT_FORMULA:
            if not rubric.hidden:
                report.append_line(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, soft formula comparison")
            report += SoftFormulaStrategy(self.key_document, document, sheet.name, rubric, self.correct_cells,
                                          report_line_prefix="\t").grade()
            html_args['rubric_type'] = "Soft formula check" if rubric.grading_nature == 'positive' else "Soft Formula Check (penalty)"
        elif rubric.rubric_type == GradingRubricType.TEST:
            if not rubric.hidden:
                report.append_line(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, test case runs")
                report.append_line(f"\t- Test cases:")
            report += TestRunStrategy(self.key_document, document, sheet.name, rubric, self.correct_cells,
                                      report_line_prefix="\t\t").grade()
            html_args['rubric_type'] = "Test runs" if rubric.grading_nature == 'positive' else "Test Runs check (penalty)"
        elif rubric.rubric_type == GradingRubricType.RELATIVE:
            if not rubric.hidden:
                report.append_line(
                    f"    #{rubric.cell_id} Cell {rubric.cell_coord}, relative comparison (accept both "
                    f"constant and formula cell)")
            report += RelativeStrategy(self.key_document, document, sheet.name, rubric, self.correct_cells,
                                       report_line_prefix="\t").grade()
            html_args['rubric_type'] = "Relative formula check (accept both constant and formula cell)" if rubric.grading_nature == 'positive' else "Relative formula check (accept both constant and formula cell) (penalty)"
        elif rubric.rubric_type == GradingRubricType.RELATIVE_F:
            if not rubric.hidden:
                report.append_line(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, relative comparison (only accept "
                                   f"formula cell)")
            report += RelativeFormulaStrategy(self.key_document, document, sheet.name, rubric, self.correct_cells,
                                              report_line_prefix="\t").grade()
            html_args['rubric_type'] = "Relative formula check (only accept formula cell)" if rubric.grading_nature == 'positive' else "Relative formula (penalty)"
        elif  rubric.rubric_type == GradingRubricType.CHECK:
            if not rubric.hidden:
                report.append_line(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, check result comparison ")
            report += CheckStrategy(self.key_document, document, sheet.name, rubric, self.correct_cells).grade()
            html_args['rubric_type'] = "Result check" if rubric.grading_nature == 'positive' else "Result check (penalty)"
        
        feedback = self.render_failure_message(document, sheet.name, rubric.fail_msg) if rubric.fail_msg else ""

        if not self.is_testmode:
            if not rubric.hidden:
                if rubric.description:
                    report.append_line(f"\t- Description: {rubric.description}")
                if rubric.fail_msg and not rubric.is_correct:
                    report.append_line(f"\t- Feedback: {feedback}")
                    html_args['feedback'] = feedback
                report.append_line(f"\t- Score: {report.submission_score} / {report.max_possible_score}")

            if rubric.hidden and not rubric.is_correct:
                # student does not pass the hidden cell, show hint
                html_args['hidden_hint'] = {'hint': feedback}
                report.append_line(f"    #{rubric.cell_id} (Hidden): {feedback}")
        else:
            report.append_line(f"\t- Test: {rubric.test_params.get('name', '')}")
            rubric.is_test_pass = (((rubric.test_params.get('expected_score', None) is None) or rubric.test_params['expected_score'] == report.submission_score) and rubric.is_correct and rubric.test_params.get("expected_result", "correct") == "correct") or \
                                        ((not rubric.is_correct) and rubric.test_params.get("expected_result", "correct") == "incorrect")
            status = "PASS" if rubric.is_test_pass else f"FAIL: {rubric.test_params.get('failure_message', '')}"
            report.append_line(f"\t- Status: {status}")

        html_args['submission_score'] = report.submission_score
        html_args['max_possible_score'] = report.max_possible_score
        html_args['is_correct'] = rubric.is_correct
        html_args['is_test_pass'] = rubric.is_test_pass
        report.report_html_args.update(html_args)
        return report

    @staticmethod
    def render_failure_message(document, sheet_name, fail_msg_template: str):
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
        pattern = re.compile(r"(\$)([A-Z]+\d+)")
        referred_cells = []
        for match in re.finditer(pattern, fail_msg_template):
            cell_coord = match.group(2)  # second group is whatever after $
            referred_cells.append(document.computed_value_wb[sheet_name][cell_coord])

        return re.sub(pattern, '{}', fail_msg_template).format(*[c.value for c in referred_cells])
