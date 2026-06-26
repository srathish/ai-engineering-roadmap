# Week 23 - Deployed AI App with Observability

A small, containerized FastAPI service that wraps Claude behind a `/summarize`
endpoint, instrumented for observability and built with responsible-AI guardrails.

## What it does

- **`POST /summarize`** - summarizes a block of text with Claude.
- **`GET /metrics`** - returns running aggregates (requests, errors, tokens, latency).
- **`GET /health`** - liveness check that also reports the active prompt version.

Built-in features:

- **Structured logging** - every request emits a single JSON log line with a
  `request_id`, prompt version, token counts, and latency.
- **Metrics** - request/error counts, input/output tokens, and total latency are
  accumulated in-process and exposed at `/metrics`.
- **Prompt versioning** - a `PROMPT_VERSION` constant selects from a `PROMPTS`
  dict, so prompt changes are explicit and show up in the logs.
- **Responsible AI** - an input length guard, a prompt-injection-resistant system
  prompt (the model is told to summarize, not obey, the input), and PII-conscious
  logging that never records the raw request body.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## How to run

Locally:

```bash
uvicorn app:app --reload --port 8000

curl -s localhost:8000/summarize \
  -H 'content-type: application/json' \
  -d '{"text": "A long passage of text you want summarized..."}'

curl -s localhost:8000/metrics
```

With Docker:

```bash
docker build -t summarize-service .
docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY -p 8000:8000 summarize-service
```

If `ANTHROPIC_API_KEY` is not set, the service still starts and returns a clear
`503` from `/summarize` rather than crashing.

## What I learned

- Observability has to be designed in, not bolted on. Emitting one structured
  JSON line per request -- with a `request_id`, token counts, and latency -- turned
  "is it slow?" from a guess into something I could grep.
- Prompt versioning sounds trivial but it's the thing that makes a prompt change
  auditable. Tagging every log line with `PROMPT_VERSION` means I can correlate a
  quality regression with the exact prompt that caused it.
- Dockerizing forced me to separate config (the API key, injected at runtime)
  from code, and to order the layers so dependency installs are cached.
- The responsible-AI work was the most eye-opening: user input is untrusted, so
  the system prompt has to stay authoritative and explicitly refuse embedded
  instructions. That's the core of prompt-injection defense at this layer.
- Not logging the raw request body, plus a hard input-length cap, were cheap
  wins for both PII safety and cost control.
