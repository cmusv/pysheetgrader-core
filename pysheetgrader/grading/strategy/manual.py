from pysheetgrader.grading.strategy.base import BaseStrategy


class ManualStrategy(BaseStrategy):
    """
    Used to grade Manual rubrics.
    """
    def grade(self):
        raise NotImplementedError

    def get_submitted_value(self):
        return self.sub_sheet_raw[self.cell_coord].value if self.sub_sheet_raw[self.cell_coord].value else self.grading_rubric.fail_msg
