from pysheetgrader.grading.rubric import GradingRubric
from pysheetgrader.grading.report import GradingReport, GradingReportType
from pysheetgrader.document import Document


class BaseStrategy:
    """
    Base class of other grading strategies.
    """

    def __init__(self, key_document: Document, sub_document: Document, sheet_name, grading_rubric: GradingRubric,correct_cells,
                 report_line_prefix: str = ""):
        """
        Initializer of this class.
        :param key_document: Document instance that used as a key.
        :param sub_document: Document instance that will be graded as a submission.
        :param sheet_name: String value of the sheet that will be graded.
        :param grading_rubric: GradingRubric instance.
        :param report_line_prefix: Prefix of the report line returned by this instance's `grade()`.
            Defaults to an empty string.
        """
        self.key_document = key_document
        self.sub_document = sub_document
        self.sheet_name = sheet_name
        self.grading_rubric = grading_rubric
        self.report_line_prefix = report_line_prefix
        self.correct_cells = correct_cells

    def grade(self):
        """
        Returns the grading report of the `sub_document` of this instance, based on the `grading_rubric` and `key_document`.
        :return: GradingReport instance of the grading.
        :exception NotImplemented   raised when this method called directly (instead of the subclass').
        """
        raise NotImplemented("The `grade` method should've been implemented in the subclasses.")

    def create_initial_report(self):
        """
        Returns initial GradingReport instance with max_possible_score assigned to this instance's rubric score.
        :return: GradingReport instance.
        """
        report: GradingReport = GradingReport(GradingReportType.RUBRIC)
        if self.grading_rubric.grading_nature == 'positive':
            report.max_possible_score += self.grading_rubric.score
        return report

    def get_key_sheet(self, computed=True):
        """
        Retrieve the key sheet from the key document, according to `sheet_name`
        :return: the key sheet
        """
        return self.key_document.formula_wb[self.sheet_name] if not computed \
            else self.key_document.computed_value_wb[self.sheet_name]

    def get_sub_sheet(self, computed=True):
        """
        Retrieve the submission sheet from the submission document, according to `sheet_name`
        :return: the submission sheet
        """
        return self.sub_document.formula_wb[self.sheet_name] if not computed \
            else self.sub_document.computed_value_wb[self.sheet_name]

    def  try_get_key_and_sub(self, report, computed=True):
        """
        Attempt to load both key and submission sheet according to `sheet_name`. Log any exception if occurs to report.
        :param computed: Should return the sheet with computed cells rather than formula strings
        :param report: the report to log any exception
        :return: the key sheet and submission sheet, None if execption occurs
        """
        try:
            key_sheet = self.get_key_sheet(computed)
            sub_sheet = self.get_sub_sheet(computed)
        except Exception as exc:
            report.append_line(f"{self.report_line_prefix}{exc}")
            report.report_html_args['error'] = exc
            return None, None
        return key_sheet, sub_sheet

    def value_matches(self, key_value, sub_value):
        """
        Returns boolean whether the passed `sub_value` match the `key_value`. If both of them are numeric and there's
        a `constant_delta` in current rubric, it will check if `sub_value` is in the range of `constant_delta`.

        :param key_value: Any value.
        :param sub_value: Any value.
        :return: True if they match, False otherwise.
        """

        # Best case: both are equals by default
        if key_value == sub_value:
            return True

        # If both of them are numbers, and there's no constant delta
        # Directly return False.
        if self.grading_rubric.constant_delta is None:
            return False

        delta = self.grading_rubric.constant_delta

        try:
            key_float = float(key_value)
            sub_float = float(sub_value)
            return (key_float - delta) <= sub_float <= (key_float + delta)
        except Exception:
            # TODO: Check if we should log an error here.
            return False

    def prereq_check(self, cell_coord, report):
        """
        Checks if the pre-requistes mentioned are correct or not the
        :param cell_coord: current correct cell coordinate to be added to correct cells list
        :return: True if the pre-requistes
        """
        if len(self.correct_cells)>0:
            prereq_check = all(item in self.correct_cells for item in self.grading_rubric.prereq_cells)
        else:
            prereq_check = False
        if len(self.grading_rubric.prereq_cells) == 1:
            prereq_string = 'Cell '+' '.join(self.grading_rubric.prereq_cells)
        else:
            prereq_string = 'Cells '+', '.join(self.grading_rubric.prereq_cells)
        if not prereq_check:
            report.append_line(f"{self.report_line_prefix} "+ prereq_string + " must be correct before this cell can be graded!")
            report.report_html_args['feedback'] = f" "+ prereq_string + " must be correct before this cell can be graded!"
        return prereq_check
