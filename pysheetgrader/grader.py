from pysheetgrader.grading.rubric import GradingRubric
from pysheetgrader.grading.rubric import GradingRubricType
from pysheetgrader.grading.strategy.constant import ConstantStrategy


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
        rubrics = GradingRubric.create_rubrics_for_sheet(self.key_document, sheet_name)
        for r in rubrics:
            score += self.grade_sheet_by_rubric(document, sheet_name, r)

        return score

    def grade_sheet_by_rubric(self, document, sheet_name, rubric):
        """
        Grades the `sheet_name` of the passed `document` using the passed `rubric`.
        :param document: Document instance.
        :param sheet_name: String value of the sheet name.
        :param rubric: GradingRubric instance.
        :return: Float value of the grade of the document's sheet.
        """
        if rubric.rubric_type == GradingRubricType.CONSTANT:
            return ConstantStrategy(self.key_document, document, sheet_name, rubric).grade()
        else: # TODO: Use the formula-based grading strategy here.
            return rubric.score
