from enum import Enum


class GradingReportType(Enum):
    """ Type of grading report.
    An assignment report consists of sheets. A sheet consists of rubrics.
    """
    RUBRIC = 1
    SHEET = 2
    ASSIGNMENT = 3


class GradingReport:
    """
    Representation of a grading report.
    Please use the `append_line()` method instead of appending the lines manually to `report_lines` property
    so it could do proper side effects (e.g. printing every new lines).

    Attributes:
        - print_appended_lines: Prints the appended line passed to the `append_line()` method. Defaults to `False`.
    """

    def __init__(self, t: GradingReportType):
        self.submission_score = 0
        self.max_possible_score = 0
        self.report_lines = []
        self.report_type = t
        self.report_html_args = {}

    def __add__(self, other):
        if self.report_type == GradingReportType.SHEET and other.report_type == GradingReportType.RUBRIC:
            self.report_html_args['rubrics'].append(other.report_html_args)
        elif self.report_type == GradingReportType.ASSIGNMENT and other.report_type == GradingReportType.SHEET:
            self.report_html_args['sheets'].append(other.report_html_args)
        elif self.report_type == GradingReportType.RUBRIC and other.report_type == GradingReportType.RUBRIC:
            self.report_html_args.update(other.report_html_args)
        else:
            raise Exception(f'Addition between report type {self.report_type} and {other.report_type} is not supported')

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

    def print_lines(self):
        """
        Print all lines in this report
        :return: None
        """
        for line in self.report_lines:
            print(line, end='')
