# alu_transcript_generator: ALU Transcript Generator

Individual Coding Lab, Introduction to Python Programming and Databases (BSE Year 1, Trimester 2).

A Python program that calculates a student's final standing from a CSV file of course grades, and a Bash script that archives the CSV and logs each run.

## Files

| File | Purpose |
|------|---------|
| `grade-evaluator.py` | Validates the data, calculates the GPA, decides PASSED/FAILED and lists resubmission options |
| `organizer.sh` | Archives `grades.csv` with a timestamp, resets the workspace and logs the action |
| `grades.csv` | Source data |
| `README.md` | This file |

## CSV format

```
assignment,group,score,weight
Quiz,Formative,85,20
Midterm Project - Simple Calculator,Summative,70,20
```

- `group` is `Formative` or `Summative`
- `score` is a percentage from 0 to 100
- `weight` is the assignment's share of the final grade

## Running the evaluator

```
python3 grade-evaluator.py
```

Enter the CSV filename when prompted (for example `grades.csv`).

### What it does

1. **Grade validation:** every score must be between 0 and 100.
2. **Weight validation:** all weights must total exactly 100, with Formative totalling 60 and Summative totalling 40.
3. **GPA:** `GPA = (Total Grade / 100) * 5.0`, where the total grade is the sum of `score * weight / 100`.
4. **Pass/Fail:** the student passes only with at least 50% in both the Formative and the Summative category.
5. **Resubmission:** among failed formative assignments (score below 50), the one with the highest weight is eligible. If several share that weight, all are listed.

### Error handling

The program prints a clear message and exits, without a traceback, when the file is missing, empty or unreadable, when required columns are missing, or when a row has a non-numeric score or weight, an invalid group or a missing name. Blank rows are skipped. Out-of-range scores and incorrect weight totals are reported before any calculation.

### Example output (provided `grades.csv`)

```
Formative: 34/60 (56.67%)
Summative: 26/40 (65.00%)
Total Grade: 60.00/100
GPA: 3.0000
Final Status: PASSED

Eligible for resubmission:
  - Group Exercise (score 40, weight 20)
  - Functions and Debugging Lab (score 45, weight 20)
```

## Running the organizer

```
chmod +x organizer.sh
./organizer.sh
```

Each run:

1. Creates the `archive/` directory if it does not exist.
2. Renames `grades.csv` to `grades_YYYYMMDD-HHMMSS.csv` and moves it into `archive/`.
3. Creates a new empty `grades.csv`.
4. Appends the timestamp, original filename and archived filename to `organizer.log`.
