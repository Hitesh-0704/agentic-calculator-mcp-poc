import pytest
from mcp import Client

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "mcp-server"))

from server import mcp  # noqa: E402


@pytest.mark.asyncio
async def test_add():
    async with Client(mcp) as client:
        result = await client.call_tool("add", {"a": 3, "b": 4})
        # Regression check: structured_content must be a real dict (not
        # None) — see server.py for why the return-type annotation matters.
        assert result.structured_content is not None
        assert result.structured_content["result"] == 7


@pytest.mark.asyncio
async def test_multiply():
    async with Client(mcp) as client:
        result = await client.call_tool("multiply", {"a": 5, "b": 6})
        assert result.structured_content is not None
        assert result.structured_content["result"] == 30


@pytest.mark.asyncio
async def test_subtract_structured_content_is_a_dict_not_a_json_string():
    """Regression test for the JSON-leak bug: previously
    `structured_content` was None and the tool's result was only available
    as a pretty-printed JSON *string* inside the text content, which then
    leaked verbatim into user-facing responses.
    """
    async with Client(mcp) as client:
        result = await client.call_tool("subtract", {"a": 10, "b": 5})
        assert isinstance(result.structured_content, dict)
        assert result.structured_content == {
            "operation": "subtract",
            "a": 10.0,
            "b": 5.0,
            "result": 5.0,
        }


@pytest.mark.asyncio
async def test_divide_by_zero():
    async with Client(mcp) as client:
        result = await client.call_tool("divide", {"a": 10, "b": 0})
        assert result.is_error is True
