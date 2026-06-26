# Week 21 - Agentic Workflow

An agent that automates a real multi-step workflow using Claude's tool-calling API.

## What it does

Given a task in plain English, the agent plans and executes a sequence of tool
calls to get the job done. It ships with three real tools:

- **calculator** - evaluates basic arithmetic safely.
- **search_notes** - looks things up in a small local knowledge base.
- **write_file** - saves results to disk.

The example task ("look up Project Alpha's budget, raise it 10%, write a summary
to a file, then report the number") forces the agent to chain all three tools:
search -> calculate -> write. It runs the full agentic loop -- the model requests
a tool, we execute it, feed the result back, and repeat until it returns a final
answer.

## Setup

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
```

## How to run

```bash
python agent.py
```

You'll see each tool call printed as the agent works, then the final answer. A
file `alpha_summary.txt` is created in the current directory.

## What I learned

- Building the agentic loop by hand made the control flow click: the model never
  runs my code -- it *asks* for a tool by name, I run it, and I hand the result
  back as a `tool_result`. The loop only ends when `stop_reason` stops being
  `"tool_use"`.
- Tool descriptions are basically prompt engineering. When my `search_notes`
  description didn't say "call this before answering," the model sometimes
  guessed from memory instead of looking things up. Being prescriptive about
  *when* to call a tool fixed it.
- I have to append the assistant's full `content` (including the `tool_use`
  blocks) back into the message history before sending results, and every
  `tool_result` has to carry the matching `tool_use_id`. Getting that wrong was
  my first bug.
- The biggest lesson was knowing when *not* to build an agent. For a single
  fixed transformation, a plain one-shot call is cheaper and easier to debug. An
  agent only earns its cost when the next step genuinely depends on the result
  of the previous one.
- Capping the loop with `max_turns` matters -- without a ceiling a confused agent
  can spin indefinitely and burn tokens.
