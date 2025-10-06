"""
Compatibility shim so tests can import `modules.knowledge_graph_memory`.
Re-exports MemoryMCPServer from app.core.knowledge_graph_memory.
"""
from app.core.knowledge_graph_memory import MemoryMCPServer

__all__ = ["MemoryMCPServer"]
