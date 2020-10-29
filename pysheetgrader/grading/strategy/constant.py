from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.grading.report import Report


class ConstantStrategy(BaseStrategy):
    """
    Used to grade Constant rubrics.
    """

    def grade(self):
        key_sheet = self.key_document.computed_value_wb[self.sheet_name]
        sub_sheet = self.sub_document.computed_value_wb[self.sheet_name]
        cell_cord = self.grading_rubric.cell_cord

        report = Report()
        report.max_possible_score += self.grading_rubric.score

        if key_sheet[cell_cord].value == sub_sheet[cell_cord].value:
            report.submission_score += self.grading_rubric.score

        return report
