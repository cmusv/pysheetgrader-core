from pysheetgrader.grading.rubric import GradingRubric
from pysheetgrader.grading.rubric import GradingRubricType
from pysheetgrader.grading.report import GradingReport
from pysheetgrader.grading.report import GradingReportType
from pysheetgrader.grading.strategy.constant import ConstantStrategy
from pysheetgrader.grading.strategy.formula import NaiveFormulaStrategy
from pysheetgrader.grading.strategy.soft import SoftFormulaStrategy
from pysheetgrader.grading.strategy.test import TestRunStrategy

import re
import os


class Grader:
    """
    Responsible to grade submission Document instances against the key Document.
    """

    def __init__(self, key_document):
        """
        Initializer of this instance.

        :param key_document: Document instance of a valid key.
        :exception ValueError: Raises a ValueError if the passed `key_document` is not a valid key.
        """
        # Sanity check
        if not key_document or not key_document.is_valid_key():
            raise ValueError(f"The document passed is not a valid key. Path: {key_document.path}")

        # Attributes
        self.key_document = key_document
        self.grading_sheet_names = key_document.grading_sheet_names()
        self.minimum_work = key_document.get_minimum_work()
        print("minimum_work: ", self.minimum_work)
        self.minimum_work_feedback = key_document.get_minimum_work_feedback()
        print("feedback min: ", self.minimum_work_feedback)

    def grade(self, document):
        """
        Grade the passed `document` against this instance's key document.
        :param document: Document instance.
        :return: GradingReport instance of the grade.
        """
        report = GradingReport(GradingReportType.ASSIGNMENT)
        report.report_html_args = {'name': os.path.basename(document.path), 'sheets': []}
        report.append_line(f"========== START GRADING PROCESS ==========")

        index = 0
        for sheet_name in self.grading_sheet_names:
            report += self.grade_sheet(document, sheet_name, index)
            #report += report_orig#self.grade_sheet(document, sheet_name, index)
            index = index + 1


        report.report_html_args['submission_score'] = report.submission_score
        report.report_html_args['max_possible_score'] = report.max_possible_score
        report.append_line(f"\nFinal score: {report.submission_score} / {report.max_possible_score}")
        return report

    def grade_sheet(self, document, sheet_name, index):
        """
        Grade the passed `sheet_name` of the passed `document` against this instance's key document.
        :param document: Document instance.
        :param sheet_name: String value of the sheet name that should be graded.
        :return: GradingReport instance of the grade for the sheet.
        """
        report = GradingReport(GradingReportType.SHEET)
        report.report_html_args = {'name': sheet_name, 'rubrics': []}
        report.append_line(f"\nGrading for sheet: {sheet_name}")
        rubrics = GradingRubric.create_rubrics_for_sheet(self.key_document, sheet_name)
        temp_report = []
        for r in rubrics:
            orig_report, temp= self.grade_sheet_by_rubric(document, sheet_name, r, index, temp_report)
            temp_report.extend(temp)
            report += orig_report

        if report.submission_score > self.minimum_work[index]:
            for result in temp_report:
                report.append_line(result)
            report.append_line(f"Score for {sheet_name} sheet: "
                           f"{report.submission_score} / {report.max_possible_score}")
        else:
            report.append_line(f"Score for {sheet_name} sheet:{self.minimum_work_feedback[index]}")
        report.report_html_args['submission_score'] = report.submission_score
        report.report_html_args['max_possible_score'] = report.max_possible_score
        return report

    def grade_sheet_by_rubric(self, document, sheet_name, rubric, index, temp_report):
        """
        Grades the `sheet_name` of the passed `document` using the passed `rubric`.
        :param document: Document instance.
        :param sheet_name: String value of the sheet name.
        :param rubric: GradingRubric instance.
        :return: GradingReport instance of the grade of the document's sheet.
        """
        report = GradingReport(GradingReportType.RUBRIC)
        threshold = self.minimum_work[index]
        threshold_feedback = self.minimum_work_feedback[index]
        temp_report = []
        html_args = {'id': rubric.cell_id, 'cell': rubric.cell_coord, 'hidden': rubric.hidden,
                     'description': rubric.description}
        if rubric.rubric_type == GradingRubricType.CONSTANT:
            if not rubric.hidden:
                #report.append_line(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, constant value comparison")
                temp_report.append(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, constant value comparison")
            orig_report = ConstantStrategy(self.key_document, document, sheet_name, rubric).grade()
            report += orig_report
            #temp_report.extend(report_copy)
            html_args['rubric_type'] = "Value check"
        elif rubric.rubric_type == GradingRubricType.FORMULA:
            if not rubric.hidden:
                #report.append_line(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, formula comparison")
                temp_report.append(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, formula comparison")
            strategy = NaiveFormulaStrategy(self.key_document, document, sheet_name, rubric, report_line_prefix="\t")
            orig_report, report_copy = strategy.grade() 
            report+= orig_report
            temp_report.extend(report_copy)
            html_args['rubric_type'] = "Formula check"
        elif rubric.rubric_type == GradingRubricType.SOFT_FORMULA:
            #report.append_line(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, soft formula comparison")
            temp_report.append(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, soft formula comparison")
            strategy = SoftFormulaStrategy(self.key_document, document, sheet_name, rubric, report_line_prefix="\t")
            orig_report, report_copy = strategy.grade() 
            report+= orig_report
            temp_report.extend(report_copy)
            html_args['rubric_type'] = "Soft formula check"
        else:
            if not rubric.hidden:
                # report.append_line(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, test case runs")
                # report.append_line(f"\t- Test cases:")
                temp_report.append(f"    #{rubric.cell_id} Cell {rubric.cell_coord}, test case runs")
                temp_report.append(f"\t- Test cases:")
            strategy = TestRunStrategy(self.key_document, document, sheet_name, rubric, report_line_prefix="\t\t")
            orig_report, report_copy = strategy.grade() 
            report+= orig_report
            temp_report.extend(report_copy)
            html_args['rubric_type'] = "Test runs"

        feedback = self.render_failure_message(document, sheet_name, rubric.fail_msg) if rubric.fail_msg else ""

        if not rubric.hidden:
            if rubric.description:
                #report.append_line(f"\t- Description: {rubric.description}")
                temp_report.append(f"\t- Description: {rubric.description}")
            if rubric.fail_msg and report.submission_score < report.max_possible_score:
                # report.append_line(
                #     f"\t- Feedback: {feedback}")
                temp_report.append(
                    f"\t- Feedback: {feedback}")
                html_args['feedback'] = feedback
            # else:
            #     report.append_line(f"\t- Score: {threshold_feedback}")

        if rubric.hidden and report.submission_score < report.max_possible_score:
            # student does not pass the hidden cell, show hint
            html_args['hidden_hint'] = {'hint': feedback}
            report.append_line(f"    #{rubric.cell_id} (Hidden): {feedback}")

        #print("I am here")
        temp_report.append(f"\t- Score: {report.submission_score} / {report.max_possible_score}")
        html_args['submission_score'] = report.submission_score
        html_args['max_possible_score'] = report.max_possible_score
        report.report_html_args.update(html_args)
        return report, temp_report

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
