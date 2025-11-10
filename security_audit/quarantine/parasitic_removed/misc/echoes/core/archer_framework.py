"""
Archer Framework: Cross-Modal Semantic Alignment
===============================================

Grounds semantic alignment across modalities using fundamental forces:
1. **Gravitational Force**: Semantic gravity wells that attract related concepts
2. **Electromagnetic Force**: Semantic field interactions between modalities
3. **Strong Nuclear Force**: Tight binding of core semantic primitives
4. **Weak Nuclear Force**: Flexible transformations between related concepts

The framework provides robust cross-modal understanding by establishing
semantic grounding forces that maintain meaning consistency across
text, vision, audio, and sensor modalities.
"""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import networkx as nx
import numpy as np

logger = logging.getLogger(__name__)


class GroundingForce(Enum):
    """Fundamental forces for semantic grounding."""

    GRAVITATIONAL = "gravitational"  # Semantic attraction between concepts
    ELECTROMAGNETIC = "electromagnetic"  # Field interactions across modalities
    STRONG_NUCLEAR = "strong_nuclear"  # Tight binding of primitives
    WEAK_NUCLEAR = "weak_nuclear"  # Flexible transformations


@dataclass
class SemanticNode:
    """Represents a semantic concept in the alignment graph."""

    concept_id: str
    modality: str
    embedding: np.ndarray
    confidence: float = 1.0
    grounding_forces: dict[GroundingForce, float] = field(default_factory=dict)
    connected_nodes: set[str] = field(default_factory=set)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AlignmentForce:
    """Represents a semantic alignment force between modalities."""

    source_concept: str
    target_concept: str
    force_type: GroundingForce
    strength: float
    modality_bridge: str
    transformation_matrix: np.ndarray | None = None


class ArcherFramework:
    """
    Archer Framework for Cross-Modal Semantic Alignment.

    Establishes semantic grounding forces that maintain meaning consistency
    across different modalities through physics-inspired alignment mechanisms.
    """

    def __init__(self):
        self.semantic_graph: nx.Graph = nx.Graph()
        self.modality_bridges: dict[str, dict[str, np.ndarray]] = {}
        self.grounding_forces: dict[str, dict[GroundingForce, float]] = {}
        self.alignment_history: list[AlignmentForce] = []

        # Initialize fundamental force parameters
        self.force_parameters = {
            GroundingForce.GRAVITATIONAL: {
                "attraction_constant": 0.1,
                "repulsion_threshold": 0.3,
                "mass_factor": 1.0,
            },
            GroundingForce.ELECTROMAGNETIC: {
                "field_strength": 0.8,
                "interaction_radius": 0.5,
                "polarity_factor": 0.9,
            },
            GroundingForce.STRONG_NUCLEAR: {
                "binding_energy": 0.95,
                "range_limit": 0.1,
                "stability_factor": 0.99,
            },
            GroundingForce.WEAK_NUCLEAR: {
                "transformation_rate": 0.3,
                "decay_constant": 0.1,
                "flexibility_factor": 0.7,
            },
        }

        logger.info("Archer Framework initialized with fundamental grounding forces")

    def add_semantic_node(self, node: SemanticNode) -> bool:
        """
        Add a semantic node to the alignment graph.

        Args:
            node: SemanticNode to add

        Returns:
            bool: True if successfully added
        """
        try:
            # Add node to graph
            self.semantic_graph.add_node(
                node.concept_id,
                modality=node.modality,
                embedding=node.embedding,
                confidence=node.confidence,
                metadata=node.metadata,
            )

            # Initialize grounding forces
            self.grounding_forces[node.concept_id] = node.grounding_forces.copy()

            # Apply gravitational attraction to existing nodes
            self._apply_gravitational_force(node)

            logger.info(
                f"Added semantic node {node.concept_id} for modality {node.modality}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to add semantic node {node.concept_id}: {str(e)}")
            return False

    def create_modality_bridge(
        self,
        source_modality: str,
        target_modality: str,
        transformation_matrix: np.ndarray,
    ) -> bool:
        """
        Create a bridge between two modalities for semantic alignment.

        Args:
            source_modality: Source modality
            target_modality: Target modality
            transformation_matrix: Matrix for transforming embeddings between modalities

        Returns:
            bool: True if bridge created successfully
        """
        try:
            bridge_key = f"{source_modality}_{target_modality}"

            # Store bidirectional transformation
            self.modality_bridges[bridge_key] = transformation_matrix
            self.modality_bridges[
                f"{target_modality}_{source_modality}"
            ] = transformation_matrix.T

            logger.info(
                f"Created modality bridge between {source_modality} and {target_modality}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to create modality bridge: {str(e)}")
            return False

    def align_semantic_concepts(
        self,
        source_concept: str,
        target_concept: str,
        force_type: GroundingForce = GroundingForce.ELECTROMAGNETIC,
    ) -> AlignmentForce | None:
        """
        Align two semantic concepts using specified grounding force.

        Args:
            source_concept: Source concept ID
            target_concept: Target concept ID
            force_type: Type of grounding force to use

        Returns:
            AlignmentForce object or None if alignment fails
        """
        if source_concept not in self.semantic_graph:
            logger.error(f"Source concept {source_concept} not found")
            return None

        if target_concept not in self.semantic_graph:
            logger.error(f"Target concept {target_concept} not found")
            return None

        try:
            # Get node data
            source_node = self.semantic_graph.nodes[source_concept]
            target_node = self.semantic_graph.nodes[target_concept]

            # Calculate alignment strength using specified force
            if force_type == GroundingForce.GRAVITATIONAL:
                strength = self._calculate_gravitational_alignment(
                    source_node, target_node
                )
            elif force_type == GroundingForce.ELECTROMAGNETIC:
                strength = self._calculate_electromagnetic_alignment(
                    source_node, target_node
                )
            elif force_type == GroundingForce.STRONG_NUCLEAR:
                strength = self._calculate_strong_nuclear_alignment(
                    source_node, target_node
                )
            elif force_type == GroundingForce.WEAK_NUCLEAR:
                strength = self._calculate_weak_nuclear_alignment(
                    source_node, target_node
                )
            else:
                strength = 0.0

            # Create transformation matrix if modalities differ
            transformation_matrix = None
            if source_node["modality"] != target_node["modality"]:
                bridge_key = f"{source_node['modality']}_{target_node['modality']}"
                transformation_matrix = self.modality_bridges.get(bridge_key)

            # Create alignment force
            alignment = AlignmentForce(
                source_concept=source_concept,
                target_concept=target_concept,
                force_type=force_type,
                strength=strength,
                modality_bridge=f"{source_node['modality']}_{target_node['modality']}",
                transformation_matrix=transformation_matrix,
            )

            # Add edge to graph
            self.semantic_graph.add_edge(
                source_concept,
                target_concept,
                force_type=force_type.value,
                strength=strength,
                transformation_matrix=transformation_matrix,
            )

            # Record alignment
            self.alignment_history.append(alignment)

            logger.info(
                f"Aligned concepts {source_concept} and {target_concept} with {force_type.value} force (strength: {strength:.3f})"
            )
            return alignment

        except Exception as e:
            logger.error(
                f"Failed to align concepts {source_concept} and {target_concept}: {str(e)}"
            )
            return None

    def _calculate_gravitational_alignment(
        self, source_node: dict[str, Any], target_node: dict[str, Any]
    ) -> float:
        """Calculate gravitational alignment strength between concepts."""
        params = self.force_parameters[GroundingForce.GRAVITATIONAL]

        # Calculate semantic distance
        embedding_distance = np.linalg.norm(
            source_node["embedding"] - target_node["embedding"]
        )

        if embedding_distance < params["repulsion_threshold"]:
            # Repulsive force for very similar concepts
            return -params["attraction_constant"] / (embedding_distance + 0.1)
        else:
            # Attractive force for related concepts
            mass_product = (
                source_node["confidence"]
                * target_node["confidence"]
                * params["mass_factor"]
            )
            return (
                params["attraction_constant"]
                * mass_product
                / (embedding_distance**2 + 0.1)
            )

    def _calculate_electromagnetic_alignment(
        self, source_node: dict[str, Any], target_node: dict[str, Any]
    ) -> float:
        """Calculate electromagnetic alignment strength between concepts."""
        params = self.force_parameters[GroundingForce.ELECTROMAGNETIC]

        # Calculate field interaction
        embedding_similarity = np.dot(
            source_node["embedding"], target_node["embedding"]
        ) / (
            np.linalg.norm(source_node["embedding"])
            * np.linalg.norm(target_node["embedding"])
        )

        # Apply polarity factor (same modality = stronger attraction)
        polarity_boost = (
            params["polarity_factor"]
            if source_node["modality"] == target_node["modality"]
            else 1.0
        )

        # Distance-based decay
        embedding_distance = np.linalg.norm(
            source_node["embedding"] - target_node["embedding"]
        )
        distance_factor = np.exp(-embedding_distance / params["interaction_radius"])

        return (
            params["field_strength"]
            * embedding_similarity
            * polarity_boost
            * distance_factor
        )

    def _calculate_strong_nuclear_alignment(
        self, source_node: dict[str, Any], target_node: dict[str, Any]
    ) -> float:
        """Calculate strong nuclear alignment strength (tight binding of primitives)."""
        params = self.force_parameters[GroundingForce.STRONG_NUCLEAR]

        # Strong nuclear force binds very similar concepts tightly
        embedding_similarity = np.dot(
            source_node["embedding"], target_node["embedding"]
        ) / (
            np.linalg.norm(source_node["embedding"])
            * np.linalg.norm(target_node["embedding"])
        )

        # Only apply strong binding for very high similarity
        if embedding_similarity > params["stability_factor"]:
            distance = np.linalg.norm(
                source_node["embedding"] - target_node["embedding"]
            )
            if distance < params["range_limit"]:
                return params["binding_energy"] * (1 - distance / params["range_limit"])
            else:
                return params["binding_energy"] * np.exp(
                    -distance / params["range_limit"]
                )

        return 0.0

    def _calculate_weak_nuclear_alignment(
        self, source_node: dict[str, Any], target_node: dict[str, Any]
    ) -> float:
        """Calculate weak nuclear alignment strength (flexible transformations)."""
        params = self.force_parameters[GroundingForce.WEAK_NUCLEAR]

        # Weak nuclear force allows flexible transformations between related concepts
        embedding_distance = np.linalg.norm(
            source_node["embedding"] - target_node["embedding"]
        )

        # Check if transformation bridge exists
        bridge_key = f"{source_node['modality']}_{target_node['modality']}"
        has_bridge = bridge_key in self.modality_bridges

        if has_bridge:
            # Boost alignment if modality bridge exists
            transformation_factor = params["transformation_rate"]
        else:
            transformation_factor = params["transformation_rate"] * 0.5

        # Apply decay over distance
        return (
            transformation_factor
            * np.exp(-params["decay_constant"] * embedding_distance)
            * params["flexibility_factor"]
        )

    def _apply_gravitational_force(self, new_node: SemanticNode):
        """Apply gravitational attraction to existing nodes when adding new node."""
        params = self.force_parameters[GroundingForce.GRAVITATIONAL]

        for existing_node_id in self.semantic_graph.nodes():
            if existing_node_id == new_node.concept_id:
                continue

            existing_node = self.semantic_graph.nodes[existing_node_id]
            distance = np.linalg.norm(new_node.embedding - existing_node["embedding"])

            if distance < params["repulsion_threshold"]:
                # Too close - create repulsive force
                force_strength = -params["attraction_constant"] / (distance + 0.1)
            else:
                # Attractive force
                mass_product = (
                    new_node.confidence
                    * existing_node["confidence"]
                    * params["mass_factor"]
                )
                force_strength = (
                    params["attraction_constant"] * mass_product / (distance**2 + 0.1)
                )

            # Update grounding forces
            if existing_node_id not in self.grounding_forces:
                self.grounding_forces[existing_node_id] = {}

            self.grounding_forces[existing_node_id][
                GroundingForce.GRAVITATIONAL
            ] = force_strength
            self.grounding_forces[new_node.concept_id][
                GroundingForce.GRAVITATIONAL
            ] = force_strength

    def find_semantic_paths(
        self, start_concept: str, end_concept: str, max_hops: int = 3
    ) -> list[list[str]]:
        """
        Find semantic paths between concepts using grounding forces.

        Args:
            start_concept: Starting concept ID
            end_concept: Ending concept ID
            max_hops: Maximum number of hops in path

        Returns:
            List of paths (each path is a list of concept IDs)
        """
        try:
            # Use NetworkX to find all simple paths
            paths = list(
                nx.all_simple_paths(
                    self.semantic_graph, start_concept, end_concept, cutoff=max_hops
                )
            )

            # Sort by path strength (sum of edge weights)
            path_strengths = []
            for path in paths:
                strength = 0
                for i in range(len(path) - 1):
                    edge_data = self.semantic_graph.get_edge_data(path[i], path[i + 1])
                    if edge_data and "strength" in edge_data:
                        strength += edge_data["strength"]
                path_strengths.append((path, strength))

            # Sort by strength descending
            path_strengths.sort(key=lambda x: x[1], reverse=True)

            return [path for path, _ in path_strengths]

        except Exception as e:
            logger.error(f"Failed to find semantic paths: {str(e)}")
            return []

    def get_grounding_stability(self, concept_id: str) -> float:
        """
        Calculate grounding stability for a concept based on all applied forces.

        Args:
            concept_id: Concept ID to analyze

        Returns:
            Stability score (0-1, higher is more stable)
        """
        if concept_id not in self.grounding_forces:
            return 0.0

        forces = self.grounding_forces[concept_id]

        # Calculate stability based on force balance
        gravitational_stability = abs(forces.get(GroundingForce.GRAVITATIONAL, 0))
        electromagnetic_stability = forces.get(GroundingForce.ELECTROMAGNETIC, 0)
        strong_nuclear_stability = forces.get(GroundingForce.STRONG_NUCLEAR, 0)
        weak_nuclear_stability = forces.get(GroundingForce.WEAK_NUCLEAR, 0)

        # Strong nuclear force provides the most stability
        # Electromagnetic provides interaction stability
        # Gravitational provides attraction stability
        # Weak nuclear provides transformation flexibility

        stability_score = (
            0.4 * strong_nuclear_stability
            + 0.3 * electromagnetic_stability
            + 0.2 * gravitational_stability
            + 0.1 * weak_nuclear_stability
        )

        return min(max(stability_score, 0.0), 1.0)

    def optimize_semantic_layout(self, iterations: int = 10) -> bool:
        """
        Optimize the semantic layout using force-directed algorithms.

        Args:
            iterations: Number of optimization iterations

        Returns:
            bool: True if optimization successful
        """
        try:
            # Use force-directed layout to optimize semantic positioning
            pos = nx.spring_layout(self.semantic_graph, iterations=iterations)

            # Update node positions in metadata
            for node_id, position in pos.items():
                if node_id in self.semantic_graph.nodes:
                    self.semantic_graph.nodes[node_id]["position"] = position

            logger.info(f"Optimized semantic layout with {iterations} iterations")
            return True

        except Exception as e:
            logger.error(f"Failed to optimize semantic layout: {str(e)}")
            return False

    def get_alignment_statistics(self) -> dict[str, Any]:
        """Get statistics about the current semantic alignment state."""
        stats = {
            "total_nodes": len(self.semantic_graph.nodes),
            "total_edges": len(self.semantic_graph.edges),
            "modalities": set(),
            "force_distribution": defaultdict(int),
            "average_stability": 0.0,
            "strongest_alignments": [],
        }

        # Collect modality information
        for node_id, node_data in self.semantic_graph.nodes(data=True):
            stats["modalities"].add(node_data.get("modality", "unknown"))

            # Calculate average stability
            stability = self.get_grounding_stability(node_id)
            stats["average_stability"] += stability

        stats["modalities"] = list(stats["modalities"])

        if stats["total_nodes"] > 0:
            stats["average_stability"] /= stats["total_nodes"]

        # Collect force distribution
        for edge_data in self.semantic_graph.edges(data=True):
            force_type = edge_data[2].get("force_type", "unknown")
            stats["force_distribution"][force_type] += 1

        # Find strongest alignments
        edge_strengths = []
        for edge in self.semantic_graph.edges(data=True):
            strength = edge[2].get("strength", 0)
            edge_strengths.append((edge[0], edge[1], strength))

        edge_strengths.sort(key=lambda x: x[2], reverse=True)
        stats["strongest_alignments"] = edge_strengths[:5]

        return dict(stats)

    def export_semantic_graph(self, format: str = "json") -> str:
        """
        Export the semantic graph for analysis or persistence.

        Args:
            format: Export format ('json', 'graphml', etc.)

        Returns:
            String representation of the graph
        """
        try:
            if format == "json":
                # Convert to JSON-serializable format
                graph_data = {
                    "nodes": [],
                    "edges": [],
                    "forces": dict(self.grounding_forces),
                }

                for node_id, node_data in self.semantic_graph.nodes(data=True):
                    graph_data["nodes"].append(
                        {
                            "id": node_id,
                            "modality": node_data.get("modality"),
                            "confidence": node_data.get("confidence"),
                            "metadata": node_data.get("metadata"),
                        }
                    )

                for edge in self.semantic_graph.edges(data=True):
                    graph_data["edges"].append(
                        {
                            "source": edge[0],
                            "target": edge[1],
                            "force_type": edge[2].get("force_type"),
                            "strength": edge[2].get("strength"),
                        }
                    )

                return json.dumps(graph_data, indent=2)

            elif format == "graphml":
                # Use NetworkX to export as GraphML
                from io import StringIO

                output = StringIO()
                nx.write_graphml(self.semantic_graph, output)
                return output.getvalue()

            else:
                return f"Unsupported export format: {format}"

        except Exception as e:
            logger.error(f"Failed to export semantic graph: {str(e)}")
            return "{}"
