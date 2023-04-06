from pysheetgrader.grading.strategy.base import BaseStrategy
import re

REGEX = r"\$[a-zA-Z]\d{1,2}"

class AssertionStrategy(BaseStrategy):
    """
    Used to grade Assertion rubrics.

    get raw key sheet value
        for each escaped character:
            replace with computed result in submission
    
    evalute as python expression and return bool

    """
    def get_submitted_value(self):
        return str(self.sub_sheet_compute[self.cell_coord].value)

    def check_correct(self, sub_cell_value, key_cell_value, key_coord) -> bool:
        return key_cell_value

    def get_key_value(self, key_coord) -> bool:
        raw_expr = self.key_sheet_raw[key_coord].value
        matches = re.findall(REGEX, raw_expr)

        for m in matches:
            raw_expr = raw_expr.replace(m, str(self.sub_sheet_compute[m].value))
        
        return eval(raw_expr)
