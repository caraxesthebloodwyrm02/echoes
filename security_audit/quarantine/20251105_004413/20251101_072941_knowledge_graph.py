#!/usr/bin/env python3
"""
Knowledge Graph System for EchoesAssistantV2
Enables meaningful communication through semantic relationships and memory
"""

import json
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph representing an entity or concept"""

    id: str
    type: str  # person, place, concept, event, document, etc.
    label: str
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    embeddings: Optional[List[float]] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    last_accessed: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    access_count: int = 0
    confidence: float = 1.0


@dataclass
class KnowledgeRelation:
    """A relationship between two knowledge nodes"""

    source_id: str
    target_id: str
    relation_type: str  # related_to, part_of, causes, enables, etc.
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    confidence: float = 1.0


@dataclass
class MemoryFragment:
    """A memory fragment with temporal and semantic information"""

    id: str
    content: str
    context: Dict[str, Any]
    entities: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    importance: float = 1.0
    decay_rate: float = 0.1  # How quickly this memory fades
    associated_nodes: List[str] = field(default_factory=list)


class KnowledgeGraph:
    """Advanced knowledge graph with memory integration for EchoesAssistantV2"""

    def __init__(self, storage_path: str = "knowledge_graph"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # NetworkX graph for structure
        self.graph = nx.MultiDiGraph()

        # In-memory indices
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.relations: List[KnowledgeRelation] = []
        self.memories: List[MemoryFragment] = []

        # Indices for fast lookup
        self.type_index: Dict[str, Set[str]] = defaultdict(set)
        self.label_index: Dict[str, Set[str]] = defaultdict(set)
        self.memory_index: Dict[str, Set[str]] = defaultdict(set)

        # Communication context
        self.conversation_history: deque = deque(maxlen=100)
        self.active_context: Dict[str, Any] = {}

        # Load existing data
        self._load_knowledge()

    def _load_knowledge(self):
        """Load existing knowledge graph from storage"""
        try:
            # Load nodes
            nodes_file = self.storage_path / "nodes.json"
            if nodes_file.exists():
                with open(nodes_file, "r", encoding="utf-8") as f:
                    nodes_data = json.load(f)
                    for node_data in nodes_data:
                        node = KnowledgeNode(**node_data)
                        self.nodes[node.id] = node
                        self.type_index[node.type].add(node.id)
                        self.label_index[node.label.lower()].add(node.id)
                        self.graph.add_node(node.id, **node.__dict__)

            # Load relations
            relations_file = self.storage_path / "relations.json"
            if relations_file.exists():
                with open(relations_file, "r", encoding="utf-8") as f:
                    relations_data = json.load(f)
                    for rel_data in relations_data:
                        relation = KnowledgeRelation(**rel_data)
                        self.relations.append(relation)
                        self.graph.add_edge(
                            relation.source_id,
                            relation.target_id,
                            relation_type=relation.relation_type,
                            weight=relation.weight,
                            **relation.properties,
                        )

            # Load memories
            memories_file = self.storage_path / "memories.json"
            if memories_file.exists():
                with open(memories_file, "r", encoding="utf-8") as f:
                    memories_data = json.load(f)
                    for mem_data in memories_data:
                        memory = MemoryFragment(**mem_data)
                        self.memories.append(memory)
                        for entity in memory.entities:
                            self.memory_index[entity].add(memory.id)

            print(
                f"✓ Knowledge graph loaded: {len(self.nodes)} nodes, {len(self.relations)} relations, {len(self.memories)} memories"
            )

        except Exception as e:
            print(f"Warning: Could not load knowledge graph: {e}")

    def _save_knowledge(self):
        """Save knowledge graph to storage"""
        try:
            # Save nodes
            nodes_file = self.storage_path / "nodes.json"
            with open(nodes_file, "w", encoding="utf-8") as f:
                nodes_data = [node.__dict__ for node in self.nodes.values()]
                json.dump(nodes_data, f, indent=2, ensure_ascii=False)

            # Save relations
            relations_file = self.storage_path / "relations.json"
            with open(relations_file, "w", encoding="utf-8") as f:
                relations_data = [rel.__dict__ for rel in self.relations]
                json.dump(relations_data, f, indent=2, ensure_ascii=False)

            # Save memories
            memories_file = self.storage_path / "memories.json"
            with open(memories_file, "w", encoding="utf-8") as f:
                memories_data = [mem.__dict__ for mem in self.memories]
                json.dump(memories_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"Warning: Could not save knowledge graph: {e}")

    def add_node(self, node: KnowledgeNode) -> str:
        """Add a node to the knowledge graph"""
        self.nodes[node.id] = node
        self.type_index[node.type].add(node.id)
        self.label_index[node.label.lower()].add(node.id)
        self.graph.add_node(node.id, **node.__dict__)
        self._save_knowledge()
        return node.id

    def add_relation(self, relation: KnowledgeRelation) -> str:
        """Add a relation between nodes"""
        self.relations.append(relation)
        self.graph.add_edge(
            relation.source_id,
            relation.target_id,
            relation_type=relation.relation_type,
            weight=relation.weight,
            **relation.properties,
        )
        self._save_knowledge()
        return f"{relation.source_id}->{relation.target_id}"

    def add_memory(self, memory: MemoryFragment) -> str:
        """Add a memory fragment"""
        self.memories.append(memory)
        for entity in memory.entities:
            self.memory_index[entity].add(memory.id)
        self._save_knowledge()
        return memory.id

    def find_nodes(
        self, query: str, node_type: Optional[str] = None, limit: int = 10
    ) -> List[KnowledgeNode]:
        """Find nodes by label or type"""
        results = []
        query_lower = query.lower()

        # Search by label
        for node_id in self.label_index.get(query_lower, set()):
            if node_id in self.nodes:
                results.append(self.nodes[node_id])

        # Fuzzy search in labels
        if len(results) < limit:
            for node_id, node in self.nodes.items():
                if query_lower in node.label.lower() and node not in results:
                    if node_type is None or node.type == node_type:
                        results.append(node)
                        if len(results) >= limit:
                            break

        return results[:limit]

    def get_related_nodes(
        self, node_id: str, relation_type: Optional[str] = None, max_depth: int = 2
    ) -> List[KnowledgeNode]:
        """Get nodes related to a given node"""
        if node_id not in self.nodes:
            return []

        related = set()
        to_visit = [(node_id, 0)]

        while to_visit:
            current_id, depth = to_visit.pop(0)
            if depth >= max_depth:
                continue

            # Get neighbors
            for neighbor in self.graph.neighbors(current_id):
                if neighbor not in related:
                    # Check relation type filter
                    edge_data = self.graph.get_edge_data(current_id, neighbor)
                    if edge_data:
                        for edge in edge_data.values():
                            if (
                                relation_type is None
                                or edge.get("relation_type") == relation_type
                            ):
                                related.add(neighbor)
                                if depth < max_depth - 1:
                                    to_visit.append((neighbor, depth + 1))
                                break

        return [self.nodes[nid] for nid in related if nid in self.nodes]

    def retrieve_memories(
        self, query: str, context: Optional[Dict] = None, limit: int = 5
    ) -> List[MemoryFragment]:
        """Retrieve relevant memories based on query and context"""
        query_lower = query.lower()
        scored_memories = []

        for memory in self.memories:
            score = 0.0

            # Text matching
            if query_lower in memory.content.lower():
                score += 2.0

            # Entity matching
            for entity in memory.entities:
                if query_lower in entity.lower():
                    score += 1.5

            # Concept matching
            for concept in memory.concepts:
                if query_lower in concept.lower():
                    score += 1.0

            # Context matching
            if context:
                for key, value in context.items():
                    if key in memory.context and memory.context[key] == value:
                        score += 0.5

            # Time decay (recent memories are more relevant)
            days_old = (
                datetime.now(timezone.utc)
                - datetime.fromisoformat(memory.timestamp.replace("Z", "+00:00"))
            ).days
            decay_factor = max(0.1, 1.0 - (days_old * memory.decay_rate / 100))
            score *= decay_factor

            # Importance weighting
            score *= memory.importance

            if score > 0:
                scored_memories.append((memory, score))

        # Sort by score and return top results
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        return [mem for mem, score in scored_memories[:limit]]

    def update_conversation_context(
        self, message: str, response: str, entities: List[str] = None
    ):
        """Update conversation context for meaningful communication"""
        context_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "message": message,
            "response": response,
            "entities": entities or [],
            "message_length": len(message),
            "response_length": len(response),
        }

        self.conversation_history.append(context_entry)

        # Update active context
        self.active_context.update(
            {
                "last_message": message,
                "last_response": response,
                "recent_entities": entities or [],
                "conversation_turns": len(self.conversation_history),
            }
        )

    def get_communication_context(self, query: str) -> Dict[str, Any]:
        """Get rich context for meaningful communication"""
        # Find relevant entities in query
        entities = self.find_nodes(query, limit=5)
        entity_names = [node.label for node in entities]

        # Retrieve relevant memories
        memories = self.retrieve_memories(query, limit=3)

        # Get conversation history
        recent_history = list(self.conversation_history)[-3:]

        # Find related concepts
        related_concepts = []
        for entity in entities:
            related = self.get_related_nodes(
                entity.id, relation_type="related_to", max_depth=1
            )
            related_concepts.extend([node.label for node in related[:3]])

        return {
            "entities": entity_names,
            "memories": [
                {"content": mem.content, "importance": mem.importance}
                for mem in memories
            ],
            "conversation_history": recent_history,
            "related_concepts": list(set(related_concepts))[:5],
            "active_context": self.active_context,
            "knowledge_graph_stats": {
                "nodes": len(self.nodes),
                "relations": len(self.relations),
                "memories": len(self.memories),
            },
        }

    def extract_entities_and_concepts(self, text: str) -> Tuple[List[str], List[str]]:
        """Extract entities and concepts from text (simplified version)"""
        # This is a simplified implementation
        # In production, you'd use NLP libraries like spaCy or transformers

        entities = []
        concepts = []

        # Simple keyword-based extraction
        known_entities = set(node.label.lower() for node in self.nodes.values())
        words = text.lower().split()

        for i in range(len(words)):
            # Check single words
            if words[i] in known_entities:
                entities.append(words[i])

            # Check multi-word phrases
            if i < len(words) - 1:
                phrase = f"{words[i]} {words[i+1]}"
                if phrase in known_entities:
                    entities.append(phrase)

        # Extract concepts (simplified - look for capitalized terms)
        import re

        concepts = re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b", text)

        return list(set(entities)), list(set(concepts))

    def learn_from_conversation(
        self, message: str, response: str, confidence: float = 0.8
    ):
        """Learn and extract knowledge from conversations"""
        entities, concepts = self.extract_entities_and_concepts(
            message + " " + response
        )

        # Create memory fragment
        memory = MemoryFragment(
            id=f"mem_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}",
            content=message,
            context={
                "response": response,
                "confidence": confidence,
                "entities": entities,
                "concepts": concepts,
            },
            entities=entities,
            concepts=concepts,
            importance=confidence,
        )

        self.add_memory(memory)

        # Update conversation context
        self.update_conversation_context(message, response, entities)

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        return {
            "nodes": len(self.nodes),
            "relations": len(self.relations),
            "memories": len(self.memories),
            "node_types": dict(Counter(node.type for node in self.nodes.values())),
            "conversation_turns": len(self.conversation_history),
            "last_updated": datetime.now(timezone.utc).isoformat(),
        }


# Global knowledge graph instance
_knowledge_graph = None


def get_knowledge_graph() -> KnowledgeGraph:
    """Get or create the global knowledge graph instance"""
    global _knowledge_graph
    if _knowledge_graph is None:
        _knowledge_graph = KnowledgeGraph()
    return _knowledge_graph


# Import Counter for stats
from collections import Counter
