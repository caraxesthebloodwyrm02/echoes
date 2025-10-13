# removed unused imports pytest, MCPClient
from app.core.tool_registry import ToolRegistry


def test_tool_registry():
    registry = ToolRegistry()
    tool = {"name": "test_tool", "description": "A test tool"}
    registry.register_tool(tool)
    assert registry.get_tool("test_tool") == tool


# Add more MCP-related tests
