from pysheetgrader.custom_excel_formula import get_excel_formula_lambdas
from pysheetgrader.grading.strategy.constant import ConstantStrategy
from pysheetgrader.formula_parser import parse_formula


class SoftFormulaStrategy(ConstantStrategy):
    """
    1. If the cell does not contain a formula, no credit.
    2. If the cell contains a formula, grade it like a constant formula
        (compare cell's evaluated result to key's evaluated result)
    """

    def grade(self):
        report = self.create_initial_report()

        # Retrieving sheets
        try:
            key_sheet = self.key_document.formula_wb[self.sheet_name]
            sub_sheet = self.sub_document.formula_wb[self.sheet_name]
        except Exception as exc:
            report.append_line(f"{self.report_line_prefix}{exc}")
            report.report_html_args['error'] = exc
            return report

        # Grading cells
        cell_coord = self.grading_rubric.cell_coord
        custom_formulas = get_excel_formula_lambdas()

        try:
            sub_cell_value = sub_sheet[cell_coord].value
            _ = parse_formula(sub_cell_value, local_dict=custom_formulas)

            # Comparison
            for key_coord in self.grading_rubric.get_all_cell_coord():
                curr_cell_value = sub_sheet[key_coord].value
                if len(curr_cell_value) == 1 and curr_cell_value[0] == '=':
                    report.append_line(f"\t- Formula is missing.")
                    return report
                if any(c.isalpha() for c in curr_cell_value):
                    report.append_line(f"\t- Found Formula:", curr_cell_value)
                    return super().grade()
                else:
                    report.append_line(f"\t- Formula is missing.")
                    return report
        except Exception as exc:
            # TODO: Revisit whether we should print the comparison key value here.
            #   It might leak the answers to the students, though.
            report.append_line(f"{self.report_line_prefix}Error: {exc}")
            report.report_html_args['error'] = f"Error: {exc}"
            return report
