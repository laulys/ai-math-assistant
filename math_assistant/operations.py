"""Pure math operations behind the agent's tools.

This module has no LangChain dependency on purpose: the logic stays easy to
read and easy to test, and `tools.py` only wraps it for the agent.

Every function returns a dict:
    {"result": <number>}   when the operation succeeds
    {"error": "<message>"} when the input can't be used
Returning an error message (instead of raising) lets the LLM read what went
wrong and explain it to the user or retry with better input.
"""

from __future__ import annotations

import math
from typing import Dict, Optional, Sequence, Union

Number = Union[int, float]
Result = Dict[str, Union[Number, str]]


TOO_LARGE = "The result is too large to calculate."


def _finish(value: float) -> Result:
    """Wrap a computed value as a result, rounding away floating-point noise
    (0.1 + 0.2 -> 0.3) and showing whole numbers as ints (40.0 -> 40)."""
    if math.isinf(value) or math.isnan(value):
        return {"error": TOO_LARGE}
    value = float(f"{value:.12g}")  # keep 12 significant digits
    if value.is_integer() and abs(value) < 1e15:
        return {"result": int(value)}
    return {"result": value}


def _validate(numbers: Optional[Sequence[Number]], minimum: int) -> Optional[str]:
    """Return an error message if `numbers` isn't a usable list, otherwise None."""
    if numbers is None or len(numbers) < minimum:
        return f"Please provide at least {minimum} number(s)."
    for n in numbers:
        if isinstance(n, bool) or not isinstance(n, (int, float)):
            return f"Invalid number: {n!r}"
        if math.isnan(n) or math.isinf(n):
            return f"Invalid number: {n!r}"
    return None


def add(numbers: Sequence[Number]) -> Result:
    """Sum of all numbers: [10, 20, 30] -> 60."""
    error = _validate(numbers, minimum=1)
    if error:
        return {"error": error}
    try:
        return _finish(math.fsum(numbers))
    except OverflowError:
        return {"error": TOO_LARGE}


def subtract(numbers: Sequence[Number]) -> Result:
    """First number minus each of the following ones: [100, 20, 10] -> 70."""
    error = _validate(numbers, minimum=2)
    if error:
        return {"error": error}
    result = float(numbers[0])
    for n in numbers[1:]:
        result -= n
    return _finish(result)


def multiply(numbers: Sequence[Number]) -> Result:
    """Product of all numbers: [2, 3, 4] -> 24."""
    error = _validate(numbers, minimum=1)
    if error:
        return {"error": error}
    return _finish(float(math.prod(numbers)))


def divide(numbers: Sequence[Number]) -> Result:
    """First number divided by each of the following ones: [100, 5, 2] -> 10."""
    error = _validate(numbers, minimum=2)
    if error:
        return {"error": error}
    if any(n == 0 for n in numbers[1:]):
        return {"error": "Cannot divide by zero."}
    result = float(numbers[0])
    for n in numbers[1:]:
        result /= n
    return _finish(result)


def power(base: Number, exponent: Number) -> Result:
    """base raised to exponent: (5, 2) -> 25, (9, 0.5) -> 3."""
    error = _validate([base, exponent], minimum=2)
    if error:
        return {"error": error}
    base, exponent = float(base), float(exponent)
    if base == 0 and exponent < 0:
        return {"error": "Zero can't be raised to a negative power (it would divide by zero)."}
    if base < 0 and not exponent.is_integer():
        return {"error": "A negative number raised to a fractional power is not a real number."}
    try:
        return _finish(math.pow(base, exponent))
    except OverflowError:
        return {"error": TOO_LARGE}
