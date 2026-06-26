"""
A simple multi-turn terminal chatbot built on the Anthropic Messages API.

How an LLM "remembers" a conversation
-------------------------------------
The Messages API is stateless: the model does not retain anything between
calls. To hold a conversation we resend the FULL history every turn as a list
of {"role": ..., "content": ...} messages. The model reads that history (its
"context window") and predicts the next assistant turn.

Tokens & context window
------------------------
Text is split into "tokens" (roughly 3-4 characters of English each). Both your
input history and the model's reply consume tokens. The context window is the
maximum number of tokens the model can consider at once. As a conversation
grows, the history grows, so very long chats eventually need trimming or
summarizing to stay within the window.
"""

import os
import sys

# Configurable default model. These IDs are current Claude models.
MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 1024


def require_api_key() -> None:
    """Exit cleanly with guidance if the API key is missing."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY is not set.\n")
        print("Set it before running, e.g.:")
        print("  export ANTHROPIC_API_KEY='your-key-here'")
        print("\nGet a key at https://console.anthropic.com/")
        sys.exit(1)


def main() -> None:
    require_api_key()

    # Import after the key check so a missing package or key surfaces clearly.
    try:
        import anthropic
    except ImportError:
        print("Error: the 'anthropic' package is not installed.")
        print("Install it with:  pip install -r requirements.txt")
        sys.exit(1)

    client = anthropic.Anthropic()

    # Conversation history grows every turn; the whole list is resent each call.
    messages = []

    print("Claude terminal chatbot. Type 'quit' to exit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break

        messages.append({"role": "user", "content": user_input})

        # Stream the reply so tokens appear as they are generated.
        print("Claude: ", end="", flush=True)
        reply_parts = []
        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                messages=messages,
            ) as stream:
                for text in stream.text_stream:
                    print(text, end="", flush=True)
                    reply_parts.append(text)
            print()  # newline after the streamed reply
        except anthropic.APIError as e:
            print(f"\n[API error: {e}]")
            # Drop the unanswered user turn so history stays consistent.
            messages.pop()
            continue

        # Append the assistant's reply so the model "remembers" it next turn.
        messages.append({"role": "assistant", "content": "".join(reply_parts)})


if __name__ == "__main__":
    main()
