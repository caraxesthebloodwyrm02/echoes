# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import threading
from typing import Any, Callable, Dict

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
