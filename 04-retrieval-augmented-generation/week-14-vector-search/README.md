# Week 14 - Vector Search

A vector search system: embed document chunks locally, store them in memory, and retrieve the top-k most similar chunks for a query by cosine similarity.

## What it does

- Loads `.txt` documents and chunks them (a small local chunker reuses the Week 13 idea).
- Embeds every chunk with `sentence-transformers` (`all-MiniLM-L6-v2`) - runs locally, no paid API.
- Stores the embeddings in an in-memory numpy matrix (a `VectorStore` class).
- Given a query, embeds it and returns the top-k chunks ranked by cosine similarity, with scores and source citations.

## Setup

```bash
pip install -r requirements.txt
```

No API key is required - embedding and search run entirely on your machine.

## How to run

```bash
# Run the built-in demo queries:
python3 vector_search.py

# Ask your own question:
python3 vector_search.py "what is pgvector"
python3 vector_search.py -k 5 "how do I scale vector search"
```

## What I learned

- Vectors are stored as a plain matrix of floats - one row per chunk - and "search" is just comparing the query vector against every stored row. Seeing it as a single matrix multiply demystified what a vector database is doing under the hood.
- Cosine similarity compares *direction*, not distance. Normalizing to unit length and taking the dot product is the whole trick, and it explains why two sentences with no shared words can still score highly.
- Brute-force scan over an in-memory numpy array is totally fine for a small corpus. The need for a real vector store only shows up at scale, when comparing against every vector gets slow.
- That's where the Chroma / pgvector / Pinecone landscape fits in: they add approximate-nearest-neighbor indexes (speed), persistence (no re-embedding on restart), and varying amounts of managed infrastructure. The core embed -> store -> search loop is identical to mine.
- Loading the embedding model the first time is slow, but embedding is a one-time cost per chunk - I can see why ingestion and querying get separated in real systems.
- Keeping the source and chunk index on each result means I can already cite where an answer came from, which is exactly what I'll need when I bolt an LLM on top next week.
