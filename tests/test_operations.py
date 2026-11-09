"""Tests for the pure math logic. No API key or network needed."""

import pytest

from math_assistant import operations as ops


@pytest.mark.parametrize(
    "func, numbers, expected",
    [
        (ops.add, [10, 20, 30], 60),
        (ops.add, [-10, -20, -30], -60),
        (ops.add, [0.1, 0.2], 0.3),
        (ops.subtract, [100, 20, 10], 70),
        (ops.subtract, [20, 50], -30),
        (ops.multiply, [2, 3, 4], 24),
        (ops.multiply, [3.5, 2], 7),
        (ops.multiply, [41288599, 0.75], 30966449.25),
        (ops.divide, [100, 5, 2], 10),
        (ops.divide, [25, 4], 6.25),
        (ops.divide, [1, 3], 0.333333333333),
    ],
)
def test_operations(func, numbers, expected):
    assert func(numbers) == {"result": expected}


def test_whole_numbers_are_returned_as_ints():
    assert isinstance(ops.add([1.0, 2.0])["result"], int)


def test_small_numbers_are_not_rounded_to_zero():
    assert ops.divide([1, 3e12])["result"] == pytest.approx(3.333333333e-13)


@pytest.mark.parametrize(
    "base, exponent, expected",
    [(5, 2, 25), (2, 10, 1024), (9, 0.5, 3), (2, -1, 0.5), (-2, 3, -8), (7, 0, 1)],
)
def test_power(base, exponent, expected):
    assert ops.power(base, exponent) == {"result": expected}


@pytest.mark.parametrize(
    "call",
    [
        lambda: ops.divide([10, 0]),
        lambda: ops.divide([10, 2, 0]),
        lambda: ops.power(0, -1),
        lambda: ops.power(-8, 0.5),
        lambda: ops.power(10, 1000),
        lambda: ops.multiply([1e300, 1e300]),
        lambda: ops.add([]),
        lambda: ops.subtract([5]),
        lambda: ops.add([1, "two"]),
        lambda: ops.add([1, float("nan")]),
        lambda: ops.add([True, 2]),
    ],
)
def test_bad_input_returns_an_error_instead_of_crashing(call):
    result = call()
    assert set(result) == {"error"}
    assert isinstance(result["error"], str)


def test_divide_by_zero_message():
    assert ops.divide([10, 0]) == {"error": "Cannot divide by zero."}
