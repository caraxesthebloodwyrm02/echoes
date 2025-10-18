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
Agent Knowledge Layer - Shared knowledge graph for multi-agent collaboration
Enables agents to discover, share, and build upon each other's insights
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from knowledge_graph.system import KnowledgeGraph, OntologyManager, SemanticReasoner
    from prompting.core.kg_bridge import KnowledgeGraphBridge

    KG_AVAILABLE = True
except ImportError:
    KG_AVAILABLE = False
    logging.warning("Knowledge graph dependencies not available")


class AgentDiscovery:
    """Represents a discovery made by an agent"""

    def __init__(
        self,
        agent_name: str,
        discovery_type: str,
        content: str,
        confidence: float,
        context: Optional[Dict[str, Any]] = None,
        related_entities: Optional[List[str]] = None,
    ):
        self.agent_name = agent_name
        self.discovery_type = discovery_type
        self.content = content
        self.confidence = confidence
        self.context = context or {}
        self.related_entities = related_entities or []
        self.timestamp = datetime.now().isoformat()
        self.discovery_id = f"{agent_name}_{discovery_type}_{hash(content) % 10000}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "agent_name": self.agent_name,
            "discovery_type": self.discovery_type,
            "content": self.content,
            "confidence": self.confidence,
            "context": self.context,
            "related_entities": self.related_entities,
            "timestamp": self.timestamp,
            "discovery_id": self.discovery_id,
        }


class AgentKnowledgeLayer:
    """
    Shared knowledge layer for agent collaboration

    Features:
    - Agents publish discoveries to shared knowledge graph
    - Agents query for relevant discoveries from other agents
    - Cross-agent pattern recognition
    - Knowledge handoffs between agents
    - Collaborative learning and insight building
    """

    def __init__(self, kg_bridge: Optional[KnowledgeGraphBridge] = None):
        """
        Initialize agent knowledge layer

        Args:
            kg_bridge: Optional KG bridge instance (creates new if None)
        """
        self.logger = logging.getLogger(__name__)

        if kg_bridge:
            self.kg_bridge = kg_bridge
        else:
            self.kg_bridge = (
                KnowledgeGraphBridge(enable_kg=True) if KG_AVAILABLE else None
            )

        # Track agent activity
        self.agent_registry: Dict[str, Dict[str, Any]] = {}
        self.discovery_count = 0
        self.query_count = 0

        self.logger.info("AgentKnowledgeLayer initialized")

    def register_agent(
        self,
        agent_name: str,
        agent_type: str,
        capabilities: List[str],
        description: str = "",
    ) -> bool:
        """
        Register an agent in the knowledge layer

        Args:
            agent_name: Unique agent identifier
            agent_type: Type/role of agent (architect, reviewer, tester, etc.)
            capabilities: List of agent capabilities
            description: Optional description

        Returns:
            True if registration successful
        """
        if agent_name in self.agent_registry:
            self.logger.warning(f"Agent {agent_name} already registered")
            return False

        self.agent_registry[agent_name] = {
            "agent_type": agent_type,
            "capabilities": capabilities,
            "description": description,
            "registered_at": datetime.now().isoformat(),
            "discoveries_made": 0,
            "queries_made": 0,
        }

        # Add agent entity to knowledge graph
        if self.kg_bridge and self.kg_bridge.enabled:
            try:
                agent_uri = self.kg_bridge.kg.add_code_entity(
                    "Agent",
                    agent_name,
                    {
                        "type": agent_type,
                        "capabilities": ",".join(capabilities),
                        "description": description,
                    },
                )
                self.logger.info(f"Agent {agent_name} registered in knowledge graph")
            except Exception as e:
                self.logger.error(f"Failed to register agent in KG: {e}")

        self.logger.info(f"Registered agent: {agent_name} ({agent_type})")
        return True

    def publish_discovery(
        self,
        agent_name: str,
        discovery_type: str,
        content: str,
        confidence: float,
        context: Optional[Dict[str, Any]] = None,
        related_entities: Optional[List[str]] = None,
    ) -> Optional[str]:
        """
        Agent publishes a discovery to shared knowledge

        Args:
            agent_name: Name of agent making discovery
            discovery_type: Type of discovery (pattern, insight, issue, solution, etc.)
            content: Discovery content
            confidence: Confidence score (0.0-1.0)
            context: Optional context dictionary
            related_entities: Optional list of related entities

        Returns:
            Discovery ID if successful, None otherwise
        """
        if agent_name not in self.agent_registry:
            self.logger.warning(f"Agent {agent_name} not registered")
            return None

        # Create discovery object
        discovery = AgentDiscovery(
            agent_name=agent_name,
            discovery_type=discovery_type,
            content=content,
            confidence=confidence,
            context=context,
            related_entities=related_entities,
        )

        # Add to knowledge graph
        if self.kg_bridge and self.kg_bridge.enabled:
            try:
                discovery_uri = self.kg_bridge.kg.add_code_entity(
                    "AgentDiscovery",
                    discovery.discovery_id,
                    {
                        "agent_name": agent_name,
                        "discovery_type": discovery_type,
                        "content": content,
                        "confidence": confidence,
                        "timestamp": discovery.timestamp,
                    },
                )

                # Link discovery to agent
                agent_uri = self.kg_bridge.kg.ns["code"][f"Agent_{agent_name}"]
                self.kg_bridge.kg.add_relationship(
                    agent_uri,
                    "made_discovery",
                    discovery_uri,
                    {"confidence": confidence},
                )

                # Link to related entities
                for entity in related_entities or []:
                    entity_uri = self.kg_bridge.kg.ns["code"][entity]
                    self.kg_bridge.kg.add_relationship(
                        discovery_uri, "related_to", entity_uri
                    )

                self.logger.info(
                    f"Agent {agent_name} published discovery: {discovery_type} "
                    f"(confidence: {confidence:.2f})"
                )

            except Exception as e:
                self.logger.error(f"Failed to publish discovery to KG: {e}")
                return None

        # Update statistics
        self.agent_registry[agent_name]["discoveries_made"] += 1
        self.discovery_count += 1

        return discovery.discovery_id

    def query_discoveries(
        self,
        agent_name: str,
        query: str,
        discovery_type: Optional[str] = None,
        min_confidence: float = 0.5,
        limit: int = 10,
        exclude_own: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Agent queries for relevant discoveries from other agents

        Args:
            agent_name: Name of querying agent
            query: Search query
            discovery_type: Optional filter by discovery type
            min_confidence: Minimum confidence threshold
            limit: Maximum results
            exclude_own: Exclude discoveries made by querying agent

        Returns:
            List of relevant discoveries
        """
        if agent_name not in self.agent_registry:
            self.logger.warning(f"Agent {agent_name} not registered")
            return []

        # Update statistics
        self.agent_registry[agent_name]["queries_made"] += 1
        self.query_count += 1

        if not self.kg_bridge or not self.kg_bridge.enabled:
            self.logger.warning("Knowledge graph not available for queries")
            return []

        try:
            # Build SPARQL query
            type_filter = (
                f'?discovery code:discovery_type "{discovery_type}" .'
                if discovery_type
                else ""
            )
            exclude_filter = (
                f'FILTER (?agent_name != "{agent_name}")' if exclude_own else ""
            )

            sparql_query = f"""
            SELECT ?discovery ?agent_name ?discovery_type ?content ?confidence ?timestamp
            WHERE {{
                ?discovery rdf:type code:AgentDiscovery .
                ?discovery code:agent_name ?agent_name .
                ?discovery code:discovery_type ?discovery_type .
                ?discovery code:content ?content .
                ?discovery code:confidence ?confidence .
                ?discovery code:timestamp ?timestamp .
                {type_filter}
                FILTER (?confidence >= {min_confidence})
                {exclude_filter}
            }}
            ORDER BY DESC(?confidence)
            LIMIT {limit * 2}
            """

            raw_results = self.kg_bridge.kg.query_knowledge(sparql_query)

            # Calculate semantic similarity
            query_lower = query.lower()
            query_terms = set(query_lower.split())

            scored_results = []
            for result in raw_results:
                content = result.get("content", "").lower()
                content_terms = set(content.split())

                # Jaccard similarity
                intersection = len(query_terms & content_terms)
                union = len(query_terms | content_terms)
                similarity = intersection / union if union > 0 else 0.0

                confidence = float(result.get("confidence", 0.5))
                combined_score = (similarity * 0.6) + (confidence * 0.4)

                scored_results.append(
                    {
                        "discovery_id": result.get("discovery", ""),
                        "agent_name": result.get("agent_name", ""),
                        "discovery_type": result.get("discovery_type", ""),
                        "content": result.get("content", ""),
                        "confidence": confidence,
                        "timestamp": result.get("timestamp", ""),
                        "similarity": similarity,
                        "combined_score": combined_score,
                    }
                )

            # Sort and limit
            scored_results.sort(key=lambda x: x["combined_score"], reverse=True)
            final_results = scored_results[:limit]

            self.logger.info(
                f"Agent {agent_name} query returned {len(final_results)} discoveries"
            )

            return final_results

        except Exception as e:
            self.logger.error(f"Discovery query failed: {e}")
            return []

    def find_collaborators(
        self,
        agent_name: str,
        task_type: str,
        required_capabilities: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Find other agents suitable for collaboration on a task

        Args:
            agent_name: Name of requesting agent
            task_type: Type of task needing collaboration
            required_capabilities: Optional list of required capabilities

        Returns:
            List of suitable collaborator agents with match scores
        """
        if agent_name not in self.agent_registry:
            return []

        collaborators = []

        for other_agent, info in self.agent_registry.items():
            if other_agent == agent_name:
                continue

            # Calculate capability match
            agent_caps = set(info["capabilities"])
            required_caps = set(required_capabilities or [])

            if required_caps:
                match_score = len(agent_caps & required_caps) / len(required_caps)
            else:
                match_score = 0.5  # Neutral score if no requirements

            # Boost score based on relevant discoveries
            discoveries_made = info.get("discoveries_made", 0)
            experience_boost = min(discoveries_made / 10.0, 0.3)  # Max 0.3 boost

            total_score = match_score + experience_boost

            collaborators.append(
                {
                    "agent_name": other_agent,
                    "agent_type": info["agent_type"],
                    "capabilities": info["capabilities"],
                    "match_score": total_score,
                    "discoveries_made": discoveries_made,
                }
            )

        # Sort by match score
        collaborators.sort(key=lambda x: x["match_score"], reverse=True)

        return collaborators

    def create_handoff_context(
        self,
        from_agent: str,
        to_agent: str,
        task_description: str,
        relevant_discoveries: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Create context package for agent handoff

        Args:
            from_agent: Handing off agent
            to_agent: Receiving agent
            task_description: Description of task being handed off
            relevant_discoveries: Optional list of relevant discovery IDs

        Returns:
            Handoff context dictionary
        """
        context = {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task_description": task_description,
            "handoff_timestamp": datetime.now().isoformat(),
            "relevant_discoveries": [],
        }

        # Gather relevant discoveries
        if relevant_discoveries and self.kg_bridge and self.kg_bridge.enabled:
            for discovery_id in relevant_discoveries:
                try:
                    query = f"""
                    SELECT ?content ?confidence ?discovery_type
                    WHERE {{
                        ?discovery code:discovery_id "{discovery_id}" .
                        ?discovery code:content ?content .
                        ?discovery code:confidence ?confidence .
                        ?discovery code:discovery_type ?discovery_type .
                    }}
                    """
                    results = self.kg_bridge.kg.query_knowledge(query)
                    if results:
                        context["relevant_discoveries"].append(results[0])
                except Exception as e:
                    self.logger.error(
                        f"Failed to retrieve discovery {discovery_id}: {e}"
                    )

        # Query for additional context
        if self.kg_bridge and self.kg_bridge.enabled:
            try:
                additional = self.query_discoveries(
                    to_agent,
                    task_description,
                    min_confidence=0.6,
                    limit=5,
                    exclude_own=False,
                )
                context["suggested_context"] = additional
            except Exception as e:
                self.logger.error(f"Failed to get additional context: {e}")

        self.logger.info(f"Created handoff context: {from_agent} → {to_agent}")

        return context

    def get_agent_statistics(self, agent_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for agent(s)

        Args:
            agent_name: Optional specific agent name (None for all agents)

        Returns:
            Statistics dictionary
        """
        if agent_name:
            if agent_name not in self.agent_registry:
                return {}
            return {"agent_name": agent_name, **self.agent_registry[agent_name]}

        # Global statistics
        return {
            "total_agents": len(self.agent_registry),
            "total_discoveries": self.discovery_count,
            "total_queries": self.query_count,
            "agents": self.agent_registry,
            "kg_enabled": self.kg_bridge.enabled if self.kg_bridge else False,
        }

    def get_cross_agent_patterns(self) -> Dict[str, List[Any]]:
        """
        Identify patterns across multiple agents' discoveries

        Returns:
            Dictionary of pattern categories
        """
        if not self.kg_bridge or not self.kg_bridge.enabled:
            return {}

        try:
            # Find discoveries shared by multiple agents
            shared_topics_query = """
            SELECT ?discovery_type (COUNT(DISTINCT ?agent) as ?agent_count)
            WHERE {
                ?discovery rdf:type code:AgentDiscovery .
                ?discovery code:discovery_type ?discovery_type .
                ?discovery code:agent_name ?agent .
            }
            GROUP BY ?discovery_type
            HAVING (?agent_count > 1)
            ORDER BY DESC(?agent_count)
            """

            results = self.kg_bridge.kg.query_knowledge(shared_topics_query)

            patterns = {
                "cross_agent_topics": results,
                "collaboration_opportunities": [],
            }

            # Identify collaboration opportunities
            for result in results:
                topic = result.get("discovery_type", "")
                agent_count = int(result.get("agent_count", 0))
                if agent_count >= 2:
                    patterns["collaboration_opportunities"].append(
                        {
                            "topic": topic,
                            "agents_interested": agent_count,
                            "recommendation": f"Consider collaborative session on {topic}",
                        }
                    )

            return patterns

        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {e}")
            return {}


__all__ = ["AgentKnowledgeLayer", "AgentDiscovery"]
