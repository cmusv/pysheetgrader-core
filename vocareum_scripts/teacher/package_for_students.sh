#!/bin/bash

# This script should be executed from PySheetGrader's root folder.
# Reference: https://stackoverflow.com/a/57162139/1448626

source venv/bin/activate
python3 -m pip install wheel
python3 setup.py bdist_egg --exclude-source-files
wheel convert dist/*.egg

# This part below is for copying the necessary files for student's setup step

if [ -d "student_installer" ];
then
  echo "Old student setup files found, deleting it for replacement"
  rm -rf student_installer
fi

mkdir student_installer
cp requirements.txt student_installer
cp *.whl student_installer
