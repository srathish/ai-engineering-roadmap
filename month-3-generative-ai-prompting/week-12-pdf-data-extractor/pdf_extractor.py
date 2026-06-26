"""
Extract structured data from a PDF using Claude.

Pipeline:
  1. Read the PDF text with pypdf.
  2. Prompt Claude to return STRUCTURED JSON (title, entities, dates, summary).
  3. Parse the JSON and pretty-print it; handle the case where the model
     returns something that isn't valid JSON.

This demonstrates the "structured outputs" / "JSON mode" mindset: instead of
parsing free-form prose, we instruct the model to emit a precise schema so the
result is machine-readable.
"""

import argparse
import json
import os
import sys

# Configurable default model.
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024

# The prompt is engineered to force a JSON-only response matching a schema.
EXTRACTION_PROMPT = """\
Extract structured information from the document text below.

Return ONLY a single JSON object (no markdown, no code fences, no commentary)
with exactly these keys:
  - "title": a short title for the document (string)
  - "key_entities": notable people, organizations, or places (array of strings)
  - "dates": any dates mentioned, as written (array of strings)
  - "summary": a 1-2 sentence summary (string)

If a field has no information, use an empty string or empty array.

--- DOCUMENT TEXT ---
{text}
--- END DOCUMENT TEXT ---"""


def read_pdf_text(path: str) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        print("Error: the 'pypdf' package is not installed.")
        print("Install it with:  pip install -r requirements.txt")
        sys.exit(1)

    try:
        reader = PdfReader(path)
    except FileNotFoundError:
        print(f"Error: file not found: {path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: could not read PDF: {e}")
        sys.exit(1)

    parts = [page.extract_text() or "" for page in reader.pages]
    text = "\n".join(parts).strip()
    if not text:
        print("Error: no extractable text found in the PDF.")
        print("(Scanned/image-only PDFs need OCR, which this tool does not do.)")
        sys.exit(1)
    return text


def extract_json(raw: str):
    """Parse the model output as JSON, tolerating stray fences/prose.

    Returns (parsed_obj_or_None, raw_text).
    """
    cleaned = raw.strip()

    # Strip a ```json ... ``` fence if the model added one despite instructions.
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned[: -3]
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned), raw
    except json.JSONDecodeError:
        # Last resort: grab the substring between the first '{' and last '}'.
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1]), raw
            except json.JSONDecodeError:
                pass
        return None, raw


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract structured JSON data from a PDF using Claude."
    )
    parser.add_argument("pdf", help="Path to the PDF file to process.")
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY is not set.\n")
        print("Set it before running, e.g.:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        print("\nGet a key at https://console.anthropic.com/")
        sys.exit(1)

    text = read_pdf_text(args.pdf)

    try:
        import anthropic
    except ImportError:
        print("Error: the 'anthropic' package is not installed.")
        print("Install it with:  pip install -r requirements.txt")
        sys.exit(1)

    client = anthropic.Anthropic()

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[
                {"role": "user", "content": EXTRACTION_PROMPT.format(text=text)}
            ],
        )
    except anthropic.APIError as e:
        print(f"API error: {e}")
        sys.exit(1)

    raw = response.content[0].text
    parsed, raw = extract_json(raw)

    if parsed is None:
        print("Warning: the model did not return valid JSON. Raw output:\n")
        print(raw)
        sys.exit(1)

    print(json.dumps(parsed, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
