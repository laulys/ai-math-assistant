"""LangChain tools the agent can call.

Each tool is a thin `@tool` wrapper around a function in `operations.py`.
The type hints become the JSON schema the LLM fills in, and the docstring is
the description the LLM reads to decide *when* to use the tool, so both are
written for the model as much as for humans.
"""

from __future__ import annotations

from typing import List

from langchain_core.tools import tool

from . import operations as ops
from . import wiki


@tool
def add(numbers: List[float]) -> dict:
    """Add numbers together and return their sum.

    Example: numbers=[25, 15] -> {"result": 40}
    """
    return ops.add(numbers)


@tool
def subtract(numbers: List[float]) -> dict:
    """Subtract numbers in order: the first number minus each of the following ones.

    Example: numbers=[100, 20, 10] -> {"result": 70}
    For "subtract 50 from 20" pass numbers=[20, 50].
    """
    return ops.subtract(numbers)


@tool
def multiply(numbers: List[float]) -> dict:
    """Multiply numbers together and return their product.

    Example: numbers=[2, 3, 4] -> {"result": 24}
    For percentages, use the decimal form: 75% of 80 -> numbers=[80, 0.75].
    """
    return ops.multiply(numbers)


@tool
def divide(numbers: List[float]) -> dict:
    """Divide numbers in order: the first number divided by each of the following ones.

    Example: numbers=[100, 5, 2] -> {"result": 10}
    Returns an error if any divisor is zero.
    """
    return ops.divide(numbers)


@tool
def power(base: float, exponent: float) -> dict:
    """Raise a base to an exponent (base^exponent).

    Examples: base=5, exponent=2 -> {"result": 25}
              base=9, exponent=0.5 -> {"result": 3}  (square root)
    """
    return ops.power(base, exponent)


@tool
def search_wikipedia(query: str) -> str:
    """Look up factual information on English Wikipedia (populations, heights, dates, ...).

    Returns the title and summary of the best-matching article. Use it to get
    real-world numbers before doing a calculation with the math tools.
    """
    return wiki.search(query)


MATH_TOOLS = [add, subtract, multiply, divide, power]
ALL_TOOLS = MATH_TOOLS + [search_wikipedia]
