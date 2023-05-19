from cgi import test
import click, os, datetime
import warnings

from pysheetgrader.document import Document
from pysheetgrader.grader import Grader


@click.command()
@click.argument('key_document_path',
                type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument('submission_document_path',
                type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.option('--score-output', type=click.Path(writable=True),
              help="File path where the score output will be saved.")
@click.option('--report-output', type=click.Path(writable=True),
              help="File path where the detailed report will be saved.")
@click.option('--html-report-output', type=click.Path(writable=True),
              help="File path where the rendered HTML report will be saved.")
@click.option('-v', '--verbose', is_flag=True, help="Print grading details verbosely in stdout")
@click.option('-i', '--ignore-warnings', is_flag=True, help="Should suppress warnings from depending modules")
@click.option('-T', '--test-mode', is_flag=True, help="Run the autograder in test mode")
@click.option('-d', '--debug-mode', is_flag=True, help="Run the autograder in debug mode")
@click.option('-l', '--log-mode', is_flag=True, help="Run the autograder in log mode")
def cli(key_document_path, submission_document_path, score_output, report_output, html_report_output, verbose,
        ignore_warnings, test_mode, debug_mode, log_mode):
    """ Grades the passed spreadsheet in SUBMISSION_DOCUMENT_PATH using the key spreadsheet from KEY_DOCUMENT_PATH."""

    print("PySheetGrader!")
    if test_mode:
        print("==========Test Mode==========")
    print(f"Key document path:\t\t{key_document_path}")
    print(f"Submission document path:\t{submission_document_path}")

    if ignore_warnings:
        warnings.filterwarnings(action='ignore')

    key_doc = Document(key_document_path, read_only=False)
    sub_doc = Document(submission_document_path, read_only=True)

    grader = Grader(key_doc, test_mode, debug_mode, log_mode)
    report = grader.grade(sub_doc)

    if verbose:
        report.print_lines()

    print(f"Grade of the submission:\t{report.submission_score} / {report.max_possible_score}")

    if score_output:
        save_score(report, score_output)

    if report_output:
        save_report(report, report_output)

    if html_report_output:
        save_html_report(report, html_report_output)
        
    key_doc.close()
    sub_doc.close()


def save_score(report, output_path):
    """
    Saves the score of the passed report to the output_path.
    :param report: GradingReport instance.
    :param output_path: String value of the output file path.
    """
    with open(output_path, 'w') as file:
        file.write(f"Assignment Score, {report.submission_score}\n")


def save_report(report, output_path):
    """
    Saves the report of the passed report to the output_path.
    :param report: GradingReport instance.
    :param output_path: String value of the output file path.
    """
    with open(output_path, 'w') as file:
        file.writelines(report.report_lines)


def save_html_report(report, output_path):
    """
    Save the HTML version of the passed report to the output_path
    :param report: GradingReport instance.
    :param output_path: String value of the output file path.
    :return:
    """
    import jinja2
    loader = jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "template"))
    env = jinja2.Environment(loader=loader)

    with open(output_path, 'w') as file:
        template = env.get_template('report.html.jinja')
        template.globals['now'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M %p')
        rendered = template.render({'html_args': report.report_html_args})
        file.write(rendered)
