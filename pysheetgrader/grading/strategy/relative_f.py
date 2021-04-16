from pysheetgrader.grading.strategy.relative import RelativeStrategy


class RelativeFormulaStrategy(RelativeStrategy):
    """
    Like the RelativeStrategy but requires the evaluated submission cell to be a formula. If the
    evaluated cell is a hardcoded constant, the student will not get score.
    """

    def grade(self):
        report = self.create_initial_report()

        # Retrieving both key and submission document
        key_sheet, sub_sheet = self.try_get_key_and_sub(report, computed=True)
        key_sheet_formula, sub_sheet_formula = self.try_get_key_and_sub(report, computed=False)

        # Grading cells
        cell_coord = self.grading_rubric.cell_coord
        key_value = key_sheet[cell_coord].value
        sub_value = sub_sheet[cell_coord].value

        key_raw_formula = key_sheet_formula[cell_coord].value
        sub_raw_formula = sub_sheet_formula[cell_coord].value

        if not sub_raw_formula or not isinstance(sub_raw_formula, str):
            # student doesn't receive score if hardcoded a constant
            return report

        # compare submission value and relative evaluation value
        key_value = self.get_formula_value(sub_sheet, key_raw_formula)
        try:
            sub_value = self.get_formula_value(sub_sheet, sub_raw_formula)
        except SyntaxError as exc:
            # do not grant score if cannot evaluate student's formula
            return report

        if self.is_key_sub_match(key_sheet, key_value, sub_value):
            report.submission_score += self.grading_rubric.score

        return report
