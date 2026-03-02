"""
Tools registry - backward compatibility layer.

This module provides backward compatibility by importing from core_modules.
"""

# Import from the tools package to avoid circular imports
try:
    from . import ToolRegistry, execute_tool, get_registry, get_tool, register_tool
except ImportError:
    # Fallback implementation
    import threading
    from collections.abc import Callable

    class ToolRegistry:
        """Thread-safe tool registry with required methods."""

        def __init__(self):
            self._registry = {}
            self._lock = threading.Lock()

        def register_tool(
            self, name: str, description: str, func: Callable[[dict], dict]
        ):
            """Register a tool with the registry."""
            with self._lock:
                self._registry[name] = {"description": description, "func": func}

        def get_tool(self, name: str):
            """Get a tool by name."""
            with self._lock:
                return self._registry.get(name)

        def get(self, name: str):
            """Get a tool by name (alias for get_tool)."""
            return self.get_tool(name)

        def has_tool(self, name: str) -> bool:
            """Check if a tool is registered."""
            with self._lock:
                return name in self._registry

        def list_tools(self) -> list[str]:
            """List all registered tool names."""
            with self._lock:
                return list(self._registry.keys())

        def execute_tool(self, name: str, payload: dict):
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
                    # Create a basic OpenAI function schema
                    schema = {
                        "type": "function",
                        "function": {
                            "name": name,
                            "description": info.get("description", ""),
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": [],
                            },
                        },
                    }
                    schemas.append(schema)
            return schemas

    _global_registry = ToolRegistry()

    def get_registry() -> ToolRegistry:
        """Get the global tool registry instance."""
        return _global_registry

    def register_tool(name: str, description: str, func):
        """Register a tool with the global registry."""
        _global_registry.register_tool(name, description, func)

    def get_tool(name: str):
        """Get a tool from the global registry."""
        return _global_registry.get_tool(name)

    def execute_tool(name: str, payload: dict):
        """Execute a tool from the global registry."""
        return _global_registry.execute_tool(name, payload)


__all__ = ["ToolRegistry", "get_registry", "register_tool", "get_tool", "execute_tool"]
