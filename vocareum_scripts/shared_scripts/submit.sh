#!/bin/bash


# Path setup

KEY_DOC_PATH=$ASNLIB/key.xlsx
SUB_DOC_PATH=$HOME/submission.xlsx

SCORE_OUTPUT_PATH=$vocareumGradeFile
REPORT_OUTPUT_PATH=$vocareumReportFile

# Activate env
source $LIB/pysheetgrader-0.3/venv/bin/activate

# Execute grading
pysheetgrader $KEY_DOC_PATH $SUB_DOC_PATH --score-output $SCORE_OUTPUT_PATH --report-output $REPORT_OUTPUT_PATH --verbose
