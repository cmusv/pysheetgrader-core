from pysheetgrader.grading.test_case import GradingTestCase
from typing import List
from enum import Enum
import yaml


class GradingRubricType(Enum):
    """
    Type of a grading rubric.
    """
    CONSTANT = 1
    FORMULA = 2
    TEST = 3

    @staticmethod
    def type_from_string(value):
        """
        Returns corresponding GradingRubricType for the passed String in `value`.
        :param value: String value.
        :return: None if it doesn't match any GradingRubricType, otherwise a valid GradingRubricType.
        """

        if value == "constant":
            return GradingRubricType.CONSTANT
        elif value == "formula":
            return GradingRubricType.FORMULA
        elif value == "test":
            return GradingRubricType.TEST
        else:
            return None


class GradingRubric:
    """
    Representation of a grading rubric in a sheet.
    """

    def __init__(self, cell_coord: str, rubric_type: GradingRubricType,
                 score: float, constant_delta: float = 0,
                 alt_cells: List[str] = [], test_cases: List[GradingTestCase] = []):
        """
        Initializer of this class' instance.
        :param cell_coord: String value of the main cell coordinate in this rubric.
        :param rubric_type: GradingRubricType enum value.
        :param score: Float value of the score for this rubric.
        :param constant_delta: Float value of the delta / precision that allowed for a constant GradingRubricType.
            Defaults to 0.
        :param alt_cells: List of String of alternative cell coordinates to be reviewed by this rubric.
            Defaults to empty list.
        :param test_cases: List of GradingTestCase instances. Defaults to empty list.
        """
        self.cell_coord = cell_coord
        self.rubric_type = rubric_type

        self.score = score
        self.constant_delta = constant_delta

        self.alt_cells = alt_cells
        self.test_cases = test_cases

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
        rubric_dict = parsed_comment['rubric'] if 'rubric' in parsed_comment else None
        alt_cells = parsed_comment['alt_cells'] if 'alt_cells' in parsed_comment else []
        test_cases = parsed_comment['test_cases'] if 'test_cases' in parsed_comment else {}

        if not rubric_dict:
            raise ValueError(f"No rubric found for cell: {cell_coord} in sheet: {key_sheet}")
            return

        # Rubric parsing
        rubric_score = rubric_dict['score'] if 'score' in rubric_dict else None
        rubric_type = rubric_dict['type'] if 'type' in rubric_dict else None
        rubric_delta = rubric_dict['delta'] if 'delta' in rubric_dict else 0

        # Rubric score parsing
        try:
            rubric_score = float(rubric_score)
        except Exception:
            raise ValueError(f"Invalid rubric score found for cell: {cell_coord} in sheet: {key_sheet}")
            return

        # Rubric type parsing
        if rubric_type is not None:
            rubric_type = GradingRubricType.type_from_string(rubric_type)

        if not rubric_type:
            raise ValueError(f"Invalid rubric comment score and type found for cell: {cell_coord} in sheet: {key_sheet}")
            return

        # Rubric delta
        try:
            rubric_delta = float(rubric_delta)
        except ValueError:
            raise ValueError(f"Invalid rubric delta format found for cell: {cell_coord} in sheet: {key_sheet}")
            return

        # Rubric test cases
        test_cases = GradingRubric.create_test_cases_from_dict(test_cases)

        return GradingRubric(cell_coord, rubric_type, rubric_score,
                             constant_delta=rubric_delta, alt_cells=alt_cells,
                             test_cases=test_cases)

    @staticmethod
    def create_test_cases_from_dict(raw_cases):
        """
        Creates a list of GradingTestCases out of passed `raw_cases` dictionary.
        :param raw_cases: Dictionary of test cases.
        :return: List of GradingTestCases.
        """

        test_cases = []
        for case_name in raw_cases:
            single_case_dict = raw_cases[case_name]

            # Mandatory key check
            if 'output' not in single_case_dict or 'input' not in single_case_dict:
                continue

            output = single_case_dict['output']
            input = single_case_dict['input']
            delta = single_case_dict['delta'] if 'delta' in single_case_dict else 0

            try:
                new_case = GradingTestCase(name=case_name,
                                           expected_output=float(output),
                                           inputs=input,
                                           output_delta=float(delta))

                test_cases.append(new_case)
            except Exception as exc:
                # TODO: Revisit if we need to print an error here.
                continue

        return test_cases

