# Week 22 - Evaluation + Cost Analysis

A small evaluation harness that runs a golden dataset through an LLM task, grades
the outputs with an LLM-as-judge, and reports accuracy, token usage, dollar cost,
and latency.

## What it does

- Loads a **golden dataset** (`golden_dataset.json`) of input/expected pairs.
- Runs each input through the task prompt (here: sentiment classification).
- Scores each output with an **LLM-as-judge** that returns PASS/FAIL + a reason.
- Tracks token usage from `response.usage`, converts it to dollars with a
  per-model **price table**, and times each call for **latency**.
- Prints a per-example breakdown plus aggregate accuracy, cost, and latency.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## How to run

```bash
python eval_runner.py
```

Edit `golden_dataset.json` to change the task or add examples -- the runner reads
the `task` field and every `examples[*]` entry, so no code changes are needed to
evaluate a different task.

## What I learned

- LLM-as-judge is surprisingly practical for fuzzy tasks where exact string
  matching fails ("positive!" vs "positive"). The trick is forcing the judge to
  return structured JSON so I can parse a clean verdict instead of regexing prose.
- A golden dataset only needs to be small to be useful. Six well-chosen examples
  caught more regressions than I expected, and they double as documentation of
  what "correct" means.
- Cost is just `tokens * price`, but I only understood where the money goes once
  I added the judge call to the tally -- grading can cost as much as the task
  itself, so the judge model choice matters.
- Tracking latency alongside cost made the tradeoffs concrete: a cheaper model
  that's faster but slightly less accurate is a real, measurable decision rather
  than a vibe.
- Things that would cut cost next: prompt caching for the shared system prompt
  across examples, and prompt compression so the judge prompt isn't re-sending
  the full task text every time.
