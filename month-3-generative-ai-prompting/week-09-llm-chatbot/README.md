# Week 9 — LLM Terminal Chatbot

A simple multi-turn command-line chatbot built on Claude that remembers the conversation and streams replies token by token.

## What it does

- Runs an interactive loop in your terminal where you chat with Claude.
- Keeps the full conversation history (a list of user/assistant messages) and resends it each turn, so the model has context for follow-up questions.
- Streams the assistant's reply as it is generated instead of waiting for the whole response.
- Type `quit` (or `exit`) to leave.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

## How to run

```bash
python3 chatbot.py
```

Then just start typing. (You need a valid `ANTHROPIC_API_KEY` for it to actually call the model.)

## What I learned

- An LLM is fundamentally a next-token predictor: it takes the text so far and predicts what comes next, one token at a time, which is exactly why streaming works.
- The Messages API is **stateless** — the model has no memory of its own. The only reason a chatbot feels like it remembers is that I resend the entire conversation history on every request.
- Text gets broken into **tokens** (roughly 3-4 characters of English each), and both my input and the model's output cost tokens. That made me realize cost and the context limit are tied to length, not just number of turns.
- The **context window** is a hard ceiling on how much text the model can see at once. A long chat eventually has to be trimmed or summarized, which I now understand is a real engineering concern, not an edge case.
- Inference (generating the reply) happens on Anthropic's servers; my job as the app developer is just to manage the history list and handle errors gracefully.
- LLMs have real limitations — they can confidently make things up, they don't truly "know" the current date or facts past their training, and they can't remember anything outside the window I send them.
