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
Codebase Visualization Tool

This script analyzes code quality metrics and generates visualizations
for codebase robustness and practicality.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Set UTF-8 encoding for entire script
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr.reconfigure(encoding="utf-8")

# Constants
METRICS_DIR = Path("metrics")
PLOTS_DIR = METRICS_DIR / "plots"
REPORTS = {
    "coverage": METRICS_DIR / "coverage.json",
    "flake8": METRICS_DIR / "flake8_report.json",
    "complexity": METRICS_DIR / "radon_cc.json",
    "maintainability": METRICS_DIR / "radon_mi.json",
}


def clean_environment():
    """Clean up previous run artifacts"""
    # Remove existing reports
    for report in REPORTS.values():
        if report.exists():
            report.unlink()

    # Remove coverage data
    coverage_files = [".coverage", ".coverage.new", "coverage.xml"]
    for cov_file in coverage_files:
        cov_path = Path(cov_file)
        if cov_path.exists():
            cov_path.unlink()

    # Ensure directories exist
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)


def check_tools() -> List[str]:
    """Check if required tools are installed"""
    tools = {
        "flake8": ["--version"],
        "coverage": ["--version"],
        "radon": ["--version"],
        "pytest": ["--version"],
    }

    missing = []
    for tool, args in tools.items():
        try:
            subprocess.run(
                [tool] + args,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            missing.append(tool)

    return missing


def run_tool(command: List[str], output_file: Optional[Path] = None) -> bool:
    """Run a tool with robust error handling"""
    try:
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                result = subprocess.run(
                    command,
                    check=False,
                    stdout=f,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding="utf-8",
                )
        else:
            result = subprocess.run(command, check=False, capture_output=True, text=True, encoding="utf-8")

        # Handle special exit codes
        if result.returncode != 0:
            if "flake8" in command[0] and result.returncode == 1:
                # Flake8 returns 1 when issues are found
                return True
            if "pytest" in " ".join(command) and result.returncode == 2:
                # Pytest returns 2 when tests fail, but coverage can still be collected
                return True
            print(f"[ERROR] Command failed: {' '.join(command)}")
            print(f"Exit code: {result.returncode}")
            if result.stderr:
                print(f"Error output:\n{result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"[EXCEPTION] Running command: {' '.join(command)}")
        print(str(e))
        return False


def generate_reports() -> bool:
    """Generate required metric reports"""
    clean_environment()

    commands = [
        (["coverage", "run", "--data-file=.coverage.new", "-m", "pytest", "-s"], None),
        (
            [
                "coverage",
                "json",
                "--data-file=.coverage.new",
                "-o",
                str(REPORTS["coverage"]),
            ],
            None,
        ),
        # Flake8 handled separately with text parsing to ensure valid JSON
        (["radon", "cc", "-j", "-O", str(REPORTS["complexity"]), "."], None),
        (["radon", "mi", "-j", "-O", str(REPORTS["maintainability"]), "."], None),
    ]

    success = True
    for command, output_file in commands:
        tool_name = command[0]
        print(f"Running {tool_name}...")
        if not run_tool(command, output_file):
            print(f"[FAILED] {tool_name}")
            success = False
        else:
            print(f"[SUCCESS] {tool_name}")

    # Handle flake8 output
    flake8_command = ["flake8", "--max-line-length=120", "."]
    print(f"Running {flake8_command[0]}...")
    result = subprocess.run(flake8_command, check=False, capture_output=True, text=True, encoding="utf-8")
    if result.returncode not in [0, 1]:
        print("[FAILED] flake8")
        success = False
    else:
        # Parse text output
        issues = []
        for line in result.stdout.splitlines():
            parts = line.split(":", 3)
            if len(parts) >= 4:
                filename, line_num, col_num, message = (
                    parts[0],
                    parts[1],
                    parts[2],
                    parts[3],
                )
                issues.append(
                    {
                        "filename": filename,
                        "line": int(line_num),
                        "column": int(col_num),
                        "message": message.strip(),
                        "code": message.split()[0] if message else "",
                    }
                )
        # Save as JSON
        with open(REPORTS["flake8"], "w", encoding="utf-8") as f:
            json.dump(issues, f)
        print("[SUCCESS] flake8")

    # Clean up temporary coverage data
    if Path(".coverage.new").exists():
        Path(".coverage.new").unlink()

    return success


def load_report(report_name: str) -> Optional[Dict[str, Any]]:
    """Load a JSON report file with error handling"""
    try:
        report_path = REPORTS[report_name]
        if not report_path.exists():
            print(f"[ERROR] Report file not found: {report_path}")
            return None

        with open(report_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {report_name}: {e}")
        return None
    except KeyError:
        print(f"[ERROR] Unknown report name: {report_name}")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to load {report_name}: {str(e)}")
        return None


def analyze_robustness() -> bool:
    """Analyze and visualize codebase robustness"""
    print("\nAnalyzing codebase robustness...")

    coverage = load_report("coverage")
    issues = load_report("flake8")

    if not coverage or not issues:
        return False

    try:
        # Process coverage data
        coverage_data = {}
        for file_path, file_data in coverage.get("files", {}).items():
            if "summary" in file_data and "percent_covered" in file_data["summary"]:
                coverage_data[file_path] = file_data["summary"]["percent_covered"]

        # Process issues data
        issue_counts = {}
        for issue in issues:
            filename = issue.get("filename", "")
            issue_counts[filename] = issue_counts.get(filename, 0) + 1

        # Prepare plot data
        x, y = [], []
        for file_path, coverage_pct in coverage_data.items():
            if file_path in issue_counts:
                x.append(issue_counts[file_path])
                y.append(coverage_pct)

        if not x or not y:
            print("Insufficient data for robustness analysis")
            return False

        # Generate visualization
        import matplotlib.pyplot as plt
        import numpy as np

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
        avg_cov = np.mean(y)
        avg_issues = np.mean(x)
        plt.figtext(
            0.15,
            0.02,
            f"Avg Coverage: {avg_cov:.1f}% | " f"Avg Issues: {avg_issues:.1f} | " f"Files: {len(x)}",
            fontsize=9,
        )

        # Save plot
        plot_path = PLOTS_DIR / "robustness_analysis.png"
        plt.tight_layout()
        plt.savefig(plot_path, dpi=120, bbox_inches="tight")
        plt.close()
        print(f"[SAVED] Robustness analysis to {plot_path}")
        return True

    except ImportError:
        print("Installing required visualization packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib", "numpy"], check=True)
        return analyze_robustness()
    except Exception as e:
        print(f"[ERROR] In robustness analysis: {e}")
        return False


def analyze_practicality() -> bool:
    """Analyze and visualize codebase practicality"""
    print("\nAnalyzing codebase practicality...")

    cc_data = load_report("complexity")
    mi_data = load_report("maintainability")

    if not cc_data or not mi_data:
        return False

    try:
        # Process complexity data
        complexity = {}
        for file_path, blocks in cc_data.items():
            if isinstance(blocks, list) and blocks:
                try:
                    total_complexity = sum(b.get("complexity", 0) for b in blocks)
                    complexity[file_path] = total_complexity / len(blocks)
                except (TypeError, KeyError):
                    continue

        # Process maintainability data
        maintainability = {}
        for file_path, file_data in mi_data.items():
            if isinstance(file_data, dict) and "mi" in file_data:
                try:
                    maintainability[file_path] = float(file_data["mi"])
                except (TypeError, ValueError):
                    continue

        # Prepare plot data
        x, y, colors = [], [], []
        for file_path, comp in complexity.items():
            if file_path in maintainability:
                mi = maintainability[file_path]
                x.append(comp)
                y.append(mi)
                colors.append("green" if mi > 20 else "orange" if mi > 10 else "red")

        if not x or not y:
            print("Insufficient data for practicality analysis")
            return False

        # Generate visualization
        import matplotlib.pyplot as plt
        import numpy as np

        plt.figure(figsize=(12, 7))
        plt.scatter(x, y, c=colors, alpha=0.6, edgecolors="w")

        # Add reference lines
        plt.axhline(y=20, color="green", linestyle="--", alpha=0.5, label="Good Maintainability")
        plt.axhline(y=10, color="red", linestyle="--", alpha=0.5, label="Low Maintainability")

        plt.title("Codebase Practicality: Complexity vs. Maintainability")
        plt.xlabel("Average Cyclomatic Complexity (Lower is Better)")
        plt.ylabel("Maintainability Index (Higher is Better)")
        plt.legend()
        plt.grid(True, alpha=0.3)

        # Add statistics
        avg_comp = np.mean(x)
        avg_mi = np.mean(y)
        plt.figtext(
            0.15,
            0.02,
            f"Avg Complexity: {avg_comp:.1f} | " f"Avg Maintainability: {avg_mi:.1f} | " f"Files: {len(x)}",
            fontsize=9,
        )

        # Save plot
        plot_path = PLOTS_DIR / "practicality_analysis.png"
        plt.tight_layout()
        plt.savefig(plot_path, dpi=120, bbox_inches="tight")
        plt.close()
        print(f"[SAVED] Practicality analysis to {plot_path}")
        return True

    except ImportError:
        print("Installing required visualization packages...")
        subprocess.run([sys.executable, "-m", "pip", "install", "matplotlib", "numpy"], check=True)
        return analyze_practicality()
    except Exception as e:
        print(f"[ERROR] In practicality analysis: {e}")
        return False


def main() -> int:
    """Main entry point for the codebase visualization tool"""
    print("\n=== Codebase Analysis Tool ===\n")

    # Check for required tools
    missing_tools = check_tools()
    if missing_tools:
        print("\nMissing required tools. Please install them with:")
        print(f"pip install {' '.join(missing_tools)}\n")
        return 1

    # Generate reports
    print("\nGenerating required reports...")
    if not generate_reports():
        print("\n[FAILED] Could not generate all required reports.")
        return 1

    # Run analyses
    success = True
    if not analyze_robustness():
        success = False
    if not analyze_practicality():
        success = False

    if success:
        print("\n[SUCCESS] Analysis complete! Check the 'metrics/plots' directory for results.")
        return 0

    print("\n[WARNING] Some analyses failed. Check the output for details.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
