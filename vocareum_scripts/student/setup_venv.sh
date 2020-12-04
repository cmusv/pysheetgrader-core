#!/bin/bash

echo "PySheetGrader Setup"
echo "Checking environment"

if ! [ -x "$(command -v python3)" ];
then
  echo "Command 'python3' cannot be found. Aborting."
  exit 1
fi

if [ -d "venv" ];
then
  echo "Folder 'venv' already exists."
else
  echo "Folder 'venv' not exist yet. Creating virtual environment in venv."
  python3 -m venv ./venv
fi

echo "Installing dependencies."

source venv/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install wheel

# These two lines are the main difference compared to the root-level setup.sh.

python3 -m pip install -r $LIB/public/pysheetgrader-vocareum/requirements.txt
python3 -m pip install $LIB/public/pysheetgrader-vocareum/*.whl