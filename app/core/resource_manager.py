from typing import List

from .mcp_client import MCPClient


class ResourceManager:
    """Manages MCP resources."""

    def __init__(self, mcp_client: MCPClient):
        self.client = mcp_client

    async def discover_resources(self) -> List[dict]:
        """Discover available resources from all servers."""
        resources = []
        for server in self.client.servers:
            server_resources = await self.client.list_resources(server)
            resources.extend(server_resources)
        return resources

    async def access_resource(self, uri: str) -> str:
        """Access a resource by URI."""
        return await self.client.read_resource(uri)
