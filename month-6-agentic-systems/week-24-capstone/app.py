"""Capstone - a RAG-powered personal knowledge assistant.

Ties together the whole roadmap: ingestion + chunking, embedding + retrieval,
generation with Claude, tool use, structured logging, and a CLI interface.

Domain: a "personal knowledge assistant" that answers questions grounded in your
own notes/docs (the sample_docs/ folder), citing the sources it used. It also
exposes a calculator tool so the model can do arithmetic on retrieved figures
instead of guessing.

Usage:
    python app.py                       # interactive REPL
    python app.py "your question here"  # single question
"""

import json
import logging
import os
import sys

from ingest import load_documents
from retriever import Retriever

try:
    import anthropic
except ImportError:
    print("The 'anthropic' package is not installed. Run: pip install -r requirements.txt")
    sys.exit(1)

MODEL = "claude-sonnet-4-6"
DOCS_DIR = os.path.join(os.path.dirname(__file__), "sample_docs")

SYSTEM_PROMPT = (
    "You are a personal knowledge assistant. Answer the user's question using "
    "ONLY the provided context from their documents. Cite the source filenames "
    "you used in square brackets, e.g. [notes.md]. If the context does not "
    "contain the answer, say so plainly. Use the calculator tool for any "
    "arithmetic rather than computing it yourself."
)

# --- Tool: calculator ------------------------------------------------------ #
TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression and return the result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "An arithmetic expression, e.g. '42000 * 1.1'.",
                }
            },
            "required": ["expression"],
        },
    }
]


def calculator(expression: str) -> str:
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "Error: unsupported characters in expression."
    try:
        return str(eval(expression, {"__builtins__": {}}, {}))  # noqa: S307
    except Exception as exc:  # noqa: BLE001
        return f"Error: {exc}"


# --- Logging --------------------------------------------------------------- #
logger = logging.getLogger("rag-assistant")
if not logger.handlers:
    h = logging.StreamHandler(sys.stderr)
    h.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(h)
logger.setLevel(logging.INFO)


def log_event(**fields) -> None:
    logger.info(json.dumps(fields))


def build_context(retriever: Retriever, question: str, k: int = 3):
    """Retrieve top-k chunks and format them as a context block + source list."""
    hits = retriever.search(question, k=k)
    sources = sorted({c.doc_id for c in hits})
    context = "\n\n".join(f"[{c.doc_id}] {c.text}" for c in hits)
    return context, sources


def answer(client, retriever: Retriever, question: str) -> str:
    """Run one RAG turn: retrieve -> generate (with tool use) -> return answer."""
    context, sources = build_context(retriever, question)
    log_event(event="retrieved", question=question, sources=sources)

    user_content = f"Context from my documents:\n{context}\n\nQuestion: {question}"
    messages = [{"role": "user", "content": user_content}]

    # Agentic loop so the model can call the calculator tool if needed.
    for _ in range(6):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        if response.stop_reason != "tool_use":
            log_event(
                event="answered",
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
            )
            return "".join(b.text for b in response.content if b.type == "text")

        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            out = calculator(block.input["expression"]) if block.name == "calculator" else "Unknown tool"
            log_event(event="tool_use", tool=block.name, input=block.input)
            results.append(
                {"type": "tool_result", "tool_use_id": block.id, "content": out}
            )
        messages.append({"role": "user", "content": results})

    return "Stopped after too many tool-use turns."


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY is not set. Export it before running:\n"
            "    export ANTHROPIC_API_KEY=sk-ant-...\n"
        )
        sys.exit(1)

    chunks = load_documents(DOCS_DIR)
    print(f"Ingested {len(chunks)} chunks from {DOCS_DIR}", file=sys.stderr)
    retriever = Retriever(chunks)
    client = anthropic.Anthropic()

    # Single-question mode.
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(answer(client, retriever, question))
        return

    # Interactive REPL.
    print("Personal knowledge assistant. Ask a question (Ctrl-D / 'quit' to exit).")
    while True:
        try:
            question = input("\n> ").strip()
        except EOFError:
            break
        if question.lower() in {"quit", "exit", ""}:
            break
        print("\n" + answer(client, retriever, question))


if __name__ == "__main__":
    main()
