import csv
import math
import sys
import os

REQUIRED_COLUMNS = ['assignment', 'group', 'score', 'weight']
VALID_GROUPS = ('formative', 'summative')


def load_csv_data():
    """
    Prompts the user for a filename, checks if it exists,
    and extracts all fields into a list of dictionaries.
    Bad rows are reported with their line number; blank rows are skipped.
    """
    filename = input("Enter the name of the CSV file to process (e.g., grades.csv): ").strip()

    if not filename:
        print("Error: no filename was entered.")
        sys.exit(1)

    if not os.path.exists(filename):
        print(f"Error: The file '{filename}' was not found.")
        sys.exit(1)

    if not os.path.isfile(filename):
        print(f"Error: '{filename}' is not a file.")
        sys.exit(1)

    if os.path.getsize(filename) == 0:
        print(f"Error: The file '{filename}' is empty.")
        sys.exit(1)

    assignments = []
    bad_rows = 0

    try:
        with open(filename, mode='r', encoding='utf-8-sig', newline='') as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                print(f"Error: The file '{filename}' has no header row.")
                sys.exit(1)

            headers = [h.strip().lower() for h in reader.fieldnames if h]
            missing = [c for c in REQUIRED_COLUMNS if c not in headers]
            if missing:
                print(f"Error: Missing required column(s): {', '.join(missing)}")
                print(f"Expected columns: {', '.join(REQUIRED_COLUMNS)}")
                sys.exit(1)

            for row in reader:
                line = reader.line_num
                # Normalise header names and strip whitespace from values
                row = {(k or '').strip().lower(): (v or '').strip() for k, v in row.items()}

                # Skip completely empty rows
                if not any(row.values()):
                    continue

                name = row['assignment']
                group = row['group'].lower()

                if not name:
                    print(f"Line {line}: assignment name is missing.")
                    bad_rows += 1
                    continue
                if group not in VALID_GROUPS:
                    print(f"Line {line}: invalid group '{row['group']}' for '{name}' "
                          f"(must be Formative or Summative).")
                    bad_rows += 1
                    continue

                try:
                    score = float(row['score'])
                    weight = float(row['weight'])
                except ValueError:
                    print(f"Line {line}: score and weight must be numbers "
                          f"(got score='{row['score']}', weight='{row['weight']}' for '{name}').")
                    bad_rows += 1
                    continue

                if not (math.isfinite(score) and math.isfinite(weight)):
                    print(f"Line {line}: score and weight must be finite numbers for '{name}'.")
                    bad_rows += 1
                    continue

                if weight < 0:
                    print(f"Line {line}: weight cannot be negative for '{name}'.")
                    bad_rows += 1
                    continue

                assignments.append({
                    'assignment': name,
                    'group': group.capitalize(),
                    'score': score,
                    'weight': weight
                })
    except (OSError, UnicodeDecodeError, csv.Error) as e:
        print(f"An error occurred while reading the file: {e}")
        sys.exit(1)

    if bad_rows:
        print(f"\n{bad_rows} invalid row(s) found. Please fix the CSV file and try again.")
        sys.exit(1)

    return assignments


def evaluate_grades(data):
    """
    Validates the data, calculates the GPA, decides Pass/Fail and
    finds the formative assignment(s) eligible for resubmission.
    'data' is a list of dictionaries containing the assignment records.
    """
    print("\n--- Processing Grades ---")

    if not data:
        print("Error: the CSV file contains no assignment records.")
        return

    # a) Grade validation: every score must be between 0 and 100
    valid = True
    for a in data:
        if not 0 <= a['score'] <= 100:
            print(f"Invalid score for '{a['assignment']}': {a['score']:g} (must be between 0 and 100)")
            valid = False

    # b) Weight validation: Total=100, Summative=40, Formative=60
    formative = [a for a in data if a['group'] == 'Formative']
    summative = [a for a in data if a['group'] == 'Summative']
    f_weight = round(sum(a['weight'] for a in formative), 6)
    s_weight = round(sum(a['weight'] for a in summative), 6)
    total_weight = round(f_weight + s_weight, 6)

    if total_weight != 100:
        print(f"Invalid weights: total is {total_weight:g}, expected 100.")
        valid = False
    if s_weight != 40:
        print(f"Invalid weights: Summative total is {s_weight:g}, expected 40.")
        valid = False
    if f_weight != 60:
        print(f"Invalid weights: Formative total is {f_weight:g}, expected 60.")
        valid = False

    if not valid:
        print("\nValidation failed. Please fix the CSV file and try again.")
        return

    # c) Final grade and GPA: GPA = (Total Grade / 100) * 5.0
    f_earned = sum(a['score'] * a['weight'] / 100 for a in formative)
    s_earned = sum(a['score'] * a['weight'] / 100 for a in summative)
    total_grade = f_earned + s_earned
    gpa = (total_grade / 100) * 5.0

    # d) Pass/Fail: >= 50% in BOTH categories
    f_pct = (f_earned / f_weight) * 100
    s_pct = (s_earned / s_weight) * 100
    passed = f_pct >= 50 and s_pct >= 50

    # e) Failed formative assignments (< 50%) with the highest weight (ties included)
    failed = [a for a in formative if a['score'] < 50]
    resubmit = []
    if failed:
        top_weight = failed[0]['weight']
        for a in failed:
            if a['weight'] > top_weight:
                top_weight = a['weight']
        resubmit = [a for a in failed if a['weight'] == top_weight]

    # f) Print the final decision and resubmission options
    print(f"{'Assignment':<40}{'Group':<12}{'Score':>7}{'Weight':>8}")
    for a in data:
        print(f"{a['assignment']:<40}{a['group']:<12}{a['score']:>7g}{a['weight']:>8g}")

    print(f"\nFormative: {f_earned:g}/{f_weight:g} ({f_pct:.2f}%)")
    print(f"Summative: {s_earned:g}/{s_weight:g} ({s_pct:.2f}%)")
    print(f"Total Grade: {total_grade:.2f}/100")
    print(f"GPA: {gpa:.4f}")
    print(f"Final Status: {'PASSED' if passed else 'FAILED'}")

    if resubmit:
        print("\nEligible for resubmission:")
        for a in resubmit:
            print(f"  - {a['assignment']} (score {a['score']:g}, weight {a['weight']:g})")
    else:
        print("\nNo failed formative assignments to resubmit.")


if __name__ == "__main__":
    # 1. Load the data
    course_data = load_csv_data()

    # 2. Process the features
    evaluate_grades(course_data)
