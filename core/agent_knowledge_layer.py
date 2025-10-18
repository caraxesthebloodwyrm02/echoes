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

# MIT License
#
# Copyright (c) 2025 Echoes Project
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

"""
Agent Knowledge Layer - Shared knowledge graph for agent collaboration
Enables cross-agent learning, context sharing, and knowledge propagation
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from knowledge_graph.system import KnowledgeGraph, SemanticReasoner
    from prompting.core.kg_bridge import KnowledgeGraphBridge

    KG_AVAILABLE = True
except ImportError:
    KG_AVAILABLE = False
    logging.warning(
        "Knowledge graph dependencies not available for AgentKnowledgeLayer"
    )


class AgentDiscovery:
    """Represents a discovery made by an agent"""

    def __init__(
        self,
        agent_name: str,
        discovery_type: str,
        content: str,
        confidence: float = 0.8,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.agent_name = agent_name
        self.discovery_type = discovery_type
        self.content = content
        self.confidence = confidence
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.discovery_id = (
            f"{agent_name}_{discovery_type}_{datetime.now().timestamp()}"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "discovery_id": self.discovery_id,
            "agent_name": self.agent_name,
            "discovery_type": self.discovery_type,
            "content": self.content,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


class AgentContext:
    """Context passed between agents during handoffs"""

    def __init__(
        self,
        source_agent: str,
        target_agent: str,
        task_description: str,
        context_data: Dict[str, Any],
        priority: str = "medium",
    ):
        self.source_agent = source_agent
        self.target_agent = target_agent
        self.task_description = task_description
        self.context_data = context_data
        self.priority = priority
        self.timestamp = datetime.now().isoformat()
        self.context_id = (
            f"ctx_{source_agent}_{target_agent}_{datetime.now().timestamp()}"
        )
        self.status = "pending"  # pending, active, completed, failed

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "context_id": self.context_id,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "task_description": self.task_description,
            "context_data": self.context_data,
            "priority": self.priority,
            "timestamp": self.timestamp,
            "status": self.status,
        }


class AgentKnowledgeLayer:
    """
    Shared knowledge layer for agent collaboration

    Enables:
    - Cross-agent knowledge sharing via unified knowledge graph
    - Context preservation during agent handoffs
    - Discovery propagation across agent network
    - Pattern learning from multi-agent interactions
    """

    def __init__(self, enable_kg: bool = True):
        """
        Initialize agent knowledge layer

        Args:
            enable_kg: Enable knowledge graph integration
        """
        self.enabled = enable_kg and KG_AVAILABLE
        self.logger = logging.getLogger(__name__)

        # Core components
        self.kg_bridge = None
        self.kg = None
        self.reasoner = None

        # In-memory stores
        self.discoveries: List[AgentDiscovery] = []
        self.contexts: List[AgentContext] = []
        self.agent_registry: Dict[str, Dict[str, Any]] = {}

        # Statistics
        self.stats = {
            "discoveries_shared": 0,
            "contexts_passed": 0,
            "patterns_learned": 0,
            "agents_registered": 0,
        }

        # Initialize KG if available
        if self.enabled:
            try:
                self.kg = KnowledgeGraph()
                self.reasoner = SemanticReasoner(self.kg)
                self.kg_bridge = KnowledgeGraphBridge(enable_kg=True)
                self.logger.info("Agent Knowledge Layer initialized with KG support")
            except Exception as e:
                self.logger.error(
                    f"Failed to initialize KG for Agent Knowledge Layer: {e}"
                )
                self.enabled = False
        else:
            self.logger.warning("Agent Knowledge Layer running without KG support")

    def register_agent(
        self,
        agent_name: str,
        agent_type: str,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Register an agent in the knowledge layer

        Args:
            agent_name: Unique agent identifier
            agent_type: Type of agent (e.g., 'code_reviewer', 'architect')
            capabilities: List of agent capabilities
            metadata: Additional agent metadata

        Returns:
            True if registration successful
        """
        try:
            self.agent_registry[agent_name] = {
                "agent_type": agent_type,
                "capabilities": capabilities,
                "metadata": metadata or {},
                "registered_at": datetime.now().isoformat(),
                "discoveries_count": 0,
                "handoffs_count": 0,
            }

            # Add agent to knowledge graph
            if self.enabled and self.kg:
                agent_uri = self.kg.add_code_entity(
                    "Agent",
                    agent_name,
                    {
                        "agent_type": agent_type,
                        "capabilities": ",".join(capabilities),
                        "registered_at": datetime.now().isoformat(),
                    },
                )

            self.stats["agents_registered"] += 1
            self.logger.info(f"Agent registered: {agent_name} ({agent_type})")
            return True

        except Exception as e:
            self.logger.error(f"Failed to register agent {agent_name}: {e}")
            return False

    def share_discovery(self, discovery: AgentDiscovery) -> bool:
        """
        Share a discovery made by an agent

        Args:
            discovery: AgentDiscovery instance

        Returns:
            True if successfully shared
        """
        try:
            self.discoveries.append(discovery)

            # Update agent stats
            if discovery.agent_name in self.agent_registry:
                self.agent_registry[discovery.agent_name]["discoveries_count"] += 1

            # Add to knowledge graph
            if self.enabled and self.kg:
                discovery_uri = self.kg.add_code_entity(
                    "AgentDiscovery",
                    discovery.discovery_id,
                    {
                        "agent_name": discovery.agent_name,
                        "discovery_type": discovery.discovery_type,
                        "content": discovery.content,
                        "confidence": discovery.confidence,
                        "timestamp": discovery.timestamp,
                    },
                )

                # Link discovery to agent
                agent_uri = self.kg.ns["code"][
                    f"Agent_{discovery.agent_name.replace('.', '_')}"
                ]
                self.kg.add_relationship(
                    agent_uri,
                    "made_discovery",
                    discovery_uri,
                    {"confidence": discovery.confidence},
                )

            self.stats["discoveries_shared"] += 1
            self.logger.info(
                f"Discovery shared by {discovery.agent_name}: {discovery.discovery_type}"
            )
            return True

        except Exception as e:
            self.logger.error(f"Failed to share discovery: {e}")
            return False

    def query_discoveries(
        self,
        agent_name: Optional[str] = None,
        discovery_type: Optional[str] = None,
        min_confidence: float = 0.5,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Query discoveries from the knowledge layer

        Args:
            agent_name: Filter by agent name
            discovery_type: Filter by discovery type
            min_confidence: Minimum confidence threshold
            limit: Maximum results to return

        Returns:
            List of discovery dictionaries
        """
        if self.enabled and self.kg_bridge:
            try:
                # Build semantic query
                query_parts = []
                if agent_name:
                    query_parts.append(f"agent:{agent_name}")
                if discovery_type:
                    query_parts.append(f"type:{discovery_type}")

                query = " ".join(query_parts) if query_parts else "discovery"

                # Use semantic search via KG bridge
                results = self.kg_bridge.semantic_search(
                    query=query,
                    category="agent_discovery"
                    if not discovery_type
                    else discovery_type,
                    limit=limit,
                    min_confidence=min_confidence,
                )

                if results:
                    return results

            except Exception as e:
                self.logger.warning(
                    f"Semantic query failed, falling back to in-memory: {e}"
                )

        # Fallback: In-memory filtering
        filtered = []
        for disc in self.discoveries:
            if agent_name and disc.agent_name != agent_name:
                continue
            if discovery_type and disc.discovery_type != discovery_type:
                continue
            if disc.confidence < min_confidence:
                continue
            filtered.append(disc.to_dict())

        # Sort by confidence and timestamp
        filtered.sort(key=lambda x: (x["confidence"], x["timestamp"]), reverse=True)
        return filtered[:limit]

    def create_handoff_context(
        self,
        source_agent: str,
        target_agent: str,
        task_description: str,
        context_data: Dict[str, Any],
        priority: str = "medium",
        include_related_discoveries: bool = True,
    ) -> AgentContext:
        """
        Create context for agent handoff

        Args:
            source_agent: Source agent name
            target_agent: Target agent name
            task_description: Description of task to hand off
            context_data: Context data to pass
            priority: Task priority (low, medium, high)
            include_related_discoveries: Include related discoveries in context

        Returns:
            AgentContext instance
        """
        # Enhance context with related discoveries if requested
        if include_related_discoveries:
            related_discoveries = self.query_discoveries(
                agent_name=source_agent, min_confidence=0.7, limit=5
            )
            context_data["related_discoveries"] = related_discoveries

            # Add relevant knowledge from KG
            if self.enabled and self.kg_bridge:
                try:
                    patterns = self.kg_bridge.infer_patterns()
                    context_data["knowledge_patterns"] = patterns
                except Exception as e:
                    self.logger.debug(f"Could not add patterns to context: {e}")

        # Create context
        context = AgentContext(
            source_agent=source_agent,
            target_agent=target_agent,
            task_description=task_description,
            context_data=context_data,
            priority=priority,
        )

        self.contexts.append(context)

        # Update agent stats
        if source_agent in self.agent_registry:
            self.agent_registry[source_agent]["handoffs_count"] += 1

        # Add context to knowledge graph
        if self.enabled and self.kg:
            try:
                context_uri = self.kg.add_code_entity(
                    "AgentContext",
                    context.context_id,
                    {
                        "source_agent": source_agent,
                        "target_agent": target_agent,
                        "task": task_description,
                        "priority": priority,
                        "timestamp": context.timestamp,
                    },
                )

                # Link agents via handoff
                source_uri = self.kg.ns["code"][
                    f"Agent_{source_agent.replace('.', '_')}"
                ]
                target_uri = self.kg.ns["code"][
                    f"Agent_{target_agent.replace('.', '_')}"
                ]
                self.kg.add_relationship(
                    source_uri,
                    "hands_off_to",
                    target_uri,
                    {"context": context.context_id, "priority": priority},
                )
            except Exception as e:
                self.logger.warning(f"Failed to add context to KG: {e}")

        self.stats["contexts_passed"] += 1
        self.logger.info(f"Handoff context created: {source_agent} → {target_agent}")
        return context

    def complete_handoff(self, context_id: str, result: Dict[str, Any]) -> bool:
        """
        Mark a handoff context as completed

        Args:
            context_id: Context ID to complete
            result: Result data from completed task

        Returns:
            True if successfully completed
        """
        for context in self.contexts:
            if context.context_id == context_id:
                context.status = "completed"
                context.context_data["result"] = result
                context.context_data["completed_at"] = datetime.now().isoformat()

                self.logger.info(f"Handoff completed: {context_id}")
                return True

        self.logger.warning(f"Context not found: {context_id}")
        return False

    def learn_patterns(self) -> Dict[str, List[str]]:
        """
        Learn patterns from agent interactions

        Returns:
            Dictionary of learned patterns by category
        """
        patterns = {
            "successful_handoffs": [],
            "common_discoveries": [],
            "agent_collaborations": [],
            "knowledge_clusters": [],
        }

        if not self.enabled or not self.reasoner:
            return patterns

        try:
            # Infer patterns from knowledge graph
            self.kg.infer_relationships()
            kg_patterns = self.reasoner.find_code_patterns()

            # Analyze successful handoffs
            successful_contexts = [c for c in self.contexts if c.status == "completed"]
            if successful_contexts:
                # Group by agent pairs
                agent_pairs = {}
                for ctx in successful_contexts:
                    pair = (ctx.source_agent, ctx.target_agent)
                    agent_pairs[pair] = agent_pairs.get(pair, 0) + 1

                for (source, target), count in sorted(
                    agent_pairs.items(), key=lambda x: x[1], reverse=True
                )[:5]:
                    patterns["successful_handoffs"].append(
                        f"{source} → {target} ({count} successful handoffs)"
                    )

            # Analyze common discovery types
            discovery_types = {}
            for disc in self.discoveries:
                if disc.confidence >= 0.7:
                    discovery_types[disc.discovery_type] = (
                        discovery_types.get(disc.discovery_type, 0) + 1
                    )

            for disc_type, count in sorted(
                discovery_types.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                patterns["common_discoveries"].append(
                    f"{disc_type} ({count} discoveries)"
                )

            # Merge KG patterns
            patterns.update(kg_patterns)

            self.stats["patterns_learned"] = sum(len(v) for v in patterns.values())
            self.logger.info(
                f"Learned {self.stats['patterns_learned']} patterns from agent interactions"
            )

        except Exception as e:
            self.logger.error(f"Pattern learning failed: {e}")

        return patterns

    def get_agent_recommendations(self, agent_name: str) -> List[Dict[str, Any]]:
        """
        Get recommendations for an agent based on knowledge layer analysis

        Args:
            agent_name: Agent to get recommendations for

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []

        if agent_name not in self.agent_registry:
            return recommendations

        agent_info = self.agent_registry[agent_name]

        # Recommend collaboration partners
        # Find agents this agent hasn't worked with yet
        collaborated_with = set()
        for ctx in self.contexts:
            if ctx.source_agent == agent_name:
                collaborated_with.add(ctx.target_agent)
            elif ctx.target_agent == agent_name:
                collaborated_with.add(ctx.source_agent)

        uncollaborated = (
            set(self.agent_registry.keys()) - collaborated_with - {agent_name}
        )
        if uncollaborated:
            recommendations.append(
                {
                    "type": "collaboration",
                    "priority": "medium",
                    "recommendation": f"Consider collaborating with: {', '.join(list(uncollaborated)[:3])}",
                    "agents": list(uncollaborated),
                }
            )

        # Recommend knowledge sharing if low discovery count
        if agent_info["discoveries_count"] < 5:
            recommendations.append(
                {
                    "type": "knowledge_sharing",
                    "priority": "medium",
                    "recommendation": "Share more discoveries to enrich the knowledge layer",
                    "current_count": agent_info["discoveries_count"],
                }
            )

        # Use KG-based recommendations
        if self.enabled and self.kg_bridge:
            try:
                kg_recs = self.kg_bridge.get_recommendations()
                recommendations.extend(kg_recs)
            except Exception as e:
                self.logger.debug(f"Could not get KG recommendations: {e}")

        return recommendations

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge layer statistics"""
        return {
            **self.stats,
            "kg_enabled": self.enabled,
            "discoveries_stored": len(self.discoveries),
            "contexts_stored": len(self.contexts),
            "active_agents": len(self.agent_registry),
            "completed_handoffs": len(
                [c for c in self.contexts if c.status == "completed"]
            ),
        }


# Convenience function
def create_agent_knowledge_layer(enable_kg: bool = True) -> AgentKnowledgeLayer:
    """
    Factory function to create AgentKnowledgeLayer instance

    Args:
        enable_kg: Enable knowledge graph integration

    Returns:
        Initialized AgentKnowledgeLayer instance
    """
    return AgentKnowledgeLayer(enable_kg=enable_kg)
