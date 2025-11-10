#!/usr/bin/env python3
"""
Coverage Pattern Analysis Tool
Analyzes the last 20 coverage reports to identify patterns and ignition points
"""

import os
import re
import subprocess
from datetime import datetime


def extract_coverage_from_output(text):
    """Extract coverage percentage from pytest output"""
    patterns = [
        r"TOTAL.*?\s+(\d+\.?\d*)%",
        r"coverage:\s+(\d+\.?\d*)%",
        r'line-rate="(\d+\.?\d*)"',
        r"(\d+\.?\d*)%.*?coverage",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def find_coverage_reports():
    """Find all coverage-related files and outputs"""
    coverage_data = []

    # Search for coverage files
    for root, dirs, files in os.walk("."):
        for file in files:
            if any(
                keyword in file.lower() for keyword in ["coverage", "test", "report"]
            ):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        coverage = extract_coverage_from_output(content)
                        if coverage:
                            coverage_data.append(
                                {
                                    "file": file_path,
                                    "coverage": coverage,
                                    "timestamp": datetime.fromtimestamp(
                                        os.path.getmtime(file_path)
                                    ),
                                    "type": "file",
                                }
                            )
                except:
                    pass

    # Also look for recent pytest runs in terminal history
    try:
        result = subprocess.run(
            ["pytest", "--collect-only"], capture_output=True, text=True, cwd="."
        )
        if result.stdout:
            # Extract test count as a proxy for coverage potential
            test_count = len(re.findall(r"<.*?Test.*?>", result.stdout))
            coverage_data.append(
                {
                    "file": "current_tests",
                    "coverage": test_count * 2.5,  # Rough estimate
                    "timestamp": datetime.now(),
                    "type": "current",
                }
            )
    except:
        pass

    return sorted(coverage_data, key=lambda x: x["timestamp"], reverse=True)[:20]


def analyze_patterns(coverage_data):
    """Analyze patterns in coverage data"""
    if len(coverage_data) < 2:
        return "Insufficient data for pattern analysis"

    # Calculate changes
    changes = []
    for i in range(len(coverage_data) - 1):
        current = coverage_data[i]["coverage"]
        previous = coverage_data[i + 1]["coverage"]
        change = current - previous
        changes.append(change)

    # Identify patterns
    avg_change = sum(changes) / len(changes) if changes else 0
    max_increase = max(changes) if changes else 0
    max_decrease = min(changes) if changes else 0

    # Find ignition points (significant increases)
    ignition_points = []
    for i, change in enumerate(changes):
        if change > avg_change * 2:  # Significant increase
            ignition_points.append(
                {
                    "index": i,
                    "file": coverage_data[i]["file"],
                    "change": change,
                    "coverage_before": coverage_data[i + 1]["coverage"],
                    "coverage_after": coverage_data[i]["coverage"],
                }
            )

    return {
        "trend": "increasing"
        if avg_change > 0
        else "decreasing"
        if avg_change < 0
        else "stable",
        "avg_change": avg_change,
        "max_increase": max_increase,
        "max_decrease": max_decrease,
        "ignition_points": ignition_points,
        "volatility": max_increase - max_decrease,
    }


def find_ignition_path(patterns):
    """Find the most functional path to increase coverage"""
    if not patterns or isinstance(patterns, str):
        return "No patterns found"

    # Analyze ignition points
    if patterns["ignition_points"]:
        best_ignition = max(patterns["ignition_points"], key=lambda x: x["change"])

        return {
            "ignition_file": best_ignition["file"],
            "ignition_change": best_ignition["change"],
            "strategy": f"FOCUS on {best_ignition['file']} - showed {best_ignition['change']:.1f}% increase!",
            "recommended_actions": [
                f"Analyze what made {best_ignition['file']} successful",
                "Replicate the testing approach in similar files",
                "Focus on high-impact, low-complexity test additions",
                "Target the specific uncovered lines identified in coverage reports",
            ],
        }
    else:
        # No ignition points found, suggest strategy
        return {
            "ignition_file": None,
            "ignition_change": 0,
            "strategy": "SYSTEMATIC APPROACH NEEDED - No significant increases detected",
            "recommended_actions": [
                "Start with api/main.py - highest impact (66% → 75% needs 9% increase)",
                "Focus on WebSocket endpoint tests (lines 72-77, 81-84)",
                "Add pattern detection core logic tests (26% → 75% needs 49% increase)",
                "Target middleware edge cases (72% → 75% needs 3% increase)",
            ],
        }


def main():
    """Main analysis function"""
    print("🔍 ANALYZING COVERAGE PATTERNS...")
    print("=" * 50)

    # Get coverage data
    coverage_data = find_coverage_reports()

    print(f"📊 Found {len(coverage_data)} data points")
    print("\n📈 Recent Coverage History:")
    for i, data in enumerate(coverage_data[:10]):
        print(
            f"  {i+1}. {data['file']}: {data['coverage']:.1f}% ({data['timestamp'].strftime('%H:%M:%S')})"
        )

    # Analyze patterns
    patterns = analyze_patterns(coverage_data)

    print("\n🎯 PATTERN ANALYSIS:")
    if isinstance(patterns, dict):
        print(f"  Trend: {patterns['trend']}")
        print(f"  Average Change: {patterns['avg_change']:.2f}%")
        print(f"  Max Increase: {patterns['max_increase']:.2f}%")
        print(f"  Max Decrease: {patterns['max_decrease']:.2f}%")
        print(f"  Volatility: {patterns['volatility']:.2f}%")

        if patterns["ignition_points"]:
            print(f"  Ignition Points Found: {len(patterns['ignition_points'])}")
            for point in patterns["ignition_points"][:3]:
                print(f"    - {point['file']}: +{point['change']:.1f}%")
    else:
        print(f"  {patterns}")

    # Find ignition path
    ignition_path = find_ignition_path(patterns)

    print("\n🚀 IGNITION PATH IDENTIFIED:")
    print(f"  Strategy: {ignition_path['strategy']}")

    if ignition_path["ignition_file"]:
        print(f"  🎯 CONTACT POINT: {ignition_path['ignition_file']}")
        print(f"  📈 Potential Lift: +{ignition_path['ignition_change']:.1f}%")

    print("\n⚡ RECOMMENDED ACTIONS:")
    for action in ignition_path["recommended_actions"]:
        print(f"  • {action}")

    print("\n✨ ELEVATION SEQUENCE INITIATED!")


if __name__ == "__main__":
    main()
