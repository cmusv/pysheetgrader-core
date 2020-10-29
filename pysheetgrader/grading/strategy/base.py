from pysheetgrader.grading.rubric import GradingRubric
from pysheetgrader.document import Document


class BaseStrategy:
    """
    Base class of other grading strategies.
    """

    def __init__(self, key_document: Document, sub_document: Document, sheet_name, grading_rubric: GradingRubric):
        """
        Initializer of this class.
        :param key_document: Document instance that used as a key.
        :param sub_document: Document instance that will be graded as a submission.
        :param sheet_name: String value of the sheet that will be graded.
        :param grading_rubric: GradingRubric instance.
        """
        self.key_document = key_document
        self.sub_document = sub_document
        self.sheet_name = sheet_name
        self.grading_rubric = grading_rubric

    def grade(self):
        """
        Returns the grading report of the `sub_document` of this instance, based on the `grading_rubric` and `key_document`.
        :return: Report instance of the grading.
        :exception NotImplemented   raised when this method called directly (instead of the subclass').
        """
        raise NotImplemented("The `grade` method should've been implemented in the subclasses.")
