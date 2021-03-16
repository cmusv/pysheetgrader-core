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
        try:
            key_sheet = self.key_document.formula_wb[self.sheet_name]
            sub_sheet = self.sub_document.formula_wb[self.sheet_name]
        except Exception as exc:
            report.append_line(f"{self.report_line_prefix}{exc}")
            return report

        # Grading cells
        cell_coord = self.grading_rubric.cell_coord
        custom_formulas = get_excel_formula_lambdas()

        try:
            sub_cell_value = sub_sheet[cell_coord].value
            sub_formula = parse_formula(sub_cell_value, local_dict=custom_formulas)

            # Comparison
            for key_coord in self.grading_rubric.get_all_cell_coord():
                key_cell_value = key_sheet[key_coord].value
                key_formula = parse_formula(key_cell_value, local_dict=custom_formulas)
                is_similar = simplify(key_formula - sub_formula) == 0

                if is_similar:
                    report.submission_score = self.grading_rubric.score
                    break

            return report
        except Exception as exc:
            # TODO: Revisit whether we should print the comparison key value here.
            #   It might leak the answers to the students, though.
            report.append_line(f"{self.report_line_prefix}- Description: {exc}")
            return report

class SoftFormulaStrategy(BaseStrategy):
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
        custom_formulas = get_excel_formula_lambdas()

        try:
            sub_cell_value = sub_sheet[cell_coord].value
            sub_formula = parse_formula(sub_cell_value, local_dict=custom_formulas)

            # Comparison
            for key_coord in self.grading_rubric.get_all_cell_coord():
                curr_cell_value = sub_sheet[key_coord].value
                if(len(curr_cell_value)==1 and curr_cell_value[0]=='='):
                    report.append_line(f"\t- Description: Formula is missing.")
                    return report
                if(any(c.isalpha() for c in curr_cell_value)):
                    print(f"\t- Description: Found formula ", curr_cell_value[1:])
                    return self.grade_constant()
                else:
                    report.append_line(f"\t- Description: Formula is missing.")
                    #report.submission_score = 0
                    return report
        except Exception as exc:
            # TODO: Revisit whether we should print the comparison key value here.
            #   It might leak the answers to the students, though.
            report.append_line(f"{self.report_line_prefix}- Description: {exc}")
            return report

    def grade_constant(self):
        report = self.create_initial_report()

        # Retrieving sheets
        try:
            key_sheet = self.key_document.computed_value_wb[self.sheet_name]
            sub_sheet = self.sub_document.computed_value_wb[self.sheet_name]
        except Exception as exc:
            report.append_line(f"{self.report_line_prefix}{exc}")
            return report

        # Grading cells
        cell_coord = self.grading_rubric.cell_coord
        sub_value = sub_sheet[cell_coord].value

        for coord in self.grading_rubric.get_all_cell_coord():
            if self.value_matches(sub_value, key_sheet[coord].value):
                report.submission_score += self.grading_rubric.score
                break

        return report

    def value_matches(self, key_value, sub_value):
        """
        Returns boolean whether the passed `sub_value` match the `key_value`. If both of them are numeric and there's
        a `constant_delta` in current rubric, it will check if `sub_value` is in the range of `constant_delta`.

        :param key_value: Any value.
        :param sub_value: Any value.
        :return: True if they match, False otherwise.
        """

        # Best case: both are equals by default
        if key_value == sub_value:
            return True

        # If both of them are numbers, and there's no constant delta
        # Directly return False.
        if self.grading_rubric.constant_delta is None:
            return False

        delta = self.grading_rubric.constant_delta

        try:
            key_float = float(key_value)
            sub_float = float(sub_value)
            return (key_float - delta) <= sub_float <= (key_float + delta)
        except Exception:
            # TODO: Check if we should log an error here.
            return False