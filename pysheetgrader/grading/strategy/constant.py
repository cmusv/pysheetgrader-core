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
        key_sheet, sub_sheet = self.try_get_key_and_sub(report, computed=True)
        if key_sheet is None:
            return report

        # Grading cells
        cell_coord = self.grading_rubric.cell_coord
        sub_value = sub_sheet[cell_coord].value
        
        # Using a flag to check alternative cells for negative grading nature
        checkflag_altcells = False
        
        
        for coord in self.grading_rubric.get_all_cell_coord():
            if self.grading_rubric.grading_nature == 'positive':
                if self.value_matches(sub_value, key_sheet[coord].value):
                    report.submission_score += self.grading_rubric.score
            elif self.grading_rubric.grading_nature == 'negative':
                if not self.value_matches(sub_value, key_sheet[coord].value):
                    checkflag_altcells = True
                else:
                    checkflag_altcells = False
                    break   
            else:
                # TODO: Revisit if we need to print an error here.
                print("Constant Strategy - if new grading nature error needs to be added")
                continue
        
        if checkflag_altcells and self.grading_rubric.grading_nature == 'negative':
            report.submission_score += self.grading_rubric.score
        return report
    
    