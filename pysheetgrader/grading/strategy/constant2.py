from pysheetgrader.grading.strategy.base import BaseStrategy


class ConstantStrategy(BaseStrategy):
    """
    Used to grade Constant rubrics.
    This instance will check the alternative cells in the key if the submission value didn't match the key value
        in the main cell.
    """

    def grade(self):
        '''
        loop through all cell cords
        setup report, validate inputs, parse formulas
        iterate through cells and compare to proper formula
            as soon as we get a correct answer, stop and sum
        
        if we must, subtract at the end
        '''
        ### setup 
        report = self.create_initial_report()
        cell_coord = self.grading_rubric.cell_coord
        key_sheet, sub_sheet = self.try_get_key_and_sub(report, computed=False)
        
        ### validate
        if key_sheet is None:
            return report

        ### grab the submitted value
        sub_cell_value = sub_sheet[cell_coord].value
 
        ### loop thru all keys, including alt cells
        for key_coord in self.grading_rubric.get_all_cell_coord():
            
            ### get proper answer
            key_cell_value = key_sheet[key_coord].value
            print('**********')
            print(key_coord, ' ', key_cell_value)
            print(sub_cell_value)
            
            ### compare to submitted
            is_correct = self.value_matches(sub_cell_value, key_cell_value)
            
            if is_correct and self.prereq_check(cell_coord, report):

                ### here is where we can add weird logic for different grading natures
                report.submission_score += self.get_correct_score(self.grading_rubric.grading_nature, self.grading_rubric.score)

                #### mark as correct
                self.grading_rubric.is_correct = True
                break
        
        ### subtract if necessary
        if  self.grading_rubric.grading_nature == 'negative' and not self.grading_rubric.is_correct:
            report.submission_score += self.grading_rubric.score
    
        return report
