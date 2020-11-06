#!/bin/bash

echo "PySheetGrader Setup"
echo "Checking environment"

if ! [ -x "$(command -v python3)" ];
then
  echo "Command 'python3' cannot be found. Aborting."
  exit 1
fi

if ! [ -x "$(command -v pip)" ];
then
  echo "Command 'pip' cannot be found. Aborting."
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
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
