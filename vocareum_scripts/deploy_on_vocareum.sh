#!/bin/bash

# run this script after unzipping pysheetgrader-vocareum.zip,
# this script should be located in $LIB/pysheetgrader-vocareum

GREEN=$(tput setaf 2)
RESET=$(tput sgr0)

# Step 1: setup venv
./setup.sh

# Step 2: Compile pysheetgrader
source vocareum_scripts/teacher/package_for_students.sh

# Step 3: Copy shared Vocareum scripts
cp -a vocareum_scripts/shared_scripts/. $ASNLIB/../scripts.0/

# Step 4: Copy configuration file
cp -a vocareum_scripts/shared_asnlib/. $ASNLIB

echo -e "${GREEN}Important TODOs for each individual assignment:

1. Configure ASSIGNMENT_PREFIX in resource/asnlib/pysheetgrader.config
2. Upload [ASSIGNMENT_PREFIX]Key.xlsx to resource/asnlib
3. Click Update*
4. Test [ASSIGNMENT_PREFIX]Submission.xlsx in Student View

${RESET}
"
