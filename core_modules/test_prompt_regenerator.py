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

"""Tests for prompt regeneration from results."""

from __future__ import annotations

from src.prompt_regenerator import (
    AnalysisResult,
    PromptRegenerator,
    RegeneratedPrompt,
)


class TestPromptRegenerator:
    """Test prompt regeneration from analysis results."""

    def test_regenerate_aligned_system(self):
        """Test regeneration for aligned system."""
        regenerator = PromptRegenerator()

        # Create aligned result
        result = AnalysisResult(
            classification="Aligned",
            efficiency_score=0.85,
            balance_angle=75.0,
            influence_productivity_angle=25.0,
            influence_creativity_angle=80.0,
            productivity_creativity_angle=70.0,
            influence_vector=[0.6, 0.8, 0.5],
            productivity_vector=[0.9, 0.4, 0.3],
            creativity_vector=[0.3, 0.7, 0.6],
            efficiency_vector=[0.6, 0.65, 0.47],
            timestamp="2025-10-16T00:00:00Z",
            seed=42,
        )

        prompt = regenerator.regenerate_from_result(result)

        # Check structure
        assert isinstance(prompt, RegeneratedPrompt)
        assert prompt.expected_classification == "Aligned"
        assert "optimal" in prompt.objective.lower() or "synergy" in prompt.objective.lower()
        assert len(prompt.constraints) > 0
        assert len(prompt.alternative_prompts) > 0

        # Check confidence
        assert 0.0 <= prompt.confidence <= 1.0
        assert prompt.confidence > 0.5, "Should have reasonable confidence"

    def test_regenerate_imbalanced_system(self):
        """Test regeneration for imbalanced system."""
        regenerator = PromptRegenerator()

        # Create imbalanced result (from our actual experiment)
        result = AnalysisResult(
            classification="Imbalanced",
            efficiency_score=0.420,
            balance_angle=105.14,
            influence_productivity_angle=28.67,
            influence_creativity_angle=133.99,
            productivity_creativity_angle=152.74,
            influence_vector=[0.537, 0.716, 0.447],
            productivity_vector=[0.874, 0.389, 0.292],
            creativity_vector=[-0.832, 0.0, -0.555],
            efficiency_vector=[0.459, 0.876, 0.146],
            timestamp="2025-10-16T00:29:43Z",
            seed=42,
        )

        prompt = regenerator.regenerate_from_result(result)

        # Check classification match
        assert prompt.expected_classification == "Imbalanced"

        # Check that productivity-creativity opposition is mentioned
        assert any("productivity" in c.lower() and "creativity" in c.lower() for c in prompt.constraints)

        # Check reasoning mentions key relationships
        assert "productivity" in prompt.reasoning.lower()
        assert "creativity" in prompt.reasoning.lower()

    def test_regenerate_fragmented_system(self):
        """Test regeneration for fragmented system."""
        regenerator = PromptRegenerator()

        # Create fragmented result
        result = AnalysisResult(
            classification="Fragmented",
            efficiency_score=0.15,
            balance_angle=145.0,
            influence_productivity_angle=160.0,
            influence_creativity_angle=155.0,
            productivity_creativity_angle=170.0,
            influence_vector=[0.5, 0.5, 0.7],
            productivity_vector=[-0.6, -0.6, -0.5],
            creativity_vector=[-0.4, -0.7, -0.6],
            efficiency_vector=[-0.17, -0.27, -0.20],
            timestamp="2025-10-16T00:00:00Z",
            seed=42,
        )

        prompt = regenerator.regenerate_from_result(result)

        # Check classification
        assert prompt.expected_classification == "Fragmented"

        # Should mention intervention or critical state
        assert any("intervention" in alt.lower() or "critical" in alt.lower() for alt in prompt.alternative_prompts)

    def test_relationship_analysis(self):
        """Test dimensional relationship analysis."""
        regenerator = PromptRegenerator()

        # Create result with clear relationships
        result = AnalysisResult(
            classification="Imbalanced",
            efficiency_score=0.5,
            balance_angle=100.0,
            influence_productivity_angle=25.0,  # Strong synergy
            influence_creativity_angle=60.0,  # Partial alignment
            productivity_creativity_angle=160.0,  # Complete opposition
            influence_vector=[0.6, 0.8, 0.5],
            productivity_vector=[0.9, 0.4, 0.3],
            creativity_vector=[-0.3, 0.0, -0.2],
            efficiency_vector=[0.4, 0.4, 0.2],
        )

        relationships = regenerator._analyze_relationships(result)

        # Check relationship detection
        assert relationships["influence_productivity"] == "strong_synergy"
        assert relationships["influence_creativity"] == "partial_alignment"
        assert relationships["productivity_creativity"] == "complete_opposition"

    def test_confidence_calculation(self):
        """Test confidence calculation logic."""
        regenerator = PromptRegenerator()

        # High confidence case (extreme values)
        high_conf_result = AnalysisResult(
            classification="Aligned",
            efficiency_score=0.95,  # Very high
            balance_angle=45.0,  # Very low
            influence_productivity_angle=20.0,
            influence_creativity_angle=120.0,
            productivity_creativity_angle=140.0,
            influence_vector=[0.6, 0.8, 0.5],
            productivity_vector=[0.9, 0.4, 0.3],
            creativity_vector=[0.3, 0.7, 0.6],
            efficiency_vector=[0.6, 0.65, 0.47],
        )

        high_conf = regenerator._calculate_confidence(high_conf_result)

        # Low confidence case (middle values)
        low_conf_result = AnalysisResult(
            classification="Imbalanced",
            efficiency_score=0.5,  # Middle
            balance_angle=100.0,  # Middle
            influence_productivity_angle=90.0,
            influence_creativity_angle=90.0,
            productivity_creativity_angle=90.0,
            influence_vector=[0.6, 0.8, 0.5],
            productivity_vector=[0.9, 0.4, 0.3],
            creativity_vector=[0.3, 0.7, 0.6],
            efficiency_vector=[0.6, 0.65, 0.47],
        )

        low_conf = regenerator._calculate_confidence(low_conf_result)

        # High confidence should be higher
        assert high_conf > low_conf
        assert high_conf > 0.7
        assert low_conf < 0.7

    def test_vector_preservation(self):
        """Test that input vectors are preserved exactly."""
        regenerator = PromptRegenerator()

        result = AnalysisResult(
            classification="Aligned",
            efficiency_score=0.8,
            balance_angle=70.0,
            influence_productivity_angle=30.0,
            influence_creativity_angle=80.0,
            productivity_creativity_angle=75.0,
            influence_vector=[0.537, 0.716, 0.447],
            productivity_vector=[0.874, 0.389, 0.292],
            creativity_vector=[-0.832, 0.0, -0.555],
            efficiency_vector=[0.459, 0.876, 0.146],
        )

        prompt = regenerator.regenerate_from_result(result)

        # Vectors should be identical
        assert prompt.input_vectors["influence"] == result.influence_vector
        assert prompt.input_vectors["productivity"] == result.productivity_vector
        assert prompt.input_vectors["creativity"] == result.creativity_vector

    def test_validation(self):
        """Test prompt regeneration validation."""
        regenerator = PromptRegenerator()

        result = AnalysisResult(
            classification="Imbalanced",
            efficiency_score=0.420,
            balance_angle=105.14,
            influence_productivity_angle=28.67,
            influence_creativity_angle=133.99,
            productivity_creativity_angle=152.74,
            influence_vector=[0.537, 0.716, 0.447],
            productivity_vector=[0.874, 0.389, 0.292],
            creativity_vector=[-0.832, 0.0, -0.555],
            efficiency_vector=[0.459, 0.876, 0.146],
        )

        prompt = regenerator.regenerate_from_result(result)
        validation = regenerator.validate_regeneration(result, prompt)

        # Check validation structure
        assert "classification_match" in validation
        assert "vector_match" in validation
        assert "is_valid" in validation

        # Should be valid
        assert validation["is_valid"]
        assert validation["classification_match"]

        # Vector similarity should be perfect
        for key in ["influence", "productivity", "creativity"]:
            assert validation["vector_match"][key] > 0.99

    def test_alternative_prompts_generation(self):
        """Test that alternative prompts are meaningful."""
        regenerator = PromptRegenerator()

        result = AnalysisResult(
            classification="Fragmented",
            efficiency_score=0.2,
            balance_angle=140.0,
            influence_productivity_angle=150.0,
            influence_creativity_angle=145.0,
            productivity_creativity_angle=165.0,
            influence_vector=[0.5, 0.5, 0.7],
            productivity_vector=[-0.6, -0.6, -0.5],
            creativity_vector=[-0.4, -0.7, -0.6],
            efficiency_vector=[-0.17, -0.27, -0.20],
        )

        prompt = regenerator.regenerate_from_result(result)

        # Should have at least 2 alternatives
        assert len(prompt.alternative_prompts) >= 2

        # Alternatives should be different from main objective
        for alt in prompt.alternative_prompts:
            assert alt != prompt.objective
            assert len(alt) > 10  # Meaningful length


class TestBidirectionalPath:
    """Test that paths are truly bidirectional (A→X and X→A)."""

    def test_forward_backward_consistency(self):
        """Test that regenerated prompt produces equivalent result."""
        regenerator = PromptRegenerator()

        # Original result
        original_result = AnalysisResult(
            classification="Imbalanced",
            efficiency_score=0.420,
            balance_angle=105.14,
            influence_productivity_angle=28.67,
            influence_creativity_angle=133.99,
            productivity_creativity_angle=152.74,
            influence_vector=[0.537, 0.716, 0.447],
            productivity_vector=[0.874, 0.389, 0.292],
            creativity_vector=[-0.832, 0.0, -0.555],
            efficiency_vector=[0.459, 0.876, 0.146],
        )

        # Regenerate prompt (backward path: Result → Prompt)
        regenerated_prompt = regenerator.regenerate_from_result(original_result)

        # Validate (forward path: Prompt → Result)
        validation = regenerator.validate_regeneration(original_result, regenerated_prompt)

        # Bidirectional consistency check
        assert validation["is_valid"], "Bidirectional path should be consistent"
        assert validation["classification_match"]

        # Vectors should match (path A→X→A preserves data)
        for key, similarity in validation["vector_match"].items():
            assert similarity > 0.99, f"{key} vector should be preserved"

    def test_multiple_regeneration_cycles(self):
        """Test that multiple regeneration cycles remain stable."""
        regenerator = PromptRegenerator()

        # Start with a result
        result1 = AnalysisResult(
            classification="Aligned",
            efficiency_score=0.85,
            balance_angle=75.0,
            influence_productivity_angle=25.0,
            influence_creativity_angle=80.0,
            productivity_creativity_angle=70.0,
            influence_vector=[0.6, 0.8, 0.5],
            productivity_vector=[0.9, 0.4, 0.3],
            creativity_vector=[0.3, 0.7, 0.6],
            efficiency_vector=[0.6, 0.65, 0.47],
        )

        # Cycle 1: Result → Prompt
        prompt1 = regenerator.regenerate_from_result(result1)

        # Cycle 2: Use same vectors to create new result
        result2 = AnalysisResult(
            classification=prompt1.expected_classification,
            efficiency_score=result1.efficiency_score,
            balance_angle=result1.balance_angle,
            influence_productivity_angle=result1.influence_productivity_angle,
            influence_creativity_angle=result1.influence_creativity_angle,
            productivity_creativity_angle=result1.productivity_creativity_angle,
            influence_vector=prompt1.input_vectors["influence"],
            productivity_vector=prompt1.input_vectors["productivity"],
            creativity_vector=prompt1.input_vectors["creativity"],
            efficiency_vector=result1.efficiency_vector,
        )

        # Cycle 3: Result → Prompt again
        prompt2 = regenerator.regenerate_from_result(result2)

        # Should be stable across cycles
        assert prompt1.expected_classification == prompt2.expected_classification
        assert prompt1.input_vectors == prompt2.input_vectors
