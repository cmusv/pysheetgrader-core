from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.grading.report import GradingReport


class ConstantStrategy(BaseStrategy):
    """
    Used to grade Constant rubrics.
    This instance will check the alternative cells in the key if the submission value didn't match the key value
        in the main cell.
    """

    def grade(self):
        key_sheet = self.key_document.computed_value_wb[self.sheet_name]
        sub_sheet = self.sub_document.computed_value_wb[self.sheet_name]
        cell_coord = self.grading_rubric.cell_coord

        report = GradingReport()
        report.max_possible_score += self.grading_rubric.score
        sub_value = sub_sheet[cell_coord].value

        for coord in self.grading_rubric.get_all_cell_coord():
            if sub_value == key_sheet[coord].value:
                report.submission_score += self.grading_rubric.score
                break

        return report
