# Week 3 — OOP and File Handling

A mini library management system that practices object-oriented programming, saving and loading data with JSON, and handling errors cleanly.

## What it does
- `library.py` — models a small library with `Book`, `Member` and `Library` classes (plus a `Person` base class that `Member` inherits from). Members can borrow and return books, the catalogue tracks availability, and the whole state is saved to and loaded from a JSON file. Invalid actions (borrowing a missing book, returning one you don't have) raise a clear error instead of crashing.

The `__main__` block runs a short demo: it creates books and members, borrows a book, tries an invalid borrow, returns the book, then saves and reloads from disk.

## How to run
```
python3 library.py
```
This creates a `library_data.json` file in the same folder.

## What I learned
- I learned how to define classes and create objects from them, giving each object its own attributes through `__init__`.
- I learned how inheritance works by making `Member` extend a `Person` base class and calling `super().__init__()`.
- I learned how to write methods that act on an object's own data, like `borrow` and `return_book` on the `Library`.
- I learned how to convert objects to and from dictionaries so they can be written as JSON and rebuilt later.
- I learned how to read and write files with `open()` and the `json` module to make data persist between runs.
- I learned how to define a custom exception and use `try`/`except` to handle problems like a missing file or an invalid operation without crashing.
