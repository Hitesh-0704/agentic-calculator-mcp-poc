import asyncio
import logging
import sys
from contextlib import AsyncExitStack
from pathlib import Path
from typing import Any

from mcp import Client, StdioServerParameters

logger = logging.getLogger(__name__)


class MCPClient:
    """Persistent MCP v2 client for the calculator server over STDIO."""

    def __init__(self, server_path: Path):
        self.server_path = server_path
        self._stack: AsyncExitStack | None = None
        self._client: Client | None = None
        self.tools: dict[str, Any] = {}
        self.connected = False

    async def connect(self) -> None:
        if self.connected:
            return

        logger.info("MCP client starting")
        self._stack = AsyncExitStack()
        await self._stack.__aenter__()

        params = StdioServerParameters(
            command=sys.executable,
            args=[str(self.server_path)],
        )

        logger.info("Connecting to calculator MCP server")
        self._client = Client(params)
        await self._stack.enter_async_context(self._client)

        listed = await self._client.list_tools()
        self.tools = {tool.name: tool for tool in listed.tools}
        self.connected = True

        logger.info("MCP connection established")
        logger.info("Discovered %d MCP tools", len(self.tools))
        for name in self.tools:
            logger.info("Discovered MCP tool: %s", name)

    async def close(self) -> None:
        self.connected = False
        self.tools = {}
        if self._stack:
            await self._stack.aclose()
            self._stack = None
            self._client = None

    def tool_infos(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description or "",
                "input_schema": getattr(tool, "input_schema", {}) or {},
            }
            for tool in self.tools.values()
        ]

    def get_tool(self, name: str) -> Any | None:
        return self.tools.get(name)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if not self.connected or self._client is None:
            raise RuntimeError("MCP client is not connected.")

        if name not in self.tools:
            raise RuntimeError(f"Unknown MCP tool: {name}")

        logger.info("Invoking MCP tool: %s", name)
        result = await asyncio.wait_for(
            self._client.call_tool(name, arguments),
            timeout=10,
        )

        if result.is_error:
            text = self._extract_text(result)
            raise RuntimeError(text or "MCP tool returned an error.")

        structured = result.structured_content
        if isinstance(structured, dict) and structured:
            return structured

        return {"result": self._extract_text(result)}

    @staticmethod
    def _extract_text(result: Any) -> str:
        chunks: list[str] = []
        for item in getattr(result, "content", []) or []:
            text = getattr(item, "text", None)
            if text:
                chunks.append(text)
        return "\n".join(chunks)
