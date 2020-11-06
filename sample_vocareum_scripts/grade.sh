#!/bin/bash


# Path setup

KEY_DOC_PATH=$ASNLIB/key.xlsx
SUB_DOC_PATH=$HOME/submission.xlsx

SCORE_OUTPUT_PATH=$vocareumGradeFile
REPORT_OUTPUT_PATH=$vocareumReportFile

# Activate env
# Make sure build.sh is executed before this.

cd $LIB/pysheetgrader-master
source venv/bin/activate

# This part is necessary to ensure missing requirements are catched, e.g. click.

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install -e .

# Execute grading

pysheetgrader $KEY_DOC_PATH $SUB_DOC_PATH --score-output $SCORE_OUTPUT_PATH --report-output $REPORT_OUTPUT_PATH --verbose 
