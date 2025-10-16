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

"""Unit tests for vector_ops module.

All tests use rtol=1e-7 for numeric precision as specified.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.vector_ops import angle_between, compute_efficiency_vector, normalize


class TestNormalize:
    """Tests for normalize function."""

    def test_simple_vector(self) -> None:
        """Test normalization of [3, 4, 0]."""
        vec = np.array([3.0, 4.0, 0.0])
        result = normalize(vec)

        # Expected: [0.6, 0.8, 0.0]
        expected = np.array([0.6, 0.8, 0.0])
        np.testing.assert_allclose(result, expected, rtol=1e-7)

        # Verify unit length
        assert np.isclose(np.linalg.norm(result), 1.0, rtol=1e-7)

    def test_already_normalized(self) -> None:
        """Test that normalizing a unit vector returns itself."""
        vec = np.array([1.0, 0.0, 0.0])
        result = normalize(vec)

        np.testing.assert_allclose(result, vec, rtol=1e-7)

    def test_negative_components(self) -> None:
        """Test normalization with negative values."""
        vec = np.array([-3.0, 4.0, 0.0])
        result = normalize(vec)

        expected = np.array([-0.6, 0.8, 0.0])
        np.testing.assert_allclose(result, expected, rtol=1e-7)

    def test_zero_vector_raises(self) -> None:
        """Test that zero vector raises ValueError."""
        vec = np.array([0.0, 0.0, 0.0])

        with pytest.raises(ValueError, match="zero vector"):
            normalize(vec)

    def test_near_zero_vector_raises(self) -> None:
        """Test that near-zero vector raises ValueError."""
        vec = np.array([1e-13, 1e-13, 1e-13])

        with pytest.raises(ValueError, match="zero vector"):
            normalize(vec)


class TestAngleBetween:
    """Tests for angle_between function."""

    def test_orthogonal_vectors(self) -> None:
        """Test angle between orthogonal vectors (90°)."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])

        angle = angle_between(v1, v2, degrees=True)
        assert np.isclose(angle, 90.0, rtol=1e-7)

    def test_parallel_vectors(self) -> None:
        """Test angle between parallel vectors (0°)."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([2.0, 0.0, 0.0])

        angle = angle_between(v1, v2, degrees=True)
        assert np.isclose(angle, 0.0, rtol=1e-7)

    def test_opposite_vectors(self) -> None:
        """Test angle between opposite vectors (180°)."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([-1.0, 0.0, 0.0])

        angle = angle_between(v1, v2, degrees=True)
        assert np.isclose(angle, 180.0, rtol=1e-7)

    def test_45_degree_angle(self) -> None:
        """Test 45° angle between vectors."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([1.0, 1.0, 0.0])

        angle = angle_between(v1, v2, degrees=True)
        assert np.isclose(angle, 45.0, rtol=1e-7)

    def test_radians_mode(self) -> None:
        """Test angle calculation in radians."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.0, 1.0, 0.0])

        angle = angle_between(v1, v2, degrees=False)
        assert np.isclose(angle, np.pi / 2, rtol=1e-7)

    def test_non_normalized_input(self) -> None:
        """Test that function handles non-normalized vectors."""
        v1 = np.array([3.0, 0.0, 0.0])
        v2 = np.array([0.0, 5.0, 0.0])

        angle = angle_between(v1, v2, degrees=True)
        assert np.isclose(angle, 90.0, rtol=1e-7)

    def test_numeric_stability(self) -> None:
        """Test numeric stability with nearly parallel vectors."""
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([0.9999999, 0.0001, 0.0])

        # Should not raise domain error
        angle = angle_between(v1, v2, degrees=True)
        assert 0.0 <= angle <= 180.0


class TestComputeEfficiencyVector:
    """Tests for compute_efficiency_vector function."""

    def test_orthogonal_base_vectors(self) -> None:
        """Test efficiency vector for orthogonal base vectors."""
        influence = np.array([1.0, 0.0, 0.0])
        productivity = np.array([0.0, 1.0, 0.0])
        creativity = np.array([0.0, 0.0, 1.0])

        result = compute_efficiency_vector(influence, productivity, creativity)

        # Should be normalized
        assert np.isclose(np.linalg.norm(result), 1.0, rtol=1e-7)

        # Should be [1/√3, 1/√3, 1/√3]
        expected = np.array([1.0, 1.0, 1.0]) / np.sqrt(3)
        np.testing.assert_allclose(result, expected, rtol=1e-7)

    def test_aligned_vectors(self) -> None:
        """Test efficiency vector when all inputs are aligned."""
        vec = np.array([1.0, 0.0, 0.0])

        result = compute_efficiency_vector(vec, vec, vec)

        # Should be normalized and equal to input
        assert np.isclose(np.linalg.norm(result), 1.0, rtol=1e-7)
        np.testing.assert_allclose(result, vec, rtol=1e-7)

    def test_default_paper_vectors(self) -> None:
        """Test with default vectors from paper."""
        influence = np.array([0.6, 0.8, 0.5])
        productivity = np.array([0.9, 0.4, 0.3])
        creativity = np.array([-0.3, 0.0, -0.2])

        result = compute_efficiency_vector(influence, productivity, creativity)

        # Should be normalized
        assert np.isclose(np.linalg.norm(result), 1.0, rtol=1e-7)

        # Verify it's the average of normalized inputs
        inf_n = influence / np.linalg.norm(influence)
        prod_n = productivity / np.linalg.norm(productivity)
        crea_n = creativity / np.linalg.norm(creativity)

        avg = (inf_n + prod_n + crea_n) / 3.0
        expected = avg / np.linalg.norm(avg)

        np.testing.assert_allclose(result, expected, rtol=1e-7)

    def test_non_normalized_input(self) -> None:
        """Test that function handles non-normalized inputs correctly."""
        influence = np.array([6.0, 8.0, 5.0])  # 10x scaled
        productivity = np.array([9.0, 4.0, 3.0])  # 10x scaled
        creativity = np.array([-3.0, 0.0, -2.0])  # 10x scaled

        result = compute_efficiency_vector(influence, productivity, creativity)

        # Should still be normalized
        assert np.isclose(np.linalg.norm(result), 1.0, rtol=1e-7)


class TestIntegration:
    """Integration tests combining multiple operations."""

    def test_full_pipeline(self) -> None:
        """Test complete pipeline: normalize → angles → efficiency."""
        # Base vectors
        influence = np.array([0.6, 0.8, 0.5])
        productivity = np.array([0.9, 0.4, 0.3])
        creativity = np.array([-0.3, 0.0, -0.2])

        # Normalize
        inf_n = normalize(influence)
        prod_n = normalize(productivity)
        crea_n = normalize(creativity)

        # Compute angles
        ang_ip = angle_between(inf_n, prod_n)
        ang_ic = angle_between(inf_n, crea_n)
        ang_pc = angle_between(prod_n, crea_n)

        # All angles should be in valid range
        assert 0.0 <= ang_ip <= 180.0
        assert 0.0 <= ang_ic <= 180.0
        assert 0.0 <= ang_pc <= 180.0

        # Compute efficiency
        eff = compute_efficiency_vector(inf_n, prod_n, crea_n)

        # Verify properties
        assert np.isclose(np.linalg.norm(eff), 1.0, rtol=1e-7)

        # Efficiency score (mean dot product)
        score = np.mean(
            [
                np.dot(eff, inf_n),
                np.dot(eff, prod_n),
                np.dot(eff, crea_n),
            ]
        )

        assert -1.0 <= score <= 1.0
