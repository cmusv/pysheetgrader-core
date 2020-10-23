from openpyxl import load_workbook


class Document:
    """
    Represents a document in the grading process.

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

    def __del__(self):
        self.formula_wb.close()
        self.computed_value_wb.close()

    def is_valid_key(self):
        """
        Returns a Boolean value to identify whether this document is a valid key document or not.
        :return: Boolean value.
        """
        return self.GRADING_ORDER_SHEET_NAME in self.formula_wb.sheetnames

    def grading_sheet_names(self):
        """
        Returns ordered list of sheet names to be graded. Will return an empty string if the `is_valid_key` is False.
        :return: List of String.
        """
        # Early return
        if not self.is_valid_key():
            return []

        sheet_names = []
        order_sheet = self.formula_wb[self.GRADING_ORDER_SHEET_NAME]

        # Assumptions of the order sheet
        # 1. The scoring column is always on B. (min_col=2, max_col=2)
        # 2. The scoring column always has a header (min_row=2)
        # 3. The scoring column is always in order
        for row in order_sheet.iter_rows(min_col=2, max_col=2, min_row=2):
            # Assuming this for-loop will only be executed for B column
            # And the cell always have the valid sheet name.
            sheet_names.extend([cell.value for cell in row])

        return sheet_names
