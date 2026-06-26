"""
Document summarizer that demonstrates prompt engineering with Claude.

The interesting part here is NOT the API call (which is short) but the prompt:
a clear role/system prompt, explicit instructions, and flags that change the
summary's style and length by rewriting the instructions we send.
"""

import argparse
import os
import sys

# Configurable default model.
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024

# The system prompt sets the model's ROLE and standing behavior. Keeping it
# stable and separate from the per-request instructions is good prompt design.
SYSTEM_PROMPT = (
    "You are a precise, professional summarization assistant. "
    "You distill documents into accurate summaries that preserve the key "
    "facts and main argument. You never invent details that are not in the "
    "source text, and you do not add your own opinions."
)


def build_instructions(style: str, length: str) -> str:
    """Build the per-request instructions from the style/length flags.

    This is prompt engineering in practice: the same task is steered into very
    different outputs purely by changing the wording of the instructions.
    """
    length_guidance = {
        "short": "Keep it concise: roughly 2-3 sentences (or 3 bullet points).",
        "long": "Be thorough: roughly 1-2 paragraphs (or 6-8 bullet points).",
    }[length]

    style_guidance = {
        "paragraph": "Write the summary as flowing prose paragraphs.",
        "bullets": "Write the summary as a list of bullet points, each on its own line.",
    }[style]

    return (
        "Summarize the document below.\n"
        f"- {style_guidance}\n"
        f"- {length_guidance}\n"
        "- Lead with the single most important point.\n"
        "- Use only information present in the document."
    )


def summarize(client, text: str, style: str, length: str) -> str:
    instructions = build_instructions(style, length)
    user_content = f"{instructions}\n\n--- DOCUMENT ---\n{text}\n--- END DOCUMENT ---"

    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )
    return response.content[0].text


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize a text file with Claude.")
    parser.add_argument(
        "file",
        nargs="?",
        default="sample.txt",
        help="Path to the text file to summarize (default: sample.txt).",
    )
    parser.add_argument(
        "--style",
        choices=["bullets", "paragraph"],
        default="paragraph",
        help="Output format (default: paragraph).",
    )
    parser.add_argument(
        "--length",
        choices=["short", "long"],
        default="short",
        help="Summary length (default: short).",
    )
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY is not set.\n")
        print("Set it before running, e.g.:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        print("\nGet a key at https://console.anthropic.com/")
        sys.exit(1)

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            text = f.read().strip()
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}")
        sys.exit(1)

    if not text:
        print(f"Error: file is empty: {args.file}")
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print("Error: the 'anthropic' package is not installed.")
        print("Install it with:  pip install -r requirements.txt")
        sys.exit(1)

    client = anthropic.Anthropic()

    try:
        summary = summarize(client, text, args.style, args.length)
    except anthropic.APIError as e:
        print(f"API error: {e}")
        sys.exit(1)

    print(f"\nSummary ({args.style}, {args.length}):\n")
    print(summary)


if __name__ == "__main__":
    main()
