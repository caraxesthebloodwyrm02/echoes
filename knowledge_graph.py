"""
Knowledge Graph module - Mock implementation for assistant functionality.

Provides a simple knowledge graph implementation for the Echoes assistant.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class KnowledgeNode:
    """Represents a node in the knowledge graph."""

    id: str
    type: str
    properties: Dict[str, Any]
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class KnowledgeRelation:
    """Represents a relation between knowledge nodes."""

    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any] = None

    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class MemoryFragment:
    """Represents a fragment of memory in the knowledge graph."""

    id: str
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SimpleKnowledgeGraph:
    """Simple in-memory knowledge graph implementation."""

    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.relations: List[KnowledgeRelation] = []
        self.fragments: Dict[str, MemoryFragment] = {}

    def add_node(self, node: KnowledgeNode):
        """Add a node to the graph."""
        self.nodes[node.id] = node

    def add_relation(self, relation: KnowledgeRelation):
        """Add a relation to the graph."""
        self.relations.append(relation)

    def add_fragment(self, fragment: MemoryFragment):
        """Add a memory fragment."""
        self.fragments[fragment.id] = fragment

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        """Get a node by ID."""
        return self.nodes.get(node_id)

    def query(self, query: str) -> List[KnowledgeNode]:
        """Simple query implementation."""
        # Basic text search in node properties
        results = []
        query_lower = query.lower()
        for node in self.nodes.values():
            for value in node.properties.values():
                if isinstance(value, str) and query_lower in value.lower():
                    results.append(node)
                    break
        return results

    def get_statistics(self) -> Dict[str, int]:
        """Get graph statistics."""
        return {
            "nodes": len(self.nodes),
            "relations": len(self.relations),
            "fragments": len(self.fragments),
        }


# Global instance
_graph = SimpleKnowledgeGraph()


def get_knowledge_graph() -> SimpleKnowledgeGraph:
    """Get the global knowledge graph instance."""
    return _graph


# Export symbols for backward compatibility
__all__ = [
    "get_knowledge_graph",
    "KnowledgeNode",
    "KnowledgeRelation",
    "MemoryFragment",
    "SimpleKnowledgeGraph",
]
