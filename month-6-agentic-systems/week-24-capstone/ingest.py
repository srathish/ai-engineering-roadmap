"""Capstone - ingestion + chunking.

Reads every text/markdown file in a documents directory and splits it into
overlapping chunks suitable for embedding and retrieval.
"""

import os
from dataclasses import dataclass


@dataclass
class Chunk:
    """A single retrievable chunk of a source document."""

    doc_id: str
    chunk_id: int
    text: str


def chunk_text(text: str, size: int = 800, overlap: int = 150) -> list[str]:
    """Split text into overlapping windows of roughly `size` characters.

    Overlap keeps context from spilling across chunk boundaries so a fact that
    straddles two windows is still retrievable.
    """
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []

    chunks = []
    start = 0
    step = max(1, size - overlap)
    while start < len(text):
        chunks.append(text[start : start + size])
        start += step
    return chunks


def load_documents(docs_dir: str) -> list[Chunk]:
    """Load and chunk every .txt/.md file under `docs_dir`."""
    chunks: list[Chunk] = []
    for name in sorted(os.listdir(docs_dir)):
        if not name.lower().endswith((".txt", ".md")):
            continue
        path = os.path.join(docs_dir, name)
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        for i, piece in enumerate(chunk_text(content)):
            chunks.append(Chunk(doc_id=name, chunk_id=i, text=piece))
    return chunks
