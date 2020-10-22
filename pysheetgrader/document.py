from openpyxl import load_workbook


class Document:
    """
    Represents a document in the grading process.
    """

    def __init__(self, path, read_only=True):
        """
        Initializer for this class.
        :param path: Valid path of the document.
        :param read_only: Boolean marker whether the document should be treated as read-only. This will affect
            the `formula_wb` and `computed_value_wb` property of this instance - whether they're read-only or not.
            Defaults to `True`.
        """

        self.path = path
        self.read_only = read_only

        self.formula_wb = load_workbook(path, read_only=read_only, data_only=False)
        self.computed_value_wb = load_workbook(path, read_only=read_only, data_only=True)
