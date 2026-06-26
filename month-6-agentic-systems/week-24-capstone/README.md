# Week 24 - Capstone: RAG Personal Knowledge Assistant

An end-to-end AI product that ties the whole roadmap together: a retrieval-augmented
assistant that answers questions grounded in your own documents, with citations.

## What it does

Ask a question in plain English and the assistant:

1. **Ingests + chunks** your documents (`sample_docs/`) into overlapping windows.
2. **Embeds + retrieves** the most relevant chunks with sentence-transformers and
   cosine similarity.
3. **Generates** an answer with Claude using *only* the retrieved context, and
   **cites** the source files it used.
4. **Uses a tool** -- a calculator -- so it can do arithmetic on retrieved numbers
   (e.g. "what's Project Alpha's budget after a 10% raise?") instead of guessing.
5. **Logs** each step as structured JSON (retrieval, tool use, token usage).

It combines everything from the month: ingestion/chunking, embedding/retrieval,
generation, tool use, logging, and a CLI interface.

## Project layout

```
app.py              # RAG pipeline + agentic loop + CLI
ingest.py           # document loading and chunking
retriever.py        # embedding + similarity search (keyword fallback)
sample_docs/        # example knowledge base
requirements.txt
ONE_PAGER.md        # problem / approach / architecture / tradeoffs / next
```

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

The first run downloads the `all-MiniLM-L6-v2` embedding model. If
sentence-transformers/numpy aren't installed, the retriever falls back to a
keyword-overlap search so the pipeline still runs.

## How to run

Interactive:

```bash
python app.py
> What is Project Alpha's budget after a 10% increase?
> How many engineers are on the team?
```

Single question:

```bash
python app.py "What is Project Beta's status and estimated cost?"
```

## What I learned

- Shipping something end-to-end is a different skill from building any one piece.
  The hard part wasn't retrieval or generation alone -- it was making ingestion,
  retrieval, the agentic loop, and logging hand off cleanly to each other.
- Writing the one-pager first clarified the product. Forcing myself to state the
  problem, the tradeoffs, and "what's next" exposed decisions (in-memory index,
  naive chunking) I'd otherwise have made by accident.
- RAG is mostly about *grounding*. The system prompt that says "use only this
  context and cite it" is what turns a chatty model into a trustworthy assistant
  that admits when the docs don't have the answer.
- Every earlier week showed up here: tool use (Week 21), the cost/latency mindset
  (Week 22), and structured logging plus a clean interface (Week 23). Seeing them
  compose into one product is what made the whole month click.
- Designing for graceful degradation (the keyword fallback when embeddings are
  missing) made the project far easier to run and demo than a brittle "all or
  nothing" pipeline.
