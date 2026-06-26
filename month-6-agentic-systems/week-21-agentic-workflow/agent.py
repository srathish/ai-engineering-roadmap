"""Week 21 - Agentic workflow with tool calling.

This agent automates a concrete workflow: answering questions about a small set
of local "notes" while doing arithmetic and writing results to disk. It uses the
official Anthropic tools API and runs the full agentic loop:

    model requests a tool  ->  we execute it  ->  feed the result back  ->  repeat
    until the model returns a final text answer (stop_reason == "end_turn").

WHEN ARE AGENTS UNNECESSARY?
    Most tasks do NOT need an agent. If the work is a single, fully-specified
    transformation (summarize this text, classify this email, extract these
    fields), a plain one-shot LLM call is cheaper, faster, and easier to debug.
    Reach for an agentic loop only when the task is genuinely multi-step and the
    sequence of steps can't be hard-coded in advance -- the model has to decide
    what to do next based on intermediate results (e.g. "look something up, do
    math on it, then save a report"). If you can write the steps as a fixed
    pipeline, write the pipeline instead.
"""

import json
import os
import sys

try:
    import anthropic
except ImportError:
    print("The 'anthropic' package is not installed. Run: pip install anthropic")
    sys.exit(1)

MODEL = "claude-sonnet-4-6"

# A tiny local "knowledge base" the search tool reads from. In a real app this
# would be a folder of markdown notes, a vector store, etc.
NOTES = {
    "project-alpha": "Project Alpha ships on 2026-07-15. Budget is $42,000. Lead is Priya.",
    "project-beta": "Project Beta is on hold pending legal review. Estimated cost $18,500.",
    "team": "The team has 6 engineers and 2 designers across two time zones.",
}


# --------------------------------------------------------------------------- #
# Tool implementations (plain Python functions)                               #
# --------------------------------------------------------------------------- #
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression safely (no names, no calls)."""
    allowed = set("0123456789+-*/(). ")
    if not set(expression) <= allowed:
        return "Error: expression contains unsupported characters."
    try:
        # eval is restricted to arithmetic only by the character allowlist above.
        result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307
    except Exception as exc:  # noqa: BLE001
        return f"Error evaluating expression: {exc}"
    return str(result)


def search_notes(query: str) -> str:
    """Return any local notes whose key or body contains the query (case-insensitive)."""
    q = query.lower()
    hits = [
        f"[{key}] {body}"
        for key, body in NOTES.items()
        if q in key.lower() or q in body.lower()
    ]
    return "\n".join(hits) if hits else "No matching notes found."


def write_file(filename: str, content: str) -> str:
    """Write content to a file in the current working directory."""
    # Guard against path traversal -- keep writes flat in the cwd.
    safe_name = os.path.basename(filename)
    if not safe_name or safe_name in (".", ".."):
        return "Error: invalid filename."
    try:
        with open(safe_name, "w", encoding="utf-8") as fh:
            fh.write(content)
    except OSError as exc:
        return f"Error writing file: {exc}"
    return f"Wrote {len(content)} characters to {safe_name}."


# Map tool names to their implementations.
TOOL_FUNCTIONS = {
    "calculator": lambda args: calculator(args["expression"]),
    "search_notes": lambda args: search_notes(args["query"]),
    "write_file": lambda args: write_file(args["filename"], args["content"]),
}

# Tool schemas advertised to the model.
TOOLS = [
    {
        "name": "calculator",
        "description": "Evaluate a basic arithmetic expression. "
        "Use for any math the user needs.",
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
    },
    {
        "name": "search_notes",
        "description": "Search the user's local notes for information. "
        "Call this before answering questions about projects, budgets, or the team.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A keyword or phrase to look for in the notes.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "write_file",
        "description": "Write text content to a file so the user can keep the result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "Target filename."},
                "content": {"type": "string", "description": "Text to write."},
            },
            "required": ["filename", "content"],
        },
    },
]


def run_agent(client: "anthropic.Anthropic", task: str, max_turns: int = 10) -> str:
    """Run the agentic loop until the model produces a final answer."""
    messages = [{"role": "user", "content": task}]

    for turn in range(max_turns):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        # Model finished -> collect and return its text.
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # Otherwise execute every requested tool and feed results back.
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            fn = TOOL_FUNCTIONS.get(block.name)
            print(f"  [turn {turn + 1}] tool: {block.name}({json.dumps(block.input)})")
            output = fn(block.input) if fn else f"Unknown tool: {block.name}"
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": output,
                    "is_error": fn is None,
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return "Stopped: reached the maximum number of turns without a final answer."


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY is not set. Export it before running:\n"
            "    export ANTHROPIC_API_KEY=sk-ant-...\n"
        )
        sys.exit(1)

    client = anthropic.Anthropic()

    # Example task that genuinely needs multiple steps:
    #   search the notes -> do arithmetic on the budget -> save a report.
    task = (
        "Look up Project Alpha in my notes. Calculate what its budget would be "
        "after a 10% increase, then write a short summary with the new budget "
        "to a file called 'alpha_summary.txt'. Finally, tell me the new budget."
    )
    print(f"Task: {task}\n")
    answer = run_agent(client, task)
    print(f"\nFinal answer:\n{answer}")


if __name__ == "__main__":
    main()
