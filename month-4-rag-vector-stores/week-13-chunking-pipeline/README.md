# Week 13 - Chunking Pipeline

A document chunking pipeline that splits text into overlapping chunks while preserving metadata. Pure standard library.

## What it does

Loads `.txt` documents and cuts them into chunks using two strategies:

- **Fixed-size with overlap** - slides a fixed-width character window across the text; consecutive windows overlap so sentences spanning a boundary survive intact.
- **Sentence/paragraph aware** - packs whole sentences up to a size budget without ever splitting mid-sentence, carrying one sentence of overlap between chunks.

Every chunk keeps its metadata: source file, chunk index, character span, and the strategy used. The script prints stats (count, total/min/avg/max size, a preview) for each strategy.

## Setup

No dependencies to install - this uses only the Python standard library.

```bash
python3 --version   # 3.8+
```

## How to run

```bash
python3 chunker.py
# or with custom parameters:
python3 chunker.py --chunk-size 300 --overlap 40
python3 chunker.py --docs "sample_docs/*.txt"
```

## What I learned

- I finally understood *why* RAG exists rather than just what it is: language models have a training cutoff and a finite context window, so you keep knowledge external and pull in only the slice each question needs.
- Chunking is the unglamorous first stage of the RAG architecture (ingest -> chunk -> embed -> store -> retrieve -> generate), and it quietly determines how good everything downstream can be.
- The fixed-size-with-overlap strategy is dead simple, but the overlap parameter matters more than I expected - without it, a fact sitting on a chunk boundary can get split and become unretrievable.
- Sentence-aware chunking is more work to implement (I had to handle paragraph breaks and sentence splitting with regex), but it keeps chunks semantically clean, which I'd expect to help retrieval on prose.
- There is no universally correct chunk size. It depends on the document shape and the kinds of questions asked, and the real answer is to measure retrieval quality and tune - something I want to actually test in later weeks.
- Carrying metadata (source + index) from the very start feels like overkill at chunk time, but I can already see I'll need it to cite sources once I'm generating answers.
