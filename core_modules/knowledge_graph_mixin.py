"""Knowledge Graph & Meaningful Communication mixin for EchoesAssistantV2.

Extracted from assistant_v2_core.py (lines 3377–3726) as part of the
god-module decomposition.  All methods operate on ``self.knowledge_graph``
and ``self.enable_knowledge_graph`` which are initialised by the host class.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class KnowledgeGraphMixin:
    """Knowledge-graph CRUD, memory fragments, contextual communication and stats."""

    # -- Attribute stubs for type checkers (set by the host class) -----------
    enable_knowledge_graph: bool
    knowledge_graph: Any  # knowledge_graph.KnowledgeGraph instance

    # -- Public API ----------------------------------------------------------

    def add_knowledge_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        description: str = "",
        properties: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Add a knowledge node to the graph.

        Args:
            node_id: Unique identifier for the node
            node_type: Type of node (person, place, concept, event, etc.)
            label: Display label for the node
            description: Optional description
            properties: Additional properties

        Returns:
            Result with node creation status
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            from knowledge_graph import KnowledgeNode

            node = KnowledgeNode(
                id=node_id,
                type=node_type,
                label=label,
                description=description,
                properties=properties or {},
            )

            self.knowledge_graph.add_node(node)

            return {
                "success": True,
                "node_id": node_id,
                "message": f"Knowledge node '{label}' added successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_knowledge_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        weight: float = 1.0,
        properties: dict[str, Any] = None,
    ) -> dict[str, Any]:
        """Add a relationship between knowledge nodes.

        Args:
            source_id: ID of source node
            target_id: ID of target node
            relation_type: Type of relationship
            weight: Relationship strength (0-1)
            properties: Additional properties

        Returns:
            Result with relation creation status
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            from knowledge_graph import KnowledgeRelation

            relation = KnowledgeRelation(
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                weight=weight,
                properties=properties or {},
            )

            relation_id = self.knowledge_graph.add_relation(relation)

            return {
                "success": True,
                "relation_id": relation_id,
                "message": f"Relation '{relation_type}' added successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def add_memory_fragment(self, content: str, context: dict[str, Any], importance: float = 1.0) -> dict[str, Any]:
        """Add a memory fragment to the knowledge system.

        Args:
            content: Memory content
            context: Context information
            importance: Importance score (0-1)

        Returns:
            Result with memory creation status
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            from knowledge_graph import MemoryFragment

            # Extract entities and concepts from content
            entities, concepts = self.knowledge_graph.extract_entities_and_concepts(content)

            memory = MemoryFragment(
                id=f"mem_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S_%f')}",
                content=content,
                context=context,
                entities=entities,
                concepts=concepts,
                importance=importance,
            )

            memory_id = self.knowledge_graph.add_memory(memory)

            return {
                "success": True,
                "memory_id": memory_id,
                "entities_found": entities,
                "concepts_found": concepts,
                "message": "Memory fragment added successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def communicate_with_context(self, message: str, system_prompt: str | None = None) -> dict[str, Any]:
        """Enable meaningful communication using knowledge graph context.

        Args:
            message: User message
            system_prompt: Optional system prompt

        Returns:
            Rich response with context and insights
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            # Get communication context
            context = self.knowledge_graph.get_communication_context(message)

            # Build enhanced system prompt with context
            enhanced_prompt = self._build_contextual_prompt(system_prompt, context)

            # Generate response with context
            response = self.chat(message, system_prompt=enhanced_prompt, stream=False)

            # Learn from this conversation
            self.knowledge_graph.learn_from_conversation(message, response, confidence=0.8)

            return {
                "success": True,
                "response": response,
                "context": context,
                "context_used": {
                    "entities": len(context["entities"]),
                    "memories": len(context["memories"]),
                    "related_concepts": len(context["related_concepts"]),
                },
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_knowledge_graph(self, query: str, node_type: str | None = None, limit: int = 10) -> dict[str, Any]:
        """Search the knowledge graph for relevant information.

        Args:
            query: Search query
            node_type: Optional node type filter
            limit: Maximum results

        Returns:
            Search results with nodes and relations
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            nodes = self.knowledge_graph.find_nodes(query, node_type, limit)

            results = []
            for node in nodes:
                # Get related nodes for each result
                related = self.knowledge_graph.get_related_nodes(node.id, max_depth=1)

                results.append(
                    {
                        "id": node.id,
                        "type": node.type,
                        "label": node.label,
                        "description": node.description,
                        "properties": node.properties,
                        "related_nodes": [{"id": r.id, "label": r.label, "type": r.type} for r in related[:3]],
                    }
                )

            return {
                "success": True,
                "results": results,
                "total_found": len(results),
                "query": query,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_knowledge_relationships(
        self, node_id: str, relation_type: str | None = None, max_depth: int = 2
    ) -> dict[str, Any]:
        """Get relationships for a specific knowledge node.

        Args:
            node_id: ID of the node
            relation_type: Optional relation type filter
            max_depth: Maximum traversal depth

        Returns:
            Related nodes and relationships
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            related_nodes = self.knowledge_graph.get_related_nodes(node_id, relation_type, max_depth)

            return {
                "success": True,
                "node_id": node_id,
                "related_nodes": [
                    {
                        "id": node.id,
                        "type": node.type,
                        "label": node.label,
                        "description": node.description,
                    }
                    for node in related_nodes
                ],
                "total_related": len(related_nodes),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def retrieve_relevant_memories(self, query: str, context: dict | None = None, limit: int = 5) -> dict[str, Any]:
        """Retrieve memories relevant to a query.

        Args:
            query: Search query
            context: Optional context filter
            limit: Maximum results

        Returns:
            Relevant memory fragments
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            memories = self.knowledge_graph.retrieve_memories(query, context, limit)

            return {
                "success": True,
                "memories": [
                    {
                        "id": mem.id,
                        "content": mem.content,
                        "context": mem.context,
                        "importance": mem.importance,
                        "timestamp": mem.timestamp,
                        "entities": mem.entities,
                        "concepts": mem.concepts,
                    }
                    for mem in memories
                ],
                "total_found": len(memories),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def learn_from_interaction(
        self, user_message: str, assistant_response: str, confidence: float = 0.8
    ) -> dict[str, Any]:
        """Learn from user interactions to improve future communication.

        Args:
            user_message: The user's message
            assistant_response: The assistant's response
            confidence: Confidence in the interaction quality

        Returns:
            Learning results
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            self.knowledge_graph.learn_from_conversation(user_message, assistant_response, confidence)

            return {
                "success": True,
                "message": "Successfully learned from interaction",
                "conversation_turns": len(self.knowledge_graph.conversation_history),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_knowledge_graph_stats(self) -> dict[str, Any]:
        """Get comprehensive statistics about the knowledge graph.

        Returns:
            Knowledge graph statistics
        """
        if not self.enable_knowledge_graph:
            return {"success": False, "error": "Knowledge graph not enabled"}

        try:
            stats = self.knowledge_graph.get_stats()

            return {
                "success": True,
                "stats": stats,
                "message": "Knowledge graph statistics retrieved successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    # -- Private helpers -----------------------------------------------------

    def _build_contextual_prompt(self, base_prompt: str | None, context: dict[str, Any]) -> str:
        """Build an enhanced prompt with knowledge graph context."""
        contextual_parts = []

        if base_prompt:
            contextual_parts.append(base_prompt)

        # Add entity context
        if context["entities"]:
            contextual_parts.append(f"Relevant entities mentioned: {', '.join(context['entities'])}")

        # Add memory context
        if context["memories"]:
            memory_texts = [mem["content"] for mem in context["memories"][:2]]
            contextual_parts.append(f"Relevant memories: {' | '.join(memory_texts)}")

        # Add related concepts
        if context["related_concepts"]:
            contextual_parts.append(f"Related concepts: {', '.join(context['related_concepts'])}")

        # Add conversation context
        if context["conversation_history"]:
            contextual_parts.append("Recent conversation context available")

        contextual_parts.append("Use this context to provide more meaningful, personalized responses.")

        return "\n\n".join(contextual_parts)
