"""End-to-end test of the agent loop with a scripted fake model (no API key needed).

The fake model plays the LLM's part: it asks for the `add` tool, then the
`multiply` tool, then answers. This checks that the tools, `create_agent`
and the CLI's message handling all fit together.
"""

import json

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolMessage

from math_assistant.__main__ import ask
from math_assistant.agent import build_agent
from math_assistant.tools import ALL_TOOLS, MATH_TOOLS


class ScriptedToolModel(GenericFakeChatModel):
    """A fake chat model that supports `bind_tools` and replies from a script."""

    def bind_tools(self, tools, **kwargs):
        return self


def tool_call(name, args, call_id):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


def test_agent_chains_two_tools(capsys):
    model = ScriptedToolModel(
        messages=iter(
            [
                tool_call("add", {"numbers": [25, 15]}, "call_1"),
                tool_call("multiply", {"numbers": [40, 2]}, "call_2"),
                AIMessage(content="25 + 15 = 40, and 40 × 2 = 80. The answer is 80."),
            ]
        )
    )
    agent = build_agent(llm=model)
    history = []

    answer = ask(agent, history, "Add 25 and 15, then multiply by 2")

    assert answer.endswith("The answer is 80.")
    tool_results = [json.loads(m.content) for m in history if isinstance(m, ToolMessage)]
    assert tool_results == [{"result": 40}, {"result": 80}]

    printed = capsys.readouterr().out
    assert "add(numbers=[25, 15])" in printed
    assert "multiply(numbers=[40, 2])" in printed


def test_tool_schemas_are_what_the_llm_sees():
    names = [t.name for t in ALL_TOOLS]
    assert names == ["add", "subtract", "multiply", "divide", "power", "search_wikipedia"]
    for t in MATH_TOOLS:
        assert t.description, f"{t.name} needs a docstring: the LLM reads it"
    assert set(ALL_TOOLS[4].args) == {"base", "exponent"}


def test_tools_return_errors_the_llm_can_read():
    divide = MATH_TOOLS[3]
    assert divide.invoke({"numbers": [10, 0]}) == {"error": "Cannot divide by zero."}
