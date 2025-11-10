"""
Tools module - backward compatibility layer.

This module provides backward compatibility for tools.
"""

# Use fallback implementation directly to avoid scipy import issues
import threading


class ToolRegistry:
    """Thread-safe tool registry with required methods."""

    def __init__(self):
        self._registry = {}
        self._lock = threading.Lock()

    def register_tool(self, name, desc, func):
        """Register a tool with the registry."""
        with self._lock:
            self._registry[name] = {"description": desc, "func": func}

    def get_tool(self, name):
        """Get a tool by name."""
        with self._lock:
            return self._registry.get(name)

    def get(self, name):
        """Get a tool by name (alias for get_tool)."""
        return self.get_tool(name)

    def has_tool(self, name):
        """Check if a tool is registered."""
        with self._lock:
            return name in self._registry

    def list_tools(self):
        """List all registered tool names."""
        with self._lock:
            return list(self._registry.keys())

    def execute_tool(self, name, payload):
        """Execute a registered tool."""
        tool = self.get_tool(name)
        if not tool:
            raise KeyError(f"Tool '{name}' not found")
        return tool["func"](payload)

    def get_openai_schemas(self):
        """Get OpenAI function schemas for all registered tools."""
        schemas = []
        with self._lock:
            for name, info in self._registry.items():
                try:
                    # Create proper OpenAI function schema with explicit parameters
                    schema = {
                        "type": "function",
                        "function": {
                            "name": name,
                            "description": info.get("description", ""),
                            "parameters": self._get_tool_parameters(name),
                        },
                    }
                    schemas.append(schema)
                except Exception as e:
                    # Skip tools that cause schema generation issues
                    print(f"Warning: Could not generate schema for tool '{name}': {e}")
                    continue
        return schemas

    def _get_tool_parameters(self, tool_name):
        """Get JSON Schema parameters for a specific tool."""
        # Define explicit parameter schemas for known tools
        tool_schemas = {
            "reverse_text": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to reverse"}
                },
                "required": ["text"],
            },
            "echo": {
                "type": "object",
                "properties": {
                    "input": {"type": "string", "description": "The input to echo back"}
                },
                "required": ["input"],
            },
            "list_directory": {
                "type": "object",
                "properties": {
                    "dirpath": {
                        "type": "string",
                        "description": "Directory path to list",
                    },
                    "pattern": {
                        "type": "string",
                        "description": "File pattern to match (default: *)",
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to list recursively (default: false)",
                    },
                },
                "required": ["dirpath"],
            },
            "read_file": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to read",
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                    },
                    "max_size": {
                        "type": "integer",
                        "description": "Maximum file size in bytes (default: 1048576)",
                    },
                },
                "required": ["filepath"],
            },
            "search_files": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Search pattern for files",
                    },
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in (default: current)",
                    },
                },
                "required": ["pattern"],
            },
            "get_file_info": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Path to the file to get info for",
                    }
                },
                "required": ["filepath"],
            },
        }

        # Return the specific schema if we have it, otherwise a generic one
        return tool_schemas.get(
            tool_name,
            {
                "type": "object",
                "properties": {
                    "args": {"type": "string", "description": "Tool arguments"}
                },
                "required": [],
            },
        )


# Global registry instance
_global_registry = ToolRegistry()


def get_registry():
    """Get the global tool registry instance."""
    return _global_registry


def register_tool(name, desc, func):
    """Register a tool with the global registry."""
    _global_registry.register_tool(name, desc, func)


def get_tool(name):
    """Get a tool from the global registry."""
    return _global_registry.get_tool(name)


def execute_tool(name, payload):
    """Execute a tool from the global registry."""
    return _global_registry.execute_tool(name, payload)


__all__ = ["get_registry", "ToolRegistry", "register_tool", "get_tool", "execute_tool"]
