import logging
from pathlib import Path

from app.mcp.client import MCPClient

logger = logging.getLogger(__name__)


class MCPManager:
    def __init__(self) -> None:
        server_path = Path(__file__).resolve().parents[3] / "mcp-server" / "server.py"
        self.client = MCPClient(server_path)

    async def startup(self) -> None:
        await self.client.connect()

    async def shutdown(self) -> None:
        await self.client.close()

    @property
    def connected(self) -> bool:
        return self.client.connected

    @property
    def tools(self) -> list[dict]:
        return self.client.tool_infos()

    async def call(self, name: str, arguments: dict) -> dict:
        return await self.client.call_tool(name, arguments)
