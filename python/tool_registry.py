from typing import Callable, Dict, Any
import threading

# Very small in-memory registry; persistent registry can be added later.
_registry: Dict[str, Dict[str, Any]] = {}
_registry_lock = threading.Lock()

def register_tool(name: str, description: str, func: Callable[[dict], dict]):
    with _registry_lock:
        _registry[name] = {"description": description, "func": func}

def get_tool(name: str):
    with _registry_lock:
        return _registry.get(name)

def execute_tool(name: str, payload: dict):
    tool = get_tool(name)
    if not tool:
        raise KeyError("tool not found")
    # run tool (synchronous); for long-running tasks add queue + approval
    return tool["func"](payload)

# Example deterministic tool you can register from startup:
def reverse_text_tool(payload: dict):
    txt = payload.get("text", "")
    return {"result": txt[::-1]}
# Registration can be performed by python/service.py on startup:
# register_tool("reverse_text", "Deterministic reverse string", reverse_text_tool)
