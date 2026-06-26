# Week 8 - Embeddings & Semantic Search

Semantic search over a set of personal notes using sentence embeddings and cosine similarity.

## What it does

- Reads notes from `notes.txt` (one note per line)
- Uses the `all-MiniLM-L6-v2` sentence-transformers model to turn each note and the search query into embedding vectors
- Computes **cosine similarity** between the query vector and every note vector
- Returns the top-k most similar notes, ranked by score

Because it matches on **meaning** rather than exact words, a query like "things to do in the garden" can surface a note about planting vegetables even when no words overlap. The script handles failures gracefully - if the package is missing or the model can't download, it prints a clear message instead of crashing.

## How to run

```bash
pip install -r requirements.txt

# Interactive: type queries at the prompt
python3 semantic_search.py

# One-shot: pass the query as an argument
python3 semantic_search.py "learning about how AI understands language"
```

## Note

The first run downloads the `all-MiniLM-L6-v2` model (~80MB) and requires an internet connection. After that the model is cached locally and runs offline.

## What I learned

- I learned that an embedding is a list of numbers (a vector) that captures the meaning of a piece of text, so that similar ideas end up close together in vector space.
- I learned how to use sentence-transformers to embed text in just a couple of lines, and that the model only needs to download once before it's cached.
- I learned how cosine similarity measures the angle between two vectors, and why normalizing the vectors first makes the comparison about direction (meaning) rather than length.
- I learned the real difference between semantic search and keyword search - semantic search can match related ideas even when the exact words are different.
- I learned that the query has to be embedded with the same model as the notes for the comparison to make sense.
- I learned to handle the model download as a failure point, since a tool that crashes with a stack trace on first run is much worse than one that explains what's wrong.
