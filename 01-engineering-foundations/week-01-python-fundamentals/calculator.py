"""A simple command-line calculator.

Supports addition, subtraction, multiplication and division.
Loops until the user chooses to quit, validates input, and
handles divide-by-zero safely.
"""


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    # Guard against division by zero instead of letting Python crash.
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b


def read_number(prompt):
    """Keep asking until the user types a valid number."""
    while True:
        value = input(prompt)
        try:
            return float(value)
        except ValueError:
            print("That's not a number. Try again.")


def read_operation():
    """Return a valid operation symbol or 'q' to quit."""
    valid = ("+", "-", "*", "/", "q")
    while True:
        choice = input("Choose operation (+, -, *, /, or q to quit): ").strip()
        if choice in valid:
            return choice
        print("Unknown operation. Please pick one of +, -, *, / or q.")


def calculate(op, a, b):
    if op == "+":
        return add(a, b)
    if op == "-":
        return subtract(a, b)
    if op == "*":
        return multiply(a, b)
    if op == "/":
        return divide(a, b)
    # Should never happen because we validate the operation first.
    raise ValueError("Unsupported operation: " + op)


def main():
    print("=== Simple Calculator ===")
    while True:
        op = read_operation()
        if op == "q":
            print("Goodbye!")
            break

        a = read_number("Enter the first number: ")
        b = read_number("Enter the second number: ")

        try:
            result = calculate(op, a, b)
        except ZeroDivisionError as error:
            print(error)
            continue

        # Show whole-number results without a trailing ".0".
        if result == int(result):
            result = int(result)
        print(f"Result: {a} {op} {b} = {result}\n")


if __name__ == "__main__":
    main()
