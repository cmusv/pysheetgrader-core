from pysheetgrader.custom_excel_formula import get_excel_formula_lambdas
from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.formula_parser import parse_formula
from sympy import simplify


class NaiveFormulaStrategy(BaseStrategy):
    """
    Naively compare whether the formula between key and submission is the same when they're simplified.
    This instance will check the alternative cells in the key if the submission formula didn't match the key formula
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
        if key_sheet is None or not self.prereq_check(cell_coord, report):
            return report

        ### grab the submitted formula
        custom_formulas = get_excel_formula_lambdas()
        sub_cell_value = sub_sheet[cell_coord].value
        sub_formula = parse_formula(sub_cell_value, local_dict=custom_formulas)

        ### loop thru all keys, including alt cells
        for key_coord in self.grading_rubric.get_all_cell_coord():
            
            ### get proper answer and parse
            key_cell_value = key_sheet[key_coord].value
            key_formula = parse_formula(key_cell_value, local_dict=custom_formulas)
            
            ### compare to submitted
            is_similar = simplify(key_formula - sub_formula) == 0
            
            if is_similar:

                ### here is where we can add weird logic for different grading natures
                report.submission_score += self.get_correct_score(self.grading_rubric.grading_nature, self.grading_rubric.score)

                #### mark as correct
                self.grading_rubric.is_correct = True
                break
        
        ### subtract if necessary
        if  self.grading_rubric.grading_nature == 'negative' and not self.grading_rubric.is_correct:
            report.submission_score += self.grading_rubric.score
    
        return report

