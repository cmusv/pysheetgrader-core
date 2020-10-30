
class GradingReport:
    """
    Representation of a grading report.
    """

    def __init__(self):
        self.submission_score = 0
        self.max_possible_score = 0
        self.report_lines = []

    def __add__(self, other):
        self.append(other)
        return self

    def append(self, other_report):
        """
        Appends another GradingReport instance properties to this instance.
        :param other_report: GradingReport instance.
        """
        # Early return
        if not isinstance(other_report, self.__class__):
            return

        self.submission_score += other_report.submission_score
        self.max_possible_score += other_report.max_possible_score
        self.report_lines.extend(other_report.report_lines)
