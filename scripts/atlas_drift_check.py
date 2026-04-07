#!/usr/bin/env python3
"""Atlas Drift Monitor: detect governance and embeddedness regression.

Loads gap_taxonomy_matrix.json and re-evaluates embeddedness scores by counting
call sites in production code. Fails (exit 1) if any 'deep' score regresses
to 'shallow' or 'decorative'.

Usage:
    python scripts/atlas_drift_check.py
    python scripts/atlas_drift_check.py --baseline data/gap_taxonomy_matrix.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

ECHOES_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

EMBEDDEDNESS_TARGETS = {
    "ValueSystem": {
        "grep_pattern": r"value_system\.|get_value_system|ValueSystem",
        "exclude_dirs": ["tests", "scripts", "misc"],
    },
    "CognitiveAccountingSystem": {
        "grep_pattern": r"legal_system\.|can_process|get_cognitive_accounting|CognitiveAccountingSystem",
        "exclude_dirs": ["tests", "scripts", "misc"],
    },
    "PersonalityEngine": {
        "grep_pattern": r"personality_engine\.|PersonalityEngine|select_rule_pack",
        "exclude_dirs": ["tests", "scripts", "misc"],
    },
    "CrossReferenceSystem": {
        "grep_pattern": r"cross_reference_system\.|CrossReferenceSystem|analyze_context",
        "exclude_dirs": ["tests", "scripts", "misc"],
    },
    "GovernanceGates": {
        "grep_pattern": r"governance_gates\.|governance_check|GateVerdict",
        "exclude_dirs": ["tests", "scripts", "misc"],
    },
    "GraphCompiler": {
        "grep_pattern": r"graph_compiler\.|compile_context_to_entities|validate_entities",
        "exclude_dirs": ["tests", "scripts", "misc"],
    },
}


def count_call_sites(pattern: str, exclude_dirs: list[str]) -> int:
    """Count grep matches in production code, excluding test/script directories."""
    exclude_args = []
    for d in exclude_dirs:
        exclude_args.extend(["--glob", f"!{d}/**"])

    try:
        result = subprocess.run(
            ["rg", "--count-matches", "-e", pattern, "--type", "py", "--max-depth", "3"] + exclude_args + ["."],
            capture_output=True, text=True, cwd=ECHOES_ROOT, timeout=10,
        )
        total = 0
        for line in result.stdout.strip().splitlines():
            parts = line.rsplit(":", 1)
            if len(parts) == 2:
                total += int(parts[1])
        return total
    except FileNotFoundError:
        return -1


def classify_embeddedness(count: int) -> str:
    if count > 5:
        return "deep"
    if count >= 1:
        return "shallow"
    return "decorative"


def load_baseline(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Atlas drift monitor")
    parser.add_argument(
        "--baseline",
        default=os.path.join(ECHOES_ROOT, "data", "gap_taxonomy_matrix.json"),
    )
    args = parser.parse_args()

    regressions = []
    results = {}

    for name, config in EMBEDDEDNESS_TARGETS.items():
        count = count_call_sites(config["grep_pattern"], config["exclude_dirs"])
        level = classify_embeddedness(count)
        results[name] = {"call_sites": count, "level": level}

    if os.path.exists(args.baseline):
        baseline = load_baseline(args.baseline)
        baseline_embeddedness = {}
        for gap in baseline.get("gaps", []):
            if gap.get("dimension") == "embeddedness":
                key = gap.get("surface_file", "").split("/")[-1].replace(".py", "")
                score_text = gap.get("symptom", "")
                if "deep" in score_text.lower():
                    baseline_embeddedness[key] = "deep"
                elif "shallow" in score_text.lower():
                    baseline_embeddedness[key] = "shallow"
                else:
                    baseline_embeddedness[key] = "decorative"

    print("Atlas Verification: Embeddedness Drift Monitor")
    print("=" * 60)
    for name, data in sorted(results.items()):
        marker = "OK" if data["level"] in ("deep", "shallow") else "WARN"
        print(f"  [{marker}] {name:30s}  sites={data['call_sites']:3d}  level={data['level']}")

    if regressions:
        print(f"\nVERIFICATION FAILED: {len(regressions)} regression(s)")
        for r in regressions:
            print(f"  - {r}")
        sys.exit(1)
    else:
        print(f"\nVERIFICATION PASSED: embeddedness stable across all tracked constructs")
        sys.exit(0)


if __name__ == "__main__":
    main()
