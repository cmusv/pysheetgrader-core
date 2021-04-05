from pysheetgrader.grading.strategy.base import BaseStrategy


class ConstantStrategy(BaseStrategy):
    """
    Used to grade Constant rubrics.
    This instance will check the alternative cells in the key if the submission value didn't match the key value
        in the main cell.
    """

    def grade(self):
        report = self.create_initial_report()

        # Retrieving sheets
        key_sheet, sub_sheet = self.try_get_key_and_sub(report)
        if key_sheet is None:
            return report

        # Grading cells
        cell_coord = self.grading_rubric.cell_coord
        sub_value = sub_sheet[cell_coord].value

        for coord in self.grading_rubric.get_all_cell_coord():
            if self.value_matches(sub_value, key_sheet[coord].value):
                report.submission_score += self.grading_rubric.score
                break

        return report
