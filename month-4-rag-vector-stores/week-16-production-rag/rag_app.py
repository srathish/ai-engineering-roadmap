"""Production-style RAG application.

Built from scratch to make the production concerns visible:

  - structured LOGGING via the standard `logging` module: retrieval scores,
    per-stage latency, and token usage
  - simple CONFIG via a dataclass
  - a RERANKING step that re-sorts retrieved candidates by combining the
    embedding score with a keyword-overlap signal, and drops weak matches
    below a threshold
  - clean STAGE separation: ingest -> retrieve -> rerank -> generate

A real deployment would more likely reach for a framework. LangChain offers
chains and retrievers that wire these stages together; LlamaIndex offers
document loaders, node parsers, and query engines. Both abstract away the
glue below. Building it from scratch here keeps every stage and every metric
in plain sight.

Retrieval runs locally with sentence-transformers (no paid API). Only the
final generation calls Claude, and the app degrades gracefully without a key.

Requires: sentence-transformers, numpy, anthropic  (see requirements.txt)
"""

from __future__ import annotations

import glob
import logging
import os
import re
import time
from dataclasses import dataclass, field

import numpy as np

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass
class RagConfig:
    """All tunable knobs in one place."""

    docs_glob: str = os.path.join(
        os.path.dirname(__file__), "sample_docs", "*.txt"
    )
    embed_model: str = "all-MiniLM-L6-v2"
    # Valid IDs: claude-opus-4-8, claude-sonnet-4-6, claude-haiku-4-5-20251001.
    llm_model: str = "claude-sonnet-4-6"
    chunk_size: int = 400
    chunk_overlap: int = 50
    retrieve_k: int = 6          # candidates pulled before reranking
    final_k: int = 3             # chunks kept after reranking
    score_threshold: float = 0.15  # drop candidates below this reranked score
    max_tokens: int = 1024


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger("rag")


def configure_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-5s %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class Chunk:
    text: str
    source: str
    index: int


@dataclass
class Scored:
    chunk: Chunk
    embed_score: float
    rerank_score: float = 0.0


# ---------------------------------------------------------------------------
# Stage 1: ingest (load + chunk + embed)
# ---------------------------------------------------------------------------


def _chunk_text(text: str, source: str, size: int, overlap: int) -> list[Chunk]:
    step = size - overlap
    out: list[Chunk] = []
    index = 0
    for start in range(0, max(len(text), 1), step):
        piece = text[start : start + size]
        if piece.strip():
            out.append(Chunk(piece, source, index))
            index += 1
        if start + size >= len(text):
            break
    return out


@dataclass
class Index:
    """An embedded, searchable index over the corpus."""

    config: RagConfig
    chunks: list[Chunk] = field(default_factory=list)
    vectors: np.ndarray | None = None
    _model: object | None = None

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.config.embed_model)
        return self._model

    def ingest(self) -> None:
        """Load documents, chunk them, and embed every chunk."""
        t0 = time.perf_counter()
        paths = sorted(glob.glob(self.config.docs_glob))
        for path in paths:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
            self.chunks.extend(
                _chunk_text(text, os.path.basename(path),
                            self.config.chunk_size, self.config.chunk_overlap)
            )
        model = self._load_model()
        self.vectors = np.asarray(
            model.encode([c.text for c in self.chunks], show_progress_bar=False),
            dtype=np.float32,
        )
        dt = (time.perf_counter() - t0) * 1000
        logger.info("ingest: %d docs -> %d chunks, embedded in %.0f ms",
                    len(paths), len(self.chunks), dt)

    def embed_query(self, query: str) -> np.ndarray:
        model = self._load_model()
        v = np.asarray(model.encode([query], show_progress_bar=False)[0],
                       dtype=np.float32)
        return v / (np.linalg.norm(v) + 1e-10)


# ---------------------------------------------------------------------------
# Stage 2: retrieve
# ---------------------------------------------------------------------------


def retrieve(index: Index, query: str, k: int) -> list[Scored]:
    """Return the top-k candidates by cosine similarity."""
    t0 = time.perf_counter()
    q = index.embed_query(query)
    mat = index.vectors / (
        np.linalg.norm(index.vectors, axis=1, keepdims=True) + 1e-10
    )
    scores = mat @ q
    top = np.argsort(scores)[::-1][:k]
    results = [Scored(index.chunks[i], float(scores[i])) for i in top]
    dt = (time.perf_counter() - t0) * 1000
    logger.info("retrieve: %d candidates in %.0f ms (top score %.3f)",
                len(results), dt, results[0].embed_score if results else 0.0)
    for r in results:
        logger.debug("  cand [%s#%d] embed=%.3f",
                     r.chunk.source, r.chunk.index, r.embed_score)
    return results


# ---------------------------------------------------------------------------
# Stage 3: rerank
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[a-z0-9]+")


def _keyword_overlap(query: str, text: str) -> float:
    """Fraction of distinct query words that appear in the chunk."""
    q_words = set(_WORD_RE.findall(query.lower()))
    if not q_words:
        return 0.0
    t_words = set(_WORD_RE.findall(text.lower()))
    return len(q_words & t_words) / len(q_words)


def rerank(query: str, candidates: list[Scored], config: RagConfig) -> list[Scored]:
    """Re-sort candidates by embed score + keyword overlap, drop weak ones.

    A simple lexical signal (keyword overlap) is blended with the dense
    embedding score. This catches cases where the embedding is close but the
    chunk does not actually mention the query terms, and vice versa.
    """
    t0 = time.perf_counter()
    for c in candidates:
        overlap = _keyword_overlap(query, c.chunk.text)
        # Weighted blend: mostly semantic, nudged by lexical overlap.
        c.rerank_score = 0.7 * c.embed_score + 0.3 * overlap

    ranked = sorted(candidates, key=lambda c: c.rerank_score, reverse=True)
    kept = [c for c in ranked if c.rerank_score >= config.score_threshold]
    kept = kept[: config.final_k]

    dt = (time.perf_counter() - t0) * 1000
    logger.info("rerank: %d -> %d kept (threshold %.2f) in %.1f ms",
                len(candidates), len(kept), config.score_threshold, dt)
    for c in kept:
        logger.debug("  kept [%s#%d] embed=%.3f rerank=%.3f",
                     c.chunk.source, c.chunk.index, c.embed_score, c.rerank_score)
    return kept


# ---------------------------------------------------------------------------
# Stage 4: generate
# ---------------------------------------------------------------------------


def _build_prompt(question: str, context: list[Scored]) -> str:
    blocks = [f"[{c.chunk.source}#{c.chunk.index}]\n{c.chunk.text.strip()}"
              for c in context]
    return (
        "Answer the question using only the context below. Cite the sources "
        "you use with their bracketed tags. If the answer is not in the "
        "context, say you don't know.\n\n"
        f"Context:\n{chr(10).join(blocks)}\n\n"
        f"Question: {question}\n\nAnswer:"
    )


def generate(question: str, context: list[Scored], config: RagConfig) -> str | None:
    """Call Claude with the injected context. Returns None without a key."""
    if not context:
        logger.warning("generate: no context survived reranking")
    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.warning("generate: ANTHROPIC_API_KEY not set - skipping LLM call")
        return None
    try:
        import anthropic
    except ImportError:
        logger.error("generate: anthropic package not installed")
        return None

    prompt = _build_prompt(question, context)
    client = anthropic.Anthropic()
    t0 = time.perf_counter()
    response = client.messages.create(
        model=config.llm_model,
        max_tokens=config.max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    dt = (time.perf_counter() - t0) * 1000
    usage = response.usage
    logger.info("generate: %.0f ms, tokens in=%d out=%d",
                dt, usage.input_tokens, usage.output_tokens)
    return "".join(b.text for b in response.content if b.type == "text")


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def answer_question(index: Index, question: str, config: RagConfig) -> None:
    """Run the full ingest-free pipeline for one question."""
    t0 = time.perf_counter()
    candidates = retrieve(index, question, config.retrieve_k)
    context = rerank(question, candidates, config)
    reply = generate(question, context, config)
    total = (time.perf_counter() - t0) * 1000
    logger.info("pipeline complete in %.0f ms", total)

    print("\n" + "=" * 60)
    print(f"Q: {question}")
    if reply is None:
        print("\n[No answer generated - context that would be sent:]")
        for c in context:
            preview = re.sub(r"\s+", " ", c.chunk.text)[:90]
            print(f"  [{c.chunk.source}#{c.chunk.index}] "
                  f"(rerank {c.rerank_score:.3f}) {preview!r}")
    else:
        print(f"\nA: {reply}")
        srcs = ", ".join(f"{c.chunk.source}#{c.chunk.index}" for c in context)
        print(f"\nSources: {srcs}")
    print("=" * 60)


def main() -> None:
    configure_logging()
    config = RagConfig()
    index = Index(config)
    index.ingest()

    if not index.chunks:
        logger.error("no documents found at %s", config.docs_glob)
        return
    if not os.environ.get("ANTHROPIC_API_KEY"):
        logger.warning("running without ANTHROPIC_API_KEY - "
                       "retrieval + rerank only")

    print("\nProduction RAG demo. Ask a question (empty line to quit).")
    while True:
        try:
            question = input("\n> ").strip()
        except EOFError:
            break
        if not question:
            break
        answer_question(index, question, config)


if __name__ == "__main__":
    main()
