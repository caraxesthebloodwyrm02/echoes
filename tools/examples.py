"""
Example tools for demonstration purposes.

Provides sample implementations of tools that can be registered with the tool registry.
"""

from typing import Any, Dict, List
from .base import BaseTool, ToolResult


class CalculatorTool(BaseTool):
    """A simple calculator tool."""

    def __init__(self) -> None:
        super().__init__("calculator", "Perform basic arithmetic operations")

    def __call__(
        self, operation: str, a: float, b: float, **kwargs: Any
    ) -> ToolResult:
        """Execute calculator operation."""
        try:
            if operation == "add":
                result = a + b
            elif operation == "subtract":
                result = a - b
            elif operation == "multiply":
                result = a * b
            elif operation == "divide":
                if b == 0:
                    return ToolResult(success=False, error="Division by zero")
                result = a / b
            else:
                return ToolResult(
                    success=False, error=f"Unknown operation: {operation}"
                )

            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def to_openai_schema(self) -> Dict[str, Any]:
        """Return OpenAI function schema."""
        return {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Perform basic arithmetic operations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": ["add", "subtract", "multiply", "divide"],
                            "description": "The arithmetic operation to perform",
                        },
                        "a": {"type": "number", "description": "First number"},
                        "b": {
                            "type": "number",
                            "description": "Second number",
                        },
                    },
                    "required": ["operation", "a", "b"],
                },
            },
        }


class TextAnalyzerTool(BaseTool):
    """A tool for analyzing text."""

    def __init__(self) -> None:
        super().__init__("text_analyzer", "Analyze text for basic statistics")

    def __call__(self, text: str, **kwargs: Any) -> ToolResult:
        """Analyze text and return statistics."""
        try:
            word_count = len(text.split())
            char_count = len(text)
            sentence_count = len([s for s in text.split(".") if s.strip()])

            result = {
                "word_count": word_count,
                "character_count": char_count,
                "sentence_count": sentence_count,
                "average_word_length": (
                    char_count / word_count if word_count > 0 else 0
                ),
            }

            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    def to_openai_schema(self) -> Dict[str, Any]:
        """Return OpenAI function schema."""
        return {
            "type": "function",
            "function": {
                "name": "text_analyzer",
                "description": "Analyze text for basic statistics",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text to analyze",
                        }
                    },
                    "required": ["text"],
                },
            },
        }


def get_example_tools() -> List[BaseTool]:
    """
    Get a list of example tools for demonstration.

    Returns:
        List of example tool instances
    """
    return [
        CalculatorTool(),
        TextAnalyzerTool(),
    ]
