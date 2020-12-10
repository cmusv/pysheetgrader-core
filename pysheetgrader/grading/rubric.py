from enum import Enum
import yaml
import re

from typing import List


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

    def __init__(self, cell_coord: str, rubric_type: GradingRubricType,
                 score: float, constant_delta: float = 0,
                 alt_cells: List[str] = [], unit_tests: List = []):
        """
        Initializer of this class' instance.
        :param cell_coord: String value of the main cell coordinate in this rubric.
        :param rubric_type: GradingRubricType enum value.
        :param score: Float value of the score for this rubric.
        :param constant_delta: Float value of the delta / precision that allowed for a constant GradingRubricType.
            Defaults to 0.
        :param alt_cells: List of String of alternative cell coordinates to be reviewed by this rubric.
            Defaults to empty list.
        :param unit_tests: List of String for unit tests (TBD). Defaults to empty list.
        """
        self.cell_coord = cell_coord
        self.rubric_type = rubric_type

        self.score = score
        self.constant_delta = constant_delta

        self.alt_cells = alt_cells
        self.unit_tests = unit_tests

    def get_all_cell_coord(self):
        """
        Returns all cell coordinate used in this rubric, with the main cell as the first element and
            alternative cells as the rest.
        :return: List of String of cell coordinates.
        """
        result = [self.cell_coord]
        if self.alt_cells:
            result.extend(self.alt_cells)

        return result


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

        # Comment parsing
        parsed_comment = yaml.load(key_comment, Loader=yaml.Loader)
        rubric_dict = parsed_comment['rubric']
        alt_cells = parsed_comment['alt_cells'] if 'alt_cells' in parsed_comment else []
        unit_tests = parsed_comment['unit_tests'] if 'unit_tests' in parsed_comment else []

        if not rubric_dict:
            raise ValueError(f"Invalid rubric comment found for cell: {cell_coord} in sheet: {key_sheet}")
            return

        # Rubric parsing
        rubric_score = rubric_dict['score']
        rubric_type = rubric_dict['type'].lower()
        rubric_delta = rubric_dict['delta'] if 'delta' in rubric_dict else 0

        # Rubric type
        if not rubric_score or not rubric_type:
            raise ValueError(f"Invalid rubric comment score and type found for cell: {cell_coord} in sheet: {key_sheet}")
            return

        valid_type = GradingRubricType.FORMULA if rubric_type == "formula" else GradingRubricType.CONSTANT

        # Rubric delta
        try:
            rubric_delta = float(rubric_delta)
        except ValueError:
            raise ValueError(f"Invalid rubric delta format found for cell: {cell_coord} in sheet: {key_sheet}")
            return

        return GradingRubric(cell_coord, valid_type, int(rubric_score),
                             constant_delta=rubric_delta, alt_cells=alt_cells, unit_tests=unit_tests)
