# Week 7 - Text Processing

A small text cleaning and tokenization module built with only the Python standard library (`re`, `string`, `collections`).

## What it does

Runs raw text through a cleaning pipeline and reports word frequencies:

1. **Lowercase** the text
2. **Strip punctuation** with a regex (`[^\w\s]`)
3. **Normalize whitespace** by collapsing runs of spaces/tabs/newlines into one space (`\s+`)
4. **Tokenize** into individual words
5. **Remove stopwords** using a small built-in stopword set
6. **Count** the remaining words with `collections.Counter`

It prints a report with token counts (before/after stopword removal), unique word count, and the top 10 words as a simple bar chart. It has a built-in sample paragraph and a CLI that can read any text file.

## How to run

```bash
# Use the built-in sample paragraph
python3 text_cleaner.py

# Or point it at a text file
python3 text_cleaner.py path/to/yourfile.txt
```

No dependencies to install - it uses the standard library only.

## What I learned

- I learned that unstructured text needs real preprocessing before it's useful, and that "cleaning" is a sequence of small, deliberate steps rather than one operation.
- I learned how to use regex meaningfully: `[^\w\s]` to remove punctuation and `\s+` to collapse whitespace, instead of chaining lots of `.replace()` calls.
- I learned what tokenization actually is - splitting text into word units - and that the quality of my tokens depends entirely on the cleaning that came before.
- I learned why stopwords matter: common words like "the" and "is" dominate raw counts and hide the words that actually describe the topic.
- I learned that `collections.Counter` and its `most_common()` method make frequency analysis almost trivial once the text is tokenized.
- I learned that normalization decisions (lowercasing, where to split) directly change the final counts, so they're choices worth being intentional about.
