"""
Compatibility alias package for tests expecting `modules.*` imports.
Exposes MemoryMCPServer from `app.core.knowledge_graph_memory`.
"""
from app.core.knowledge_graph_memory import MemoryMCPServer

__all__ = ["MemoryMCPServer"]
