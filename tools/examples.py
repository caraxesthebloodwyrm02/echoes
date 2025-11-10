"""
Tools examples module.

This module provides example tools for the registry.
"""

from typing import Dict, Any


def reverse_text_tool(payload: dict) -> Dict[str, Any]:
    """Example tool that reverses text."""
    txt = payload.get("text", "")
    return {"result": txt[::-1]}


def echo_tool(payload: dict) -> Dict[str, Any]:
    """Example tool that echoes back the input."""
    return {"echo": payload}


def get_example_tools():
    """Get a list of example tools to register."""
    return [
        ("reverse_text", "Reverse text string", reverse_text_tool),
        ("echo", "Echo back input", echo_tool),
    ]


# Auto-register example tools when imported
def _register_examples():
    """Register example tools with the global registry."""
    try:
        from . import register_tool

        for name, desc, func in get_example_tools():
            register_tool(name, desc, func)
    except ImportError as e:
        print(f"Warning: Could not register example tools: {e}")


# Register examples on import
_register_examples()

__all__ = ["get_example_tools", "reverse_text_tool", "echo_tool"]
