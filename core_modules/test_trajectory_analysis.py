#!/usr/bin/env python3
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

"""Unit tests for trajectory_analysis module.

Tests cover:
- Data model validation (TrajectoryPoint, VectorSet, EfficiencySummary)
- Vector operations (normalize, angle_between, compute_efficiency_vector)
- Metrics calculation (calculate_efficiency_metrics)
- Edge cases and error handling

Run with: pytest test_trajectory_analysis.py -v
"""

import numpy as np
import pytest

from trajectory_analysis import (
    EfficiencySummary,
    TrajectoryPoint,
    VectorSet,
    angle_between,
    calculate_efficiency_metrics,
    compute_efficiency_vector,
    get_default_trajectory_data,
    normalize,
)

# ============================================================================
# DATA MODEL TESTS
# ============================================================================


class TestTrajectoryPoint:
    """Tests for TrajectoryPoint dataclass."""

    def test_valid_point(self):
        """Test creating a valid trajectory point."""
        point = TrajectoryPoint(1, "Test", 100.0, 0.5, 0.5, 0.5)
        assert point.index == 1
        assert point.archetype == "Test"
        assert point.frequency == 100.0
        assert point.x == 0.5
        assert point.y == 0.5
        assert point.z == 0.5

    def test_vector_property(self):
        """Test vector property returns correct numpy array."""
        point = TrajectoryPoint(1, "Test", 100.0, 0.5, 0.6, 0.7)
        vec = point.vector
        assert isinstance(vec, np.ndarray)
        assert vec.shape == (3,)
        np.testing.assert_array_equal(vec, [0.5, 0.6, 0.7])

    def test_invalid_index(self):
        """Test that index < 1 raises ValueError."""
        with pytest.raises(ValueError, match="Index must be >= 1"):
            TrajectoryPoint(0, "Test", 100.0, 0.5, 0.5, 0.5)

    def test_invalid_frequency(self):
        """Test that frequency <= 0 raises ValueError."""
        with pytest.raises(ValueError, match="Frequency must be positive"):
            TrajectoryPoint(1, "Test", -10.0, 0.5, 0.5, 0.5)

    def test_empty_archetype(self):
        """Test that empty archetype raises ValueError."""
        with pytest.raises(ValueError, match="Archetype cannot be empty"):
            TrajectoryPoint(1, "", 100.0, 0.5, 0.5, 0.5)

    def test_immutability(self):
        """Test that TrajectoryPoint is immutable (frozen)."""
        point = TrajectoryPoint(1, "Test", 100.0, 0.5, 0.5, 0.5)
        with pytest.raises(AttributeError):
            point.x = 0.8  # type: ignore


class TestVectorSet:
    """Tests for VectorSet dataclass."""

    def test_valid_vector_set(self):
        """Test creating a valid vector set."""
        influence = np.array([1.0, 0.0, 0.0])
        productivity = np.array([0.0, 1.0, 0.0])
        creativity = np.array([0.0, 0.0, 1.0])
        # Properly normalized [1,1,1] vector
        efficiency = np.array([1.0, 1.0, 1.0]) / np.sqrt(3)

        vectors = VectorSet(influence, productivity, creativity, efficiency)
        np.testing.assert_array_equal(vectors.influence, influence)

    def test_non_normalized_vector_rejected(self):
        """Test that non-normalized vectors raise ValueError."""
        influence = np.array([2.0, 0.0, 0.0])  # Not normalized
        productivity = np.array([0.0, 1.0, 0.0])
        creativity = np.array([0.0, 0.0, 1.0])
        efficiency = np.array([0.577, 0.577, 0.577])

        with pytest.raises(ValueError, match="must be normalized"):
            VectorSet(influence, productivity, creativity, efficiency)

    def test_wrong_dimension_rejected(self):
        """Test that non-3D vectors raise ValueError."""
        influence = np.array([1.0, 0.0])  # 2D instead of 3D
        productivity = np.array([0.0, 1.0, 0.0])
        creativity = np.array([0.0, 0.0, 1.0])
        efficiency = np.array([0.577, 0.577, 0.577])

        with pytest.raises(ValueError, match="must be 3D vector"):
            VectorSet(influence, productivity, creativity, efficiency)


class TestEfficiencySummary:
    """Tests for EfficiencySummary dataclass."""

    def test_valid_summary(self):
        """Test creating a valid efficiency summary."""
        summary = EfficiencySummary(
            efficiency_vector=np.array([0.577, 0.577, 0.577]),
            efficiency_score=0.75,
            balance_factor_degrees=90.0,
            angle_influence_productivity=45.0,
            angle_influence_creativity=90.0,
            angle_productivity_creativity=90.0,
        )
        assert summary.efficiency_score == 0.75
        assert summary.balance_factor_degrees == 90.0

    def test_interpretation_high_alignment(self):
        """Test interpretation for high alignment scenario."""
        summary = EfficiencySummary(
            efficiency_vector=np.array([0.577, 0.577, 0.577]),
            efficiency_score=0.8,  # High
            balance_factor_degrees=50.0,  # High synergy
            angle_influence_productivity=30.0,
            angle_influence_creativity=40.0,
            angle_productivity_creativity=50.0,
        )
        interp = summary.interpretation()
        assert "High alignment" in interp
        assert "High synergy" in interp

    def test_interpretation_low_alignment(self):
        """Test interpretation for low alignment scenario."""
        summary = EfficiencySummary(
            efficiency_vector=np.array([0.577, 0.577, 0.577]),
            efficiency_score=0.1,  # Low
            balance_factor_degrees=140.0,  # Antagonistic
            angle_influence_productivity=150.0,
            angle_influence_creativity=140.0,
            angle_productivity_creativity=140.0,
        )
        interp = summary.interpretation()
        assert "Low alignment" in interp
        assert "Antagonistic" in interp

    def test_to_dict(self):
        """Test JSON serialization."""
        summary = EfficiencySummary(
            efficiency_vector=np.array([0.577, 0.577, 0.577]),
            efficiency_score=0.75,
            balance_factor_degrees=90.0,
            angle_influence_productivity=45.0,
            angle_influence_creativity=90.0,
            angle_productivity_creativity=90.0,
        )
        result = summary.to_dict()
        assert isinstance(result, dict)
        assert "efficiency_vector" in result
        assert "efficiency_score" in result
        assert "interpretation" in result
        assert isinstance(result["efficiency_vector"], list)


# ============================================================================
# VECTOR OPERATIONS TESTS
# ============================================================================


class TestNormalize:
    """Tests for normalize function."""

    def test_normalize_simple(self):
        """Test normalizing a simple vector."""
        vec = np.array([3.0, 4.0, 0.0])
        normalized = normalize(vec)
        assert np.isclose(np.linalg.norm(normalized), 1.0)
        np.testing.assert_array_almost_equal(normalized, [0.6, 0.8, 0.0])

    def test_normalize_already_normalized(self):
        """Test normalizing an already normalized vector."""
        vec = np.array([1.0, 0.0, 0.0])
        normalized = normalize(vec)
        np.testing.assert_array_almost_equal(normalized, vec)

    def test_normalize_zero_vector(self):
        """Test that zero vector raises ValueError."""
        vec = np.array([0.0, 0.0, 0.0])
        with pytest.raises(ValueError, match="Cannot normalize zero vector"):
            normalize(vec)

    def test_normalize_negative_values(self):
        """Test normalizing vector with negative values."""
        vec = np.array([-3.0, 4.0, 0.0])
        normalized = normalize(vec)
        assert np.isclose(np.linalg.norm(normalized), 1.0)
        np.testing.assert_array_almost_equal(normalized, [-0.6, 0.8, 0.0])


class TestAngleBetween:
    """Tests for angle_between function."""

    def test_angle_orthogonal(self):
        """Test angle between orthogonal vectors."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])
        angle = angle_between(v1, v2)
        assert np.isclose(angle, 90.0)

    def test_angle_parallel(self):
        """Test angle between parallel vectors."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([2.0, 0.0, 0.0])
        angle = angle_between(v1, v2)
        assert np.isclose(angle, 0.0)

    def test_angle_opposite(self):
        """Test angle between opposite vectors."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([-1.0, 0.0, 0.0])
        angle = angle_between(v1, v2)
        assert np.isclose(angle, 180.0)

    def test_angle_45_degrees(self):
        """Test angle at 45 degrees."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([1.0, 1.0, 0.0])
        angle = angle_between(v1, v2)
        assert np.isclose(angle, 45.0, atol=0.1)

    def test_angle_non_normalized_input(self):
        """Test that function handles non-normalized inputs."""
        v1 = np.array([3.0, 0.0, 0.0])
        v2 = np.array([0.0, 5.0, 0.0])
        angle = angle_between(v1, v2)
        assert np.isclose(angle, 90.0)


class TestComputeEfficiencyVector:
    """Tests for compute_efficiency_vector function."""

    def test_efficiency_orthogonal_vectors(self):
        """Test efficiency vector for orthogonal base vectors."""
        influence = np.array([1.0, 0.0, 0.0])
        productivity = np.array([0.0, 1.0, 0.0])
        creativity = np.array([0.0, 0.0, 1.0])

        efficiency = compute_efficiency_vector(influence, productivity, creativity)

        # Should be normalized
        assert np.isclose(np.linalg.norm(efficiency), 1.0)

        # Should be roughly [1/√3, 1/√3, 1/√3]
        expected = np.array([1.0, 1.0, 1.0]) / np.sqrt(3)
        np.testing.assert_array_almost_equal(efficiency, expected)

    def test_efficiency_aligned_vectors(self):
        """Test efficiency vector when all vectors are aligned."""
        vec = np.array([1.0, 0.0, 0.0])

        efficiency = compute_efficiency_vector(vec, vec, vec)

        # Should be normalized and equal to the input
        assert np.isclose(np.linalg.norm(efficiency), 1.0)
        np.testing.assert_array_almost_equal(efficiency, vec)


# ============================================================================
# METRICS CALCULATION TESTS
# ============================================================================


class TestCalculateEfficiencyMetrics:
    """Tests for calculate_efficiency_metrics function."""

    def test_default_trajectory_data(self):
        """Test metrics calculation with default trajectory data."""
        points = get_default_trajectory_data()
        summary = calculate_efficiency_metrics(points)

        # Verify output structure
        assert isinstance(summary, EfficiencySummary)
        assert summary.efficiency_vector.shape == (3,)
        assert -1.0 <= summary.efficiency_score <= 1.0
        assert 0.0 <= summary.balance_factor_degrees <= 180.0

    def test_custom_base_vectors(self):
        """Test metrics with custom base vectors."""
        points = get_default_trajectory_data()
        custom_influence = np.array([1.0, 0.0, 0.0])
        custom_productivity = np.array([0.0, 1.0, 0.0])

        summary = calculate_efficiency_metrics(
            points,
            influence_base=custom_influence,
            productivity_base=custom_productivity,
        )

        assert isinstance(summary, EfficiencySummary)

    def test_missing_creativity_archetype(self):
        """Test that missing creativity archetype raises ValueError."""
        points = [TrajectoryPoint(1, "Test", 100.0, 0.5, 0.5, 0.5)]

        with pytest.raises(ValueError, match="not found in trajectory"):
            calculate_efficiency_metrics(points, creativity_archetype="NonExistent")

    def test_metrics_reproducibility(self):
        """Test that metrics are reproducible."""
        points = get_default_trajectory_data()

        summary1 = calculate_efficiency_metrics(points)
        summary2 = calculate_efficiency_metrics(points)

        np.testing.assert_array_almost_equal(summary1.efficiency_vector, summary2.efficiency_vector)
        assert summary1.efficiency_score == summary2.efficiency_score


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestIntegration:
    """Integration tests for the complete workflow."""

    def test_full_workflow(self):
        """Test complete workflow from data to metrics."""
        # Load data
        points = get_default_trajectory_data()
        assert len(points) == 15

        # Calculate metrics
        summary = calculate_efficiency_metrics(points)

        # Verify all components
        assert isinstance(summary, EfficiencySummary)
        assert np.isclose(np.linalg.norm(summary.efficiency_vector), 1.0)

        # Verify interpretation is generated
        interp = summary.interpretation()
        assert len(interp) > 0

        # Verify JSON serialization
        result_dict = summary.to_dict()
        assert "efficiency_score" in result_dict
        assert "angles" in result_dict

    def test_expected_values_match_original(self):
        """Test that refactored code produces same results as original."""
        points = get_default_trajectory_data()
        summary = calculate_efficiency_metrics(points)

        # Expected values from original code
        # Influence: [0.537, 0.716, 0.447]
        # Productivity: [0.874, 0.389, 0.292]
        # Creativity: [-0.832, 0.000, -0.555]
        # Efficiency: [0.459, 0.877, 0.146]

        expected_efficiency = np.array([0.459, 0.877, 0.146])
        np.testing.assert_array_almost_equal(summary.efficiency_vector, expected_efficiency, decimal=2)

        # Efficiency score ≈ 0.42
        assert 0.40 <= summary.efficiency_score <= 0.45

        # Balance factor ≈ 105°
        assert 100.0 <= summary.balance_factor_degrees <= 110.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
