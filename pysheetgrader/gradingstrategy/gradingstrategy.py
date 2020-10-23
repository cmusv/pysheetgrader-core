
class GradingStrategy:
    """
    Base class of other grading strategies.
    """

    def __init__(self, key_document, sub_document, sheet_name, grading_rubric):
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
        Returns the grade of the `sub_document` of this instance, based on the `grading_rubric` and `key_document`.
        :return: Float value of the grade.
        :exception NotImplemented   raised when this method called directly (instead of the subclass').
        """
        raise NotImplemented("The `grade` method should've been implemented in the subclasses.")
