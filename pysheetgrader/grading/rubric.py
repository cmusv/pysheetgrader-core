import sys
from enum import Enum
from typing import List
import yaml
from openpyxl.worksheet.worksheet import Worksheet

from email import header
from pysheetgrader.sheet import Sheet
from pysheetgrader.grading.test_case import GradingTestCase
from pysheetgrader.utils import get_headers



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
    CHECK = 7
    

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
        elif value == "check":
            return GradingRubricType.CHECK
        else:
            raise Exception(f"Unsupported rubric type {value}")


class GradingRubric:
    """
    Representation of a grading rubric in a sheet.
    """

    def __init__(self, values: dict):
        """
        Initializer of this class' instance. Accepts a dictionary with below parameters.
        :param cell_id: String value of the rubric identifier
        :param cell_coord: String value of the main cell coordinate in this rubric.
        :param description: String value of the description.
        :param hidden: Boolean value indicating should the cell be hidden to students.
        :param killer: Boolean value indicating if the cell is a killer cell
        :param fail_msg: String value of general failure message, for example,
                "This cell should have used standard deviation, which was $B3 according to your calculation."
        :param rubric_type: GradingRubricType enum value.
        :param score: Float value of the score for this rubric.
        :param result_coord: String value of the result cell coordinate in this rubric.
        :param constant_delta: Float value of the delta / precision that allowed for a constant GradingRubricType.
            Defaults to 0.
        :param alt_cells: List of String of alternative cell coordinates to be reviewed by this rubric.
            Defaults to empty list.
        :param test_cases: List of GradingTestCase instances. Defaults to empty list.
        :param test_params: Dictionary of data to be used in test mode.
        :param is_correct: True if evaluated and correct, false otherwise.
        :param is_test_pass: True if Test is passing, false otherwise.
        """
        self.cell_id = values["cell_id"]
        self.cell_coord = values["cell_coord"]
        self.rubric_type = values["rubric_type"]

        self.grading_nature = values.get("grading_nature", "positive")
        self.score = values["score"]
        self.constant_delta = values.get("constant_delta", 0)
        self.result_coord = values["result_coord"]

        self.alt_cells = values.get("alt_cells", [])
        self.test_cases = values.get("test_cases", [])

        self.hidden = values["hidden"]
        self.killer = values["killer"]
        self.description = values["description"]
        self.fail_msg = values["fail_msg"]
        self.prereq_cells = values.get("prereq_cells", [])
        self.test_params = values["test_params"]
        self.is_correct = False
        self.is_test_pass = False

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

    def get_result_cell_coord(self):
        """
        Returns result cell coordinate used in this rubric
        """
        result = [self.result_coord]
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
        COLUMN_HEADER_NAMES = {
            "cell_id": ["number", "cell-id", "id"],
            "cell_coord": ["cell"],
            "cell_description": ["description"],
            "cell_hidden_or_killer": ["special"],
            "fail_msg": ["feedback"],
            "test_name": ["test-name"],
            "test_result": ["expected-result"],
            "test_failure_message": ["failure-message"],
            "expected_score": ["expected-score"],
        }
        first_row = next(order_sheet.iter_rows(values_only=True))
        header_index = get_headers(COLUMN_HEADER_NAMES, first_row)
        has_cell_id = "cell_id" in header_index
        has_cell_coord = "cell_coord" in header_index
        has_cell_description = "cell_description" in header_index
        has_cell_hidden_or_killer = "cell_hidden_or_killer" in header_index
        has_fail_msg = "fail_msg" in header_index
        has_test_name = "test_name" in header_index
        has_test_result = "test_result" in header_index
        has_test_failure_message = "test_failure_message" in header_index
        has_expected_score = "expected_score" in header_index

        for row in order_sheet.iter_rows(min_row=2, values_only=True):
            # Assuming this for-loop will only be executed for B column
            # TODO: Revisit if the failed rubric parsing is necessary to be reported.
            try:
                cell_id = row[header_index["cell_id"]] if has_cell_id else None
                cell_coord = row[header_index["cell_coord"]] if has_cell_coord else None
                cell_description = row[header_index["cell_description"]] if has_cell_description else None
                cell_hidden_or_killer = row[header_index["cell_hidden_or_killer"]] if has_cell_hidden_or_killer else None
                fail_msg = row[header_index["fail_msg"]] if has_fail_msg else None


                hidden = cell_hidden_or_killer == "H" or cell_hidden_or_killer == "h" or cell_hidden_or_killer == "HK" or cell_hidden_or_killer == "hk" or cell_hidden_or_killer == "KH" or cell_hidden_or_killer == "kh"
                killer = cell_hidden_or_killer == "K" or cell_hidden_or_killer == "k" or cell_hidden_or_killer == "HK" or cell_hidden_or_killer == "hk" or cell_hidden_or_killer == "KH" or cell_hidden_or_killer == "kh"
                test_params = {
                    "name": row[header_index["test_name"]] if has_test_name else None,
                    "expected_result": row[header_index["test_result"]] if has_test_result else None,
                    "failure_message": row[header_index["test_failure_message"]] if has_test_failure_message else None,
                    "expected_score": row[header_index["expected_score"]] if has_expected_score else None
                }
                r = GradingRubric.create_rubric_from_cell(cell_id, cell_coord,
                                                          cell_description, hidden, killer, fail_msg, key_sheet, test_params)
                
                rubrics.append(r)
            except Exception as exc:
                print(f"Exception when creating rubric: {exc}", file=sys.stderr)
                continue

        return rubrics

    @staticmethod
    def create_rubric_from_cell(cell_id: str, cell_coord: str, description: str, hidden: bool, killer: bool,fail_msg: str,
                                key_sheet: Worksheet, test_params: dict):
        """
        Creates GradingRubric instance from passed `cell_coord` of the `key_sheet`.
        This method assumes the cell of the passed coordinate will have notes that holds the rubric.

        :param cell_id: String value of the cell identifier. It is the number left to the `cell_coord`
            in the `_CheckOrder` sheet
        :param cell_coord: String value of the cell coordinate in the `key_sheet`. It assumes that the cell coordinate
            has note value that holds the grading rubric.
        :param description: String value of the cell description. It is the third column in the `_CheckOrder` sheet.
        :param hidden: True if the cell is hidden and not visible to students.
        :param killer: True if the cell is killer cell 
        :param fail_msg: String value of general failure message, for example,
                "This cell should have used standard deviation, which was $B3 according to your calculation."
        :param key_sheet: Openpyxl's Worksheet instance of the key document.
        :param test_params: dictionary of parameters requried in test mode
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
        fail_msg_tst = parsed_comment['fail'] if 'fail' in parsed_comment else {}
        test_cases['fail'] = fail_msg_tst

        if not rubric_dict:
            raise ValueError(f"No valid rubric found for cell: {cell_coord} in sheet: {key_sheet.title}")

        # Rubric parsing
        rubric_grading_nature = rubric_dict['grading'] if 'grading' in rubric_dict else 'positive'
        rubric_score = rubric_dict['score'] if 'score' in rubric_dict else None
        rubric_type = rubric_dict['type'] if 'type' in rubric_dict else None
        rubric_delta = rubric_dict['delta'] if 'delta' in rubric_dict else 0
        rubric_result_coord = rubric_dict['result'] if 'result' in rubric_dict else None
        rubric_prereq = rubric_dict['prereq'] if 'prereq' in rubric_dict else None


        # Rubric score parsing
        try:
            rubric_score = float(rubric_score)
        except Exception:
            raise ValueError(f"Invalid rubric score found for cell: {cell_coord} in sheet: {key_sheet.title}")
            
        # Rubric Grading Parse

        if rubric_grading_nature == 'negative' and rubric_score > 0:
            raise ValueError(f" For neagtive rubric, the score has to be negative in the cell {cell_coord} in sheet: {key_sheet.title}")
        
        
        # Rubric type parsing
        if rubric_type is not None:
            rubric_type = GradingRubricType.type_from_string(rubric_type)

        if not rubric_type:
            raise ValueError(f"Invalid rubric comment score and type found for cell: {cell_coord} "
                             f"in sheet: {key_sheet.title}")

        # Rubric result cell parsing
        if rubric_result_coord is not None:
            rubric_result_coord = str(rubric_result_coord)

        # Rubric delta
        try:
            rubric_delta = float(rubric_delta)
        except ValueError:
            raise ValueError(f"Invalid rubric delta format found for cell: {cell_coord} in sheet: {key_sheet.title}")

        # Rubric test cases
        test_cases = GradingRubric.create_test_cases_from_dict(test_cases)
        values = {
            "cell_id": cell_id,
            "cell_coord": cell_coord,
            "description": description,
            "hidden": hidden,
            "killer": killer,
            "fail_msg": fail_msg,
            "rubric_type": rubric_type,
            "score": rubric_score,
            "result_coord": rubric_result_coord,
            "grading_nature": rubric_grading_nature,
            "constant_delta": rubric_delta,
            "alt_cells": alt_cells,
            "test_cases": test_cases,
            "prereq_cells": rubric_prereq,
            "test_params": test_params
        }
        return GradingRubric(values)

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
            failmsg = single_case_dict['fail'] if 'fail' in single_case_dict else ""

            try:
                new_case = GradingTestCase(name=case_name,
                                           expected_output=float(output),
                                           inputs=input,
                                           output_delta=float(delta), failmsg=failmsg)

                test_cases.append(new_case)
            except Exception as exc:
                # TODO: Revisit if we need to print an error here.
                continue

        return test_cases
        
