class Sheet:
    """
    Represents a sheet in the grading process.
    """

    def __init__(self, name: str, minimum_work: int, feedback: str):
        """
        Initialize a sheet object representing a graded sheet

        :param name: the name of the sheet
        :param minimum_work: an int, if the student's score below this, the grading will abort
        :param feedback: the feedback string when student doesn't achieve the minimum work
        """
        self.name = name
        self.minimum_work = minimum_work
        self.feedback = feedback
