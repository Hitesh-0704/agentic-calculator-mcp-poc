"""Regression tests for:

1. The number-formatting bug: `_format_result` used Python's `:g` format,
   which silently switches to scientific notation for large numbers
   (e.g. 1_000_000.0 -> "1e+06"). Fixed to always use comma-grouped,
   non-scientific notation.
2. The CalculatorService's handling of divide-by-zero (must stay a clean
   200 response, never a 502) and of multi-calculation input (must be
   rejected up front with a clean message, never reach Gemini/fallback).
"""

import pytest

from app.agent.gemini_client import GeminiAgent
from app.mcp.manager import MCPManager
from app.services.calculator_service import CalculatorService


def test_format_number_no_scientific_notation_for_large_numbers():
    assert GeminiAgent._format_number(1_000_000.0) == "1,000,000"
    assert GeminiAgent._format_number(2_000_000.0) == "2,000,000"


def test_format_number_whole_numbers_have_no_decimal():
    assert GeminiAgent._format_number(48.0) == "48"


def test_format_number_decimals_are_trimmed():
    assert GeminiAgent._format_number(151.0) == "151"
    assert GeminiAgent._format_number(0.30000000000000004) == "0.3"


def test_format_result_consistent_across_sizes():
    small = GeminiAgent._format_result(
        "add", {"a": 10.0, "b": 20.0}, {"result": 30.0}
    )
    large = GeminiAgent._format_result(
        "add", {"a": 1_000_000.0, "b": 2_000_000.0}, {"result": 3_000_000.0}
    )
    assert small == "10 + 20 = 30"
    assert large == "1,000,000 + 2,000,000 = 3,000,000"


class _NoGeminiAgent(GeminiAgent):
    """A GeminiAgent stand-in that always behaves as if Gemini is
    unavailable, forcing CalculatorService onto the fallback parser path.
    """

    def __init__(self):
        super().__init__(api_key="", model="unused")


@pytest.mark.asyncio
async def test_divide_by_zero_is_clean_not_502():
    mcp = MCPManager()
    await mcp.startup()
    try:
        service = CalculatorService(mcp, _NoGeminiAgent())
        response = await service.chat("10 / 0")
        assert "divide by zero" in response.response.lower()
        assert response.pipeline.result is None
    finally:
        await mcp.shutdown()


@pytest.mark.asyncio
async def test_symbolic_expression_works_without_gemini():
    mcp = MCPManager()
    await mcp.startup()
    try:
        service = CalculatorService(mcp, _NoGeminiAgent())
        response = await service.chat("2 + 5")
        assert response.pipeline.result == 7.0
        assert "7" in response.response
    finally:
        await mcp.shutdown()


@pytest.mark.asyncio
async def test_multiple_calculations_rejected_up_front():
    mcp = MCPManager()
    await mcp.startup()
    try:
        service = CalculatorService(mcp, _NoGeminiAgent())
        response = await service.chat("10 + 20 10 - 5 10 * 5 100 / 5")
        assert response.pipeline.intent == "unsupported"
        assert "one calculation at a time" in response.response.lower()
    finally:
        await mcp.shutdown()
