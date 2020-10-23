from enum import Enum

class GradingRubricType(Enum):
    """
    Type of a grading rubric.
    """
    CONSTANT = 1
    FORMULA = 2

class GradingRubric:
    """
    Representation of a grading rubric in a sheet.
    """

    def __init__(self, cell_coord, rubric_type, score, unit_tests):
        """
        Initializer of this class' instance.
        :param cell_coord: String value of the cell coordinate in this rubric.
        :param rubric_type: GradingRubricType enum value.
        :param score: Float value of the score for this rubric.
        :param unit_tests: List of String for unit tests (TBD)
        """
        self.cell_cord = cell_coord
        self.rubric_type = rubric_type
        self.score = score
        self.unit_tests = unit_tests

    @staticmethod
    def create_rubrics_for_sheet(key_document, sheet_name):
        """
        Create list of GradingRubric instance from the passed `sheet_name` of the `key_document`.
        Will return empty list of the passed key_document is invalid or doesn't have rubrics in the passed sheet.

        :param key_document: Valid Document instance.
        :param sheet_name: String value of the sheet name
        :return: List of GradingRubric.
        """
        # Sanity check
        order_sheet = None
        if not key_document or not key_document.is_valid_key():
            return []
        try:
            order_sheet = key_document.formula_wb[sheet_name + "_CheckOrder"]
        except KeyError:
            return []

        # Rubric creation
        rubrics = []

        # Assumptions of the order sheet
        # 1. The scoring column is always on B. (min_col=2, max_col=2)
        # 2. The scoring column always has a header (min_row=2)
        # 3. The scoring column is always in order
        for row in order_sheet.iter_rows(min_col=2, max_col=2, min_row=2):
            # Assuming this for-loop will only be executed for B column
            rubrics.extend([GradingRubric.create_rubrics_from_cell(c)
                            for c in row])

        return rubrics


    @staticmethod
    def create_rubrics_from_cell(cell_coord, key_sheet):
        """
        Creates GradingRubric instance from passed `cell_coord` of the `key_sheet`.
        :param cell_coord: String value of the cell coordinate in the `key_sheet`. It assumes that the cell coordinate
            has note value that holds the grading rubric.
        :param key_sheet: Openpyxl's Worksheet instance of the key document.
        :return: GradingRubric instance.
        """

        # TODO: Implement proper parser.
        return GradingRubric(cell_coord, GradingRubricType.CONSTANT, 10, [])