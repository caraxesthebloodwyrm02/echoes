"""
Tools Package

This package contains all the tools available in the Echoes Assistant.
"""

import os
import sys
import importlib

# Add project root to path for consistent imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    _m = importlib.import_module("core.ethos")
    getattr(_m, "enforce")()
except Exception:
    pass

# Import tool modules to make them available when importing from tools
try:
    from .base import BaseTool, ToolResult, ToolError
except ImportError:
    from tools.base import BaseTool, ToolResult, ToolError

try:
    from .examples import get_example_tools
except ImportError:
    from tools.examples import get_example_tools

try:
    from .business_tools import get_business_tools
except (ImportError, ModuleNotFoundError):
    # business_tools module not available
    def get_business_tools():
        return []


# Make these available when importing from tools
__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolError",
    "get_example_tools",
    "get_business_tools",
]
