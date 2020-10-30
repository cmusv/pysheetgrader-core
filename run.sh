#!/bin/sh
# TODO: Add proper installation / environment check steps here.
source venv/bin/activate

KEY_DOC_PATH=sample_excel_files/type_1_key.xlsx
SUB_DOC_PATH=sample_excel_files/type_1_sub_right_different_formula_1.xlsx
SCORE_OUTPUT_PATH=$vocareumGradeFile
REPORT_OUTPUT_PATH=$vocareumReportFile
pysheetgrader $KEY_DOC_PATH $SUB_DOC_PATH --score-output $SCORE_OUTPUT_PATH --report-output $REPORT_OUTPUT_PATH --verbose