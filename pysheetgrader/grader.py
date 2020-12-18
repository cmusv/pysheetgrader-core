from pysheetgrader.grading.rubric import GradingRubric
from pysheetgrader.grading.rubric import GradingRubricType
from pysheetgrader.grading.report import GradingReport
from pysheetgrader.grading.strategy.constant import ConstantStrategy
from pysheetgrader.grading.strategy.formula import NaiveFormulaStrategy
from pysheetgrader.grading.strategy.test import TestRunStrategy


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

    def grade(self, document):
        """
        Grade the passed `document` against this instance's key document.
        :param document: Document instance.
        :return: GradingReport instance of the grade.
        """
        report = GradingReport()
        report.append_line(f"========== START GRADING PROCESS ==========")

        for sheet_name in self.grading_sheet_names:
            report += self.grade_sheet(document, sheet_name)

        report.append_line(f"\nFinal score: {report.submission_score} / {report.max_possible_score}")
        return report

    def grade_sheet(self, document, sheet_name):
        """
        Grade the passed `sheet_name` of the passed `document` against this instance's key document.
        :param document: Document instance.
        :param sheet_name: String value of the sheet name that should be graded.
        :return: GradingReport instance of the grade for the sheet.
        """
        report = GradingReport()
        report.append_line(f"\nGrading for sheet: {sheet_name}")
        rubrics = GradingRubric.create_rubrics_for_sheet(self.key_document, sheet_name)
        for r in rubrics:
            report += self.grade_sheet_by_rubric(document, sheet_name, r)

        return report

    def grade_sheet_by_rubric(self, document, sheet_name, rubric):
        """
        Grades the `sheet_name` of the passed `document` using the passed `rubric`.
        :param document: Document instance.
        :param sheet_name: String value of the sheet name.
        :param rubric: GradingRubric instance.
        :return: GradingReport instance of the grade of the document's sheet.
        """
        report = GradingReport()

        if rubric.rubric_type == GradingRubricType.CONSTANT:
            report.append_line(f"\t- Cell {rubric.cell_coord}, constant value comparison.")
            report += ConstantStrategy(self.key_document, document, sheet_name, rubric).grade()
        elif rubric.rubric_type == GradingRubricType.FORMULA:
            report.append_line(f"\t- Cell {rubric.cell_coord}, formula comparison.")
            strategy = NaiveFormulaStrategy(self.key_document, document, sheet_name, rubric, report_line_prefix="\t")
            report += strategy.grade()
        else:
            report.append_line(f"\t- Cell {rubric.cell_coord}, test case runs.")
            report.append_line(f"\t\tTest cases:")
            strategy = TestRunStrategy(self.key_document, document, sheet_name, rubric, report_line_prefix="\t\t")
            report += strategy.grade()

        report.append_line(f"\tScore: {report.submission_score} / {report.max_possible_score}")
        return report
