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

"""
Codebase Analysis and Visualization Tool

This script analyzes code quality metrics and generates visualizations
for codebase robustness and practicality.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import List

# Constants
REPORTS = {
    "coverage": "coverage.json",
    "flake8": "flake8_report.json",
    "complexity": "radon_cc.json",
    "maintainability": "radon_mi.json",
}

PLOTS_DIR = Path("metrics") / "plots"


def check_tools() -> List[str]:
    """Check for required tools and return missing ones."""
    tools = {
        "flake8": "flake8 --version",
        "coverage": "coverage --version",
        "radon": "radon --version",
        "pytest": "pytest --version",
    }

    missing = []
    for tool, cmd in tools.items():
        try:
            subprocess.run(
                cmd,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            missing.append(tool)

    return missing


def generate_reports() -> bool:
    """Generate required metric reports."""
    cmds = {
        "coverage": "coverage run -m pytest && coverage json -o coverage.json",
        "flake8": "flake8 --format=json > flake8_report.json",
        "complexity": "radon cc -j -O radon_cc.json .",
        "maintainability": "radon mi -j -O radon_mi.json .",
    }

    success = True
    for name, cmd in cmds.items():
        if not os.path.exists(REPORTS[name]):
            print(f"\nGenerating {name} report...")
            try:
                subprocess.run(cmd, shell=True, check=True)
                print(f"✓ Generated {REPORTS[name]}")
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to generate {REPORTS[name]}: {e}")
                success = False

    return success


def load_report(name: str) -> dict:
    """Load a report file with error handling."""
    try:
        with open(REPORTS[name], encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading {REPORTS[name]}: {e}")
        return {}


def analyze_robustness() -> bool:
    """Analyze and visualize codebase robustness."""
    print("\nAnalyzing codebase robustness...")

    # Load required reports
    coverage = load_report("coverage")
    issues = load_report("flake8")

    if not coverage or not issues:
        return False

    # Process data
    coverage_data = {
        f: d["summary"]["percent_covered"]
        for f, d in coverage.get("files", {}).items()
        if "summary" in d and "percent_covered" in d["summary"]
    }

    issue_counts = {}
    for issue in issues:
        if isinstance(issue, dict) and "filename" in issue:
            f = issue["filename"]
            issue_counts[f] = issue_counts.get(f, 0) + 1

    # Prepare plot data
    x, y = [], []
    for f, cov in coverage_data.items():
        if f in issue_counts:
            x.append(issue_counts[f])
            y.append(cov)

    if not x or not y:
        print("Insufficient data for robustness analysis")
        return False

    # Create plot
    try:
        import matplotlib.pyplot as plt
        import numpy as np

        PLOTS_DIR.mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(12, 7))
        plt.scatter(x, y, alpha=0.6, c="blue", edgecolors="w")

        # Add trend line if enough points
        if len(x) > 1:
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            plt.plot(x, p(x), "r--")

        plt.title("Codebase Robustness: Test Coverage vs. Code Issues")
        plt.xlabel("Number of Flake8 Issues (Lower is Better)")
        plt.ylabel("Test Coverage % (Higher is Better)")
        plt.grid(True, alpha=0.3)

        # Add statistics
        avg_cov = sum(y) / len(y)
        avg_issues = sum(x) / len(x)
        plt.figtext(
            0.15,
            0.02,
            f"Avg Coverage: {avg_cov:.1f}% | "
            f"Avg Issues: {avg_issues:.1f} | "
            f"Files: {len(x)}",
            fontsize=9,
        )

        plot_path = PLOTS_DIR / "robustness_analysis.png"
        plt.tight_layout()
        plt.savefig(plot_path, dpi=120, bbox_inches="tight")
        print(f"✓ Saved robustness analysis to {plot_path}")
        return True

    except ImportError:
        print("Matplotlib not found. Installing...")
        subprocess.run("pip install matplotlib numpy", shell=True, check=True)
        return analyze_robustness()  # Retry after installation

    except Exception as e:
        print(f"Error creating robustness visualization: {e}")
        return False


def analyze_practicality() -> bool:
    """Analyze and visualize codebase practicality."""
    print("\nAnalyzing codebase practicality...")

    # Load required reports
    complexity = load_report("complexity")
    maintainability = load_report("maintainability")

    if not complexity or not maintainability:
        return False

    # Process complexity data
    comp_data = {}
    for f, blocks in complexity.items():
        if blocks and isinstance(blocks, list):
            try:
                comp_data[f] = sum(b["complexity"] for b in blocks) / len(blocks)
            except (KeyError, TypeError):
                continue

    # Process maintainability data
    mi_data = {}
    for f, data in maintainability.items():
        if isinstance(data, dict) and "mi" in data:
            try:
                mi_data[f] = float(data["mi"])
            except (TypeError, ValueError):
                continue

    # Prepare plot data
    x, y = [], []
    for f, comp in comp_data.items():
        if f in mi_data:
            x.append(comp)
            y.append(mi_data[f])

    if not x or not y:
        print("Insufficient data for practicality analysis")
        return False

    # Create plot
    try:
        import matplotlib.pyplot as plt

        PLOTS_DIR.mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(12, 7))

        # Color points based on maintainability
        colors = []
        for mi in y:
            if mi > 20:  # Good
                colors.append("green")
            elif mi > 10:  # Moderate
                colors.append("orange")
            else:  # Low
                colors.append("red")

        plt.scatter(x, y, c=colors, alpha=0.6, edgecolors="w")

        # Add reference lines
        plt.axhline(
            y=20, color="green", linestyle="--", alpha=0.5, label="Good Maintainability"
        )
        plt.axhline(
            y=10, color="red", linestyle="--", alpha=0.5, label="Low Maintainability"
        )

        plt.title("Codebase Practicality: Complexity vs. Maintainability")
        plt.xlabel("Average Cyclomatic Complexity (Lower is Better)")
        plt.ylabel("Maintainability Index (Higher is Better)")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Add statistics
        avg_comp = sum(x) / len(x)
        avg_mi = sum(y) / len(y)
        plt.figtext(
            0.15,
            0.02,
            f"Avg Complexity: {avg_comp:.1f} | "
            f"Avg Maintainability: {avg_mi:.1f} | "
            f"Files: {len(x)}",
            fontsize=9,
        )

        plot_path = PLOTS_DIR / "practicality_analysis.png"
        plt.tight_layout()
        plt.savefig(plot_path, dpi=120, bbox_inches="tight")
        print(f"✓ Saved practicality analysis to {plot_path}")
        return True

    except ImportError:
        print("Matplotlib not found. Installing...")
        subprocess.run("pip install matplotlib numpy", shell=True, check=True)
        return analyze_practicality()  # Retry after installation

    except Exception as e:
        print(f"Error creating practicality visualization: {e}")
        return False


def main() -> int:
    """Main function to run the analysis."""
    print("\n=== Codebase Analysis Tool ===\n")

    # Check for required tools
    missing_tools = check_tools()
    if missing_tools:
        print("\nMissing required tools. Please install them with:")
        print(f"pip install {' '.join(missing_tools)}\n")
        return 1

    # Generate reports if needed
    if not generate_reports():
        print("\nFailed to generate all required reports.")
        return 1

    # Run analyses
    success = True
    if not analyze_robustness():
        success = False
    if not analyze_practicality():
        success = False

    if success:
        print("\n✓ Analysis complete! Check the 'metrics/plots' directory for results.")
        return 0
    else:
        print("\n! Some analyses failed. Check the output for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
