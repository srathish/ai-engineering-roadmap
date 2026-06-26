# Week 15 - Document Q&A Bot

A full RAG question-answering bot over your own documents: retrieve relevant chunks, inject them into a prompt, ask Claude, and print the answer with cited sources.

## What it does

End-to-end RAG pipeline in a CLI loop:

1. **Load** the `.txt` docs in `sample_docs/` (a fictional product FAQ + support notes).
2. **Chunk** them (fixed-size with overlap, reusing the Week 13 idea).
3. **Embed** the chunks locally with `sentence-transformers` (`all-MiniLM-L6-v2`).
4. **Retrieve** the top-k chunks for your question by cosine similarity.
5. **Inject** those chunks into a prompt as labeled context.
6. **Ask Claude** (`claude-sonnet-4-6`) to answer using only that context, citing sources.
7. Print the answer plus the sources consulted.

If `ANTHROPIC_API_KEY` is not set, the bot still runs and shows the retrieved context (so you can see exactly what would be sent), it just skips answer generation.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # required only for answer generation
```

Retrieval works without any key; only the final answer needs Claude.

## How to run

```bash
python3 qa_bot.py
# then ask questions at the prompt, e.g.:
#   > How much does the Pro plan cost?
#   > How do I recover a deleted note?
#   > Does it work offline?
```

## What I learned

- This is where retrieval and generation finally come together. Weeks 13 and 14 felt like plumbing; here the chunks I retrieve become the *context* the model reasons over, and the whole thing clicks.
- Context injection is mostly prompt engineering: I label each chunk with its source tag and tell the model to answer only from the provided context and to cite those tags. That framing is what turns a generic chatbot into a grounded, citable Q&A bot.
- Telling the model "if the context does not contain the answer, say so" noticeably reduces the temptation to hallucinate - the retrieved context is doing the heavy lifting, not the model's memory.
- Separating retrieval from generation paid off: I made the bot degrade gracefully when there's no API key by still printing the retrieved context. That made it much easier to debug retrieval on its own.
- Keeping source + chunk index all the way through means citations are basically free - the model just echoes the tags I gave it, and I can show which sources were consulted.
- I can already see the gaps a production version needs: there's no reranking yet, no logging of latency or token usage, and no handling for when retrieval returns weak matches. That's exactly what Week 16 is about.
