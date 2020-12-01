#!/bin/bash

# This script should be executed from PySheetGrader's root folder.
# Reference: https://stackoverflow.com/a/57162139/1448626

source venv/bin/activate
python3 -m pip install wheel
python3 setup.py bdist_egg --exclude-source-files
wheel convert dist/*.egg