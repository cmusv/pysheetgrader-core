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
        report = self.create_initial_report()

        # Retrieving sheets
        key_sheet, sub_sheet = self.try_get_key_and_sub(report, computed=False)
        if key_sheet is None:
            return report

        # Grading cells
        cell_coord = self.grading_rubric.cell_coord
        custom_formulas = get_excel_formula_lambdas()
        

                
        # Using a flag to check alternative cells for negative grading nature
        checkflag_altcells = False
        
        try:
            sub_cell_value = sub_sheet[cell_coord].value
            sub_formula = parse_formula(sub_cell_value, local_dict=custom_formulas)
            # Comparison
            for key_coord in self.grading_rubric.get_all_cell_coord():
                
                key_cell_value = key_sheet[key_coord].value
                key_formula = parse_formula(key_cell_value, local_dict=custom_formulas)
                is_similar = simplify(key_formula - sub_formula) == 0
                
                if self.grading_rubric.grading_nature == 'positive':
                    if is_similar:
                        if self.grading_rubric.prereq_cells is not None:
                            if self.prereq_check(cell_coord, report):
                                report.submission_score += self.grading_rubric.score
                            else:
                                return report
                        else:
                            report.submission_score += self.grading_rubric.score
                elif self.grading_rubric.grading_nature == 'negative':
                    if not is_similar:
                        checkflag_altcells = True
                    else:
                        checkflag_altcells = False
                        break 
                else:
                    # TODO: Revisit if we need to print an error here.
                    print("Formula Strategy - if new grading nature error needs to be added")
                    continue
            
            if checkflag_altcells and self.grading_rubric.grading_nature == 'negative':
                report.submission_score += self.grading_rubric.score

            return report
        except Exception as exc:
            # TODO: Revisit whether we should print the comparison key value here.
            #   It might leak the answers to the students, though.
            if self.grading_rubric.grading_nature == 'negative':
                report.submission_score += self.grading_rubric.score
            report.append_line(f"{self.report_line_prefix}Error: {exc}")
            report.report_html_args['error'] = f"Error: {exc}"
            return report
