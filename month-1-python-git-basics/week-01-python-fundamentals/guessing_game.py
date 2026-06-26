"""A number guessing game.

The computer picks a secret number between 1 and 100.
The player guesses, gets higher/lower hints, and the game
tracks how many attempts it took. A play-again loop lets the
player keep playing.
"""

import random

LOW = 1
HIGH = 100


def read_guess():
    """Ask for a guess and validate it is a number in range."""
    while True:
        raw = input(f"Guess a number between {LOW} and {HIGH}: ").strip()
        try:
            guess = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue

        if guess < LOW or guess > HIGH:
            print(f"Out of range. Stay between {LOW} and {HIGH}.")
            continue
        return guess


def play_one_round():
    """Play a single round and return the number of attempts."""
    secret = random.randint(LOW, HIGH)
    attempts = 0

    while True:
        guess = read_guess()
        attempts += 1

        if guess < secret:
            print("Higher!")
        elif guess > secret:
            print("Lower!")
        else:
            print(f"Correct! You got it in {attempts} attempts.")
            return attempts


def ask_play_again():
    while True:
        answer = input("Play again? (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please answer y or n.")


def main():
    print("=== Number Guessing Game ===")
    while True:
        play_one_round()
        if not ask_play_again():
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
