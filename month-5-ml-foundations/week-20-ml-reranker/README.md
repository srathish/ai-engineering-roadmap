# Week 20 — ML Re-ranker for RAG

A small ML-enhanced re-ranker that reorders retrieved passages so the best ones
reach the LLM first.

## What it does

`reranker.py` takes a query and a list of candidate passages, each with a naive
first-pass similarity score (what a vector search would give you). It then:

1. Builds simple features per passage: vector similarity, keyword overlap with
   the query, and a length signal.
2. Re-scores the candidates with a tiny trained **LogisticRegression** when
   scikit-learn is installed, or a transparent **feature-weighted heuristic** as a
   graceful fallback.
3. Prints the **before** (naive similarity) and **after** (re-ranked) orderings so
   you can see which passages moved up.

The demo is built so that passages which truly answer "how do I reset my
password?" rise above superficially-similar ones (password *rules*, company
history) that the first pass over-ranked.

## How to run

```bash
pip install -r requirements.txt
python3 reranker.py
```

It runs with or without scikit-learn — without it, you'll get the heuristic
re-ranker and a note saying so. `sentence-transformers` is listed as optional for
a stronger cross-encoder approach but isn't needed for this demo.

## When is fine-tuning worth it?

A re-ranker is itself a lightweight, high-leverage form of "tuning" your retrieval
without touching the base embedding model. Full fine-tuning of an embedding or
cross-encoder model is worth it when:

- **Your domain language is unusual** (legal, medical, internal jargon) and
  off-the-shelf embeddings clearly mis-rank — measured, not assumed.
- **You have enough labeled query→passage relevance data** to train and *evaluate*
  on (a few hundred to thousands of judged pairs), not a handful.
- **Retrieval quality is the proven bottleneck** — you've already tried a re-ranker,
  better chunking, and better prompts, and they weren't enough.

It's usually **not** worth it when a simple re-ranker, better chunking, or hybrid
(keyword + vector) retrieval already gets you there. Fine-tuning adds data
collection, training, evaluation, and maintenance cost, so it should be the last
lever you pull, not the first.

## What I learned

- Embeddings came back into focus this week: vector similarity is a great *first*
  pass but it's coarse — it rewards passages that look topically similar even when
  they don't actually answer the question.
- A re-ranker is a clean fix for that: take the cheap top-k, then spend a little
  more compute scoring them carefully and reordering. It made the two-stage
  "retrieve then re-rank" pattern click for me.
- Turning text into features (similarity + keyword overlap + length) and training a
  logistic regression on relevance labels showed me how a model can *learn* how much
  to trust each signal instead of me guessing weights by hand.
- The heuristic fallback taught me something too: a sensible weighted formula gets
  you surprisingly far, and it's worth having a non-ML baseline to compare against.
- The biggest takeaway was on fine-tuning: it's powerful but expensive, and most of
  the time a re-ranker, better chunking, or hybrid search beats reaching for
  fine-tuning first. You fine-tune when you've proven the simpler levers aren't enough.
