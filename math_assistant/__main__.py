"""Command-line chat with the math agent.

    python -m math_assistant                      # interactive chat
    python -m math_assistant "What is 2^10?"      # one question
    python -m math_assistant --quiet "..."        # hide the tool calls
"""

from __future__ import annotations

import argparse
import json
import os
import sys

try:
    import readline  # noqa: F401  enables arrow keys, history and Ctrl+L in the chat prompt
except ImportError:  # not available on Windows
    pass

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from .agent import build_agent
from .llm import ConfigError


def message_text(message) -> str:
    """Plain text of a message, whether its content is a string or a list of blocks."""
    content = message.content
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "") if isinstance(block, dict) else str(block) for block in content
    )


def format_call(call: dict) -> str:
    args = ", ".join(f"{key}={json.dumps(value)}" for key, value in call["args"].items())
    return f"{call['name']}({args})"


def for_terminal(text: str) -> str:
    """Drop Markdown bold markers (**80** -> 80): terminals show them as literal asterisks."""
    return text.replace("**", "")


def shorten(text: str, limit: int = 160) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def ask(agent, history: list, question: str, show_steps: bool = True) -> str:
    """Send `question` to the agent, keeping the conversation in `history`. Returns the answer."""
    history.append(HumanMessage(question))
    result = agent.invoke({"messages": history})
    new_messages = result["messages"][len(history):]

    if show_steps:
        for message in new_messages:
            if isinstance(message, AIMessage) and message.tool_calls:
                for call in message.tool_calls:
                    print(f"  🔧 {format_call(call)}")
            elif isinstance(message, ToolMessage):
                print(f"     → {shorten(message_text(message))}")

    history[:] = result["messages"]
    return message_text(history[-1])


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m math_assistant", description="Chat with an AI math assistant."
    )
    parser.add_argument("question", nargs="*", help="ask one question and exit")
    parser.add_argument("-q", "--quiet", action="store_true", help="don't show tool calls")
    args = parser.parse_args(argv)

    load_dotenv()
    try:
        agent = build_agent()
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 1

    history: list = []

    def safe_ask(question: str):
        """Ask, but turn connection/API problems into a readable message."""
        before = len(history)
        try:
            return ask(agent, history, question, show_steps=not args.quiet)
        except Exception as exc:  # e.g. Ollama not running, invalid API key
            del history[before:]  # forget the failed turn
            print(f"Error talking to the model: {exc}", file=sys.stderr)
            if os.getenv("LLM_PROVIDER", "ollama").lower() == "ollama":
                model = os.getenv("OLLAMA_MODEL", "qwen3:8b")
                if "not found" in str(exc):
                    hint = f"Download the model first: ollama pull {model}"
                else:
                    hint = "Is Ollama running? Start it with: ollama serve"
                print(hint, file=sys.stderr)
            return None

    if args.question:
        answer = safe_ask(" ".join(args.question))
        if answer is None:
            return 1
        print(for_terminal(answer))
        return 0

    print("🧮 AI Math Assistant. Ask me a math question (type 'exit' to quit).\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if question.lower() in {"exit", "quit", "salir"}:
            return 0
        if question:
            answer = safe_ask(question)
            if answer is not None:
                print(f"\nAssistant: {for_terminal(answer)}\n")


if __name__ == "__main__":
    sys.exit(main())
