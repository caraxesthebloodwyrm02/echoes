"""
Base classes and types for the tool system.

Provides:
- BaseTool: Abstract base class for all tools
- ToolResult: Container for tool execution results
- ToolError: Exception for tool-related errors
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class ToolError(Exception):
    """Exception raised for tool-related errors."""

    def __init__(self, message: str, tool_name: Optional[str] = None):
        super().__init__(message)
        self.tool_name = tool_name


class ToolResult:
    """Container for tool execution results."""

    def __init__(
        self,
        success: bool,
        data: Any = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.data = data
        self.error = error

    def __repr__(self) -> str:
        status = "success" if self.success else "failed"
        return f"ToolResult({status})"


class BaseTool(ABC):
    """Abstract base class for all tools."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def __call__(self, **kwargs: Any) -> ToolResult:
        """Execute the tool with given parameters."""
        ...

    @abstractmethod
    def to_openai_schema(self) -> Dict[str, Any]:
        """Convert tool to OpenAI function calling schema."""
        ...

    def get_stats(self) -> Dict[str, Any]:
        """Get tool statistics."""
        return {
            "name": self.name,
            "description": self.description,
        }
