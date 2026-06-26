# Week 2 — Functions and Data Structures

Two programs that practice writing reusable functions and using Python's core data structures: a student marks analyzer and an in-memory to-do list.

## What it does
- `marks_analyzer.py` — reads student names and marks (or uses sample data) and reports the average, highest, lowest, and who passed or failed. It uses lists, dicts, tuples and sets, and splits the work into small functions.
- `todo.py` — a menu-driven to-do list where you can add, list, complete and delete tasks. Tasks are kept in memory as a list of dicts.

## How to run
```
python3 marks_analyzer.py
python3 todo.py
```

## What I learned
- I learned how to break a program into small functions that take arguments and return values instead of writing one long block of code.
- I learned about variable scope — that a variable created inside a function is local to that function and not visible outside it.
- I learned how to use a dict to map keys to values (student names to marks) and how to loop over its items.
- I learned how to use lists to store ordered collections and a list of dicts to model records like to-do items.
- I learned how to return more than one value from a function using a tuple, such as the passed and failed groups.
- I learned how a set automatically removes duplicates, which made finding the distinct mark values easy.
- I learned how reusable functions like `find_task` keep the code DRY by being called from several places.
