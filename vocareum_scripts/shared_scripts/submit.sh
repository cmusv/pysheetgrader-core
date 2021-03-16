#!/bin/bash

# Local dependency setup
# This is necessary because the submission workspace is different than the normal student workspace.
# The path relies on the folder structure. Check zip_for_vocareum.sh as reference.

source $LIB/pysheetgrader-vocareum/vocareum_scripts/student/setup_venv.sh > /dev/null

# Activate python virtual environment

source venv/bin/activate

# Take env variables from assignment config

source $ASNLIB/pysheetgrader.config

# Path setup

KEY_DOC_PATH="${ASNLIB}/${ASSIGNMENT_PREFIX}Key.xlsx"
SUB_DOC_PATH="${HOME}/${ASSIGNMENT_PREFIX}Submission.xlsx"

SCORE_OUTPUT_PATH=$vocareumGradeFile
REPORT_OUTPUT_PATH=$vocareumReportFile
HTML_REPORT_OUTPUT_PATH="${HOME}/${ASSIGNMENT_PREFIX}Report.html"

# Execute grading

pysheetgrader $KEY_DOC_PATH $SUB_DOC_PATH --score-output $SCORE_OUTPUT_PATH --report-output $REPORT_OUTPUT_PATH \
  --html-report-output $HTML_REPORT_OUTPUT_PATH --verbose



