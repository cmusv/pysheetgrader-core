#!/bin/sh

echo "PySheetGrader Setup"
echo "Checking environment"

if ! command -v python3 &>/dev/null;
then
  echo "Command 'python3' cannot be found. Aborting."
  exit 1
fi

if ! command -v pip &>/dev/null;
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
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
