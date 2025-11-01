"""
Tool Registry for managing and discovering tools.

Implements:
- Centralized tool management
- Tool discovery
- Version control
- Security validation
"""

import logging
from typing import Dict, List, Optional, Any
from .base import BaseTool, ToolResult, ToolError

logger = logging.getLogger(__name__)


class ToolRegistry:
    """
    Central registry for managing tools.

    Features:
    - Register/unregister tools
    - Tool discovery
    - Access control
    - Statistics tracking
    """

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: Dict[str, BaseTool] = {}
        self._tool_categories: Dict[str, List[str]] = {}
        self._access_control: Dict[str, List[str]] = {}  # tool_name: [allowed_roles]

    def register(
        self,
        tool: BaseTool,
        category: str = "general",
        allowed_roles: Optional[List[str]] = None,
    ) -> None:
        """
        Register a tool in the registry.

        Args:
            tool: Tool instance to register
            category: Category for organization
            allowed_roles: List of roles that can use this tool (None = all)

        Raises:
            ToolError: If tool name already exists
        """
        if tool.name in self._tools:
            raise ToolError(f"Tool '{tool.name}' already registered", tool_name=tool.name)

        self._tools[tool.name] = tool

        # Add to category
        if category not in self._tool_categories:
            self._tool_categories[category] = []
        self._tool_categories[category].append(tool.name)

        # Set access control
        if allowed_roles:
            self._access_control[tool.name] = allowed_roles

        logger.info(f"Registered tool: {tool.name} in category: {category}")

    def unregister(self, tool_name: str) -> None:
        """
        Unregister a tool.

        Args:
            tool_name: Name of tool to unregister
        """
        if tool_name in self._tools:
            del self._tools[tool_name]

            # Remove from categories
            for category, tools in self._tool_categories.items():
                if tool_name in tools:
                    tools.remove(tool_name)

            # Remove access control
            if tool_name in self._access_control:
                del self._access_control[tool_name]

            logger.info(f"Unregistered tool: {tool_name}")

    def get(self, tool_name: str) -> Optional[BaseTool]:
        """
        Get a tool by name.

        Args:
            tool_name: Name of the tool

        Returns:
            BaseTool instance or None
        """
        return self._tools.get(tool_name)

    def has_tool(self, tool_name: str) -> bool:
        """
        Check if a tool exists in the registry.

        Args:
            tool_name: Name of the tool

        Returns:
            True if tool exists, False otherwise
        """
        return tool_name in self._tools

    def list_tools(self, category: Optional[str] = None) -> List[str]:
        """
        List all tools or tools in a category.

        Args:
            category: Optional category filter

        Returns:
            List of tool names
        """
        if category:
            return self._tool_categories.get(category, [])
        return list(self._tools.keys())

    def list_categories(self) -> List[str]:
        """Get list of all categories."""
        return list(self._tool_categories.keys())

    def execute(self, tool_name: str, user_role: Optional[str] = None, **kwargs) -> ToolResult:
        """
        Execute a tool with access control.

        Args:
            tool_name: Name of tool to execute
            user_role: Role of the user executing the tool
            **kwargs: Tool parameters

        Returns:
            ToolResult: Execution result
        """
        tool = self.get(tool_name)
        if not tool:
            return ToolResult(success=False, data=None, error=f"Tool '{tool_name}' not found")

        # Check access control
        if tool_name in self._access_control:
            allowed_roles = self._access_control[tool_name]
            if user_role not in allowed_roles:
                return ToolResult(
                    success=False,
                    data=None,
                    error=f"Access denied. Required roles: {allowed_roles}",
                )

        # Execute the tool
        return tool(**kwargs)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "total_tools": len(self._tools),
            "categories": {cat: len(tools) for cat, tools in self._tool_categories.items()},
            "tool_stats": {name: tool.get_stats() for name, tool in self._tools.items()},
        }

    def get_openai_schemas(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get OpenAI function calling schemas for registered tools.

        Args:
            category: Optional category filter

        Returns:
            List of OpenAI function schemas
        """
        tools_to_export = self.list_tools(category) if category else self.list_tools()

        schemas = []
        for tool_name in tools_to_export:
            tool = self.get(tool_name)
            if tool:
                schemas.append(tool.to_openai_schema())

        return schemas

    def search_tools(self, query: str) -> List[str]:
        """
        Search tools by name or description.

        Args:
            query: Search query

        Returns:
            List of matching tool names
        """
        query_lower = query.lower()
        matches = []

        for name, tool in self._tools.items():
            if query_lower in name.lower() or query_lower in tool.description.lower():
                matches.append(name)

        return matches


# Global registry instance
_global_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get the global tool registry."""
    return _global_registry
