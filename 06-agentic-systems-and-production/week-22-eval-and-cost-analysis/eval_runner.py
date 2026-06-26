"""Week 22 - Evaluation + cost analysis tool.

Runs a small golden dataset through an LLM task, then uses an LLM-as-judge to
score each output. It also tracks token usage, computes dollar cost from a price
table, and measures latency. The result is a printed report you can paste into a
PR or a weekly review.

Pipeline per example:
    1. Run the TASK prompt through the model        -> candidate answer
    2. Run the JUDGE prompt (LLM-as-judge)          -> PASS / FAIL + reason
    3. Accumulate tokens, cost, and latency

Gracefully exits with a clear message if ANTHROPIC_API_KEY is missing.
"""

import json
import os
import sys
import time

try:
    import anthropic
except ImportError:
    print("The 'anthropic' package is not installed. Run: pip install anthropic")
    sys.exit(1)

MODEL = "claude-sonnet-4-6"
DATASET_PATH = os.path.join(os.path.dirname(__file__), "golden_dataset.json")

# Price table in USD per 1M tokens. Keep this in sync with current pricing.
PRICES = {
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-opus-4-8": {"input": 5.00, "output": 25.00},
    "claude-haiku-4-5": {"input": 1.00, "output": 5.00},
}


def cost_usd(model: str, in_tokens: int, out_tokens: int) -> float:
    """Convert token counts to a dollar cost using the price table."""
    price = PRICES.get(model, {"input": 0.0, "output": 0.0})
    return (in_tokens / 1_000_000) * price["input"] + (
        out_tokens / 1_000_000
    ) * price["output"]


def run_task(client, task: str, user_input: str):
    """Run one example through the task model. Returns (answer, usage, latency_s)."""
    start = time.time()
    response = client.messages.create(
        model=MODEL,
        max_tokens=64,
        system=task,
        messages=[{"role": "user", "content": user_input}],
    )
    latency = time.time() - start
    answer = "".join(b.text for b in response.content if b.type == "text").strip()
    return answer, response.usage, latency


def judge(client, task: str, user_input: str, expected: str, candidate: str):
    """LLM-as-judge: score the candidate against the expected answer."""
    judge_prompt = (
        "You are a strict grader. Given a task, an input, the expected answer, "
        "and a candidate answer, decide whether the candidate is correct.\n"
        "Reply with a JSON object only: {\"verdict\": \"PASS\" or \"FAIL\", "
        "\"reason\": \"<short reason>\"}.\n\n"
        f"TASK: {task}\n"
        f"INPUT: {user_input}\n"
        f"EXPECTED: {expected}\n"
        f"CANDIDATE: {candidate}\n"
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=128,
        messages=[{"role": "user", "content": judge_prompt}],
    )
    text = "".join(b.text for b in response.content if b.type == "text").strip()
    try:
        parsed = json.loads(text)
        verdict = parsed.get("verdict", "FAIL")
        reason = parsed.get("reason", "")
    except json.JSONDecodeError:
        # Fall back to a substring check if the judge didn't return clean JSON.
        verdict = "PASS" if "PASS" in text.upper() else "FAIL"
        reason = "judge output was not valid JSON"
    return verdict, reason, response.usage


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "ANTHROPIC_API_KEY is not set. Export it before running:\n"
            "    export ANTHROPIC_API_KEY=sk-ant-...\n"
        )
        sys.exit(1)

    with open(DATASET_PATH, encoding="utf-8") as fh:
        data = json.load(fh)
    task = data["task"]
    examples = data["examples"]

    client = anthropic.Anthropic()

    passed = 0
    total_in = total_out = 0
    total_latency = 0.0
    rows = []

    for ex in examples:
        answer, task_usage, latency = run_task(client, task, ex["input"])
        verdict, reason, judge_usage = judge(
            client, task, ex["input"], ex["expected"], answer
        )

        in_tok = task_usage.input_tokens + judge_usage.input_tokens
        out_tok = task_usage.output_tokens + judge_usage.output_tokens
        total_in += in_tok
        total_out += out_tok
        total_latency += latency
        if verdict == "PASS":
            passed += 1

        rows.append(
            {
                "id": ex["id"],
                "expected": ex["expected"],
                "answer": answer,
                "verdict": verdict,
                "reason": reason,
                "latency": latency,
                "cost": cost_usd(MODEL, in_tok, out_tok),
            }
        )

    # ----- Report ----------------------------------------------------------- #
    n = len(examples)
    print("=" * 72)
    print(f"EVAL REPORT  -  model: {MODEL}  -  examples: {n}")
    print("=" * 72)
    for r in rows:
        mark = "PASS" if r["verdict"] == "PASS" else "FAIL"
        print(
            f"[{mark}] {r['id']:6}  expected={r['expected']:9} got={r['answer']!r:12}"
            f"  {r['latency']:.2f}s  ${r['cost']:.6f}"
        )
        if r["verdict"] == "FAIL":
            print(f"        reason: {r['reason']}")
    print("-" * 72)
    print(f"Accuracy        : {passed}/{n}  ({100 * passed / n:.1f}%)")
    print(f"Total tokens    : {total_in} in / {total_out} out")
    print(f"Total cost      : ${cost_usd(MODEL, total_in, total_out):.6f}")
    print(f"Avg latency     : {total_latency / n:.2f}s per example")
    print(f"Total wall time : {total_latency:.2f}s")
    print("=" * 72)


if __name__ == "__main__":
    main()
