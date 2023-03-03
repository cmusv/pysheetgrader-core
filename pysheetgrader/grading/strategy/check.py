from pysheetgrader.grading.strategy.base import BaseStrategy

class CheckStrategy(BaseStrategy):
    """
    Used to grade Check rubrics.
    This instance will check the alternative cells in the key if the submission value didn't match the key value
        in the main cell.
    """
    def grade(self):
        report = self.create_initial_report()

        # # Retrieving sheets
        key_sheet,_ = self.try_get_key_and_sub(computed=False)
        _,sub_sheet = self.try_get_key_and_sub(computed=True)

        if key_sheet is None:
            return report

        try:
            # Grading cells
            cell_coord = self.grading_rubric.cell_coord
            key_raw_formula = key_sheet[cell_coord].value
            sub_evaluated_value = self.get_formula_value(sub_sheet, key_raw_formula)
            for coord in self.grading_rubric.get_result_cell_coord():

                # if a result or alt cell is specified
                if coord is not None:
                    key_evaluated_value = key_sheet[coord].value
                # else check the value of the given cell in the key
                else:
                    key_evaluated_value = self.get_formula_value(key_sheet, key_raw_formula)

                if self.value_matches(sub_evaluated_value, key_evaluated_value):
                    if self.grading_rubric.prereq_cells is not None:
                        if self.prereq_check(cell_coord,report):
                            report.submission_score += self.grading_rubric.score
                            self.grading_rubric.is_correct = True
                        else:
                            break
                    else:
                        report.submission_score += self.grading_rubric.score
                        self.grading_rubric.is_correct = True
                    break

            return report
        except Exception as exc:
            report.append_line(f"{self.report_line_prefix}Error: {exc}")
            report.report_html_args['error'] = f"Error: {exc}"
            return report
        
