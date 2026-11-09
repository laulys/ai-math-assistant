"""Builds the math agent: an LLM + tools + instructions, wired by LangChain's `create_agent`."""

from __future__ import annotations

from langchain.agents import create_agent

from .llm import get_llm
from .tools import ALL_TOOLS

SYSTEM_PROMPT = """You are a careful math assistant.

- Never do arithmetic in your head. Always use the math tools, one operation
  at a time, and feed each result into the next step.
- If a question needs real-world data (a population, a height, a date...),
  look it up with search_wikipedia first, then calculate with the math tools.
- If a tool returns an error, explain the problem to the user in plain words.
- End with a short explanation of the steps and the final answer.
- Reply in the same language the user writes in."""


def build_agent(llm=None, tools=None):
    """Create the agent. Pass `llm`/`tools` to override the defaults (useful in tests)."""
    return create_agent(
        model=llm if llm is not None else get_llm(),
        tools=tools if tools is not None else ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )
