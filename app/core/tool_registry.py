from typing import List


class ToolRegistry:
    """Registry of available MCP tools."""

    def __init__(self):
        self.tools = {}

    def register_tool(self, tool: dict):
        """Register a new MCP tool."""
        self.tools[tool["name"]] = tool

    def get_tool(self, name: str) -> dict:
        """Retrieve a tool by name."""
        return self.tools.get(name)

    def list_tools(self) -> List[dict]:
        """List all registered tools."""
        return list(self.tools.values())
