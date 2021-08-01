#!/bin/bash

echo ">>>> Local PySheetGrader Setup <<<<"
echo "Checking environment..."

if ! [ -x "$(command -v python3)" ];
then
  echo ">> Command 'python3' cannot be found: install python3 first. Aborting..."
  exit 1
fi

if [ -d "venv" ];
then
  echo ">> Folder 'venv' already exists. Deleting..."
  rm -rf venv
fi

echo ">> Creating a new virtual environment in venv folder..."
python3 -m venv ./venv

echo ">> Activating virtual environment..."

source venv/bin/activate


echo ">> Installing dependencies..."

python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
