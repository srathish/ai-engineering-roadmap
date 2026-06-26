"""Vector search over chunked documents.

Builds an in-memory vector index:

  1. Load .txt documents and chunk them (a small local chunker is included
     so this file stands alone - it reuses the Week 13 idea).
  2. Embed each chunk with sentence-transformers ("all-MiniLM-L6-v2").
  3. Given a query, embed it and return the top-k most similar chunks by
     cosine similarity.

Storage here is a plain numpy matrix held in memory, which is enough to
understand how vector search works. In production you would reach for a
dedicated vector store such as Chroma, pgvector, or Pinecone - the mechanics
(embed -> store -> nearest-neighbor search) are identical; those tools just
add persistence, scaling, and an approximate-nearest-neighbor index.

Requires: sentence-transformers, numpy  (see requirements.txt)
Retrieval works with NO paid API - the embedding model runs locally.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
from dataclasses import dataclass, field

import numpy as np

EMBED_MODEL = "all-MiniLM-L6-v2"


@dataclass
class Chunk:
    text: str
    source: str
    index: int


@dataclass
class SearchResult:
    chunk: Chunk
    score: float


def chunk_text(text: str, source: str, chunk_size: int = 400,
               overlap: int = 50) -> list[Chunk]:
    """Small local fixed-size chunker (reuses the Week 13 chunking idea)."""
    step = chunk_size - overlap
    chunks: list[Chunk] = []
    index = 0
    for start in range(0, max(len(text), 1), step):
        piece = text[start : start + chunk_size]
        if piece.strip():
            chunks.append(Chunk(piece, source, index))
            index += 1
        if start + chunk_size >= len(text):
            break
    return chunks


def load_chunks(pattern: str) -> list[Chunk]:
    """Load and chunk every file matching the glob pattern."""
    chunks: list[Chunk] = []
    for path in sorted(glob.glob(pattern)):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks.extend(chunk_text(text, os.path.basename(path)))
    return chunks


def _cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """Cosine similarity between one query vector and a matrix of vectors."""
    query_norm = query / (np.linalg.norm(query) + 1e-10)
    matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
    return matrix_norm @ query_norm


@dataclass
class VectorStore:
    """An in-memory vector store backed by a numpy matrix."""

    model_name: str = EMBED_MODEL
    chunks: list[Chunk] = field(default_factory=list)
    vectors: np.ndarray | None = None
    _model: object | None = None

    def _load_model(self):
        if self._model is None:
            # Imported lazily so the file can be syntax-checked without the
            # heavy dependency installed.
            from sentence_transformers import SentenceTransformer

            print(f"Loading embedding model: {self.model_name} ...")
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def add(self, chunks: list[Chunk]) -> None:
        """Embed and store a list of chunks."""
        model = self._load_model()
        texts = [c.text for c in chunks]
        embeddings = np.asarray(
            model.encode(texts, show_progress_bar=False), dtype=np.float32
        )
        self.chunks.extend(chunks)
        if self.vectors is None:
            self.vectors = embeddings
        else:
            self.vectors = np.vstack([self.vectors, embeddings])

    def search(self, query: str, k: int = 3) -> list[SearchResult]:
        """Return the top-k chunks most similar to the query."""
        if self.vectors is None or not self.chunks:
            return []
        model = self._load_model()
        query_vec = np.asarray(
            model.encode([query], show_progress_bar=False)[0], dtype=np.float32
        )
        scores = _cosine_similarity(query_vec, self.vectors)
        top_idx = np.argsort(scores)[::-1][:k]
        return [SearchResult(self.chunks[i], float(scores[i])) for i in top_idx]


def main() -> None:
    parser = argparse.ArgumentParser(description="Vector search over documents.")
    parser.add_argument(
        "--docs",
        default=os.path.join(os.path.dirname(__file__), "sample_docs", "*.txt"),
    )
    parser.add_argument("-k", type=int, default=3, help="Number of results.")
    parser.add_argument("query", nargs="*", help="Query text.")
    args = parser.parse_args()

    chunks = load_chunks(args.docs)
    if not chunks:
        print(f"No documents matched: {args.docs}")
        return

    store = VectorStore()
    store.add(chunks)
    print(f"Indexed {len(chunks)} chunks from "
          f"{len(set(c.source for c in chunks))} document(s).\n")

    if args.query:
        queries = [" ".join(args.query)]
    else:
        # Demo queries when none are supplied on the command line.
        queries = [
            "How does cosine similarity work?",
            "What is a vector database used for?",
        ]

    for query in queries:
        print(f"Query: {query!r}")
        for rank, result in enumerate(store.search(query, k=args.k), start=1):
            preview = re.sub(r"\s+", " ", result.chunk.text)[:90]
            print(f"  {rank}. score={result.score:.3f} "
                  f"[{result.chunk.source}#{result.chunk.index}] {preview!r}")
        print()


if __name__ == "__main__":
    main()
