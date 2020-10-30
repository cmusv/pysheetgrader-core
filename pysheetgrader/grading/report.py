
class Report:
    """
    Representation of a grading report.
    """

    def __init__(self):
        self.submission_score = 0
        self.max_possible_score = 0
        self.report_lines = []

    def __add__(self, other):
        self.append(other)

    def append(self, other_report):
        """
        Appends another Report instance properties to this instance.
        :param other_report: Report instance.
        """
        # Early return
        if not isinstance(other_report, self.__class__):
            return

        self.submission_score += other_report.submission_score
        self.max_possible_score += other_report.max_possible_score
        self.report_lines.extend(self.report_lines)
