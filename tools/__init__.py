"""
Tools module - backward compatibility layer.

This module provides backward compatibility for tools.
All tool execution is routed through a single gate for allowlist, payload
validation, and audit logging.
"""

# Use fallback implementation directly to avoid scipy import issues
import hashlib
import json
import logging
import threading
from collections.abc import Callable
from typing import Any

# Single audit point for tool execution
_TOOL_GATE_LOGGER = logging.getLogger("echoes.tools.gate")

# Keys that must not appear in payload (injection risk)
_DANGEROUS_PAYLOAD_KEYS = frozenset(
    {"__import__", "eval", "exec", "compile", "open", "file", "input", "breakpoint"}
)


def _validate_payload(payload: Any) -> None:
    """Reject payloads that look like code injection. Raises ValueError on invalid."""
    if not isinstance(payload, dict):
        raise ValueError("Payload must be a dict")
    for key in payload:
        if isinstance(key, str) and key in _DANGEROUS_PAYLOAD_KEYS:
            raise ValueError(f"Payload key not allowed: {key!r}")


def safe_dispatch_tool(
    registry: "ToolRegistry",
    name: str,
    payload: dict[str, Any],
    actor: str | None = None,
) -> Any:
    """
    Single gate for tool execution: allowlist check, payload validation, audit log, then dispatch.
    Use this for all tool execution so unknown tools and invalid payloads are rejected and audited.
    """
    if not registry.has_tool(name):
        _TOOL_GATE_LOGGER.warning(
            "tool_gate_rejected unknown_tool name=%s actor=%s", name, actor or "unknown"
        )
        raise KeyError(f"Tool '{name}' not found")
    _validate_payload(payload)
    payload_hash = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()
    _TOOL_GATE_LOGGER.info(
        "tool_gate_dispatch actor=%s tool=%s payload_hash=%s",
        actor or "unknown",
        name,
        payload_hash,
    )
    try:
        tool = registry.get_tool(name)
        result = tool["func"](payload)
        _TOOL_GATE_LOGGER.info(
            "tool_gate_outcome actor=%s tool=%s outcome=success",
            actor or "unknown",
            name,
        )
        return result
    except Exception as e:
        _TOOL_GATE_LOGGER.warning(
            "tool_gate_outcome actor=%s tool=%s outcome=failure error=%s",
            actor or "unknown",
            name,
            str(e),
        )
        raise


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

    def execute_tool(self, name, payload, actor: str | None = None):
        """Execute a registered tool via the single tool gate (allowlist, validation, audit)."""
        if not isinstance(payload, dict):
            raise ValueError("Payload must be a dict")
        return safe_dispatch_tool(self, name, payload, actor=actor)

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


def execute_tool(name, payload, actor: str | None = None):
    """Execute a tool from the global registry via the tool gate."""
    return _global_registry.execute_tool(name, payload, actor=actor)


__all__ = [
    "get_registry",
    "ToolRegistry",
    "register_tool",
    "get_tool",
    "execute_tool",
    "safe_dispatch_tool",
]
