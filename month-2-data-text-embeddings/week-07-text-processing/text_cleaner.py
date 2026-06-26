"""Text cleaning and tokenization using only the Python standard library.

Pipeline: lowercase -> strip punctuation -> normalize whitespace ->
tokenize -> remove stopwords -> count word frequencies.

Usage:
    python3 text_cleaner.py            # run on the built-in sample paragraph
    python3 text_cleaner.py notes.txt  # run on a file
"""

import re
import string
import sys
from collections import Counter

# A small, hand-picked stopword set. These words are common but carry little
# meaning, so we drop them before counting frequencies.
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "while", "is", "are", "was",
    "were", "be", "been", "being", "to", "of", "in", "on", "for", "with",
    "as", "at", "by", "from", "this", "that", "these", "those", "it", "its",
    "i", "you", "he", "she", "they", "we", "them", "his", "her", "their",
    "our", "my", "me", "not", "no", "so", "than", "then", "too", "very",
    "can", "will", "just", "do", "does", "did", "have", "has", "had",
}

SAMPLE_TEXT = (
    "Natural language processing lets computers work with human language. "
    "Before a model can use text, the text must be cleaned and tokenized. "
    "Cleaning text means lowercasing words, removing punctuation, and "
    "normalizing the whitespace between words. Tokenizing text splits it "
    "into individual words, and removing stopwords keeps only the words that "
    "carry real meaning. Counting those words shows which topics the text "
    "is really about."
)

# Matches one or more whitespace characters; used to collapse runs of spaces,
# tabs, and newlines into a single space.
_WHITESPACE_RE = re.compile(r"\s+")

# Matches any character that is NOT a word character or whitespace. Used to
# strip punctuation while leaving letters, digits, and spaces intact.
_PUNCT_RE = re.compile(r"[^\w\s]")


def normalize(text):
    """Lowercase, strip punctuation, and collapse whitespace."""
    text = text.lower()
    text = _PUNCT_RE.sub(" ", text)          # punctuation -> space
    text = _WHITESPACE_RE.sub(" ", text)     # collapse runs of whitespace
    return text.strip()


def tokenize(text):
    """Split normalized text into a list of word tokens."""
    normalized = normalize(text)
    if not normalized:
        return []
    return normalized.split(" ")


def remove_stopwords(tokens, stopwords=STOPWORDS):
    """Drop tokens that are in the stopword set (or are pure punctuation)."""
    return [t for t in tokens if t and t not in stopwords]


def word_frequencies(text, stopwords=STOPWORDS):
    """Return a Counter of word -> count after the full cleaning pipeline."""
    tokens = remove_stopwords(tokenize(text), stopwords)
    return Counter(tokens)


def read_text(path):
    """Read a text file as UTF-8."""
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def print_report(text):
    """Print a small readable report for the given text."""
    raw_tokens = tokenize(text)
    kept = remove_stopwords(raw_tokens)
    freqs = Counter(kept)

    print("=" * 50)
    print("TEXT CLEANING REPORT")
    print("=" * 50)
    print(f"Characters (raw):        {len(text)}")
    print(f"Tokens (before stopwords): {len(raw_tokens)}")
    print(f"Tokens (after stopwords):  {len(kept)}")
    print(f"Unique words:            {len(freqs)}")
    print("\nTop 10 words by frequency:")
    for word, count in freqs.most_common(10):
        bar = "#" * count
        print(f"  {word:<14} {count:>2}  {bar}")


def main(argv):
    if len(argv) > 1:
        path = argv[1]
        try:
            text = read_text(path)
        except OSError as exc:
            print(f"Could not read file '{path}': {exc}")
            return 1
        print(f"(reading from {path})\n")
    else:
        text = SAMPLE_TEXT
        print("(no file given, using built-in sample paragraph)\n")

    print_report(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
