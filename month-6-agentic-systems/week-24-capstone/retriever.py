"""Capstone - embedding + retrieval.

Embeds document chunks with sentence-transformers and retrieves the most
relevant chunks for a query using cosine similarity. Falls back to a simple
keyword overlap scorer if sentence-transformers / numpy are unavailable, so the
rest of the pipeline can still be exercised.
"""

from ingest import Chunk

try:
    import numpy as np
    from sentence_transformers import SentenceTransformer

    _HAVE_EMBEDDINGS = True
except ImportError:
    _HAVE_EMBEDDINGS = False

EMBED_MODEL = "all-MiniLM-L6-v2"


class Retriever:
    """In-memory vector index over document chunks."""

    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self._model = None
        self._matrix = None

        if _HAVE_EMBEDDINGS and chunks:
            self._model = SentenceTransformer(EMBED_MODEL)
            self._matrix = self._model.encode(
                [c.text for c in chunks], normalize_embeddings=True
            )

    def search(self, query: str, k: int = 3) -> list[Chunk]:
        """Return the top-k chunks most relevant to `query`."""
        if not self.chunks:
            return []

        if self._model is not None:
            q = self._model.encode([query], normalize_embeddings=True)[0]
            scores = self._matrix @ q  # cosine sim (vectors are normalized)
            top = np.argsort(scores)[::-1][:k]
            return [self.chunks[i] for i in top]

        # Fallback: keyword overlap so the demo still runs without embeddings.
        terms = set(query.lower().split())
        scored = sorted(
            self.chunks,
            key=lambda c: len(terms & set(c.text.lower().split())),
            reverse=True,
        )
        return scored[:k]
