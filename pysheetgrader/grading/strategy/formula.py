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
        try:
            key_sheet = self.key_document.formula_wb[self.sheet_name]
            sub_sheet = self.sub_document.formula_wb[self.sheet_name]
        except Exception as exc:
            report.append_line(f"{self.report_line_prefix}{exc}")
            return report

        # Grading cells
        cell_coord = self.grading_rubric.cell_coord

        try:
            sub_cell_value = sub_sheet[cell_coord].value
            sub_formula = parse_formula(sub_cell_value)

            # Comparison
            for key_coord in self.grading_rubric.get_all_cell_coord():
                key_cell_value = key_sheet[key_coord].value
                key_formula = parse_formula(key_cell_value)
                is_similar = simplify(key_formula - sub_formula) == 0

                if is_similar:
                    report.submission_score = self.grading_rubric.score
                    break

            return report
        except Exception as exc:
            # TODO: Revisit whether we should print the comparison key value here.
            #   It might leak the answers to the students, though.
            report.append_line(f"{self.report_line_prefix}Error: {exc}")
            return report
