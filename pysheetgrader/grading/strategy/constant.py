from pysheetgrader.grading.strategy.base import BaseStrategy
from pysheetgrader.grading.report import GradingReport


class ConstantStrategy(BaseStrategy):
    """
    Used to grade Constant rubrics.
    This instance will check the alternative cells in the key if the submission value didn't match the key value
        in the main cell.
    """

    def grade(self):
        key_sheet = self.key_document.computed_value_wb[self.sheet_name]
        sub_sheet = self.sub_document.computed_value_wb[self.sheet_name]
        cell_coord = self.grading_rubric.cell_coord

        report = GradingReport()
        report.max_possible_score += self.grading_rubric.score
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
