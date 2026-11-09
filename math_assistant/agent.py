"""Builds the math agent: an LLM + tools + instructions, wired by LangChain's `create_agent`."""

from __future__ import annotations

from langchain.agents import create_agent

from .llm import get_llm
from .tools import ALL_TOOLS

# Short, numbered, imperative rules work best with small local models: a softer
# version of this prompt let qwen3:8b skip the tools on 2 of 6 test questions.
SYSTEM_PROMPT = """You are a math assistant that MUST use tools for every calculation.

Rules:
1. For ANY arithmetic (even 2 + 2), call a tool. Never calculate in your head.
2. Do one operation at a time. Wait for the tool result before the next step.
3. If you need real-world data, call search_wikipedia first.
4. Only report numbers that a tool returned. If a tool returns an error, explain it.
5. Answer in the user's language, with a short explanation of the steps."""


def build_agent(llm=None, tools=None):
    """Create the agent. Pass `llm`/`tools` to override the defaults (useful in tests)."""
    return create_agent(
        model=llm if llm is not None else get_llm(),
        tools=tools if tools is not None else ALL_TOOLS,
        system_prompt=SYSTEM_PROMPT,
    )
