#!/bin/bash

# Local dependency setup
# This is necessary because the submission workspace is different than the normal student workspace.
# The path relies on the folder structure. Check zip_for_vocareum.sh as reference.

source $LIB/pysheetgrader-vocareum/vocareum_scripts/student/setup_venv.sh > /dev/null

# Activate python virtual environment

source venv/bin/activate

# Path setup

KEY_DOC_PATH=$ASNLIB/key.xlsx
SUB_DOC_PATH=$HOME/submission.xlsx

SCORE_OUTPUT_PATH=$vocareumGradeFile
REPORT_OUTPUT_PATH=$vocareumReportFile

# Execute grading

pysheetgrader $KEY_DOC_PATH $SUB_DOC_PATH --score-output $SCORE_OUTPUT_PATH --report-output $REPORT_OUTPUT_PATH --verbose

