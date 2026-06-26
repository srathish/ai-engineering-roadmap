"""
A small wrapper around the Anthropic Messages API that:
  - lets you call different Claude models (haiku / sonnet / opus) behind one
    interface,
  - tracks token usage and an *estimated* cost per call, and
  - keeps a running cost tally across calls.

It also handles errors and does a basic retry on transient failures
(rate limits and server errors).
"""

import os
import sys
import time

# Friendly names mapped to current Claude model IDs.
MODELS = {
    "haiku": "claude-haiku-4-5-20251001",
    "sonnet": "claude-sonnet-4-6",
    "opus": "claude-opus-4-8",
}

DEFAULT_MODEL = "sonnet"

# Illustrative prices in USD per 1,000,000 tokens (input, output).
# NOTE: these numbers are for demonstration only and may not reflect current
# pricing — always check the official pricing page before relying on them.
PRICES = {
    "haiku": {"input": 1.00, "output": 5.00},
    "sonnet": {"input": 3.00, "output": 15.00},
    "opus": {"input": 5.00, "output": 25.00},
}


class LLMClient:
    """One interface over multiple Claude models with cost tracking."""

    def __init__(self, default_model: str = DEFAULT_MODEL, max_retries: int = 3):
        self._require_api_key()
        try:
            import anthropic
        except ImportError:
            print("Error: the 'anthropic' package is not installed.")
            print("Install it with:  pip install -r requirements.txt")
            sys.exit(1)

        self._anthropic = anthropic
        self.client = anthropic.Anthropic()
        self.default_model = default_model
        self.max_retries = max_retries

        # Running totals across all calls made through this client.
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    @staticmethod
    def _require_api_key() -> None:
        if not os.environ.get("ANTHROPIC_API_KEY"):
            print("Error: ANTHROPIC_API_KEY is not set.\n")
            print("Set it before running, e.g.:")
            print("  export ANTHROPIC_API_KEY='your-key-here'")
            print("\nGet a key at https://console.anthropic.com/")
            sys.exit(1)

    @staticmethod
    def estimate_cost(model_key: str, input_tokens: int, output_tokens: int) -> float:
        price = PRICES[model_key]
        return (
            input_tokens / 1_000_000 * price["input"]
            + output_tokens / 1_000_000 * price["output"]
        )

    def chat(self, prompt: str, model: str = None, max_tokens: int = 1024) -> str:
        """Send a single-turn prompt and return the text reply.

        Tracks token usage and cost, retries transient failures.
        """
        model_key = model or self.default_model
        if model_key not in MODELS:
            raise ValueError(
                f"Unknown model '{model_key}'. Choose from: {', '.join(MODELS)}"
            )
        model_id = MODELS[model_key]

        last_error = None
        for attempt in range(self.max_retries):
            try:
                response = self.client.messages.create(
                    model=model_id,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}],
                )
                self._record_usage(model_key, response)
                return response.content[0].text

            except (self._anthropic.RateLimitError,
                    self._anthropic.InternalServerError) as e:
                # Transient — back off and retry.
                last_error = e
                wait = 2 ** attempt
                print(f"[transient error, retrying in {wait}s: {type(e).__name__}]")
                time.sleep(wait)
            except self._anthropic.APIError as e:
                # Non-transient (bad request, auth, etc.) — don't retry.
                raise

        # Exhausted retries.
        raise RuntimeError(f"Failed after {self.max_retries} retries: {last_error}")

    def _record_usage(self, model_key: str, response) -> None:
        usage = response.usage
        cost = self.estimate_cost(model_key, usage.input_tokens, usage.output_tokens)

        self.total_input_tokens += usage.input_tokens
        self.total_output_tokens += usage.output_tokens
        self.total_cost += cost

        print(
            f"[{model_key}] in={usage.input_tokens} out={usage.output_tokens} "
            f"tok | call ${cost:.6f} | running total ${self.total_cost:.6f}"
        )


def main() -> None:
    """Tiny demo: ask the same question to each model and compare cost."""
    client = LLMClient()

    prompt = "In one sentence, what is a large language model?"
    for model_key in ("haiku", "sonnet", "opus"):
        print(f"\n=== {model_key} ===")
        try:
            answer = client.chat(prompt, model=model_key, max_tokens=200)
            print(answer)
        except Exception as e:
            print(f"Error calling {model_key}: {e}")

    print(
        f"\nGrand total: {client.total_input_tokens} input + "
        f"{client.total_output_tokens} output tokens, "
        f"estimated ${client.total_cost:.6f}"
    )


if __name__ == "__main__":
    main()
