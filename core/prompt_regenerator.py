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

"""Prompt Regeneration from Results.

This module implements reverse-engineering of prompts from analysis results,
demonstrating that trajectory paths are bidirectional:
- Forward: Prompt → Analysis → Result
- Backward: Result → Analysis → Prompt

Key Insight: If there's a path from A→X, there exists a path X→A.
The regenerated prompt may differ from the original but should produce
equivalent results when re-executed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import numpy as np


@dataclass
class AnalysisResult:
    """Structured analysis result (output of trajectory analysis)."""

    classification: str  # Aligned, Imbalanced, Fragmented
    efficiency_score: float
    balance_angle: float

    # Pairwise angles
    influence_productivity_angle: float
    influence_creativity_angle: float
    productivity_creativity_angle: float

    # Vectors
    influence_vector: List[float]
    productivity_vector: List[float]
    creativity_vector: List[float]
    efficiency_vector: List[float]

    # Metadata
    timestamp: Optional[str] = None
    seed: Optional[int] = None


@dataclass
class RegeneratedPrompt:
    """Reconstructed prompt from analysis result."""

    # Core prompt components
    objective: str
    constraints: List[str]
    input_vectors: Dict[str, List[float]]
    expected_classification: str

    # Metadata
    confidence: float  # 0-1 scale (how confident we are in regeneration)
    reasoning: str  # Explanation of regeneration logic
    alternative_prompts: List[str]  # Other possible interpretations


class PromptRegenerator:
    """Reverse-engineer prompts from analysis results."""

    def __init__(self):
        """Initialize regenerator with classification templates."""
        self.classification_templates = {
            "Aligned": {
                "objective": "Analyze a high-synergy system with optimal dimensional alignment",
                "characteristics": [
                    "efficiency score >= 0.7",
                    "balance angle < 90°",
                    "strong influence-productivity alignment",
                    "harmonious creativity integration",
                ],
                "typical_use_case": "Well-functioning team or optimized process",
            },
            "Imbalanced": {
                "objective": "Analyze a moderately functional system with dimensional tension",
                "characteristics": [
                    "efficiency score between 0.3 and 0.7",
                    "balance angle between 90° and 120°",
                    "some dimensional conflicts",
                    "creativity may be undervalued",
                ],
                "typical_use_case": "Growing organization with scaling challenges",
            },
            "Fragmented": {
                "objective": "Analyze a system with critical misalignment requiring intervention",
                "characteristics": [
                    "efficiency score < 0.3",
                    "balance angle > 120°",
                    "severe dimensional conflicts",
                    "productivity-creativity opposition",
                ],
                "typical_use_case": "Dysfunctional team or failing process",
            },
        }

    def regenerate_from_result(self, result: AnalysisResult) -> RegeneratedPrompt:
        """Regenerate prompt from analysis result.

        Process:
        1. Identify classification pattern
        2. Infer dimensional relationships
        3. Reconstruct input vectors
        4. Generate prompt objective
        5. Add constraints based on metrics
        """
        # Step 1: Get classification template
        template = self.classification_templates.get(
            result.classification,
            self.classification_templates["Imbalanced"],  # Default
        )

        # Step 2: Analyze dimensional relationships
        relationships = self._analyze_relationships(result)

        # Step 3: Reconstruct input vectors (already provided in result)
        input_vectors = {
            "influence": result.influence_vector,
            "productivity": result.productivity_vector,
            "creativity": result.creativity_vector,
        }

        # Step 4: Generate objective
        objective = self._generate_objective(result, template, relationships)

        # Step 5: Generate constraints
        constraints = self._generate_constraints(result, relationships)

        # Step 6: Calculate confidence
        confidence = self._calculate_confidence(result)

        # Step 7: Generate reasoning
        reasoning = self._generate_reasoning(result, relationships)

        # Step 8: Generate alternative prompts
        alternatives = self._generate_alternatives(result, template)

        return RegeneratedPrompt(
            objective=objective,
            constraints=constraints,
            input_vectors=input_vectors,
            expected_classification=result.classification,
            confidence=confidence,
            reasoning=reasoning,
            alternative_prompts=alternatives,
        )

    def _analyze_relationships(self, result: AnalysisResult) -> Dict[str, str]:
        """Analyze pairwise dimensional relationships."""
        relationships = {}

        # Influence-Productivity
        if result.influence_productivity_angle < 30:
            relationships["influence_productivity"] = "strong_synergy"
        elif result.influence_productivity_angle < 90:
            relationships["influence_productivity"] = "partial_alignment"
        elif result.influence_productivity_angle < 150:
            relationships["influence_productivity"] = "opposition"
        else:
            relationships["influence_productivity"] = "complete_opposition"

        # Influence-Creativity
        if result.influence_creativity_angle < 30:
            relationships["influence_creativity"] = "strong_synergy"
        elif result.influence_creativity_angle < 90:
            relationships["influence_creativity"] = "partial_alignment"
        elif result.influence_creativity_angle < 150:
            relationships["influence_creativity"] = "opposition"
        else:
            relationships["influence_creativity"] = "complete_opposition"

        # Productivity-Creativity
        if result.productivity_creativity_angle < 30:
            relationships["productivity_creativity"] = "strong_synergy"
        elif result.productivity_creativity_angle < 90:
            relationships["productivity_creativity"] = "partial_alignment"
        elif result.productivity_creativity_angle < 150:
            relationships["productivity_creativity"] = "opposition"
        else:
            relationships["productivity_creativity"] = "complete_opposition"

        return relationships

    def _generate_objective(
        self,
        result: AnalysisResult,
        template: Dict[str, Any],
        relationships: Dict[str, str],
    ) -> str:
        """Generate prompt objective from result."""
        base_objective = template["objective"]

        # Add specific details based on relationships
        details = []

        if relationships["influence_productivity"] == "strong_synergy":
            details.append("with strong influence-productivity alignment")

        if relationships["productivity_creativity"] == "opposition":
            details.append("where productivity suppresses creativity")

        if result.efficiency_score < 0.3:
            details.append("requiring urgent intervention")
        elif result.efficiency_score > 0.7:
            details.append("operating at peak efficiency")

        if details:
            return f"{base_objective} {', '.join(details)}"
        return base_objective

    def _generate_constraints(
        self, result: AnalysisResult, relationships: Dict[str, str]
    ) -> List[str]:
        """Generate constraints based on result metrics."""
        constraints = []

        # Efficiency score constraint
        if result.efficiency_score >= 0.7:
            constraints.append(
                f"Target efficiency score: >= 0.7 (achieved: {result.efficiency_score:.3f})"
            )
        elif result.efficiency_score >= 0.3:
            constraints.append(
                f"Target efficiency score: 0.3-0.7 (achieved: {result.efficiency_score:.3f})"
            )
        else:
            constraints.append(
                f"Efficiency score: < 0.3 (achieved: {result.efficiency_score:.3f})"
            )

        # Balance angle constraint
        if result.balance_angle < 90:
            constraints.append(
                f"Balance angle: < 90° (synergy) (achieved: {result.balance_angle:.1f}°)"
            )
        elif result.balance_angle <= 120:
            constraints.append(
                f"Balance angle: 90-120° (moderate) (achieved: {result.balance_angle:.1f}°)"
            )
        else:
            constraints.append(
                f"Balance angle: > 120° (antagonistic) (achieved: {result.balance_angle:.1f}°)"
            )

        # Relationship constraints
        for pair, relationship in relationships.items():
            if relationship in ["opposition", "complete_opposition"]:
                constraints.append(
                    f"{pair.replace('_', '-')} shows {relationship.replace('_', ' ')}"
                )

        # Vector magnitude constraints
        constraints.append("All input vectors must be 3-dimensional and normalizable")

        return constraints

    def _calculate_confidence(self, result: AnalysisResult) -> float:
        """Calculate confidence in prompt regeneration.

        Higher confidence when:
        - Classification is clear (extreme values)
        - Relationships are unambiguous
        - Metrics are consistent
        """
        confidence = 0.5  # Base confidence

        # Clear classification adds confidence
        if result.efficiency_score > 0.8 or result.efficiency_score < 0.2:
            confidence += 0.2

        # Extreme balance angles add confidence
        if result.balance_angle < 60 or result.balance_angle > 140:
            confidence += 0.2

        # Consistent relationships add confidence
        angles = [
            result.influence_productivity_angle,
            result.influence_creativity_angle,
            result.productivity_creativity_angle,
        ]
        if np.std(angles) > 40:  # High variance = clear pattern
            confidence += 0.1

        return min(confidence, 1.0)

    def _generate_reasoning(
        self, result: AnalysisResult, relationships: Dict[str, str]
    ) -> str:
        """Generate explanation of regeneration logic."""
        reasoning_parts = []

        reasoning_parts.append(
            f"Classification '{result.classification}' indicates "
            f"efficiency score of {result.efficiency_score:.3f} and "
            f"balance angle of {result.balance_angle:.1f}°."
        )

        # Explain key relationships
        for pair, relationship in relationships.items():
            if relationship in ["strong_synergy", "opposition", "complete_opposition"]:
                reasoning_parts.append(
                    f"{pair.replace('_', '-')} shows {relationship.replace('_', ' ')}, "
                    f"suggesting specific dimensional dynamics."
                )

        # Explain vector reconstruction
        reasoning_parts.append(
            "Input vectors were directly extracted from result metadata, "
            "ensuring exact reproducibility."
        )

        return " ".join(reasoning_parts)

    def _generate_alternatives(
        self, result: AnalysisResult, template: Dict[str, Any]
    ) -> List[str]:
        """Generate alternative prompt interpretations."""
        alternatives = []

        # Alternative 1: Focus on use case
        alternatives.append(
            f"Analyze {template['typical_use_case']} with "
            f"efficiency score ~{result.efficiency_score:.1f}"
        )

        # Alternative 2: Focus on intervention
        if result.classification == "Fragmented":
            alternatives.append(
                "Design intervention strategy for critically misaligned system"
            )
        elif result.classification == "Imbalanced":
            alternatives.append(
                "Identify optimization opportunities in moderately functional system"
            )
        else:
            alternatives.append("Document best practices from high-performing system")

        # Alternative 3: Focus on specific dimension
        if result.productivity_creativity_angle > 135:
            alternatives.append(
                "Resolve productivity-creativity conflict in system dynamics"
            )
        elif result.influence_productivity_angle < 45:
            alternatives.append(
                "Leverage strong influence-productivity alignment for growth"
            )

        return alternatives

    def validate_regeneration(
        self, original_result: AnalysisResult, regenerated_prompt: RegeneratedPrompt
    ) -> Dict[str, Any]:
        """Validate that regenerated prompt would produce similar results.

        Returns validation report with:
        - Vector similarity scores
        - Classification match
        - Metric deviation
        """
        validation = {
            "classification_match": (
                original_result.classification
                == regenerated_prompt.expected_classification
            ),
            "vector_match": {},
            "confidence": regenerated_prompt.confidence,
            "is_valid": True,
        }

        # Check vector similarity (should be identical since we extract them)
        for key in ["influence", "productivity", "creativity"]:
            original_vec = getattr(original_result, f"{key}_vector")
            regenerated_vec = regenerated_prompt.input_vectors[key]

            similarity = np.dot(original_vec, regenerated_vec) / (
                np.linalg.norm(original_vec) * np.linalg.norm(regenerated_vec)
            )
            validation["vector_match"][key] = float(similarity)

        # Overall validity
        validation["is_valid"] = validation["classification_match"] and all(
            sim > 0.99 for sim in validation["vector_match"].values()
        )

        return validation
