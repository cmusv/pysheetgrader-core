from pysheetgrader.grading.strategy.base import BaseStrategy


class ConstantStrategy(BaseStrategy):
    """
    Used to grade Constant rubrics.
    This instance will check the alternative cells in the key if the submission value didn't match the key value
        in the main cell.
    """
    def get_submitted_value(self):
        return self.sub_sheet_compute[self.cell_coord].value

    def check_correct(self, sub_cell_value, key_cell_value, key_coord):
        return self.value_matches(sub_cell_value, key_cell_value)

    def get_key_value(self, key_coord):
        return self.key_sheet_compute[key_coord].value
