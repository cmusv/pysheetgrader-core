
class Grader:
    """
    Responsible to grade submission Document instances against the key Document.
    """

    def __init__(self, key_document):
        """
        Initializer of this instance.

        :param key_document: Document instance of a valid key.
        :exception ValueError: Raises a ValueError if the passed `key_document` is not a valid key.
        """
        # Sanity check
        if not key_document or not key_document.is_valid_key():
            raise ValueError(f"The document passed is not a valid key. Path: {key_document.path}")

        # Attributes
        self.key_document = key_document
        self.grading_sheet_names = key_document.grading_sheet_names()

    def grade(self, document):
        """
        Grade the passed `document` against this instance's key document.
        :param document: Document instance.
        :return: Float value of the grade.
        """
        score = 0
        for sheet_name in self.grading_sheet_names:
            score += self.grade_sheet(document, sheet_name)

        return score

    def grade_sheet(self, document, sheet_name):
        """
        Grade the passed `sheet_name` of the passed `document` against this instance's key document.
        :param document: Document instance.
        :param sheet_name: String value of the sheet name that should be graded.
        :return: Float value of the grade for the sheet.
        """

        score = 0
        graded_cells = self.cell_grading_order(sheet_name)
        for _ in graded_cells:
            # TODO: Update this method to properly use grading rubric.
            score += 10

        return score

    def cell_grading_order(self, sheet_name):
        """
        Return ordered String list of cell coordinate to be graded for the passed `sheet_name` based on this
            instance's key document.

        :param sheet_name: String of the sheet name.
        :return: List of Strings.
        """

        # TODO: Update this method to return the grading rubric.

        order_sheet = self.key_document.formula_wb[sheet_name + "_CheckOrder"]
        cell_orders = []

        # Assumptions of the order sheet
        # 1. The scoring column is always on B. (min_col=2, max_col=2)
        # 2. The scoring column always has a header (min_row=2)
        # 3. The scoring column is always in order
        for row in order_sheet.iter_rows(min_col=2, max_col=2, min_row=2):
            # Assuming this for-loop will only be executed for B column
            # And the reference cells always have comment text for rubric.
            cell_orders.extend([cell.value for cell in row])

        return cell_orders
