
## How to setup in Vocareum (Deprecated)

Running PySheetGrader in Vocareum could be tricky. PySheetGrader relies on other Python packages (e.g., `sympy` and `openpyxl`) and Vocareum seems to have different user levels, which makes it hard for installing a package once and reusing it at other user levels.
However, a fresh PySheetGrader installation will only take one to two minutes, which considered to be acceptable for a single student's submission. 

Here are the general steps on setting up PySheetGrader in Vocareum to make it usable for the students in an assignment:

1. Teacher sets up PySheetGrader inside Vocareum's teacher workspace 
2. Teacher compiles PySheetGrader to installable wheel package 
3. Teacher copies shared Vocareum scripts to corresponding folder in Vocareum workspace 
4. Teacher copies shared assignment files to Vocareum's assignment folder
5. Teacher set up variables in the configuration file for the assignment
6. Teacher uploads the key spreadsheet for the assignment to Vocareum's assignment folder
7. Student uploads the submission spreadsheet to their workspace

Here are the details for each step above:

### 1. Set up the teacher's workspace

1. Zip the necessary files to run PySheetGrader by executing `./vocareum_scripts/zip_for_vocareum.sh` from the root folder. This will generate `pysheetgrader-vocareum.zip`.
2. Upload `pysheetgrader-vocareum.zip` to `resource/lib` in Vocareum's teacher workspace.
3. In the Vocareum's terminal, go to the uploaded directory by executing `cd $LIB/pysheetgrader-vocareum`.
4. Execute `./setup.sh` to set up the virtual environment.

### 2. Compile PySheetGrader (teacher)

Right after setting up the workspace, we need to execute `./vocareum_scripts/teacher/package_for_students.sh`. This script will create an installable *.whl file in the `pysheetgrader-vocareum` folder and copy it to `student_installer` folder at the root level. It will also copy the `requirements.txt` file to the folder, which contains the Python dependencies to be installed later. The contents of `student_installer` will be used for installing PySheetGrader at the student level.

The compilation process needs to be done on Vocareum to make sure the grader is compiled for the execution environment Vocareum uses, which will be different from that of a local platform.

### 3. Copy shared Vocareum scripts (teacher)

In the `vocareum_scripts` folder, there's a folder named `shared_scripts`. Please copy the contents of each script to the corresponding filename in Vocareum workspace's `scripts` folder.

### 4. Copy configuration file (teacher)

In the `vocareum_scripts` folder, there's a folder named `shared_asnlib`. Please copy the folder's contents to the `asnlib` folder in the workspace.

### 5. Configure assignment variables (teacher)

In the `pysheetgrader.config` of the `asnlib` folder (copied from previous step), there's variable called `ASSIGNMENT_PREFIX`. Please set up the value of the variable to be used for the key and submission file in this assignment.

### 6. Upload the key Excel document (teacher)

The `submit.sh` script will take an excel file named `[ASSIGNMENT_PREFIX]Key.xlsx` in the `asnlib` folder. Please upload your key Excel file to the `asnlib` folder and rename it correspondingly. For example, if the `ASSIGNMENT_PREFIX` value is `A1` in the config file, the key spreadsheet should be named as `A1Key.xlsx`.

### 7. Uploads the submission Excel document (student)

The student needs to upload their `*.xlsx` file to the root folder of their workspace and rename it to `[ASSIGNMENT_PREFIX]Submission.xlsx`. The `submit.sh` will take the submitted file and compare it to the corresponding key file. For example, if the `ASSIGNMENT_PREFIX` value is `A1` in the config file, the submission spreadsheet should be named as `A1Submission.xlsx`.
