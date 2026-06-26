"""Document Q&A bot - a full RAG pipeline over your own docs.

Pipeline:
  load docs -> chunk -> embed -> retrieve top-k for a question
            -> inject context into a prompt -> ask Claude
            -> print the answer with cited sources

Retrieval (chunking + embedding + similarity) runs locally with
sentence-transformers and needs no paid API. Only the final answer
generation calls Claude.

Set ANTHROPIC_API_KEY to enable answer generation. Without it, the bot still
runs and shows the retrieved context so you can see what would be sent to the
model.

Requires: sentence-transformers, numpy, anthropic  (see requirements.txt)
"""

from __future__ import annotations

import glob
import os
import re
from dataclasses import dataclass

import numpy as np

# Default model per project conventions. Valid IDs: claude-opus-4-8,
# claude-sonnet-4-6, claude-haiku-4-5-20251001.
DEFAULT_MODEL = "claude-sonnet-4-6"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K = 3


@dataclass
class Chunk:
    text: str
    source: str
    index: int


@dataclass
class Retrieved:
    chunk: Chunk
    score: float


def chunk_text(text: str, source: str, chunk_size: int = 400,
               overlap: int = 50) -> list[Chunk]:
    """Fixed-size chunking with overlap (the Week 13 idea)."""
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
    chunks: list[Chunk] = []
    for path in sorted(glob.glob(pattern)):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        chunks.extend(chunk_text(text, os.path.basename(path)))
    return chunks


class Retriever:
    """Embeds chunks once and retrieves the top-k by cosine similarity."""

    def __init__(self, chunks: list[Chunk], model_name: str = EMBED_MODEL):
        from sentence_transformers import SentenceTransformer

        self.chunks = chunks
        print(f"Loading embedding model: {model_name} ...")
        self.model = SentenceTransformer(model_name)
        self.vectors = np.asarray(
            self.model.encode([c.text for c in chunks], show_progress_bar=False),
            dtype=np.float32,
        )

    def retrieve(self, query: str, k: int = TOP_K) -> list[Retrieved]:
        q = np.asarray(
            self.model.encode([query], show_progress_bar=False)[0],
            dtype=np.float32,
        )
        q /= np.linalg.norm(q) + 1e-10
        mat = self.vectors / (
            np.linalg.norm(self.vectors, axis=1, keepdims=True) + 1e-10
        )
        scores = mat @ q
        top = np.argsort(scores)[::-1][:k]
        return [Retrieved(self.chunks[i], float(scores[i])) for i in top]


def build_prompt(question: str, retrieved: list[Retrieved]) -> str:
    """Inject the retrieved chunks into a prompt as labeled context."""
    blocks = []
    for r in retrieved:
        tag = f"[{r.chunk.source}#{r.chunk.index}]"
        blocks.append(f"{tag}\n{r.chunk.text.strip()}")
    context = "\n\n".join(blocks)
    return (
        "Answer the question using only the context below. "
        "Cite the sources you used with their bracketed tags, e.g. "
        "[file.txt#2]. If the context does not contain the answer, say so.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\nAnswer:"
    )


def ask_claude(prompt: str, model: str = DEFAULT_MODEL) -> str | None:
    """Send the prompt to Claude. Returns None if no API key is configured."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    try:
        import anthropic
    except ImportError:
        print("  (anthropic package not installed - run: pip install anthropic)")
        return None

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(block.text for block in response.content
                   if block.type == "text")


def answer(question: str, retriever: Retriever, model: str = DEFAULT_MODEL) -> None:
    """Run one full RAG turn and print the answer with sources."""
    retrieved = retriever.retrieve(question)

    print("\nRetrieved context:")
    for r in retrieved:
        preview = re.sub(r"\s+", " ", r.chunk.text)[:90]
        print(f"  - score={r.score:.3f} "
              f"[{r.chunk.source}#{r.chunk.index}] {preview!r}")

    prompt = build_prompt(question, retrieved)
    reply = ask_claude(prompt, model)

    if reply is None:
        print("\n[No ANTHROPIC_API_KEY set - showing retrieved context only.]")
        print("Set the key to have Claude generate an answer:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
    else:
        print(f"\nAnswer:\n{reply}")
        sources = ", ".join(f"{r.chunk.source}#{r.chunk.index}" for r in retrieved)
        print(f"\nSources consulted: {sources}")


def main() -> None:
    docs = os.path.join(os.path.dirname(__file__), "sample_docs", "*.txt")
    chunks = load_chunks(docs)
    if not chunks:
        print(f"No documents found at {docs}")
        return

    retriever = Retriever(chunks)
    print(f"Indexed {len(chunks)} chunks from "
          f"{len(set(c.source for c in chunks))} document(s).")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Note: ANTHROPIC_API_KEY is not set - retrieval works, but "
              "answers will not be generated.")

    print("\nAsk a question (empty line or Ctrl-D to quit).")
    while True:
        try:
            question = input("\n> ").strip()
        except EOFError:
            break
        if not question:
            break
        answer(question, retriever)


if __name__ == "__main__":
    main()
