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

"""Tests for trajectory optimization comparing Data-Driven vs Fast Compounding."""

from __future__ import annotations

import numpy as np

from src.trajectory_optimizer import (
    OptimizationMethod,
    TrajectoryOptimizer,
)


class TestTrajectoryOptimizer:
    """Test trajectory optimization strategies."""

    def test_data_driven_characteristics(self):
        """Test that data-driven method has expected characteristics."""
        optimizer = TrajectoryOptimizer(seed=42)
        result = optimizer.simulate_trajectory(
            OptimizationMethod.DATA_DRIVEN, num_steps=20
        )

        # High attention
        avg_attention = np.mean([d.attention_spent for d in result.decisions])
        assert avg_attention > 0.6, "Data-driven should have high attention"

        # High cognitive load
        avg_load = result.total_cognitive_load / result.total_steps
        assert avg_load > 0.5, "Data-driven should have high cognitive load"

        # Consistent quality (low variance)
        qualities = [d.quality for d in result.decisions]
        quality_std = np.std(qualities)
        assert quality_std < 0.15, "Data-driven should have consistent quality"

    def test_fast_compound_characteristics(self):
        """Test that fast compounding has expected characteristics."""
        optimizer = TrajectoryOptimizer(seed=42)
        result = optimizer.simulate_trajectory(
            OptimizationMethod.FAST_COMPOUND, num_steps=20
        )

        # Low attention
        avg_attention = np.mean([d.attention_spent for d in result.decisions])
        assert avg_attention < 0.5, "Fast compound should have low attention"

        # Low cognitive load
        avg_load = result.total_cognitive_load / result.total_steps
        assert avg_load < 0.4, "Fast compound should have low cognitive load"

        # Quality improves over time (positive slope)
        assert result.learning_curve_slope > 0, "Fast compound should show learning"

    def test_compounding_effect(self):
        """Test that fast compounding shows exponential improvement."""
        optimizer = TrajectoryOptimizer(seed=42)
        result = optimizer.simulate_trajectory(
            OptimizationMethod.FAST_COMPOUND, num_steps=30
        )

        # Early vs late quality
        early_quality = np.mean([d.quality for d in result.decisions[:10]])
        late_quality = np.mean([d.quality for d in result.decisions[-10:]])

        improvement = late_quality - early_quality
        assert improvement > 0.15, "Fast compound should show significant improvement"

        # Compound gain should be substantial
        assert result.compound_gain > 1.0, "Compound gain should accumulate"

    def test_time_efficiency(self):
        """Test that fast compounding is faster."""
        optimizer = TrajectoryOptimizer(seed=42)

        dda_result = optimizer.simulate_trajectory(
            OptimizationMethod.DATA_DRIVEN, num_steps=20
        )
        fc_result = optimizer.simulate_trajectory(
            OptimizationMethod.FAST_COMPOUND, num_steps=20
        )

        # Fast compound should be significantly faster
        time_saved = dda_result.total_time - fc_result.total_time
        assert time_saved > 5.0, "Fast compound should save significant time"

        # Efficiency ratio should favor fast compound
        assert fc_result.efficiency_ratio > dda_result.efficiency_ratio

    def test_longer_trajectories_favor_fast_compound(self):
        """Test that fast compound advantage increases with trajectory length."""
        optimizer = TrajectoryOptimizer(seed=42)

        # Short trajectory
        short_dda = optimizer.simulate_trajectory(
            OptimizationMethod.DATA_DRIVEN, num_steps=10
        )
        short_fc = optimizer.simulate_trajectory(
            OptimizationMethod.FAST_COMPOUND, num_steps=10
        )

        # Long trajectory
        long_dda = optimizer.simulate_trajectory(
            OptimizationMethod.DATA_DRIVEN, num_steps=50
        )
        long_fc = optimizer.simulate_trajectory(
            OptimizationMethod.FAST_COMPOUND, num_steps=50
        )

        # Calculate quality advantage
        short_advantage = short_fc.final_quality - short_dda.final_quality
        long_advantage = long_fc.final_quality - long_dda.final_quality

        # Long trajectory should show greater advantage for FC
        assert long_advantage > short_advantage, (
            "Fast compound advantage should increase with trajectory length"
        )

    def test_compare_methods(self):
        """Test method comparison across multiple trials."""
        optimizer = TrajectoryOptimizer(seed=42)
        comparison = optimizer.compare_methods(num_steps=20, num_trials=5)

        # Check structure
        assert "data_driven" in comparison
        assert "fast_compound" in comparison
        assert "advantages" in comparison

        # Fast compound should save time
        assert comparison["advantages"]["fc_time_saved"] > 0

        # Fast compound should save cognitive load
        assert comparison["advantages"]["fc_cognitive_saved"] > 0

        # Fast compound should have efficiency gain
        assert comparison["advantages"]["fc_efficiency_gain"] > 0

    def test_against_the_clock(self):
        """Test time-constrained optimization."""
        optimizer = TrajectoryOptimizer(seed=42)
        results = optimizer.against_the_clock(time_budget=30.0, decision_time_limit=2.0)

        # Both methods should complete
        assert "data_driven" in results
        assert "fast_compound" in results

        # Fast compound should complete more steps
        fc_steps = results["fast_compound"].total_steps
        dda_steps = results["data_driven"].total_steps

        assert fc_steps > dda_steps, (
            "Fast compound should complete more steps in same time"
        )

        # Both should respect time budget
        assert results["data_driven"].total_time <= 30.0
        assert results["fast_compound"].total_time <= 30.0

    def test_reproducibility(self):
        """Test that same seed produces identical results."""
        optimizer1 = TrajectoryOptimizer(seed=42)
        optimizer2 = TrajectoryOptimizer(seed=42)

        result1 = optimizer1.simulate_trajectory(
            OptimizationMethod.FAST_COMPOUND, num_steps=15
        )
        result2 = optimizer2.simulate_trajectory(
            OptimizationMethod.FAST_COMPOUND, num_steps=15
        )

        # Should be identical
        assert result1.average_quality == result2.average_quality
        assert result1.total_time == result2.total_time
        assert result1.compound_gain == result2.compound_gain

    def test_decision_metrics_validation(self):
        """Test that decision metrics are within valid ranges."""
        optimizer = TrajectoryOptimizer(seed=42)
        result = optimizer.simulate_trajectory(
            OptimizationMethod.FAST_COMPOUND, num_steps=20
        )

        for decision in result.decisions:
            # All metrics should be in [0, 1] range
            assert 0.0 <= decision.attention_spent <= 1.0
            assert 0.0 <= decision.quality <= 1.0
            assert 0.0 <= decision.cognitive_load <= 1.0
            assert 0.0 <= decision.experience_factor <= 1.0
            assert 0.0 <= decision.compound_efficiency <= 1.0

            # Time should be positive
            assert decision.time_spent > 0


class TestConceptualScenarios:
    """Test with conceptual scenarios to demonstrate differences."""

    def test_startup_scaling_scenario(self):
        """Scenario: Startup scaling from 10 to 100 employees."""
        optimizer = TrajectoryOptimizer(seed=42)

        # Simulate 50 decision points (hiring, process changes, etc.)
        dda_result = optimizer.simulate_trajectory(
            OptimizationMethod.DATA_DRIVEN, num_steps=50
        )
        fc_result = optimizer.simulate_trajectory(
            OptimizationMethod.FAST_COMPOUND, num_steps=50
        )

        print("\n=== Startup Scaling Scenario ===")
        print(f"Data-Driven: {dda_result}")
        print(f"Fast Compound: {fc_result}")
        print(f"Time saved: {dda_result.total_time - fc_result.total_time:.1f}s")
        print(
            f"Quality difference: {fc_result.final_quality - dda_result.final_quality:.3f}"
        )

        # Fast compound should excel in long-term scaling
        assert fc_result.final_quality >= dda_result.final_quality * 0.95
        assert fc_result.total_time < dda_result.total_time * 0.5

    def test_crisis_response_scenario(self):
        """Scenario: Responding to urgent crisis (short trajectory)."""
        optimizer = TrajectoryOptimizer(seed=42)

        # Simulate 5 critical decisions under pressure
        dda_result = optimizer.simulate_trajectory(
            OptimizationMethod.DATA_DRIVEN, num_steps=5
        )
        fc_result = optimizer.simulate_trajectory(
            OptimizationMethod.FAST_COMPOUND, num_steps=5
        )

        print("\n=== Crisis Response Scenario ===")
        print(f"Data-Driven: {dda_result}")
        print(f"Fast Compound: {fc_result}")

        # In short trajectories, data-driven may have quality edge
        # but fast compound still saves time
        assert fc_result.total_time < dda_result.total_time

    def test_product_development_sprint(self):
        """Scenario: 2-week sprint with daily decisions."""
        optimizer = TrajectoryOptimizer(seed=42)

        # 10 working days = 10 decision points
        results = optimizer.against_the_clock(
            time_budget=80.0,
            decision_time_limit=5.0,  # 8 hours per day  # Max 5 hours per decision
        )

        print("\n=== Product Development Sprint ===")
        print(f"Data-Driven: {results['data_driven']}")
        print(f"Fast Compound: {results['fast_compound']}")
        print(
            f"Steps completed - DDA: {results['data_driven'].total_steps}, "
            f"FC: {results['fast_compound'].total_steps}"
        )

        # Fast compound should complete more iterations
        assert results["fast_compound"].total_steps > results["data_driven"].total_steps
