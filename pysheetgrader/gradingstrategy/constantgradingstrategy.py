from pysheetgrader.gradingstrategy.gradingstrategy import GradingStrategy


class ConstantGradingStrategy(GradingStrategy):
    """
    Used to grade Constant rubrics.
    """

    def grade(self):
        key_sheet = self.key_document.computed_value_wb[self.sheet_name]
        sub_sheet = self.sub_document.computed_value_wb[self.sheet_name]

        cell_cord = self.grading_rubric.cell_cord

        if key_sheet[cell_cord].value == sub_sheet[cell_cord].value:
            return self.grading_rubric.score
        else:
            return 0
