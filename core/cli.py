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

"""Typer-based CLI for trajectory efficiency analysis.

Commands:
    run      - Execute deterministic experiment (wraps run_experiment.py)
    ingest   - Process o3 JSON artifact into interactive HTML + docs
    validate - Validate JSON artifact against schema
"""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer(help="Trajectory Efficiency Analysis CLI")
console = Console()

# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command()
def run(
    input_file: Path = typer.Option(
        Path("data/input_vectors.json"), "--input", "-i", help="Input vectors JSON file"
    ),
    auto_ingest: bool = typer.Option(
        False, "--auto-ingest", help="Automatically run ingest after experiment"
    ),
) -> None:
    """Run deterministic trajectory efficiency experiment."""
    console.print("[bold blue]Running experiment...[/bold blue]")

    # Import here to avoid circular dependencies
    import run_experiment

    try:
        run_experiment.main()
        console.print("[bold green]✓ Experiment complete[/bold green]")

        if auto_ingest:
            # Find latest JSON
            results_dir = Path("results")
            json_files = sorted(results_dir.glob("*-analysis.json"))
            if json_files:
                latest = json_files[-1]
                console.print(f"[bold blue]Auto-ingesting {latest}...[/bold blue]")
                ingest(latest, create_pr=False)
    except Exception as e:
        console.print(f"[bold red]✗ Error: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def ingest(
    json_path: Path = typer.Argument(..., help="Path to analysis JSON"),
    create_pr: bool = typer.Option(
        False, "--create-pr", help="Create GitHub PR with updates"
    ),
) -> None:
    """Process o3 JSON artifact into interactive HTML and documentation."""
    if not json_path.exists():
        console.print(f"[bold red]✗ File not found: {json_path}[/bold red]")
        raise typer.Exit(1)

    console.print(f"[bold blue]Ingesting {json_path}...[/bold blue]")

    # Load and validate
    with json_path.open("r") as f:
        data = json.load(f)

    # Validate schema
    if not validate_schema(data, silent=True):
        console.print("[bold red]✗ Invalid JSON schema[/bold red]")
        raise typer.Exit(1)

    # Generate interactive HTML
    from .plotting import create_interactive_html

    html_path = json_path.parent / f"{json_path.stem}.html"
    create_interactive_html(data, html_path)
    console.print(f"[bold green]✓ Interactive HTML: {html_path}[/bold green]")

    # Update README
    _update_readme(data)
    console.print("[bold green]✓ README updated[/bold green]")

    # Generate executive summary
    summary = _generate_executive_summary(data)
    summary_path = json_path.parent / f"{json_path.stem}-executive.md"
    summary_path.write_text(summary, encoding="utf-8")
    console.print(f"[bold green]✓ Executive summary: {summary_path}[/bold green]")

    if create_pr:
        console.print("[bold yellow]PR creation not yet implemented[/bold yellow]")


@app.command()
def validate(
    json_path: Path = typer.Argument(..., help="Path to analysis JSON"),
) -> None:
    """Validate JSON artifact against schema."""
    if not json_path.exists():
        console.print(f"[bold red]✗ File not found: {json_path}[/bold red]")
        raise typer.Exit(1)

    with json_path.open("r") as f:
        data = json.load(f)

    if validate_schema(data, silent=False):
        console.print("[bold green]✓ Valid JSON schema[/bold green]")
    else:
        raise typer.Exit(1)


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def validate_schema(data: dict, silent: bool = False) -> bool:
    """Validate JSON against expected schema."""
    required_keys = ["timestamp", "seed", "vectors", "metrics", "classification"]

    for key in required_keys:
        if key not in data:
            if not silent:
                console.print(f"[bold red]✗ Missing key: {key}[/bold red]")
            return False

    # Validate vectors
    vector_keys = ["influence", "productivity", "creativity", "efficiency"]
    for vkey in vector_keys:
        if vkey not in data["vectors"]:
            if not silent:
                console.print(f"[bold red]✗ Missing vector: {vkey}[/bold red]")
            return False

    # Validate metrics
    if "efficiency_score" not in data["metrics"]:
        if not silent:
            console.print("[bold red]✗ Missing efficiency_score[/bold red]")
        return False

    return True


def _update_readme(data: dict) -> None:
    """Update README.md with latest results."""
    readme_path = Path("README.md")

    # Create results section
    classification = data["classification"]
    metrics = data["metrics"]

    results_section = f"""
## Latest Results

**Classification:** {classification["label"]}
**Efficiency Score:** {metrics["efficiency_score"]:.3f}
**Balance Angle:** {metrics["balance_angle_deg"]:.2f}°

**Interpretation:** {classification["reason"]}

See `{data.get("artifacts", {}).get("png", "results/")}` for visualization.
"""

    # Append or update
    if readme_path.exists():
        content = readme_path.read_text(encoding="utf-8")
        if "## Latest Results" in content:
            # Replace existing section
            import re

            content = re.sub(
                r"## Latest Results.*?(?=\n##|\Z)",
                results_section.strip(),
                content,
                flags=re.DOTALL,
            )
        else:
            content += "\n" + results_section
        readme_path.write_text(content, encoding="utf-8")


def _generate_executive_summary(data: dict) -> str:
    """Generate executive summary from analysis data."""
    classification = data["classification"]
    metrics = data["metrics"]
    angles = metrics.get("pairwise_angles_deg", {})

    # Determine key insights
    label = classification["label"]
    score = metrics["efficiency_score"]
    balance = metrics["balance_angle_deg"]

    # Build narrative
    summary = f"""# Executive Summary

## System Classification: {label}

The trajectory efficiency analysis reveals a **{label.lower()}** system with an efficiency score of {score:.3f} and balance angle of {balance:.2f}°. {classification["reason"]}.

### Key Findings

"""

    # Add specific insights based on classification
    if label == "Aligned":
        summary += """
- **Strong Synergy**: All three dimensions (influence, productivity, creativity) work harmoniously together
- **Optimal Performance**: The system operates at peak efficiency with minimal internal friction
- **Sustainable Model**: Current configuration supports long-term growth and innovation
"""
    elif label == "Imbalanced":
        summary += f"""
- **Moderate Tension**: The system functions but shows signs of dimensional misalignment
- **Influence-Productivity Angle**: {angles.get("influence_productivity", 0):.1f}° indicates {"strong alignment" if angles.get("influence_productivity", 0) < 45 else "some friction"}
- **Creativity Gap**: Creativity dimension ({angles.get("productivity_creativity", 0):.1f}° from productivity) may be undervalued
"""
    else:  # Fragmented
        summary += """
- **Critical Misalignment**: Significant conflicts exist between core dimensions
- **Productivity-Creativity Opposition**: These dimensions work against each other, limiting innovation
- **Urgent Intervention Required**: Current trajectory is unsustainable without structural changes
"""

    # Tactical recommendations
    summary += """
### Tactical Recommendations

"""

    if label == "Aligned":
        summary += """1. **Maintain Current Balance**: Document and preserve successful practices
2. **Scale Gradually**: Expand operations while monitoring dimensional alignment
3. **Invest in Innovation**: Leverage strong creativity alignment for R&D initiatives
4. **Knowledge Transfer**: Codify processes to maintain alignment during growth
5. **Regular Monitoring**: Quarterly efficiency audits to detect early drift
6. **Celebrate Success**: Recognize teams maintaining this optimal configuration
"""
    elif label == "Imbalanced":
        summary += """1. **Creativity Integration**: Introduce structured ideation sessions (weekly 2-hour blocks)
2. **Cross-Functional Teams**: Mix productivity-focused and creativity-focused individuals
3. **Dual-Track KPIs**: Balance output metrics with innovation/exploration metrics
4. **Psychological Safety**: Create space for experimental work without penalty
5. **Resource Allocation**: Dedicate 15-20% of capacity to exploratory projects
6. **Feedback Loops**: Implement monthly retrospectives on creative vs. productive balance
"""
    else:  # Fragmented
        summary += """1. **Emergency Realignment**: Conduct immediate leadership workshop on dimensional conflicts
2. **Pause Non-Critical Work**: Focus on resolving core structural issues first
3. **Separate Tracks**: Create distinct teams for productivity and creativity with clear handoffs
4. **Cultural Reset**: Address underlying values driving opposition between dimensions
5. **External Facilitation**: Bring in organizational development consultant
6. **Phased Transformation**: 90-day intensive realignment program with weekly check-ins
"""

    summary += f"""
---
*Generated from analysis: {data["timestamp"]}*
*Seed: {data["seed"]}*
"""

    return summary


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app()
