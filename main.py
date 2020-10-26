import click
from pysheetgrader.document import Document
from pysheetgrader.grader import Grader


@click.command()
@click.argument('key_document_path',
                type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument('submission_document_path',
                type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
def cli(key_document_path, submission_document_path):
    """ Grades the passed spreadsheet in SUBMISSION_DOCUMENT_PATH using the key spreadsheet from KEY_DOCUMENT_PATH."""
    print("PySheetGrader!")
    print(f"Key document path:\t\t{key_document_path}")
    print(f"Submission document path:\t{submission_document_path}")

    key_doc = Document(key_document_path, read_only=False)
    sub_doc = Document(submission_document_path, read_only=True)

    grader = Grader(key_doc)
    sub_score = grader.grade(sub_doc)

    print(f"Grade of the submission:\t{sub_score}")

