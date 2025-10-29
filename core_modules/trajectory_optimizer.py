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

"""Trajectory Optimization: Data-Driven vs Fast Compounding Analysis.

This module implements two competing optimization strategies:

1. **Data-Driven Analysis (DDA):**
   - High attention/focus at each decision point
   - Analyzes all available paths before choosing
   - Slower but more accurate per-step decisions
   - Higher cognitive load

2. **Fast Compounding (FC):**
   - Low attention/focus per decision (fast context)
   - Makes quick decisions based on accumulated experience
   - Compounds efficiency over longer trajectories
   - Lower cognitive load, learns from momentum

Key Insight: FC may fail early but compounds exponentially over time,
while DDA maintains consistent quality but with diminishing returns.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List

import numpy as np


class OptimizationMethod(Enum):
    """Optimization strategy types."""

    DATA_DRIVEN = "data_driven"
    FAST_COMPOUND = "fast_compound"


@dataclass
class DecisionMetrics:
    """Metrics for a single decision point in trajectory."""

    step: int
    attention_spent: float  # 0-1 scale
    time_spent: float  # seconds
    quality: float  # 0-1 scale (decision quality)
    cognitive_load: float  # 0-1 scale
    experience_factor: float  # Accumulated learning (0-1)

    # Compounding metrics
    compound_efficiency: float = 0.0  # Efficiency gained from previous steps
    path_refinement: float = 0.0  # How much better than previous step

    def __repr__(self) -> str:
        return (
            f"Step {self.step}: quality={self.quality:.3f}, "
            f"attention={self.attention_spent:.3f}, "
            f"compound={self.compound_efficiency:.3f}"
        )


@dataclass
class TrajectoryResult:
    """Complete trajectory optimization result."""

    method: OptimizationMethod
    total_steps: int
    decisions: List[DecisionMetrics]

    # Aggregate metrics
    total_time: float
    total_cognitive_load: float
    average_quality: float
    final_quality: float

    # Compounding metrics
    compound_gain: float  # Total efficiency from compounding
    learning_curve_slope: float  # Rate of improvement

    # Against-the-clock metrics
    quality_per_second: float
    efficiency_ratio: float  # Quality / (time * cognitive_load)

    def __repr__(self) -> str:
        return (
            f"{self.method.value.upper()}: "
            f"avg_quality={self.average_quality:.3f}, "
            f"final_quality={self.final_quality:.3f}, "
            f"time={self.total_time:.2f}s, "
            f"efficiency={self.efficiency_ratio:.3f}"
        )


class TrajectoryOptimizer:
    """Simulates and compares optimization strategies."""

    def __init__(self, seed: int = 42):
        """Initialize optimizer with random seed for reproducibility."""
        self.rng = np.random.RandomState(seed)
        self.seed = seed

    def data_driven_decision(
        self, step: int, total_steps: int, experience: float, base_quality: float = 0.7
    ) -> DecisionMetrics:
        """Simulate data-driven analysis decision.

        Characteristics:
        - High attention (0.7-0.9)
        - Longer time per decision
        - Consistent quality
        - High cognitive load
        - Minimal compounding benefit
        """
        # High attention allocation
        attention = 0.7 + self.rng.uniform(0, 0.2)

        # Time scales with attention
        time_spent = 1.0 + attention * self.rng.uniform(0.5, 1.5)

        # Quality is high but plateaus (diminishing returns)
        quality = base_quality + attention * 0.2 - (step / total_steps) * 0.05
        quality = np.clip(quality, 0.0, 1.0)

        # High cognitive load
        cognitive_load = 0.6 + attention * 0.3

        # Minimal compounding (experience helps slightly)
        compound_efficiency = experience * 0.1
        path_refinement = 0.02  # Small incremental improvement

        return DecisionMetrics(
            step=step,
            attention_spent=attention,
            time_spent=time_spent,
            quality=quality,
            cognitive_load=cognitive_load,
            experience_factor=experience,
            compound_efficiency=compound_efficiency,
            path_refinement=path_refinement,
        )

    def fast_compound_decision(
        self, step: int, total_steps: int, experience: float, base_quality: float = 0.5
    ) -> DecisionMetrics:
        """Simulate fast compounding decision.

        Characteristics:
        - Low attention (0.2-0.4)
        - Quick decisions
        - Quality improves with experience (compounding)
        - Low cognitive load
        - Exponential learning curve
        """
        # Low attention allocation (fast context)
        attention = 0.2 + self.rng.uniform(0, 0.2)

        # Fast decisions
        time_spent = 0.3 + attention * self.rng.uniform(0.1, 0.3)

        # Quality starts lower but compounds exponentially
        # Key insight: experience^1.5 creates compounding effect
        compound_efficiency = (experience**1.5) * 0.6

        # Quality improves dramatically with experience
        quality = base_quality + compound_efficiency
        quality = np.clip(quality, 0.0, 1.0)

        # Low cognitive load (less mental effort)
        cognitive_load = 0.2 + attention * 0.2

        # Path refinement accelerates with experience
        path_refinement = experience * 0.15 * (1 + step / total_steps)

        return DecisionMetrics(
            step=step,
            attention_spent=attention,
            time_spent=time_spent,
            quality=quality,
            cognitive_load=cognitive_load,
            experience_factor=experience,
            compound_efficiency=compound_efficiency,
            path_refinement=path_refinement,
        )

    def simulate_trajectory(
        self,
        method: OptimizationMethod,
        num_steps: int = 20,
        base_quality: float = None,
    ) -> TrajectoryResult:
        """Simulate complete trajectory optimization.

        Parameters
        ----------
        method
            Optimization strategy to use
        num_steps
            Number of decision points in trajectory
        base_quality
            Starting quality level (auto-set if None)

        Returns
        -------
        TrajectoryResult with complete metrics
        """
        decisions: List[DecisionMetrics] = []
        experience = 0.0  # Starts at 0, accumulates

        # Set base quality based on method
        if base_quality is None:
            base_quality = 0.7 if method == OptimizationMethod.DATA_DRIVEN else 0.5

        # Select decision function
        decision_fn = (
            self.data_driven_decision if method == OptimizationMethod.DATA_DRIVEN else self.fast_compound_decision
        )

        # Simulate each step
        for step in range(num_steps):
            decision = decision_fn(step, num_steps, experience, base_quality)
            decisions.append(decision)

            # Update experience (accumulates with quality)
            # Fast compound learns faster from mistakes
            learning_rate = 0.08 if method == OptimizationMethod.FAST_COMPOUND else 0.05
            experience += decision.quality * learning_rate
            experience = min(experience, 1.0)  # Cap at 1.0

        # Calculate aggregate metrics
        total_time = sum(d.time_spent for d in decisions)
        total_cognitive_load = sum(d.cognitive_load for d in decisions)
        average_quality = np.mean([d.quality for d in decisions])
        final_quality = decisions[-1].quality

        # Compounding metrics
        compound_gain = sum(d.compound_efficiency for d in decisions)

        # Learning curve slope (linear regression)
        qualities = [d.quality for d in decisions]
        steps = np.arange(num_steps)
        learning_curve_slope = np.polyfit(steps, qualities, 1)[0]

        # Against-the-clock metrics
        quality_per_second = average_quality / (total_time / num_steps)
        efficiency_ratio = average_quality / (total_time * total_cognitive_load / num_steps)

        return TrajectoryResult(
            method=method,
            total_steps=num_steps,
            decisions=decisions,
            total_time=total_time,
            total_cognitive_load=total_cognitive_load,
            average_quality=average_quality,
            final_quality=final_quality,
            compound_gain=compound_gain,
            learning_curve_slope=learning_curve_slope,
            quality_per_second=quality_per_second,
            efficiency_ratio=efficiency_ratio,
        )

    def compare_methods(self, num_steps: int = 20, num_trials: int = 10) -> Dict[str, any]:
        """Compare both methods across multiple trials.

        Returns
        -------
        dict with comparison metrics and statistical analysis
        """
        dda_results = []
        fc_results = []

        for _ in range(num_trials):
            dda_results.append(self.simulate_trajectory(OptimizationMethod.DATA_DRIVEN, num_steps))
            fc_results.append(self.simulate_trajectory(OptimizationMethod.FAST_COMPOUND, num_steps))

        # Aggregate statistics
        comparison = {
            "num_steps": num_steps,
            "num_trials": num_trials,
            "data_driven": {
                "avg_quality": np.mean([r.average_quality for r in dda_results]),
                "final_quality": np.mean([r.final_quality for r in dda_results]),
                "avg_time": np.mean([r.total_time for r in dda_results]),
                "avg_cognitive_load": np.mean([r.total_cognitive_load for r in dda_results]),
                "efficiency_ratio": np.mean([r.efficiency_ratio for r in dda_results]),
                "learning_slope": np.mean([r.learning_curve_slope for r in dda_results]),
            },
            "fast_compound": {
                "avg_quality": np.mean([r.average_quality for r in fc_results]),
                "final_quality": np.mean([r.final_quality for r in fc_results]),
                "avg_time": np.mean([r.total_time for r in fc_results]),
                "avg_cognitive_load": np.mean([r.total_cognitive_load for r in fc_results]),
                "efficiency_ratio": np.mean([r.efficiency_ratio for r in fc_results]),
                "learning_slope": np.mean([r.learning_curve_slope for r in fc_results]),
                "compound_gain": np.mean([r.compound_gain for r in fc_results]),
            },
        }

        # Calculate advantages
        comparison["advantages"] = {
            "fc_time_saved": (comparison["data_driven"]["avg_time"] - comparison["fast_compound"]["avg_time"]),
            "fc_cognitive_saved": (
                comparison["data_driven"]["avg_cognitive_load"] - comparison["fast_compound"]["avg_cognitive_load"]
            ),
            "fc_efficiency_gain": (
                comparison["fast_compound"]["efficiency_ratio"] / comparison["data_driven"]["efficiency_ratio"] - 1.0
            )
            * 100,  # Percentage
            "fc_learning_advantage": (
                comparison["fast_compound"]["learning_slope"] / comparison["data_driven"]["learning_slope"] - 1.0
            )
            * 100,  # Percentage
        }

        return comparison

    def against_the_clock(
        self, time_budget: float = 30.0, decision_time_limit: float = 2.0
    ) -> Dict[str, TrajectoryResult]:
        """Simulate both methods with time constraints.

        Parameters
        ----------
        time_budget
            Total time available (seconds)
        decision_time_limit
            Max time per decision (seconds)

        Returns
        -------
        dict with results for both methods
        """
        results = {}

        for method in [
            OptimizationMethod.DATA_DRIVEN,
            OptimizationMethod.FAST_COMPOUND,
        ]:
            decisions = []
            experience = 0.0
            elapsed_time = 0.0
            step = 0

            decision_fn = (
                self.data_driven_decision if method == OptimizationMethod.DATA_DRIVEN else self.fast_compound_decision
            )

            # Run until time budget exhausted
            while elapsed_time < time_budget:
                decision = decision_fn(step, 100, experience)  # Assume long trajectory

                # Apply time limit
                decision.time_spent = min(decision.time_spent, decision_time_limit)

                # Check if we have time for this decision
                if elapsed_time + decision.time_spent > time_budget:
                    break

                decisions.append(decision)
                elapsed_time += decision.time_spent

                # Update experience
                learning_rate = 0.08 if method == OptimizationMethod.FAST_COMPOUND else 0.05
                experience += decision.quality * learning_rate
                experience = min(experience, 1.0)

                step += 1

            # Build result
            if decisions:
                total_cognitive_load = sum(d.cognitive_load for d in decisions)
                average_quality = np.mean([d.quality for d in decisions])
                final_quality = decisions[-1].quality
                compound_gain = sum(d.compound_efficiency for d in decisions)

                qualities = [d.quality for d in decisions]
                steps_arr = np.arange(len(decisions))
                learning_curve_slope = np.polyfit(steps_arr, qualities, 1)[0] if len(decisions) > 1 else 0.0

                quality_per_second = average_quality / (elapsed_time / len(decisions))
                efficiency_ratio = average_quality / (elapsed_time * total_cognitive_load / len(decisions))

                results[method.value] = TrajectoryResult(
                    method=method,
                    total_steps=len(decisions),
                    decisions=decisions,
                    total_time=elapsed_time,
                    total_cognitive_load=total_cognitive_load,
                    average_quality=average_quality,
                    final_quality=final_quality,
                    compound_gain=compound_gain,
                    learning_curve_slope=learning_curve_slope,
                    quality_per_second=quality_per_second,
                    efficiency_ratio=efficiency_ratio,
                )

        return results
