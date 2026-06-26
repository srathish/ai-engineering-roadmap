# Week 10 — Document Summarizer

A command-line tool that summarizes a text file using Claude, with flags to control the summary's style and length. The focus is prompt engineering: a clear role, explicit instructions, and controllable output.

## What it does

- Reads a text file (defaults to the included `sample.txt`).
- Sends it to Claude with a **system prompt** that defines the assistant's role and a set of **instructions** that steer the output.
- Supports `--style bullets|paragraph` and `--length short|long`, which rewrite the instructions to produce noticeably different summaries from the same source.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

## How to run

```bash
# Default: summarize sample.txt as a short paragraph
python3 summarizer.py

# Bullet points, longer summary
python3 summarizer.py sample.txt --style bullets --length long

# Summarize your own file
python3 summarizer.py myfile.txt --style paragraph --length short
```

You need a valid `ANTHROPIC_API_KEY` for it to actually run.

## What I learned

- A good prompt has structure: I separated the **role** (system prompt) from the **task instructions** (user message), and that separation made the behavior much more predictable than cramming everything into one blob of text.
- Being explicit matters. Telling the model "use only information present in the document" and "do not add opinions" measurably reduced the model wandering off or hallucinating details.
- I can control output format and length purely through wording — the `--style` and `--length` flags don't do any post-processing, they just change the instructions I send, and the model adapts. That was a real "aha" about how much leverage prompting gives you.
- Prompt iteration is the actual workflow: my first instructions were vague ("summarize this") and produced inconsistent results; tightening them point by point is what made the tool reliable.
- Leading the model with "start with the most important point" shapes the structure of the answer, which taught me that you guide an LLM by describing the shape of what you want, not just the topic.
- Even with careful prompting, the model is only as accurate as the source text and its own limitations, so I treat summaries as a strong draft, not ground truth.
