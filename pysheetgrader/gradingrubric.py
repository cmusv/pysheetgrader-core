from enum import Enum
import re


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
        Create ordered list of GradingRubric instance from the passed `sheet_name` of the `key_document`.
        Will return empty list of the passed key_document is invalid or doesn't have rubrics in the passed sheet.

        :param key_document: Valid Document instance.
        :param sheet_name: String value of the sheet name
        :return: List of GradingRubric.
        """
        # Sanity check
        if not key_document or not key_document.is_valid_key():
            return []
        try:
            order_sheet = key_document.formula_wb[sheet_name + "_CheckOrder"]
            key_sheet = key_document.formula_wb[sheet_name]
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
            rubrics.extend([GradingRubric.create_rubrics_from_cell(c.value, key_sheet)
                            for c in row])

        return rubrics

    @staticmethod
    def create_rubrics_from_cell(cell_coord, key_sheet):
        """
        Creates GradingRubric instance from passed `cell_coord` of the `key_sheet`.
        This method assumes the cell of the passed coordinate will have notes that holds the rubric.

        :param cell_coord: String value of the cell coordinate in the `key_sheet`. It assumes that the cell coordinate
            has note value that holds the grading rubric.
        :param key_sheet: Openpyxl's Worksheet instance of the key document.
        :return: GradingRubric instance.
        """

        key_cell = key_sheet[cell_coord]
        key_comment = key_cell.comment.text

        # Rubric parsing
        # TODO: Update this to use YAML later.
        rubric_by_line = key_comment.split(sep="\n")

        # Assumption:
        # 1. Grading rubric is always on the second line.
        # 2. Unit tests is always on the fourth line forward.
        rubric_lines = rubric_by_line[1] if len(rubric_by_line) >= 2 else None
        unit_tests_lines = rubric_by_line[3:] if len(rubric_by_line) >= 4 else None

        grade_search = re.search('\t(.+?)P', rubric_lines) if rubric_lines else None
        type_search = re.search('P-(.+?)', rubric_lines) if rubric_lines else None

        grade = grade_search.group(1) if grade_search else None
        grading_type = type_search.group(1) if type_search else None

        if grade and grading_type:
            rubric_type = GradingRubricType.FORMULA if grading_type == "F" else GradingRubricType.CONSTANT
            return GradingRubric(cell_coord, rubric_type, int(grade), unit_tests_lines)
        else:
            raise ValueError(f"Invalid rubric comment found for cell: {cell_coord} in sheet: {key_sheet}")
