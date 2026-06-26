# Week 11 — Multi-Model API Wrapper with Cost Tracking

A small Python wrapper class that calls different Claude models (haiku, sonnet, opus) through a single interface, tracks token usage and estimated cost per call, and keeps a running total.

## What it does

- Exposes one `LLMClient.chat(prompt, model=...)` method that works across `haiku`, `sonnet`, and `opus`.
- Reads `response.usage.input_tokens` / `output_tokens` after each call and multiplies them by a small price table to estimate cost.
- Prints a per-call line and a running cost tally, plus a grand total at the end.
- Retries transient failures (rate limits, server errors) with exponential backoff, and surfaces non-transient errors (bad requests, auth) immediately.

> The price table is **illustrative** — it's hardcoded for demonstration and may not match current pricing.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

## How to run

```bash
python3 llm_client.py
```

The demo sends the same question to each model and prints token usage and estimated cost for each. You need a valid `ANTHROPIC_API_KEY` to actually run it.

## What I learned

- Calling a GenAI API is just an HTTP request under the hood, but the SDK makes it clean: pick a model ID, send messages, read `response.content[0].text`. Wrapping that behind one method made swapping models trivial.
- The response carries a `usage` object with `input_tokens` and `output_tokens`, which is the real source of truth for what a call cost — I learned to read those rather than guess from string length.
- Cost is genuinely a model-choice decision: the same prompt is several times cheaper on haiku than opus, so tracking a running tally made the tradeoff concrete instead of abstract.
- Not all errors should be retried. Rate limits (429) and server errors (5xx) are transient and worth a backoff retry; a bad request or auth error won't fix itself, so retrying just wastes time. Distinguishing them was the key insight.
- Exponential backoff (waiting longer after each failed attempt) is the standard, polite way to handle rate limits instead of hammering the API.
- Building a thin wrapper class is a good pattern: it centralizes the API key check, the model mapping, the cost math, and the retry logic in one place so the rest of an app stays simple.
