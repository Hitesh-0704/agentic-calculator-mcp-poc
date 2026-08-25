from mcp.server import MCPServer

mcp = MCPServer("calculator-mcp-server")

# BUG FIX: these tools were previously annotated `-> dict:` (a bare, untyped
# dict). This MCP SDK version (2.1.0) only auto-derives a structured-output
# schema for *parameterized* generic types like `dict[str, T]` — a bare
# `dict` gets NO schema, so `structured_content` came back as `None` on
# every call, and the tool's return value was instead serialized as a
# pretty-printed JSON *string* inside the unstructured text content.
#
# Downstream, `app/mcp/client.py` treats that string as the tool's
# `"result"` field, which is exactly why responses like
# `6.0 x 8.0 = { "operation": "multiply", "a": 6.0, "b": 8.0, "result": 48.0 }`
# were showing up: `value` in `_format_result` was that whole JSON string,
# not the number 48.0.
#
# Using `dict[str, float | str]` gives the SDK enough type information to
# populate `structured_content` correctly with the exact same flat shape
# (`{"operation": ..., "a": ..., "b": ..., "result": ...}`) that the rest
# of the backend already expects.

CalculationResult = dict[str, float | str]


@mcp.tool()
def add(a: float, b: float) -> CalculationResult:
    """Add two numbers and return the structured result."""
    return {"operation": "add", "a": a, "b": b, "result": a + b}


@mcp.tool()
def subtract(a: float, b: float) -> CalculationResult:
    """Subtract b from a and return the structured result."""
    return {"operation": "subtract", "a": a, "b": b, "result": a - b}


@mcp.tool()
def multiply(a: float, b: float) -> CalculationResult:
    """Multiply two numbers and return the structured result."""
    return {"operation": "multiply", "a": a, "b": b, "result": a * b}


@mcp.tool()
def divide(a: float, b: float) -> CalculationResult:
    """Divide a by b and return the structured result."""
    if b == 0:
        raise ValueError("I can't divide by zero.")
    return {"operation": "divide", "a": a, "b": b, "result": a / b}


if __name__ == "__main__":
    # STDIO is the transport used by the FastAPI host's MCP client.
    mcp.run()
