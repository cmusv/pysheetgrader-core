from pysheetgrader.grading.strategy.base import BaseStrategy

class CheckStrategy(BaseStrategy):
    """
    Used to grade Check rubrics.
    This instance will check the alternative cells in the key if the submission value didn't match the key value
        in the main cell.
    """
    def get_submitted_value(self):
        key_raw_formula = self.key_sheet_raw[self.cell_coord].value
        return self.get_formula_value(self.sub_sheet_compute, key_raw_formula)

    def get_key_value(self, key_coord):
        '''
        template pattern: this is how to get the key value
        '''
        key_raw_formula = self.key_sheet_raw[self.cell_coord].value
        # if we have a result coord, use that
        if self.grading_rubric.result_coord is not None:
            return self.key_sheet_compute[self.grading_rubric.result_coord].value
        # else check the value of the given cell in the key
        else:
            return self.get_formula_value(self.key_sheet_raw, key_raw_formula)    
    
    def check_correct(self, sub_cell_value, key_cell_value, key_coord):
        '''
        template pattern: this is how to check if the value is correct
        '''
        if(key_coord and key_coord in self.grading_rubric.alt_cells):
            # we must get the sub cell value again if it is a formula
             # TODO: consider?
            try:
                sub_cell_value = self.get_formula_value(self.sub_sheet_compute, self.key_sheet_raw[key_coord].value)
            except:
                sub_cell_value = sub_cell_value
        
        return self.value_matches(sub_cell_value, key_cell_value)

    def get_key_coord_set(self):
        return self.grading_rubric.get_result_cell_coord()