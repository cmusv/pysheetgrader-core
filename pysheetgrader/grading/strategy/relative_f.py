from pysheetgrader.grading.strategy.relative import RelativeStrategy


class RelativeFormulaStrategy(RelativeStrategy):
    """
    Like the RelativeStrategy but requires the evaluated submission cell to be a formula. If the
    evaluated cell is a hardcoded constant, the student will not get score.
    """
    def additional_fail_check(self):
        if not self.sub_sheet_raw or not isinstance(self.sub_sheet_raw, str):
            # student doesn't receive score if hardcoded a constant
            return True