from pysheetgrader.sheet import Sheet

from openpyxl import load_workbook


class Document:
    """
    Represents a document in the grading process. Please call the `close()` method when it's not used anymore.

    Attributes:
        GRADING_ORDER_SHEET_NAME    Holds the name of the sheet in a key workbook that contains the order
                                    of grading other sheets.
    """

    GRADING_ORDER_SHEET_NAME = 'SheetGradingOrder'

    def __init__(self, path, read_only=True):
        """
        Initializer for this class.
        :param path: Valid path of the document. This path will be opened into two workbooks: `formula_wb` and
            `computed_value_wb`.
        :param read_only: Boolean marker whether the document should be treated as read-only. This will affect
            the `formula_wb` and `computed_value_wb` property of this instance - whether they're read-only or not.
            Please set this to `False` when creating key documents, so the rubric notes can be accessed.
            Defaults to `True`.
        """

        self.path = path
        self.read_only = read_only

        self.formula_wb = load_workbook(path, read_only=read_only, data_only=False)
        self.computed_value_wb = load_workbook(path, read_only=read_only, data_only=True)

    def is_valid_key(self):
        """
        Returns a Boolean value to identify whether this document is a valid key document or not.
        :return: Boolean value.
        """
        return self.GRADING_ORDER_SHEET_NAME in self.formula_wb.sheetnames

    def get_grading_sheets(self) -> [Sheet]:
        """
        Returns ordered list of sheets to be graded (not including the GradingOrderSheet).
        Will return an empty array if the `is_valid_key` is False.

        :return: List of Sheet.
        """

        # Early return
        if not self.is_valid_key():
            return []

        sheets = []
        order_sheet = self.formula_wb[self.GRADING_ORDER_SHEET_NAME]

        # Assumptions of the order sheet
        # 1a. The scoring column is on B is the sheet name. (min_col=2, max_col=2, required)
        # 1b. The scoring column is on C is the minimum work. (min_col=3, max_col=3, optional, default 0)
        # 1c. The scoring column is on D is the feedback when not achieving minimum work.
        # (min_col=4, max_col=4, optional, default "")
        # 2. The scoring column always has a header (min_row=2)
        # 3. The scoring column is always in order
        for row in order_sheet.iter_rows(min_col=2, max_col=4, min_row=2):
            name, minimum_work, feedback = row
            sheets.append(Sheet(name.value, minimum_work.value, feedback.value))

        return sheets

    def close(self):
        """
        Closes this document. Call this method only after the document is not used anymore.
        """
        self.formula_wb.close()
        self.computed_value_wb.close()
