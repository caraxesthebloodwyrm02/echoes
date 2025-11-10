"""
Tools examples module.

This module provides example tools for the registry.
"""

import os
from typing import Any


def reverse_text_tool(payload: dict) -> dict[str, Any]:
    """Example tool that reverses text."""
    txt = payload.get("text", "")
    return {"reversed_text": txt[::-1]}


def echo_tool(payload: dict) -> dict[str, Any]:
    """Example tool that echoes back the input."""
    input_text = payload.get("input", "")
    return {"echo": input_text}


# Filesystem tools for interacting with the codebase
def list_directory_tool(payload: dict) -> dict[str, Any]:
    """List directory contents safely."""
    try:
        # Lazy import to avoid issues during module loading
        import sys

        sys.path.insert(0, "e:/Projects/Echoes")
        from app.filesystem import FilesystemTools

        fs_tools = FilesystemTools(root_dir=os.getcwd())
        dirpath = payload.get("dirpath", ".")
        pattern = payload.get("pattern", "*")
        recursive = payload.get("recursive", False)
        return fs_tools.list_directory(dirpath, pattern, recursive)
    except Exception as e:
        return {"success": False, "error": str(e)}


def read_file_tool(payload: dict) -> dict[str, Any]:
    """Read file contents safely."""
    try:
        # Lazy import to avoid issues during module loading
        import sys

        sys.path.insert(0, "e:/Projects/Echoes")
        from app.filesystem import FilesystemTools

        fs_tools = FilesystemTools(root_dir=os.getcwd())
        filepath = payload.get("filepath", "")
        encoding = payload.get("encoding", "utf-8")
        max_size = payload.get("max_size", 1024 * 1024)  # 1MB default
        return fs_tools.read_file(filepath, encoding, max_size)
    except Exception as e:
        return {"success": False, "error": str(e)}


def search_files_tool(payload: dict) -> dict[str, Any]:
    """Search for files by name or content."""
    try:
        # Lazy import to avoid issues during module loading
        import sys

        sys.path.insert(0, "e:/Projects/Echoes")
        from app.filesystem import FilesystemTools

        fs_tools = FilesystemTools(root_dir=os.getcwd())
        query = payload.get("query", "")
        search_path = payload.get("search_path")
        file_pattern = payload.get("file_pattern", "*")
        max_results = payload.get("max_results", 50)
        return fs_tools.search_files(query, search_path, file_pattern, max_results)
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_file_info_tool(payload: dict) -> dict[str, Any]:
    """Get file metadata."""
    try:
        # Lazy import to avoid issues during module loading
        import sys

        sys.path.insert(0, "e:/Projects/Echoes")
        from app.filesystem import FilesystemTools

        fs_tools = FilesystemTools(root_dir=os.getcwd())
        filepath = payload.get("filepath", "")
        return fs_tools.get_file_info(filepath)
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_example_tools():
    """Get a list of example tools to register."""
    return [
        ("reverse_text", "Reverse text string", reverse_text_tool),
        ("echo", "Echo back input", echo_tool),
        ("list_directory", "List directory contents safely", list_directory_tool),
        ("read_file", "Read file contents safely", read_file_tool),
        ("search_files", "Search for files by name", search_files_tool),
        ("get_file_info", "Get file metadata and information", get_file_info_tool),
    ]


# Auto-register example tools when imported
def _register_examples():
    """Register example tools with the global registry."""
    try:
        # Use absolute import instead of relative import
        from tools import register_tool

        for name, desc, func in get_example_tools():
            register_tool(name, desc, func)
    except ImportError as e:
        print(f"Warning: Could not register example tools: {e}")
    except Exception as e:
        print(f"Warning: Error registering example tools: {e}")


# Register examples on import
_register_examples()

__all__ = ["get_example_tools", "reverse_text_tool", "echo_tool"]
