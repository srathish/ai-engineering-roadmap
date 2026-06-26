# Week 1 — Python Fundamentals

Two small command-line programs to practice the basics of Python: a calculator and a number guessing game.

## What it does
- `calculator.py` — a CLI calculator that adds, subtracts, multiplies and divides two numbers. It validates input, handles divide-by-zero, and loops until you quit.
- `guessing_game.py` — picks a random number from 1 to 100 and gives higher/lower hints until you guess it, counting your attempts. You can play again as many times as you like.

## How to run
```
python3 calculator.py
python3 guessing_game.py
```

## What I learned
- I learned how to work with variables and number types, including converting strings from `input()` into `int` and `float`.
- I learned how to use conditionals (`if`/`elif`/`else`) to branch the program based on the user's choice and to give higher/lower hints.
- I learned how to write loops that keep running until a condition is met, like a menu loop and a play-again loop.
- I learned how to validate user input by catching errors with `try`/`except` so a bad entry doesn't crash the program.
- I learned how to prevent a divide-by-zero crash by checking the divisor before dividing.
- I learned how to debug by testing edge cases (zero, negative numbers, non-numeric text) and watching how the program responds.
