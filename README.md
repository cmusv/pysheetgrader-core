# PySheetGrader

## How to setup

You could run `./setup.sh` as a quick way to install PySheetGrader to your system. This will require your system to have `python3` and `pip` installed.

Otherwise, you could do it manually by executing these steps:

```
python3 -m venv ./venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
``` 

## How to run

After setting up PySheetGrader, make sure to activate the virtualenv:
```
source venv/bin/activate
```

Then, you can call the `pysheetgrader` command:

```
pysheetgrader $KEY_DOC_PATH $SUB_DOC_PATH --score-output $SCORE_OUTPUT_PATH --report-output $REPORT_OUTPUT_PATH --verbose
```

Explanation for each variables:

- `KEY_DOC_PATH`: path to the key document, used for grading.
- `SUB_DOC_PATH`: path to the submission document that will be graded.
- `SCORE_OUTPUT_PATH`: path to the file where the grading score will be stored. This is optional, since the score will be shown in the terminal window.
- `SCORE_REPORT_PATH`: path to the file where the detailed report will be stored. This is optional.

There's also the `--verbose` flag that will output the report to the terminal throughout the process.
