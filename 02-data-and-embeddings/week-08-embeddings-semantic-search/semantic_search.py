"""Semantic search over a set of personal notes using sentence embeddings.

Embeds each note and a query with the "all-MiniLM-L6-v2" sentence-transformers
model, then ranks notes by cosine similarity to the query and prints the
top-k matches. Unlike keyword search, this matches on meaning, so a query
like "tasks for my garden" can match a note about planting vegetables even
if it shares no words.

Usage:
    python3 semantic_search.py                 # interactive prompt
    python3 semantic_search.py "your query"    # one-shot query
"""

import os
import sys

import numpy as np

HERE = os.path.dirname(__file__)
NOTES_FILE = os.path.join(HERE, "notes.txt")
MODEL_NAME = "all-MiniLM-L6-v2"


def load_notes(path):
    """Read notes from a file, one note per non-empty line."""
    with open(path, "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip()]


def cosine_similarity(query_vec, note_vecs):
    """Cosine similarity between one query vector and many note vectors.

    Returns a 1-D array of similarity scores, one per note.
    """
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    note_norms = note_vecs / (
        np.linalg.norm(note_vecs, axis=1, keepdims=True) + 1e-10
    )
    return note_norms @ query_norm


def search(model, notes, note_embeddings, query, top_k=3):
    """Return the top-k (note, score) matches for a query."""
    query_embedding = model.encode([query])[0]
    scores = cosine_similarity(np.asarray(query_embedding),
                               np.asarray(note_embeddings))
    ranked = sorted(zip(notes, scores), key=lambda pair: pair[1], reverse=True)
    return ranked[:top_k]


def run(query, model, notes, note_embeddings):
    """Run one search and print the results."""
    results = search(model, notes, note_embeddings, query)
    print(f"\nQuery: {query!r}")
    print("Top matches:")
    for note, score in results:
        print(f"  [{score:.3f}] {note}")


def main():
    notes = load_notes(NOTES_FILE)
    if not notes:
        print(f"No notes found in {NOTES_FILE}.")
        return 1

    # Importing and loading the model is the part most likely to fail (no
    # internet on first run, missing package), so guard it and explain clearly.
    try:
        from sentence_transformers import SentenceTransformer

        print(f"Loading model '{MODEL_NAME}' (first run downloads ~80MB)...")
        model = SentenceTransformer(MODEL_NAME)
        note_embeddings = model.encode(notes)
    except ImportError:
        print(
            "sentence-transformers is not installed.\n"
            "Install it with:  pip install -r requirements.txt"
        )
        return 1
    except Exception as exc:  # network errors, model download failures, etc.
        print(
            "Could not load the embedding model. This usually means the model "
            "could not be downloaded.\n"
            f"Details: {exc}\n"
            "Make sure you have an internet connection on the first run so the "
            "model can be cached locally."
        )
        return 1

    print(f"Loaded {len(notes)} notes and embedded them.")

    if len(sys.argv) > 1:
        run(" ".join(sys.argv[1:]), model, notes, note_embeddings)
        return 0

    print("\nEnter a query (or press Enter / Ctrl-D to quit).")
    while True:
        try:
            query = input("\nquery> ").strip()
        except EOFError:
            print()
            break
        if not query:
            break
        run(query, model, notes, note_embeddings)
    return 0


if __name__ == "__main__":
    sys.exit(main())
