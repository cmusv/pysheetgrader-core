## License and Copyright

See LICENSE file.

# PySheetGrader

Blog: https://se-edu.org/auto-grading-spreadsheet-assignments/

## What does PySheetGrader do?

PySheetGrader is a grading automation system for spreadsheet-based assignments. Spreadsheets are frequently used in data-oriented courses due to its WYSISWG nature and low learning curve, such as 18657 Decision Analysis for Software Engineers. Grading these assignments manually are tedious and error prone, and PySheetGrader helps the teaching team by automating the grading process.

## How to setup

Here are the files that need to be copied to make PySheetGrader works:

- `pysheetgrader` directory
- `main.py`
- `requirements.txt`
- `setup.py`
- `setup.sh`

After downloading or cloning this repository, you could run `./setup.sh` as a quick way to install PySheetGrader to your system. Your system needs to have `python3` and `pip` installed.

Otherwise, you could do it manually by executing these steps:

```
python3 -m venv ./venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
``` 

## How to run

After setting up PySheetGrader, make sure to activate the virtualenv:
```
source venv/bin/activate
```

Then, you can execute the `pysheetgrader` command:

```
pysheetgrader $KEY_DOC_PATH $SUB_DOC_PATH --score-output $SCORE_OUTPUT_PATH --report-output $REPORT_OUTPUT_PATH --html-report-output $HTML_REPORT_OUTPUT_PATH
```

Arguments of `pysheetgrader` are:

- `KEY_DOC_PATH`: path to the key document, used for grading (an excel spreadsheet with .xlsx extension).
- `SUB_DOC_PATH`: path to the submission document that will be graded (an excel spreadsheet with .xlsx extension).
- `SCORE_OUTPUT_PATH`: path to the file where the grading score will be stored. This is optional, since the score will be shown in the terminal window.
- `SCORE_REPORT_PATH`: path to the file where the detailed report will be stored. This is optional.
- `HTML_REPORT_OUTPUT_PATH_`: path to the html file where a tabulated HTML report will be stored. This is optional.

There's also the `--verbose` flag that will output the report to the terminal throughout the process.

For example, you could execute the command below to see how it works with a sample spreadsheet:

```
pysheetgrader sample_excel_files/MasterGalleryKey.xlsx sample_excel_files/MasterGallerySubmission.xlsx --verbose
```

## Creating a key document

PySheetGrader will require a key document to run. A proper *.xlsx key document should have these specifications:

1. A sheet named `SheetGradingOrder`, which contains the order of the sheets that needs to be graded on the B column, starting from row 2.
2. For each graded sheet, there should be a pairing sheet with name of `[sheet_name]_CheckOrder`, which contains the order of the cells that needs to be graded on the B column, starting from row 2.
3. An Excel cell note, called rubric note, for each graded cell that contains a rubric specification to grade that cell. The details of the rubric note will be provided in the next section.

Here are some sample images:

- SheetGradingOrder content:

![Image of the content in SheetGradingOrder](readme_images/sheet_grading_order.png)

- CheckOrder sheet content (in this case, it's `Constant Samples_CheckOrder`):

![Image of the content in CheckOrder](readme_images/cell_check_order.png)

- Rubric note of one of the graded cells, as an Excel note attached to cell B8 of Constant Samples:

![Image of the rubric note of cell B6 in Sheet3](readme_images/cell_rubric_note.png)

The complete sample of a key document is available on the [MasterGalleryKey.xlsx](sample_excel_files/MasterGalleryKey.xlsx).

## Creating a rubric note

Rubric notes of a cell are written in YAML format. It consists of a mandatory section called `rubric` and optional sections called `alt_cells` and `test_cases`.

```
rubric:
 ...
alt_cells:
 ...
test_cases:
 ...
```


### Typsetting rubric notes: known issue with rich text and workarounds 

**Use striclty plain text for entering a rubric note.** 

Excel's cell notes support rich text, and using rich text in rubric notes will crash the rubric parsing process. When writing a new rubric note, by default you will enter plain YAML text, however sometimes Excel will automatically add boilerplate text in rich text to a new cell note. Also be careful with copy-paste: copying the rubric content from an external text editor or another spreadsheet cell and pasting it into a new rubric note may also copy any rich-text formatting. Here are some tips and workarounds:

1. When a rubric note is corrupted by rich text, try coping the rubric content to a plain text editor (e.g., Sublime Text or VSCode) first, delete the faulty rubric note, create a new rubric note, then copy the content back from the plain text editor to the new rubric note. 
2. To clone a correclty typeset rubric note in an existing cell, simply copy the cell in Excel and use `Edit > Paste Special > Comments` to paste it onto the other cell. This paste command copies the cell note as well as comments, without copying the actual cell contents. 
3. If you add a rubric with `Right-Click > New Note`, the author, if defined, is by default typset in bold (rich text), so make sure to completely zap this rich-text part otherwise the rubric will not work. Deleting the author simply by backspacing here may not work, and instead the whole rubric may end up being typset in bold!
 

### Rubric 

The `rubric` section defines the main rubric properties and consists of these attributes:

```
rubric:
 score: ...
 type: ... 
 delta: ...
 grading: ...
```


1. `score` (mandatory, an integer or float), which contains a positive value that will be awarded when the graded cell is correct in the submission sheet or contains a negative value that will be deducted when the graded cell is incorrect in the submission sheet. 
2. `type` (mandatory), which determines how this cell will be graded. There are two options: 
    - `constant`, which compares the evaluated value of the corresponding submission sheet cell to the evaluated value of the key cell. Will utilize the `delta`for precision, if specified for cells with numeric values.
    - `formula`,  which compares the formula of the corresponding submission sheet cell to the formula given in this cell.
    - `test`, which evaluates the formula of the submission sheet cell against the test cases.
    - `soft_formula`, which requires the submission cell to be a formula, but otherwise performs the comparison with evaluated values as in the `constant` rubric type.
    - `relative` or `relative_f`, which evaluates the formula in the key cell using values from the submission cells and compares the result to the value in the submission cell. 
    - `check`, which compares the result to a given cell's value in the Key (rather than the submission) 
3. `delta` (optional, an integer or float), which specifies precision in numeric value comparisons. Will only work with non-formula rubric types when they check numeric calculations; e.g., `constant`, `relative`, `relative_f`, `soft_formula`, and `test` (inside individual test cases) rubric types. 
4. `grading` (optional), which is used to allow negative grading:
   - `positive` (default value): if the calculation is correct according to the specified rubric type, then the points specified in the `score` attribute is awarded for the cell, and no feedback is given (green row in the HTML report). Otherwise, no points are awarded and the specified feedback is given (red row in HTML report). If `grading` is unspecified, it is assumed to be `positive`. The rubric's `score` attribute must have a positive value. 
   - `negative`: if the calculation is correct according to the specified rubric type, then no points are deducted, no feedback is given (green row in the HTML report), and the cell gets the maximum score of 0. Otherwise, the cell receives the negative points specified in the `score` attribute, which are deducted from the total grade, and the specified feedback is given (red row in HTML report). The rubric's `score` attribute must have a negative value, indicating a deduction or penalty. 

### Alternative cells 

The `alt_cells` section consists of an array of cell references to the key sheet. 


```
alt_cells:
 - ...
 - ...
 - ...
 ...
```

The  cell references point to alternative contents in the key sheet to be used in grading the the cell. The references may contain constants or formulas, depending on the rubric type. This section is useful if a single cell has multiple correct answers or different ways of calculating the same correct answer. Below is an example rubric with alternative cells. Say this rubric note defined in cell H5 of the key sheet:

```
rubric:
 score: 1
 type: formula 
alt_cells:
 - P5
 - Q5
 - R5
```

Here PySheetGrader will compare the formula of the submission and key in the cell H5 first. If the formulas don't match, PySheetGrader will compare submission's H5 formula against the key's P5, Q5, and R5 formulas, in that order. If any of them matches the submission formula, the submission cell will be graded as correct.

### Test cases

The `test_cases` section is used with the `test` rubric type and pecifies the test cases to run against the submission sheet cell's formula. It consist of a test case name, which holds three attributes: `input`, `output`, and the optional `delta`. The `test_cases` section is invalid with rubric types other than the `test` rubric type.

```
test_cases:
 ...:
  output: ...
  input:
   ...: ...
   ...: ...
   ...
  delta: ...
 ...:
   output: ...
   input:
    ...: ...
    ...: ...
    ...
   delta: ...
 ...
```

Here's a sample use case. In the [MasterGalleryKey.xlsx](sample_excel_files/MasterGalleryKey.xlsx), cell `B5` of the `Test Case Samples` sheet has this formula:

```
= ROUNDUP(B2 / 100, B4)
```

The corresponding excel sheet for submission, [MasterGallerySubmission.xlsx](sample_excel_files/MasterGallerySubmission.xlsx), has this formula for the same cell and sheet:

```
= ROUNDUP(B2 * 0.01, B4)
```

Although both inherently similar, Sympy didn't regard both as similar due to use of custom formula (`ROUNDUP`) and difference in the passed parameter (`B2 / 100` vs `B2 * 0.01`). Using `formula` rubric will make the submission marked as incorrect. However, passing custom values for B2 and B4 to them using the `test` rubric will mark the submission as correct! Here's the sample rubric, taken from the MasterGalleryKey, sheet `Test Case Samples`, cell `B5`:

```
rubric:
 score: 1.5
 type: test
test_cases:
 default_test:
  output: 21
  input:
   B2: 2020
   B4: 0
 custom_rounding_input:
   output: 20.2
   input:
    B2: 2020
    B4: 1
```

PySheetGrader will also print the test case name in the report output (or the terminal, if ran with `--verbose` flag). Here's a sample output for the sheet:

```
Grading for sheet: Test Case Samples
	- Cell B5, test case runs.
		Test cases:
		- default_test: PASS
		- custom_rounding_input: PASS
	Score: 1.5 / 1.5
	- Cell B9, test case runs.
		Test cases:
		- default_test: PASS
	Score: 1.5 / 1.5
	- Cell B10, test case runs.
		Test cases:
		- default_test: PASS
	Score: 1.5 / 1.5
```

A single test case might also have `delta` for its output. Here's a sample rubric with test case that uses delta, taken from cell `B9` of the `Test Case Samples` sheet:

```
rubric:
 score: 1.5
 type: test
test_cases:
 default_test:
  output: 3280.84
  delta: 0.26
  input:
   B7: 1000
```

Based on the rubric above, the submission will be regarded as right if the output falls between `3280.58` to `3281`.

## Rubric Types

### Soft Rubric type
The rubric type `soft_formula` evaluates the key cell as follows:
1) If the cell does not contain a formula, no credit is given.
2) If the cell contains a formula, grade it like a constant rubric type (compare cell's evaluated result to key's evaluated result, ignoring the formulas). 
For example, for a given cell the key expects the answer 0.5 using the formula `0.1* B2`. In this case, under the `soft_formula` rubric, the grader checks the submission cell if contains a formula or not. If the formula is present (even if it is not equivalent to the key cell's formula), it assigns grade based on the actual cell value. So, if the submission cell evaluates to 0.5 through theformula`0.6*B3`, the student still gets full credit.

### Relative Formula rubric type
Relative formulas are now possible with two rubric types:  `relative` or `relative_f`.

* `relative` compares the evaluation of key's formula using the **submission cells values** (the actual values of the key cells referenced in the submission cell). For example, suppose the cell A1 in `A1Key.xlsx` contains a formula `=IF(A2 = "ok", B2, C2)`. Inside the student submission, suppose A1 contains 13, A2 contains "not_ok", B2 contains 13, and C2 contains 14. The instructor's formula will be evaluated with the student submission's cells, which gives a value of 14. This evaluated answer will be checked against the submission's evaluated A1 cell value, which is 13. In this case, A1 doesn't pass the rubric (the actual value is 13, but the expected value is 14).  

* `relative_f` is a stricter version of `relative` rubric. It grades like the `relative`, but additionally it requires the evaluated submission cell to be a formula. If the evaluated cell is a hardcoded constant, the student will not get a score. In the above example, even if the student's A1 contains a hardcoded value 14, the rubric still doesn't pass.

As a side note, both `relative` and `relative_f` supports the `delta` and `alt_cells` rubric modifiers for flexibility.

## Minimum work feature
This feature allows the instructor to specify the minimum score for every sheet and corresponding message in the SheetGradingOrder sheet.
So, if for any sheet, a student scores less than the minimum value, the student does not get the feedback for questions answered in that sheet. The student instead receieves a message in the report saying "Need more work to recieve a grade". 

Below is an example of the SheetGradingOrder sheet: 
![Image of the Check Order with Minimum Work](readme_images/min_work_crop.png)

If there is no minimum threshold for any sheet, in that case, 0 is used as the default threshold.

## Failure message for failed test cases
This feature allows us to provide a specialized, optional failure message per test case in the test_cases rubric. They can be used to give a useful clue without giving the answer, in the same manner as unit test failure messages.

Example:

A message could be "if cell A1 = 5 and A2 = 3, this cell value should be 8, but was 3!".

Without failure message:

```
rubric:
 score: 2
 type: test
test_cases:
 t1:
  output: 3280.84
  delta: 0.1
  input:
   B7: 1000
   B8: 25
```

With failure message:

```
rubric:
 score: 2
 type: test
test_cases:
 t1:
  output: 3280.84
  delta: 0.1
  input:
   B7: 1000
   B8: 25
  fail: "When B7 is $B7 and B8 is $B8, this cell should be $expected, but was $actual!"
```

If the t1 fails, this message is printed next to in sub report next to the failure. The $ variables refer to input cells, the output cell (expected) and the actual evaluated value (actual). 
So, in the above example, the output message will be: When B7 is 1000 and B8 is 25, this cell should be 3280.84, but was 2025.34!
Also, it is important to be careful about indentation while creating this rubric. fail should have the same indentation as input, output and delta. 

## Sub-sheet totals
This feature provides subtotals for each sheet in the SheetGradingOrder sheet. It provides the output as the subtotal for each sheet followed by total score for all sheets.

```
Sheet1
Total: xx / yy

Sheet2
Total xx / yy

Assignment Score: << grand total of all subtotals >>
```

## Hidden cells

Some cells can be graded secretively, with student feedback indicating that something went wrong in that cell without specifing which cell caused the problem. In the CheckOrder sheet of a graded tab, there is a decidaced column titled "Hidden" to indicated this. Enter H in this column if the cell is to be graded secretively. 