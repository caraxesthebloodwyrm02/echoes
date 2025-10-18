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

"""Demonstration of Trajectory Optimization Research.

This script demonstrates:
1. Data-Driven Analysis vs Fast Compounding comparison
2. Prompt regeneration from results (bidirectional paths)
3. Against-the-clock optimization
4. Conceptual scenarios with quantified differences
"""

from __future__ import annotations

import json
from pathlib import Path

from src.prompt_regenerator import AnalysisResult, PromptRegenerator
from src.trajectory_optimizer import OptimizationMethod, TrajectoryOptimizer


def print_section(title: str) -> None:
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def demo_optimization_comparison():
    """Demonstrate Data-Driven vs Fast Compounding comparison."""
    print_section("OPTIMIZATION METHOD COMPARISON")

    optimizer = TrajectoryOptimizer(seed=42)

    # Run comparison across multiple trials
    comparison = optimizer.compare_methods(num_steps=30, num_trials=10)

    print("Data-Driven Analysis:")
    print(f"  Average Quality:     {comparison['data_driven']['avg_quality']:.3f}")
    print(f"  Final Quality:       {comparison['data_driven']['final_quality']:.3f}")
    print(f"  Average Time:        {comparison['data_driven']['avg_time']:.2f}s")
    print(
        f"  Cognitive Load:      {comparison['data_driven']['avg_cognitive_load']:.2f}"
    )
    print(f"  Efficiency Ratio:    {comparison['data_driven']['efficiency_ratio']:.3f}")
    print(f"  Learning Slope:      {comparison['data_driven']['learning_slope']:.4f}")

    print("\nFast Compounding:")
    print(f"  Average Quality:     {comparison['fast_compound']['avg_quality']:.3f}")
    print(f"  Final Quality:       {comparison['fast_compound']['final_quality']:.3f}")
    print(f"  Average Time:        {comparison['fast_compound']['avg_time']:.2f}s")
    print(
        f"  Cognitive Load:      {comparison['fast_compound']['avg_cognitive_load']:.2f}"
    )
    print(
        f"  Efficiency Ratio:    {comparison['fast_compound']['efficiency_ratio']:.3f}"
    )
    print(f"  Learning Slope:      {comparison['fast_compound']['learning_slope']:.4f}")
    print(f"  Compound Gain:       {comparison['fast_compound']['compound_gain']:.3f}")

    print("\nFast Compounding Advantages:")
    print(
        f"  Time Saved:          {comparison['advantages']['fc_time_saved']:.2f}s ({comparison['advantages']['fc_time_saved'] / comparison['data_driven']['avg_time'] * 100:.1f}%)"
    )
    print(
        f"  Cognitive Load Saved: {comparison['advantages']['fc_cognitive_saved']:.2f} ({comparison['advantages']['fc_cognitive_saved'] / comparison['data_driven']['avg_cognitive_load'] * 100:.1f}%)"
    )
    print(
        f"  Efficiency Gain:     +{comparison['advantages']['fc_efficiency_gain']:.1f}%"
    )
    print(
        f"  Learning Advantage:  +{comparison['advantages']['fc_learning_advantage']:.1f}%"
    )


def demo_against_the_clock():
    """Demonstrate time-constrained optimization."""
    print_section("AGAINST THE CLOCK (30 second budget)")

    optimizer = TrajectoryOptimizer(seed=42)
    results = optimizer.against_the_clock(time_budget=30.0, decision_time_limit=2.0)

    dda = results["data_driven"]
    fc = results["fast_compound"]

    print("Data-Driven Analysis:")
    print(f"  Steps Completed:     {dda.total_steps}")
    print(f"  Time Used:           {dda.total_time:.2f}s / 30.0s")
    print(f"  Average Quality:     {dda.average_quality:.3f}")
    print(f"  Final Quality:       {dda.final_quality:.3f}")
    print(f"  Quality/Second:      {dda.quality_per_second:.3f}")

    print("\nFast Compounding:")
    print(f"  Steps Completed:     {fc.total_steps}")
    print(f"  Time Used:           {fc.total_time:.2f}s / 30.0s")
    print(f"  Average Quality:     {fc.average_quality:.3f}")
    print(f"  Final Quality:       {fc.final_quality:.3f}")
    print(f"  Quality/Second:      {fc.quality_per_second:.3f}")
    print(f"  Compound Gain:       {fc.compound_gain:.3f}")

    print("\nComparison:")
    print(
        f"  FC completed {fc.total_steps - dda.total_steps} more steps (+{(fc.total_steps / dda.total_steps - 1) * 100:.1f}%)"
    )
    print(
        f"  FC quality/second is {fc.quality_per_second / dda.quality_per_second:.2f}x higher"
    )


def demo_trajectory_length_impact():
    """Demonstrate how trajectory length affects method performance."""
    print_section("TRAJECTORY LENGTH IMPACT")

    optimizer = TrajectoryOptimizer(seed=42)

    lengths = [10, 20, 50, 100]

    print(
        f"{'Length':<10} {'DDA Avg':<12} {'FC Avg':<12} {'FC Final':<12} {'FC Advantage':<15}"
    )
    print("-" * 70)

    for length in lengths:
        dda = optimizer.simulate_trajectory(
            OptimizationMethod.DATA_DRIVEN, num_steps=length
        )
        fc = optimizer.simulate_trajectory(
            OptimizationMethod.FAST_COMPOUND, num_steps=length
        )

        advantage = fc.final_quality - dda.final_quality

        print(
            f"{length:<10} {dda.average_quality:<12.3f} {fc.average_quality:<12.3f} "
            f"{fc.final_quality:<12.3f} {advantage:+.3f} ({advantage / dda.final_quality * 100:+.1f}%)"
        )

    print("\nKey Insight: Fast Compounding advantage grows with trajectory length")
    print("due to exponential learning curve (experience^1.5)")


def demo_prompt_regeneration():
    """Demonstrate prompt regeneration from results."""
    print_section("PROMPT REGENERATION (Bidirectional Paths)")

    regenerator = PromptRegenerator()

    # Use actual experiment result
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

    print("Original Result:")
    print(f"  Classification:      {result.classification}")
    print(f"  Efficiency Score:    {result.efficiency_score:.3f}")
    print(f"  Balance Angle:       {result.balance_angle:.2f}°")
    print(f"  Influence-Productivity: {result.influence_productivity_angle:.2f}°")
    print(f"  Productivity-Creativity: {result.productivity_creativity_angle:.2f}°")

    # Regenerate prompt (backward path: Result → Prompt)
    prompt = regenerator.regenerate_from_result(result)

    print("\nRegenerated Prompt:")
    print(f"  Objective:           {prompt.objective}")
    print(f"  Confidence:          {prompt.confidence:.2f}")
    print("\n  Constraints:")
    for constraint in prompt.constraints:
        print(f"    - {constraint}")

    print("\n  Reasoning:")
    print(f"    {prompt.reasoning}")

    print("\n  Alternative Prompts:")
    for i, alt in enumerate(prompt.alternative_prompts, 1):
        print(f"    {i}. {alt}")

    # Validate bidirectional consistency
    validation = regenerator.validate_regeneration(result, prompt)

    print("\nValidation (Forward Path: Prompt -> Result):")
    print(f"  Classification Match: {validation['classification_match']}")
    print("  Vector Similarity:")
    for key, sim in validation["vector_match"].items():
        print(f"    {key:<15}: {sim:.6f}")
    print(f"  Is Valid:            {validation['is_valid']}")

    print("\nKey Insight: If path A->X exists, path X->A also exists")
    print("Regenerated prompt produces equivalent results when re-executed")


def demo_conceptual_scenarios():
    """Demonstrate real-world scenarios."""
    print_section("CONCEPTUAL SCENARIOS")

    optimizer = TrajectoryOptimizer(seed=42)

    # Scenario 1: Startup Scaling
    print("Scenario 1: Startup Scaling (10 -> 100 employees)")
    print("-" * 50)

    dda = optimizer.simulate_trajectory(OptimizationMethod.DATA_DRIVEN, num_steps=50)
    fc = optimizer.simulate_trajectory(OptimizationMethod.FAST_COMPOUND, num_steps=50)

    print(
        f"Data-Driven:  quality={dda.final_quality:.3f}, time={dda.total_time:.1f}s, load={dda.total_cognitive_load:.1f}"
    )
    print(
        f"Fast Compound: quality={fc.final_quality:.3f}, time={fc.total_time:.1f}s, load={fc.total_cognitive_load:.1f}"
    )
    print(
        f"Result: FC saves {dda.total_time - fc.total_time:.1f}s ({(1 - fc.total_time / dda.total_time) * 100:.1f}%) with {fc.final_quality / dda.final_quality:.2f}x final quality"
    )

    # Scenario 2: Crisis Response
    print("\nScenario 2: Crisis Response (5 critical decisions)")
    print("-" * 50)

    dda_crisis = optimizer.simulate_trajectory(
        OptimizationMethod.DATA_DRIVEN, num_steps=5
    )
    fc_crisis = optimizer.simulate_trajectory(
        OptimizationMethod.FAST_COMPOUND, num_steps=5
    )

    print(
        f"Data-Driven:  quality={dda_crisis.average_quality:.3f}, time={dda_crisis.total_time:.1f}s"
    )
    print(
        f"Fast Compound: quality={fc_crisis.average_quality:.3f}, time={fc_crisis.total_time:.1f}s"
    )
    print(
        f"Result: FC is {dda_crisis.total_time / fc_crisis.total_time:.1f}x faster (critical in crisis)"
    )

    # Scenario 3: Product Sprint
    print("\nScenario 3: 2-Week Sprint (80 hour budget)")
    print("-" * 50)

    sprint_results = optimizer.against_the_clock(
        time_budget=80.0, decision_time_limit=5.0
    )

    dda_sprint = sprint_results["data_driven"]
    fc_sprint = sprint_results["fast_compound"]

    print(
        f"Data-Driven:  {dda_sprint.total_steps} iterations, quality={dda_sprint.final_quality:.3f}"
    )
    print(
        f"Fast Compound: {fc_sprint.total_steps} iterations, quality={fc_sprint.final_quality:.3f}"
    )
    print(
        f"Result: FC completes {fc_sprint.total_steps - dda_sprint.total_steps} more iterations (+{(fc_sprint.total_steps / dda_sprint.total_steps - 1) * 100:.1f}%)"
    )


def save_results_to_file():
    """Save demonstration results to JSON."""
    print_section("SAVING RESULTS")

    optimizer = TrajectoryOptimizer(seed=42)

    # Run comprehensive comparison
    comparison = optimizer.compare_methods(num_steps=50, num_trials=10)

    # Run against-the-clock
    atc_results = optimizer.against_the_clock(time_budget=60.0)

    # Combine results
    output = {
        "comparison": comparison,
        "against_the_clock": {
            "data_driven": {
                "total_steps": atc_results["data_driven"].total_steps,
                "average_quality": atc_results["data_driven"].average_quality,
                "final_quality": atc_results["data_driven"].final_quality,
                "total_time": atc_results["data_driven"].total_time,
                "efficiency_ratio": atc_results["data_driven"].efficiency_ratio,
            },
            "fast_compound": {
                "total_steps": atc_results["fast_compound"].total_steps,
                "average_quality": atc_results["fast_compound"].average_quality,
                "final_quality": atc_results["fast_compound"].final_quality,
                "total_time": atc_results["fast_compound"].total_time,
                "efficiency_ratio": atc_results["fast_compound"].efficiency_ratio,
                "compound_gain": atc_results["fast_compound"].compound_gain,
            },
        },
    }

    # Save to file
    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    output_path = results_dir / "trajectory_optimization_results.json"
    with output_path.open("w") as f:
        json.dump(output, f, indent=2)

    print(f"Results saved to: {output_path}")
    print(f"File size: {output_path.stat().st_size} bytes")


def main():
    """Run all demonstrations."""
    print("\n" + "=" * 70)
    print("  TRAJECTORY OPTIMIZATION RESEARCH DEMONSTRATION")
    print("  Comparing Data-Driven Analysis vs Fast Compounding")
    print("=" * 70)

    demo_optimization_comparison()
    demo_against_the_clock()
    demo_trajectory_length_impact()
    demo_prompt_regeneration()
    demo_conceptual_scenarios()
    save_results_to_file()

    print("\n" + "=" * 70)
    print("  DEMONSTRATION COMPLETE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
