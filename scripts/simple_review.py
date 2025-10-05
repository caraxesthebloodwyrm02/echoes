"""
Simple Task Review Script

A simplified version to analyze tasks from discover_tasks.json
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def main():
    # Configuration
    tasks_file = Path(
        "e:/Projects/automation-framework-clean/automation/reports/discover_tasks.json"
    )

    # Load tasks
    try:
        with open(tasks_file, "r") as f:
            tasks = json.load(f)
        print(f"Successfully loaded {len(tasks)} tasks")

        # Print task summary
        print("\nTask Summary:")
        print("-" * 50)
        print(f"{'ID':<15} {'Name':<25} {'Severity':<10} {'Category':<15} {'Files'}")
        print("-" * 50)

        for task in tasks:
            print(
                f"{task.get('task_id', 'N/A'):<15} "
                f"{task.get('task_name', 'Unnamed'):<25} "
                f"{task.get('severity', 'N/A'):<10} "
                f"{task.get('category', 'N/A'):<15} "
                f"{len(task.get('files', []))} files"
            )

        # Count by severity and category
        severity_count = {}
        category_count = {}

        for task in tasks:
            severity = task.get("severity", "unknown")
            category = task.get("category", "uncategorized")

            severity_count[severity] = severity_count.get(severity, 0) + 1
            category_count[category] = category_count.get(category, 0) + 1

        # Print summary
        print("\nSeverity Counts:")
        for severity, count in severity_count.items():
            print(f"- {severity}: {count}")

        print("\nCategory Counts:")
        for category, count in category_count.items():
            print(f"- {category}: {count}")

        # Find high-risk tasks
        high_risk = [
            t
            for t in tasks
            if t.get("severity") == "high" or t.get("category") in ["security", "refactor"]
        ]

        print(f"\nFound {len(high_risk)} high-risk or security-related tasks")

        for task in high_risk:
            print(f"\nHigh-Risk Task: {task.get('task_id')} - {task.get('task_name')}")
            print(f"  Category: {task.get('category')}")
            print(f"  Severity: {task.get('severity')}")
            print(f"  Description: {task.get('description')}")
            print(f"  Suggested Fix: {task.get('suggested_fix')}")
            print(f"  Files: {', '.join(task.get('files', []))}")
            print(f"  Branch: automation/highrisk/{task.get('task_id')}")

    except FileNotFoundError:
        print(f"Error: File not found - {tasks_file}")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {tasks_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
