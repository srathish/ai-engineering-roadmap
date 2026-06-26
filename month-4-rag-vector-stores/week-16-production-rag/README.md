# Week 16 - Production-Style RAG

A RAG app built from scratch with the things a real deployment needs: structured logging, a config dataclass, a reranking step, and clean stage separation.

## What it does

Runs a RAG pipeline with production concerns made explicit:

- **Structured logging** (`logging` module): retrieval scores, per-stage latency, and token usage (input/output) on every model call.
- **Config** in one `RagConfig` dataclass: models, chunk size/overlap, retrieve-k, final-k, score threshold, max tokens.
- **Reranking**: retrieves a broad candidate set, then re-sorts by blending the dense embedding score with a keyword-overlap signal, and drops candidates below a score threshold.
- **Clean stage separation**: `ingest -> retrieve -> rerank -> generate`, each a separate function with its own logging.

LangChain and LlamaIndex are noted in the code comments as the framework alternatives; this implements the stages from scratch so every metric is visible. Retrieval runs locally; generation calls Claude (`claude-sonnet-4-6`) and degrades gracefully without a key.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # required only for answer generation
```

## How to run

```bash
python3 rag_app.py
# watch the log lines for per-stage latency, scores, and token usage, e.g.:
#   > What is reranking and why is it useful?
#   > How do I keep token costs down?
```

Set the log level to DEBUG in `configure_logging()` to see per-candidate scores.

## What I learned

- Observability is the real difference between a demo and something you'd run. By logging retrieval scores, per-stage latency, and token usage, I can now tell *which* stage failed when an answer is bad - retrieval, reranking, or generation - instead of guessing.
- Splitting the pipeline into named stages (ingest/retrieve/rerank/generate) wasn't just tidiness: it's what made the logging meaningful and let me time each stage independently. Generation is reliably the slowest and the only part that costs money per token.
- Reranking clicked once I built it: dense retrieval is fast but blunt, and a cheap keyword-overlap signal blended with the embedding score catches chunks that are semantically near but not actually on-topic. The score threshold then prunes weak matches before they waste tokens.
- A config dataclass sounds boring but it changed how I work - every knob (chunk size, k values, threshold, model) is in one place, so tuning is editing one object instead of hunting through the code.
- Token usage is the cost lever. Logging input/output tokens made it concrete that every injected chunk is something I pay for, which reframes "retrieve fewer, better chunks" as a cost decision, not just a quality one.
- I get why frameworks like LangChain and LlamaIndex exist - they package exactly this glue. Building it by hand first means I now understand what they're abstracting, so I'd reach for them knowing what's underneath rather than treating them as magic.
