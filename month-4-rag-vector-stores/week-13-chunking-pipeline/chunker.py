"""Document chunking pipeline.

Loads plain-text files and splits them into overlapping chunks while
preserving metadata (source file, chunk index, character span). Two
strategies are provided:

  1. fixed_size_chunks    - fixed character window with configurable overlap
  2. sentence_aware_chunks - groups whole sentences/paragraphs up to a size
                             budget, with sentence-level overlap

This is the first stage of a RAG pipeline: documents are too large to feed
to an LLM whole, and embedding a whole document loses the fine-grained
signal needed for retrieval. Chunking trades those off.

Pure standard library - no third-party dependencies.
"""

from __future__ import annotations

import argparse
import glob
import os
import re
from dataclasses import dataclass, field


@dataclass
class Chunk:
    """A single chunk of text plus its provenance metadata."""

    text: str
    source: str
    index: int
    start_char: int
    end_char: int
    metadata: dict = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.text)


def load_text(path: str) -> str:
    """Read a UTF-8 text file from disk."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def fixed_size_chunks(
    text: str,
    source: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[Chunk]:
    """Split text into fixed-size character windows that overlap.

    Each chunk is `chunk_size` characters; consecutive chunks share
    `overlap` characters so that a sentence spanning a boundary still
    appears intact in at least one chunk.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and < chunk_size")

    step = chunk_size - overlap
    chunks: list[Chunk] = []
    index = 0
    for start in range(0, max(len(text), 1), step):
        piece = text[start : start + chunk_size]
        if not piece.strip():
            continue
        chunks.append(
            Chunk(
                text=piece,
                source=source,
                index=index,
                start_char=start,
                end_char=start + len(piece),
                metadata={"strategy": "fixed_size", "chunk_size": chunk_size,
                          "overlap": overlap},
            )
        )
        index += 1
        if start + chunk_size >= len(text):
            break
    return chunks


# Split on sentence-ending punctuation followed by whitespace, while keeping
# paragraph breaks as hard boundaries.
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")


def _split_sentences(text: str) -> list[str]:
    """Break text into sentence-ish units, respecting paragraph breaks."""
    units: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        for sentence in _SENTENCE_RE.split(paragraph):
            sentence = sentence.strip()
            if sentence:
                units.append(sentence)
    return units


def sentence_aware_chunks(
    text: str,
    source: str,
    chunk_size: int = 500,
    overlap: int = 1,
) -> list[Chunk]:
    """Group whole sentences into chunks up to a character budget.

    `chunk_size` is a soft character budget; sentences are never split
    mid-way. `overlap` here is a number of *sentences* carried over to the
    start of the next chunk, preserving context across boundaries.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0:
        raise ValueError("overlap must be >= 0")

    sentences = _split_sentences(text)
    chunks: list[Chunk] = []
    index = 0
    current: list[str] = []
    current_len = 0
    char_cursor = 0  # approximate position in the source

    def flush(sents: list[str]) -> None:
        nonlocal index, char_cursor
        if not sents:
            return
        joined = " ".join(sents)
        start = char_cursor
        chunks.append(
            Chunk(
                text=joined,
                source=source,
                index=index,
                start_char=start,
                end_char=start + len(joined),
                metadata={"strategy": "sentence_aware",
                          "sentence_count": len(sents)},
            )
        )
        index += 1
        char_cursor = start + len(joined) + 1

    for sentence in sentences:
        # +1 accounts for the joining space.
        if current and current_len + len(sentence) + 1 > chunk_size:
            flush(current)
            # Carry the last `overlap` sentences into the next chunk.
            current = current[-overlap:] if overlap else []
            current_len = sum(len(s) + 1 for s in current)
        current.append(sentence)
        current_len += len(sentence) + 1

    flush(current)
    return chunks


def print_stats(label: str, chunks: list[Chunk]) -> None:
    """Print summary statistics for a list of chunks."""
    print(f"\n=== {label} ===")
    if not chunks:
        print("  (no chunks produced)")
        return
    sizes = [len(c) for c in chunks]
    print(f"  chunks:      {len(chunks)}")
    print(f"  total chars: {sum(sizes)}")
    print(f"  min / avg / max size: "
          f"{min(sizes)} / {sum(sizes) // len(sizes)} / {max(sizes)}")
    preview = chunks[0].text[:80].replace("\n", " ")
    print(f"  first chunk [{chunks[0].source}#{chunks[0].index}]: {preview!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Chunk text documents.")
    parser.add_argument(
        "--docs",
        default=os.path.join(os.path.dirname(__file__), "sample_docs", "*.txt"),
        help="Glob pattern for input .txt files.",
    )
    parser.add_argument("--chunk-size", type=int, default=500)
    parser.add_argument("--overlap", type=int, default=50)
    args = parser.parse_args()

    paths = sorted(glob.glob(args.docs))
    if not paths:
        print(f"No documents matched: {args.docs}")
        return

    all_fixed: list[Chunk] = []
    all_sentence: list[Chunk] = []
    for path in paths:
        text = load_text(path)
        source = os.path.basename(path)
        all_fixed.extend(
            fixed_size_chunks(text, source, args.chunk_size, args.overlap)
        )
        # For sentence-aware we use a small sentence overlap (1 sentence).
        all_sentence.extend(
            sentence_aware_chunks(text, source, args.chunk_size, overlap=1)
        )

    print(f"Loaded {len(paths)} document(s): "
          f"{', '.join(os.path.basename(p) for p in paths)}")
    print_stats("Fixed-size with overlap", all_fixed)
    print_stats("Sentence/paragraph aware", all_sentence)


if __name__ == "__main__":
    main()
