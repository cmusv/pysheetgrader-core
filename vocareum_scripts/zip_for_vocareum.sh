#!/bin/bash

# This script should be executed from PySheetGrader's root folder.

# Copy necessary files to pysheetgrader-vocareum
mkdir pysheetgrader-vocareum
cp -r pysheetgrader pysheetgrader-vocareum
cp -r vocareum_scripts pysheetgrader-vocareum
cp ./{requirements.txt,setup.py,setup.sh} pysheetgrader-vocareum

# Zip the folder
zip -r pysheetgrader-vocareum.zip pysheetgrader-vocareum

# Folder cleanup
rm -rf pysheetgrader-vocareum