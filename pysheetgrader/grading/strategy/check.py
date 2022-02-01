from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.custom_excel_formula import get_excel_formula_lambdas
from pysheetgrader.formula_parser import parse_formula_inputs, parse_formula, \
    encode_cell_reference, transform_excel_formula_to_sympy

class CheckStrategy(BaseStrategy):
    """
    Used to grade Check rubrics.
    This instance will check the alternative cells in the key if the submission value didn't match the key value
        in the main cell.
    """
    def grade(self):
        report = self.create_initial_report()

        # # Retrieving sheets
        key_sheet,_ = self.try_get_key_and_sub(report, computed=False)
        _,sub_sheet = self.try_get_key_and_sub(report, computed=True)

        if key_sheet is None:
            return report

        try:
            # Grading cells
            cell_coord = self.grading_rubric.cell_coord
            key_raw_formula = key_sheet[cell_coord].value
            key_value = self.get_formula_value(sub_sheet, key_raw_formula)
            for coord in self.grading_rubric.get_result_cell_coord():
                if coord is not None:
                    if self.value_matches(key_value, key_sheet[coord].value):
                        if self.grading_rubric.prereq_cells is not None:
                            if self.prereq_check(cell_coord,report):
                                report.submission_score += self.grading_rubric.score
                            else:
                                break
                        else:
                            report.submission_score += self.grading_rubric.score
                        break
                elif key_value:
                    if self.grading_rubric.prereq_cells is not None:
                        if self.prereq_check(cell_coord, report):
                            report.submission_score += self.grading_rubric.score
                    else:
                        report.submission_score += self.grading_rubric.score
                    break
            return report
        except Exception as exc:
            report.append_line(f"{self.report_line_prefix}Error: {exc}")
            report.report_html_args['error'] = f"Error: {exc}"
            return report
        

    def get_formula_value(self, sub_sheet, key_raw_formula: str):
        """
        Evaluate the relative value from student's submission cells, using the formula from the Key cell.

        :param sub_sheet: the student's submission sheet
        :param key_raw_formula: the String value of the relative formula from the Key.
        :return:
        """
        lowercased_formula = transform_excel_formula_to_sympy(key_raw_formula)
        
        # extract input coordinates
        input_coords = parse_formula_inputs(key_raw_formula, encoded=False)
        encoded_inputs = {encode_cell_reference(coord): sub_sheet[coord].value for coord in input_coords}
        local_dict = get_excel_formula_lambdas()
        local_dict.update(encoded_inputs)

        result = parse_formula(lowercased_formula, local_dict)
        return result