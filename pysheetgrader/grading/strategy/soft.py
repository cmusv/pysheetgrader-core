from pysheetgrader.grading.strategy.constant import ConstantStrategy


class SoftFormulaStrategy(ConstantStrategy):
    """
    1. If the cell does not contain a formula, no credit.
    2. If the cell contains a formula, grade it like a constant formula
        (compare cell's evaluated result to key's evaluated result)
    """
    def get_submitted_value(self):
        return self.sub_sheet_raw[self.cell_coord].value

    def check_correct(self, sub_cell_value, key_cell_value, key_coord):
         # TODO: REFACTOR
        curr_cell_value = self.sub_sheet_raw[key_coord].value
        
        if len(curr_cell_value) == 1 and curr_cell_value[0] == '=':
            return False

        if any(c.isalpha() for c in curr_cell_value):
            return super().check_correct(sub_cell_value, key_cell_value, key_coord)

    def get_key_value(self, key_coord):
        return self.key_sheet_compute[key_coord].value