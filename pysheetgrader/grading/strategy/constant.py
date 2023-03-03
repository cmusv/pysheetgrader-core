from pysheetgrader.grading.strategy.base import BaseStrategy


class ConstantStrategy(BaseStrategy):
    """
    Used to grade Constant rubrics.
    This instance will check the alternative cells in the key if the submission value didn't match the key value
        in the main cell.
    """
    def get_submitted_value(self, sub_sheet, cell_coord):
        return sub_sheet[cell_coord].value

    def check_correct(self, sub_cell_value, key_cell_value):
        return self.value_matches(sub_cell_value, key_cell_value)

    def get_key_value(self, key_sheet, key_coord):
        return key_sheet[key_coord].value
