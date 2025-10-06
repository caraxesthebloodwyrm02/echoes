"""
QueensGambit: Daily Codebase Insights & Failsafe Logger

- Aggregates and logs findings from janitor/maintenance/automation runs
- Produces JSON insight snippets for user review
- Designed for robust daily review and failsafe design
- Can be extended to auto-email, alert, or trigger further actions

Usage:
    python queensgambit.py [--report-dir automation/reports] [--output queensgambit_insights.json]

Options:
    --report-dir   Directory to scan for JSON/YAML reports (default: automation/reports)
    --output       Output file for aggregated insights (default: queensgambit_insights.json)
"""
import argparse
import json
import os
from pathlib import Path
from datetime import datetime
import glob


def collect_reports(report_dir):
    findings = []
    for ext in ("*.json", "*.yaml", "*.yml"):
        for file in Path(report_dir).glob(ext):
            try:
                if file.suffix == ".json":
                    with open(file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                else:
                    import yaml

                    with open(file, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)
                findings.append({"file": str(file), "data": data})
            except Exception as e:
                findings.append({"file": str(file), "error": str(e)})
    return findings


def extract_insights(findings):
    insights = []
    for item in findings:
        file = item.get("file")
        data = item.get("data", {})
        if not data:
            continue
        # Foreign Dependency
        if "classification" in data:
            crit = data["classification"].get("critical", [])
            if crit:
                insights.append(
                    {
                        "type": "foreign_dependency_violation",
                        "file": file,
                        "details": crit,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
        # Security Monitoring
        if "security_score" in data:
            if data["security_score"] < 80:
                insights.append(
                    {
                        "type": "security_risk",
                        "file": file,
                        "score": data["security_score"],
                        "timestamp": datetime.now().isoformat(),
                    }
                )
        # Semantic Guardrails
        if "violations" in data:
            if data["violations"]:
                insights.append(
                    {
                        "type": "semantic_guardrail_violation",
                        "file": file,
                        "count": len(data["violations"]),
                        "examples": data["violations"][:3],
                        "timestamp": datetime.now().isoformat(),
                    }
                )
    return insights


def main():
    parser = argparse.ArgumentParser(
        description="QueensGambit: Daily Codebase Insights & Failsafe Logger"
    )
    parser.add_argument(
        "--report-dir", default="automation/reports", help="Directory to scan for reports"
    )
    parser.add_argument(
        "--output", default="queensgambit_insights.json", help="Output JSON file for insights"
    )
    args = parser.parse_args()

    findings = collect_reports(args.report_dir)
    insights = extract_insights(findings)

    summary = {
        "timestamp": datetime.now().isoformat(),
        "insights": insights,
        "findings_count": len(findings),
        "insights_count": len(insights),
    }
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
    print(f"QueensGambit: {len(insights)} insights written to {args.output}")


if __name__ == "__main__":
    main()
