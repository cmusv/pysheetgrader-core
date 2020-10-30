 #!/bin/sh
 # TODO: Add proper installation / environment check steps here.
 source venv/bin/activate
 pysheetgrader sample_excel_files/type_1_key.xlsx sample_excel_files/type_1_sub_right_different_formula_1.xlsx --score-output ./score-output.csv --report-output ./report-output.txt --verbose