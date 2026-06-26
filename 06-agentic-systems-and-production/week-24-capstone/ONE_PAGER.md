# Personal Knowledge Assistant - One-Pager

## Problem
Notes, project docs, and team info pile up across files, and finding a specific
fact ("what's Project Alpha's budget?") means grepping or scrolling. A plain LLM
can't answer because it has never seen your private documents, and pasting
everything into a prompt doesn't scale and is expensive.

## Approach
A retrieval-augmented generation (RAG) assistant. It ingests your documents,
indexes them as embeddings, retrieves the most relevant chunks for each question,
and asks Claude to answer **using only that context** -- with citations. A
calculator tool lets the model do arithmetic on retrieved numbers (e.g. a 10%
budget increase) instead of guessing.

## Architecture
```
docs/ --> ingest (chunk) --> embed (sentence-transformers) --> in-memory index
                                                                     |
question --> retrieve top-k chunks --> build context --> Claude (system prompt) --> answer + citations
                                                              |
                                                       tool use: calculator
```
- **ingest.py** - reads .md/.txt, splits into overlapping chunks.
- **retriever.py** - embeds chunks, cosine-similarity search (keyword fallback).
- **app.py** - retrieval, the agentic generation loop with tool use, structured
  logging, and a CLI.

## Evaluation approach
- A small golden set of question/expected-source pairs to check retrieval hits
  the right document (recall@k).
- LLM-as-judge (from Week 22) to grade whether answers are grounded in the cited
  context and free of hallucination.
- Track cost (token usage x price table) and latency per query, as in Week 23.

## Tradeoffs
- **In-memory index** keeps the demo simple but won't scale to large corpora; a
  real deployment would use a persistent vector DB.
- **Character-based chunking** is fast but naive; semantic/structure-aware
  chunking would improve retrieval quality.
- **Grounding vs. helpfulness**: the strict "use only the context" instruction
  reduces hallucination but means the assistant declines questions the docs don't
  cover -- the right default for a knowledge base.

## What's next
- Persist embeddings to a vector store so ingestion isn't repeated every run.
- Add an evaluation harness wiring in the Week 22 judge for regression testing.
- Wrap the CLI in the Week 23 FastAPI service for an HTTP interface with metrics.
- Reranking and citation highlighting for higher-precision answers.
