import click


@click.command()
@click.argument('key_document',
                type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
@click.argument('submission_document',
                type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True))
def cli(key_document, submission_document):
    """ Grades the passed SUBMISSION_DOCUMENT using the KEY_DOCUMENT."""
    print("PySheetGrader!")
    print(f"Input key document: {key_document}")
    print(f"Submission key document: {submission_document}")
