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

"""Trajectory Analysis System - Modular vector analysis for influence, productivity, and creativity.

This module provides a complete refactored implementation of trajectory analysis with:
- Data models (TrajectoryPoint, VectorSet, EfficiencySummary)
- Vector operations (normalize, angle_between, compute_efficiency_vector)
- Metrics calculation (calculate_efficiency_metrics)
- 3D visualization (plot_trajectory_3d)
- CLI interface for batch processing

Usage:
    python trajectory_analysis.py --interactive  # Show 3D plot
    python trajectory_analysis.py --output results.json --save-plot trajectory.png
    python trajectory_analysis.py --no-plot  # Metrics only (CI/batch mode)

Example:
    from trajectory_analysis import TrajectoryPoint, calculate_efficiency_metrics

    points = [TrajectoryPoint(1, "Test", 100.0, 0.5, 0.5, 0.5)]
    summary = calculate_efficiency_metrics(points)
    print(summary.interpretation())
"""

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt
import pandas as pd

__version__ = "1.0.0"
__author__ = "Echoes Team"


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass(frozen=True)
class TrajectoryPoint:
    """Represents a single point in the trajectory space.

    Attributes:
        index: Sequential identifier (1-based)
        archetype: Symbolic name representing the point's conceptual identity
        frequency: Harmonic frequency value (Hz)
        x: Conceptual dimension coordinate
        y: Emotional dimension coordinate
        z: Energetic dimension coordinate
    """

    index: int
    archetype: str
    frequency: float
    x: float
    y: float
    z: float

    @property
    def vector(self) -> npt.NDArray[np.float64]:
        """Return the 3D coordinate vector [x, y, z]."""
        return np.array([self.x, self.y, self.z], dtype=np.float64)

    def __post_init__(self) -> None:
        """Validate trajectory point data."""
        if self.index < 1:
            raise ValueError(f"Index must be >= 1, got {self.index}")
        if self.frequency <= 0:
            raise ValueError(f"Frequency must be positive, got {self.frequency}")
        if not self.archetype.strip():
            raise ValueError("Archetype cannot be empty")


@dataclass(frozen=True)
class VectorSet:
    """Collection of normalized vectors for trajectory analysis.

    Attributes:
        influence: Emotional + energetic drive vector
        productivity: Conceptual + energetic output vector
        creativity: Innovation and ideation vector (typically from Leonardo da Vinci point)
        efficiency: Balanced optimization vector (computed from the three base vectors)
    """

    influence: npt.NDArray[np.float64]
    productivity: npt.NDArray[np.float64]
    creativity: npt.NDArray[np.float64]
    efficiency: npt.NDArray[np.float64]

    def __post_init__(self) -> None:
        """Validate that all vectors are 3D and normalized."""
        for name, vec in [
            ("influence", self.influence),
            ("productivity", self.productivity),
            ("creativity", self.creativity),
            ("efficiency", self.efficiency),
        ]:
            if vec.shape != (3,):
                raise ValueError(f"{name} must be 3D vector, got shape {vec.shape}")
            norm = np.linalg.norm(vec)
            if not np.isclose(norm, 1.0, atol=1e-6):
                raise ValueError(
                    f"{name} must be normalized (norm=1), got norm={norm:.6f}"
                )


@dataclass(frozen=True)
class EfficiencySummary:
    """Summary of efficiency metrics for trajectory analysis.

    Attributes:
        efficiency_vector: The computed efficiency (balance) vector
        efficiency_score: Mean dot product of efficiency with base vectors (range: -1 to 1)
        balance_factor_degrees: Average angular separation between base vectors (degrees)
        angle_influence_productivity: Angle between influence and productivity vectors (degrees)
        angle_influence_creativity: Angle between influence and creativity vectors (degrees)
        angle_productivity_creativity: Angle between productivity and creativity vectors (degrees)

    Interpretation:
        - efficiency_score > 0.5: High alignment across all dimensions
        - efficiency_score 0.2-0.5: Moderate alignment with some tension
        - efficiency_score < 0.2: Low alignment, significant conflicts
        - balance_factor ~90°: Orthogonal (independent dimensions)
        - balance_factor <60°: High synergy
        - balance_factor >120°: Antagonistic relationship
    """

    efficiency_vector: npt.NDArray[np.float64]
    efficiency_score: float
    balance_factor_degrees: float
    angle_influence_productivity: float
    angle_influence_creativity: float
    angle_productivity_creativity: float

    def __post_init__(self) -> None:
        """Validate efficiency summary metrics."""
        if self.efficiency_vector.shape != (3,):
            raise ValueError(
                f"efficiency_vector must be 3D, got {self.efficiency_vector.shape}"
            )
        if not -1.0 <= self.efficiency_score <= 1.0:
            raise ValueError(
                f"efficiency_score must be in [-1, 1], got {self.efficiency_score}"
            )
        for name, angle in [
            ("balance_factor_degrees", self.balance_factor_degrees),
            ("angle_influence_productivity", self.angle_influence_productivity),
            ("angle_influence_creativity", self.angle_influence_creativity),
            ("angle_productivity_creativity", self.angle_productivity_creativity),
        ]:
            if not 0.0 <= angle <= 180.0:
                raise ValueError(f"{name} must be in [0, 180] degrees, got {angle}")

    def interpretation(self) -> str:
        """Return human-readable interpretation of the metrics."""
        lines = []

        # Efficiency score interpretation
        if self.efficiency_score > 0.5:
            lines.append(
                "[+] High alignment: System operates with strong synergy across dimensions"
            )
        elif self.efficiency_score > 0.2:
            lines.append(
                "[!] Moderate alignment: Some tension exists but system is functional"
            )
        else:
            lines.append("[-] Low alignment: Significant conflicts between dimensions")

        # Balance factor interpretation
        if self.balance_factor_degrees < 60:
            lines.append("[+] High synergy: Dimensions work together harmoniously")
        elif self.balance_factor_degrees < 120:
            lines.append(
                "[!] Moderate independence: Dimensions operate somewhat independently"
            )
        else:
            lines.append("[-] Antagonistic: Dimensions work against each other")

        # Specific dimension relationships
        if self.angle_influence_productivity < 45:
            lines.append("[+] Influence and productivity are strongly aligned")
        elif self.angle_influence_productivity > 135:
            lines.append("[-] Influence and productivity are in conflict")

        if self.angle_influence_creativity > 120:
            lines.append("[!] Creativity is undervalued relative to influence")

        if self.angle_productivity_creativity > 135:
            lines.append(
                "[!] Risk: Productivity may be suppressing creative exploration"
            )

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert summary to dictionary for JSON serialization."""
        return {
            "efficiency_vector": self.efficiency_vector.tolist(),
            "efficiency_score": float(self.efficiency_score),
            "balance_factor_degrees": float(self.balance_factor_degrees),
            "angles": {
                "influence_productivity": float(self.angle_influence_productivity),
                "influence_creativity": float(self.angle_influence_creativity),
                "productivity_creativity": float(self.angle_productivity_creativity),
            },
            "interpretation": self.interpretation(),
        }


# ============================================================================
# VECTOR OPERATIONS
# ============================================================================


def normalize(vector: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """Normalize a vector to unit length.

    Args:
        vector: Input vector of any length

    Returns:
        Normalized vector with magnitude 1.0

    Raises:
        ValueError: If vector has zero magnitude
    """
    norm = np.linalg.norm(vector)
    if norm < 1e-10:
        raise ValueError(f"Cannot normalize zero vector (norm={norm})")
    return vector / norm


def angle_between(v1: npt.NDArray[np.float64], v2: npt.NDArray[np.float64]) -> float:
    """Calculate angle between two vectors in degrees.

    Args:
        v1: First vector
        v2: Second vector

    Returns:
        Angle in degrees [0, 180]
    """
    # Normalize inputs to handle non-unit vectors
    v1_norm = normalize(v1)
    v2_norm = normalize(v2)

    # Clip dot product to handle numerical errors
    dot_product = np.clip(np.dot(v1_norm, v2_norm), -1.0, 1.0)

    # Return angle in degrees
    return np.degrees(np.arccos(dot_product))


def compute_efficiency_vector(
    influence: npt.NDArray[np.float64],
    productivity: npt.NDArray[np.float64],
    creativity: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """Compute efficiency vector as normalized average of base vectors.

    The efficiency vector represents the optimal balance point between
    influence, productivity, and creativity dimensions.

    Args:
        influence: Influence vector (should be normalized)
        productivity: Productivity vector (should be normalized)
        creativity: Creativity vector (should be normalized)

    Returns:
        Normalized efficiency vector
    """
    # Average the three vectors
    avg_vector = (influence + productivity + creativity) / 3.0

    # Normalize to unit length
    return normalize(avg_vector)


# ============================================================================
# METRICS CALCULATION
# ============================================================================


def calculate_efficiency_metrics(
    trajectory_points: List[TrajectoryPoint],
    influence_base: Optional[npt.NDArray[np.float64]] = None,
    productivity_base: Optional[npt.NDArray[np.float64]] = None,
    creativity_archetype: str = "Leonardo da Vinci",
) -> EfficiencySummary:
    """Calculate efficiency metrics from trajectory data.

    Args:
        trajectory_points: List of trajectory points
        influence_base: Base influence vector (default: [0.6, 0.8, 0.5])
        productivity_base: Base productivity vector (default: [0.9, 0.4, 0.3])
        creativity_archetype: Archetype name to use for creativity vector

    Returns:
        EfficiencySummary with all computed metrics

    Raises:
        ValueError: If creativity archetype not found in trajectory points
    """
    # Set default base vectors if not provided
    if influence_base is None:
        influence_base = np.array([0.6, 0.8, 0.5], dtype=np.float64)
    if productivity_base is None:
        productivity_base = np.array([0.9, 0.4, 0.3], dtype=np.float64)

    # Normalize base vectors
    influence_vector = normalize(influence_base)
    productivity_vector = normalize(productivity_base)

    # Find creativity vector from trajectory
    creativity_point = next(
        (p for p in trajectory_points if p.archetype == creativity_archetype), None
    )
    if creativity_point is None:
        raise ValueError(
            f"Creativity archetype '{creativity_archetype}' not found in trajectory"
        )

    creativity_vector = normalize(creativity_point.vector)

    # Compute efficiency vector
    efficiency_vector = compute_efficiency_vector(
        influence_vector, productivity_vector, creativity_vector
    )

    # Calculate angular relationships
    angle_inf_prod = angle_between(influence_vector, productivity_vector)
    angle_inf_crea = angle_between(influence_vector, creativity_vector)
    angle_prod_crea = angle_between(productivity_vector, creativity_vector)

    # Calculate efficiency score (mean alignment with base vectors)
    efficiency_score = np.mean(
        [
            np.dot(efficiency_vector, influence_vector),
            np.dot(efficiency_vector, productivity_vector),
            np.dot(efficiency_vector, creativity_vector),
        ]
    )

    # Calculate balance factor (average angular separation)
    balance_factor = (angle_inf_prod + angle_inf_crea + angle_prod_crea) / 3.0

    return EfficiencySummary(
        efficiency_vector=efficiency_vector,
        efficiency_score=efficiency_score,
        balance_factor_degrees=balance_factor,
        angle_influence_productivity=angle_inf_prod,
        angle_influence_creativity=angle_inf_crea,
        angle_productivity_creativity=angle_prod_crea,
    )


# ============================================================================
# PLOTTING
# ============================================================================


def plot_trajectory_3d(
    trajectory_points: List[TrajectoryPoint],
    vectors: VectorSet,
    title: str = "Influence–Productivity–Creativity Alignment with Efficiency Vector",
    show: bool = True,
    save_path: Optional[Path] = None,
    figsize: Tuple[int, int] = (12, 8),
    dpi: int = 100,
) -> plt.Figure:
    """Create 3D visualization of trajectory and vectors.

    Args:
        trajectory_points: List of trajectory points to plot
        vectors: VectorSet containing influence, productivity, creativity, efficiency
        title: Plot title
        show: Whether to display the plot interactively
        save_path: Optional path to save the figure
        figsize: Figure size in inches (width, height)
        dpi: Resolution for saved figure

    Returns:
        Matplotlib figure object
    """
    # Create DataFrame for easier plotting
    df = pd.DataFrame(
        [
            {
                "index": p.index,
                "archetype": p.archetype,
                "frequency": p.frequency,
                "x": p.x,
                "y": p.y,
                "z": p.z,
            }
            for p in trajectory_points
        ]
    )

    # Create figure and 3D axis
    fig = plt.figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111, projection="3d")

    # Plot trajectory path
    ax.plot(
        df["x"],
        df["y"],
        df["z"],
        color="gray",
        linewidth=1.5,
        alpha=0.5,
        label="Trajectory",
    )

    # Plot trajectory points colored by frequency
    scatter = ax.scatter(
        df["x"],
        df["y"],
        df["z"],
        c=df["frequency"],
        cmap="plasma",
        s=80,
        alpha=0.7,
        edgecolors="black",
        linewidths=0.5,
    )

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax, pad=0.1, shrink=0.8)
    cbar.set_label("Frequency (Hz)", rotation=270, labelpad=20)

    # Plot vectors from origin
    origin = np.zeros(3)
    vector_configs = [
        (vectors.influence, "blue", "Influence", 0.5, 2.5),
        (vectors.productivity, "green", "Productivity", 0.5, 2.5),
        (vectors.creativity, "purple", "Creativity", 0.5, 2.5),
        (vectors.efficiency, "red", "Efficiency (Balance)", 0.6, 3.0),
    ]

    for vec, color, label, length, linewidth in vector_configs:
        ax.quiver(
            *origin,
            *vec,
            color=color,
            length=length,
            linewidth=linewidth,
            arrow_length_ratio=0.15,
            label=label,
            alpha=0.9,
        )

    # Set labels and title
    ax.set_xlabel("Conceptual (x)", fontsize=11, labelpad=10)
    ax.set_ylabel("Emotional (y)", fontsize=11, labelpad=10)
    ax.set_zlabel("Energetic (z)", fontsize=11, labelpad=10)
    ax.set_title(title, fontsize=13, fontweight="bold", pad=20)

    # Add legend
    ax.legend(loc="upper left", fontsize=9, framealpha=0.9)

    # Set viewing angle for better perspective
    ax.view_init(elev=20, azim=45)

    # Improve grid
    ax.grid(True, alpha=0.3)

    # Tight layout
    plt.tight_layout()

    # Save if path provided
    if save_path:
        plt.savefig(save_path, dpi=dpi, bbox_inches="tight")
        print(f"Figure saved to {save_path}")

    # Show if requested
    if show:
        plt.show()

    return fig


# ============================================================================
# DATA LOADING
# ============================================================================


def load_trajectory_data(data: List[Tuple]) -> List[TrajectoryPoint]:
    """Load trajectory data from list of tuples.

    Args:
        data: List of (index, archetype, frequency, x, y, z) tuples

    Returns:
        List of TrajectoryPoint objects
    """
    return [
        TrajectoryPoint(
            index=int(row[0]),
            archetype=str(row[1]),
            frequency=float(row[2]),
            x=float(row[3]),
            y=float(row[4]),
            z=float(row[5]),
        )
        for row in data
    ]


def get_default_trajectory_data() -> List[TrajectoryPoint]:
    """Return the default trajectory dataset."""
    data = [
        (1, "Elephant", 20, -0.9, -0.8, -0.9),
        (2, "Completed", 32.76, -0.7, -0.5, -0.7),
        (3, "Saturn", 53.65, -0.6, -0.4, -0.5),
        (4, "Hydrogen", 87.88, -0.5, -0.2, -0.4),
        (5, "Leonardo da Vinci", 143.94, -0.3, 0.0, -0.2),
        (6, "Imagine", 235.75, -0.1, 0.2, -0.1),
        (7, "5 (Change)", 386.14, 0.0, 0.3, 0.0),
        (8, "Maya Angelou", 632.46, 0.1, 0.5, 0.1),
        (9, "1984", 1035.89, 0.2, 0.2, 0.3),
        (10, "Inception", 1696.69, 0.3, 0.4, 0.4),
        (11, "Gandalf", 2778.99, 0.5, 0.6, 0.6),
        (12, "Buddhism", 4551.69, 0.6, 0.7, 0.5),
        (13, "Zeus", 7455.19, 0.7, 0.5, 0.7),
        (14, "Sirius", 12210.80, 0.8, 0.8, 0.9),
        (15, "Prince", 20000.00, 0.9, 0.9, 1.0),
    ]
    return load_trajectory_data(data)


# ============================================================================
# CLI INTERFACE
# ============================================================================


def print_summary(summary: EfficiencySummary) -> None:
    """Print formatted efficiency summary to console."""
    print("\n" + "=" * 70)
    print("TRAJECTORY EFFICIENCY ANALYSIS")
    print("=" * 70)

    print(
        f"\nEfficiency Vector: [{summary.efficiency_vector[0]:.3f}, "
        f"{summary.efficiency_vector[1]:.3f}, {summary.efficiency_vector[2]:.3f}]"
    )
    print(f"Efficiency Score: {summary.efficiency_score:.3f} (range: -1 to 1)")
    print(f"Balance Factor: {summary.balance_factor_degrees:.2f} degrees")

    print("\nAngular Relationships:")
    print(
        f"  Influence <-> Productivity: {summary.angle_influence_productivity:.2f} degrees"
    )
    print(
        f"  Influence <-> Creativity:   {summary.angle_influence_creativity:.2f} degrees"
    )
    print(
        f"  Productivity <-> Creativity: {summary.angle_productivity_creativity:.2f} degrees"
    )

    print("\nInterpretation:")
    for line in summary.interpretation().split("\n"):
        print(f"  {line}")
    print("\n" + "=" * 70 + "\n")


def main() -> int:
    """Main CLI entrypoint."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Trajectory Analysis System - Analyze influence, productivity, and creativity vectors",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python trajectory_analysis.py --interactive
  python trajectory_analysis.py --output results.json --save-plot trajectory.png
  python trajectory_analysis.py --no-plot  # Metrics only (CI/batch mode)
        """,
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Show interactive 3D plot"
    )
    parser.add_argument("--output", type=Path, help="Path to save JSON results")
    parser.add_argument(
        "--save-plot", type=Path, help="Path to save plot image (PNG, PDF, SVG)"
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Skip plotting (useful for CI/batch processing)",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    try:
        # Load default trajectory data
        print("Loading trajectory data...")
        trajectory_points = get_default_trajectory_data()
        print(f"Loaded {len(trajectory_points)} trajectory points")

        # Calculate metrics
        print("Calculating efficiency metrics...")
        summary = calculate_efficiency_metrics(trajectory_points)

        # Print summary
        print_summary(summary)

        # Save JSON if requested
        if args.output:
            with open(args.output, "w") as f:
                json.dump(summary.to_dict(), f, indent=2)
            print(f"[OK] Results saved to {args.output}")

        # Create plot if not disabled
        if not args.no_plot:
            # Create vector set
            influence_vec = normalize(np.array([0.6, 0.8, 0.5]))
            productivity_vec = normalize(np.array([0.9, 0.4, 0.3]))
            creativity_point = next(
                p for p in trajectory_points if p.archetype == "Leonardo da Vinci"
            )
            creativity_vec = normalize(creativity_point.vector)

            vectors = VectorSet(
                influence=influence_vec,
                productivity=productivity_vec,
                creativity=creativity_vec,
                efficiency=summary.efficiency_vector,
            )

            # Plot
            print("Generating 3D visualization...")
            plot_trajectory_3d(
                trajectory_points,
                vectors,
                show=args.interactive,
                save_path=args.save_plot,
            )

            if not args.interactive and not args.save_plot:
                print(
                    "[!] Plot generated but not displayed. Use --interactive or --save-plot"
                )

        print("[OK] Analysis complete")
        return 0

    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
