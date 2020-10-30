
class GradingReport:
    """
    Representation of a grading report.
    Please use the `append_line()` method instead of appending the lines manually to `report_lines` property
    so it could do proper side effects (e.g. printing every new lines).

    Attributes:
        - print_appended_lines: Prints the appended line passed to the `append_line()` method. Defaults to `False`.
    """

    print_appended_lines = False

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

    def append_line(self, string_line):
        """
        Appends the passed string_line to this instance's `report_lines`.
        :param string_line: String instance.
        """
        self.report_lines.append(string_line + "\n")
        if self.print_appended_lines:
            print(string_line)