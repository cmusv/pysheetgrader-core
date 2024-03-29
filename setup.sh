#!/bin/bash

# pip install --upgrade should not run Vocareum, so this should be removed for Vocareum installation!

# update this with additional log messages from latest instance of the DASE course

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

echo ">> WARNING: Upgrading pip may break pysheetgrader installation on Vocareum!"
echo ">> Do you want to upgrade pip (Yes/No)?"
select yn in "Yes" "No"; do
    case $yn in
        Yes ) echo "You answered Yes: upgrading pip..."; python3 -m pip install --upgrade pip; break;;
        No )  echo "You answered No": skipping pip upgrade...""; break;;
        * ) echo "Please enter 1 for Yes or 2 for No.";;
    esac
done

# python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 -m pip install -e .
