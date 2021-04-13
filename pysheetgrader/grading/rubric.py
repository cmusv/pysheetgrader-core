from pysheetgrader.sheet import Sheet
from pysheetgrader.grading.test_case import GradingTestCase

from openpyxl.worksheet.worksheet import Worksheet
from typing import List
from enum import Enum
import yaml, sys


class GradingRubricType(Enum):
    """
    Type of a grading rubric.
    """
    CONSTANT = 1
    FORMULA = 2
    TEST = 3
    SOFT_FORMULA = 4
    RELATIVE = 5
    RELATIVE_F = 6

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
        elif value == "soft_formula":
            return GradingRubricType.SOFT_FORMULA
        elif value == "relative":
            return GradingRubricType.RELATIVE
        elif value == "relative_f":
            return GradingRubricType.RELATIVE_F
        else:
            raise Exception(f"Unsupported rubric type {value}")


class GradingRubric:
    """
    Representation of a grading rubric in a sheet.
    """

    def __init__(self, cell_id: str, cell_coord: str, description: str, hidden: bool, fail_msg: str,
                 rubric_type: GradingRubricType, score: float, constant_delta: float = 0,
                 alt_cells: List[str] = [], test_cases: List[GradingTestCase] = []):
        """
        Initializer of this class' instance.
        :param cell_id: String value of the rubric identifier
        :param cell_coord: String value of the main cell coordinate in this rubric.
        :param description: String value of the description.
        :param hidden: Boolean value indicating should the cell be hidden to students.
        :param fail_msg: String value of general failure message, for example,
                "This cell should have used standard deviation, which was $B3 according to your calculation."
        :param rubric_type: GradingRubricType enum value.
        :param score: Float value of the score for this rubric.
        :param constant_delta: Float value of the delta / precision that allowed for a constant GradingRubricType.
            Defaults to 0.
        :param alt_cells: List of String of alternative cell coordinates to be reviewed by this rubric.
            Defaults to empty list.
        :param test_cases: List of GradingTestCase instances. Defaults to empty list.
        """
        self.cell_id = cell_id
        self.cell_coord = cell_coord
        self.rubric_type = rubric_type

        self.score = score
        self.constant_delta = constant_delta

        self.alt_cells = alt_cells
        self.test_cases = test_cases

        self.hidden = hidden
        self.description = description
        self.fail_msg = fail_msg

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
    def create_rubrics_for_sheet(key_document, sheet: Sheet):
        """
        Create ordered list of GradingRubric instance from the passed `sheet_name` of the `key_document`.
        Will return empty list of the passed key_document is invalid or doesn't have rubrics in the passed sheet.

        :param key_document: Valid Document instance.
        :param sheet: The Sheet object that represents the sheet to be graded
        :return: List of GradingRubric.
        """
        # Sanity check
        if not key_document or not key_document.is_valid_key():
            return []
        try:
            order_sheet = key_document.formula_wb[sheet.name + "_CheckOrder"]
            key_sheet = key_document.formula_wb[sheet.name]
        except KeyError:
            return []

        # Rubric creation
        rubrics = []

        # Assumptions of the order sheet
        # 1. The scoring column is always on B. (min_col=2, max_col=2)
        # 2. The scoring column always has a header (min_row=2)
        # 3. The scoring column is always in order
        # 4. The indexing column is always on A, one-cell left from the scoring column
        for row in order_sheet.iter_rows(min_col=1, max_col=5, min_row=2):
            # Assuming this for-loop will only be executed for B column
            # TODO: Revisit if the failed rubric parsing is necessary to be reported.
            try:
                cell_id, cell_coord, cell_description, cell_hidden, fail_msg = \
                    row[0].value, row[1].value, row[2].value, row[3].value, row[4].value

                hidden = cell_hidden == "H" or cell_hidden == "h"

                r = GradingRubric.create_rubric_from_cell(cell_id, cell_coord,
                                                          cell_description, hidden, fail_msg, key_sheet)
                rubrics.append(r)
            except Exception as exc:
                print(f"Exception when creating rubric: {exc}", file=sys.stderr)
                continue

        return rubrics

    @staticmethod
    def create_rubric_from_cell(cell_id: str, cell_coord: str, description: str, hidden: bool, fail_msg: str,
                                key_sheet: Worksheet):
        """
        Creates GradingRubric instance from passed `cell_coord` of the `key_sheet`.
        This method assumes the cell of the passed coordinate will have notes that holds the rubric.

        :param cell_id: String value of the cell identifier. It is the number left to the `cell_coord`
            in the `_CheckOrder` sheet
        :param cell_coord: String value of the cell coordinate in the `key_sheet`. It assumes that the cell coordinate
            has note value that holds the grading rubric.
        :param description: String value of the cell description. It is the third column in the `_CheckOrder` sheet.
        :param hidden: True if the cell is hidden and not visible to students.
        :param fail_msg: String value of general failure message, for example,
                "This cell should have used standard deviation, which was $B3 according to your calculation."
        :param key_sheet: Openpyxl's Worksheet instance of the key document.
        :return: GradingRubric instance.
        """

        try:
            key_cell = key_sheet[cell_coord]
            key_comment = key_cell.comment.text
        except Exception:
            raise Exception(f"No rubric note found for cell: {cell_coord} in sheet: {key_sheet.title}")

        # Comment parsing
        parsed_comment = yaml.load(key_comment, Loader=yaml.Loader)
        rubric_dict = parsed_comment['rubric'] if 'rubric' in parsed_comment else None
        alt_cells = parsed_comment['alt_cells'] if 'alt_cells' in parsed_comment else []
        test_cases = parsed_comment['test_cases'] if 'test_cases' in parsed_comment else {}

        if not rubric_dict:
            raise ValueError(f"No valid rubric found for cell: {cell_coord} in sheet: {key_sheet.title}")

        # Rubric parsing
        rubric_score = rubric_dict['score'] if 'score' in rubric_dict else None
        rubric_type = rubric_dict['type'] if 'type' in rubric_dict else None
        rubric_delta = rubric_dict['delta'] if 'delta' in rubric_dict else 0

        # Rubric score parsing
        try:
            rubric_score = float(rubric_score)
        except Exception:
            raise ValueError(f"Invalid rubric score found for cell: {cell_coord} in sheet: {key_sheet.title}")

        # Rubric type parsing
        if rubric_type is not None:
            rubric_type = GradingRubricType.type_from_string(rubric_type)

        if not rubric_type:
            raise ValueError(f"Invalid rubric comment score and type found for cell: {cell_coord} "
                             f"in sheet: {key_sheet.title}")

        # Rubric delta
        try:
            rubric_delta = float(rubric_delta)
        except ValueError:
            raise ValueError(f"Invalid rubric delta format found for cell: {cell_coord} in sheet: {key_sheet.title}")

        # Rubric test cases
        test_cases = GradingRubric.create_test_cases_from_dict(test_cases)

        return GradingRubric(cell_id, cell_coord, description, hidden, fail_msg, rubric_type, rubric_score,
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
