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
/usr/bin/python3.7 -m venv ./venv

echo ">> Activating virtual environment..."

source venv/bin/activate


echo ">> Installing dependencies..."

# /usr/bin/pip3.7 install --upgrade pip
/usr/bin/pip3.7 install -r requirements.txt
pip3.7 install -e .
