"""A mini library management system.

Demonstrates object-oriented programming (classes, objects and
inheritance), borrowing and returning books, persisting state to a
JSON file, and handling errors cleanly.

Run it directly to see a small demo of the whole flow:

    python3 library.py
"""

import json
import os

DATA_FILE = "library_data.json"


class Person:
    """Base class for anyone in the library system."""

    def __init__(self, name):
        self.name = name

    def describe(self):
        return self.name


class Member(Person):
    """A library member. Inherits from Person and tracks borrowed books."""

    def __init__(self, name, member_id, borrowed=None):
        super().__init__(name)
        self.member_id = member_id
        # List of ISBNs this member currently has out.
        self.borrowed = borrowed if borrowed is not None else []

    def describe(self):
        return f"{self.name} (#{self.member_id})"

    def to_dict(self):
        return {
            "name": self.name,
            "member_id": self.member_id,
            "borrowed": self.borrowed,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["name"], data["member_id"], data.get("borrowed", []))


class Book:
    """A book in the catalogue."""

    def __init__(self, isbn, title, author, available=True):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.available = available

    def describe(self):
        status = "available" if self.available else "borrowed"
        return f'"{self.title}" by {self.author} [{status}]'

    def to_dict(self):
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "available": self.available,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data["isbn"],
            data["title"],
            data["author"],
            data.get("available", True),
        )


class LibraryError(Exception):
    """Raised for invalid library operations (e.g. borrowing a missing book)."""


class Library:
    """Holds books and members and coordinates borrow/return."""

    def __init__(self):
        self.books = {}    # isbn -> Book
        self.members = {}  # member_id -> Member

    def add_book(self, book):
        self.books[book.isbn] = book

    def add_member(self, member):
        self.members[member.member_id] = member

    def borrow(self, member_id, isbn):
        member = self.members.get(member_id)
        if member is None:
            raise LibraryError(f"No member with id {member_id}.")

        book = self.books.get(isbn)
        if book is None:
            raise LibraryError(f"No book with ISBN {isbn}.")

        if not book.available:
            raise LibraryError(f'"{book.title}" is already borrowed.')

        book.available = False
        member.borrowed.append(isbn)
        return book

    def return_book(self, member_id, isbn):
        member = self.members.get(member_id)
        if member is None:
            raise LibraryError(f"No member with id {member_id}.")

        if isbn not in member.borrowed:
            raise LibraryError(f"{member.name} has not borrowed ISBN {isbn}.")

        book = self.books.get(isbn)
        if book is None:
            raise LibraryError(f"No book with ISBN {isbn}.")

        book.available = True
        member.borrowed.remove(isbn)
        return book

    # ----- persistence -----

    def save(self, path=DATA_FILE):
        """Write the whole library state to a JSON file."""
        data = {
            "books": [book.to_dict() for book in self.books.values()],
            "members": [m.to_dict() for m in self.members.values()],
        }
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    @classmethod
    def load(cls, path=DATA_FILE):
        """Load a library from a JSON file.

        Returns an empty Library if the file is missing or unreadable.
        """
        library = cls()
        if not os.path.exists(path):
            print(f"No data file at {path}, starting with an empty library.")
            return library

        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (json.JSONDecodeError, OSError) as error:
            print(f"Could not read {path}: {error}. Starting empty.")
            return library

        for raw in data.get("books", []):
            library.add_book(Book.from_dict(raw))
        for raw in data.get("members", []):
            library.add_member(Member.from_dict(raw))
        return library

    def show_catalogue(self):
        print("--- Catalogue ---")
        if not self.books:
            print("  (no books)")
        for book in self.books.values():
            print("  " + book.describe())


def demo():
    """Demonstrate the full borrow/return/save/load flow."""
    print("=== Library Demo ===\n")

    library = Library()
    library.add_book(Book("111", "The Pragmatic Programmer", "Hunt & Thomas"))
    library.add_book(Book("222", "Clean Code", "Robert Martin"))
    library.add_member(Member("Asha", 1))
    library.add_member(Member("Ben", 2))

    library.show_catalogue()

    print("\nAsha borrows ISBN 111...")
    library.borrow(1, "111")
    library.show_catalogue()

    print("\nTrying to borrow the same book again (should fail):")
    try:
        library.borrow(2, "111")
    except LibraryError as error:
        print("  Error:", error)

    print("\nAsha returns ISBN 111...")
    library.return_book(1, "111")
    library.show_catalogue()

    print(f"\nSaving state to {DATA_FILE}...")
    library.save()

    print("Reloading from disk...")
    reloaded = Library.load()
    reloaded.show_catalogue()


if __name__ == "__main__":
    demo()
