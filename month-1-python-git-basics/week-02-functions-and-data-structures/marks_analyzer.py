"""Student marks analyzer.

Reads student names and marks, then computes the average, highest,
lowest, and pass/fail status. Along the way it demonstrates functions
with arguments, return values and local scope, plus the four core
built-in data structures: lists, dicts, tuples and sets.
"""

PASS_MARK = 40

# A dict mapping student name -> mark. Sample data so the script
# runs without any input, but read_marks() can replace it.
SAMPLE_MARKS = {
    "Asha": 78,
    "Ben": 35,
    "Carla": 92,
    "Dev": 40,
    "Erin": 21,
}


def average(marks):
    """Return the average of a list of marks (a local variable, scoped here)."""
    if not marks:
        return 0
    total = sum(marks)
    return total / len(marks)


def highest(marks):
    """Return the highest mark, or None for an empty list."""
    return max(marks) if marks else None


def lowest(marks):
    """Return the lowest mark, or None for an empty list."""
    return min(marks) if marks else None


def split_pass_fail(student_marks):
    """Return a tuple of (passed, failed) name lists.

    Demonstrates returning a tuple and building lists.
    """
    passed = []
    failed = []
    for name, mark in student_marks.items():
        if mark >= PASS_MARK:
            passed.append(name)
        else:
            failed.append(name)
    return passed, failed


def unique_marks(student_marks):
    """Use a set to find the distinct mark values."""
    return set(student_marks.values())


def read_marks():
    """Read names and marks from the user.

    Returns a dict. If the user enters nothing, fall back to the sample data.
    """
    student_marks = {}
    print("Enter student marks. Leave the name blank to finish.")
    while True:
        name = input("Name: ").strip()
        if name == "":
            break
        raw = input(f"Mark for {name} (0-100): ").strip()
        try:
            mark = int(raw)
        except ValueError:
            print("That's not a whole number, skipping this student.")
            continue
        student_marks[name] = mark

    if not student_marks:
        print("No input given, using sample data.\n")
        return dict(SAMPLE_MARKS)
    return student_marks


def report(student_marks):
    """Print a full report for the given marks."""
    marks = list(student_marks.values())

    print("--- Marks Report ---")
    for name, mark in student_marks.items():
        status = "PASS" if mark >= PASS_MARK else "FAIL"
        print(f"  {name}: {mark} ({status})")

    print()
    print(f"Average: {average(marks):.1f}")
    print(f"Highest: {highest(marks)}")
    print(f"Lowest:  {lowest(marks)}")

    passed, failed = split_pass_fail(student_marks)
    print(f"Passed ({len(passed)}): {', '.join(passed) if passed else 'none'}")
    print(f"Failed ({len(failed)}): {', '.join(failed) if failed else 'none'}")
    print(f"Distinct marks: {sorted(unique_marks(student_marks))}")


def main():
    student_marks = read_marks()
    report(student_marks)


if __name__ == "__main__":
    main()
