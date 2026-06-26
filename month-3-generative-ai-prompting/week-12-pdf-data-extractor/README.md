# Week 12 — PDF Data Extractor (Structured JSON)

Extracts structured data from a PDF using Claude. It reads the PDF text with `pypdf`, prompts Claude to return JSON matching a fixed schema, then parses and pretty-prints the result.

## What it does

- Reads text from a PDF you supply with `pypdf`.
- Prompts Claude to return a single JSON object with `title`, `key_entities`, `dates`, and `summary`.
- Parses the JSON and pretty-prints it. If the model returns something that isn't valid JSON (stray prose, code fences), it tries to recover the JSON and, failing that, shows the raw output instead of crashing.
- Demonstrates the "structured outputs / JSON mode" mindset via prompt instructions: tell the model exactly what schema to emit so the output is machine-readable.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your-key-here
```

## How to run

**You supply your own PDF path** — there is no sample PDF bundled:

```bash
python3 pdf_extractor.py path/to/your/document.pdf
```

It prints the extracted data as formatted JSON. You need a valid `ANTHROPIC_API_KEY` to actually run it. Note that scanned/image-only PDFs won't work because `pypdf` can only read embedded text (no OCR).

## What I learned

- Structured outputs are a different mindset from chatting: instead of reading prose, I tell the model the exact JSON shape I want and then treat the response as data. That makes the output usable by other code.
- "JSON mode" via prompting is mostly about being strict and explicit — listing the exact keys, saying "return ONLY JSON, no markdown or commentary," and specifying what to do when a field is empty all measurably improved how clean the output was.
- The model doesn't always obey perfectly, so I learned to write a tolerant parser: strip code fences the model sometimes adds, and fall back to grabbing the substring between the first `{` and last `}` before giving up.
- Always handle the non-JSON case. A naive `json.loads()` on raw model output will eventually throw, so catching `JSONDecodeError` and showing the raw text is what makes the tool robust.
- Separating the pipeline into clear stages (read PDF → prompt → parse) made it much easier to reason about where things can fail and to give specific error messages at each step.
- This is the same idea behind function calling / tool use: constraining the model to a schema so its output can drive real software, rather than just being read by a human.
