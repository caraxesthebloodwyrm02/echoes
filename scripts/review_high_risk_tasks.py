"""
High-Risk Task Review and Remediation Script

This script analyzes tasks from discover_tasks.json and generates a structured
review of high-risk tasks that require human attention.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import subprocess
import sys

# Configuration
PROJECT_ROOT = Path("e:/Projects/automation-framework-clean")
TASKS_FILE = PROJECT_ROOT / "automation" / "reports" / "discover_tasks.json"
OUTPUT_FILE = PROJECT_ROOT / "automation" / "reports" / "highrisk_review.json"


def load_tasks() -> List[Dict[str, Any]]:
    """Load tasks from the discovery report."""
    if not TASKS_FILE.exists():
        print(f"Error: Task report not found: {TASKS_FILE}")
        sys.exit(1)

    with open(TASKS_FILE, "r") as f:
        return json.load(f)


def filter_high_risk_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter tasks to include only high-risk or security-related ones."""
    return [
        task
        for task in tasks
        if task.get("severity") == "high" or task.get("category") in ["security", "refactor"]
    ]


def get_code_context(
    file_path: str, line_numbers: List[int], context_lines: int = 8
) -> Dict[int, List[str]]:
    """Get context around specified line numbers in a file."""
    context = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line_num in line_numbers:
            start = max(0, line_num - context_lines // 2 - 1)
            end = min(len(lines), line_num + context_lines // 2)
            context[line_num] = [
                f"{start + i + 1}: {line.rstrip()}" for i, line in enumerate(lines[start:end])
            ]
    except Exception as e:
        context[line_num] = [f"Error reading file: {e}"]

    return context


def create_review(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create a structured review for each task."""
    reviews = []

    for task in tasks:
        task_id = task["task_id"]
        task_name = task["task_name"]

        # Get code context for each file
        file_contexts = {}
        for file_path in task.get("files", []):
            abs_path = PROJECT_ROOT / file_path
            if abs_path.exists():
                file_contexts[file_path] = get_code_context(
                    str(abs_path),
                    [
                        int(line)
                        for line in task.get("lines", [])
                        if isinstance(line, (int, str)) and str(line).isdigit()
                    ],
                )

        # Create review entry
        review = {
            "task_id": task_id,
            "task_name": task_name,
            "category": task.get("category", "uncategorized"),
            "severity": task.get("severity", "medium"),
            "files": task.get("files", []),
            "description": task.get("description", "No description provided"),
            "suggested_fix": task.get("suggested_fix", "No suggested fix provided"),
            "code_context": file_contexts,
            "risk_assessment": "",  # Will be filled based on task details
            "remediation_steps": [],
            "required_approvals": [],
            "estimated_effort": "M",  # Default to Medium
            "branch_name": f"automation/highrisk/{task_id}",
            "pr_title": f"[{task_id}] {task_name}",
            "pr_body": f"""## Task: {task_name} ({task_id})

**Category:** {task.get('category', 'N/A')}  
**Severity:** {task.get('severity', 'N/A')}

### Description
{task.get('description', 'No description provided')}

### Suggested Fix
{task.get('suggested_fix', 'No suggested fix provided')}

### Affected Files
"""
            + "\n".join(f"- `{file}`" for file in task.get("files", []))
            + """

### Required Approvals
- [ ] Tech Lead
- [ ] Security Team (if security-related)

### Test Plan
1. Run unit tests: `pytest tests/`
2. Run integration tests: `pytest tests/integration/`
3. Manual verification steps:
   - [ ] Verify functionality
   - [ ] Check logs for errors

### Rollback Plan
1. Revert branch
2. Run tests to verify rollback
""",
        }

        # Set risk assessment based on task type
        if task.get("category") == "security":
            review["risk_assessment"] = (
                "Security-related changes require careful review to prevent "
                "vulnerabilities. Changes may affect authentication, authorization, "
                "or data protection."
            )
            review["required_approvals"].extend(["Security Team", "Tech Lead"])
        elif task.get("severity") == "high":
            review["risk_assessment"] = (
                "High severity issue that could impact system stability or data integrity. "
                "Requires thorough testing before deployment."
            )
            review["required_approvals"].append("Tech Lead")
        else:
            review["risk_assessment"] = "Standard risk assessment pending review."

        # Add remediation steps
        review["remediation_steps"] = [
            {
                "step": 1,
                "action": f"Review the code changes needed for {task_id}",
                "details": f"See code context in the 'code_context' field",
            },
            {"step": 2, "action": "Run tests", "details": "pytest tests/"},
            {
                "step": 3,
                "action": "Get required approvals",
                "details": ", ".join(review["required_approvals"]),
            },
            {
                "step": 4,
                "action": "Merge and deploy",
                "details": "After approvals and successful testing",
            },
        ]

        reviews.append(review)

    return reviews


def create_branch(branch_name: str) -> bool:
    """Create a git branch for the task (dry run)."""
    print(f"[DRY RUN] Would create branch: {branch_name}")
    print(f"  git checkout -b {branch_name}")
    return True


def create_pr(branch_name: str, title: str, body: str) -> bool:
    """Create a PR for the task (dry run)."""
    print(f"\n[DRY RUN] Would create PR for branch: {branch_name}")
    print(f"Title: {title}")
    print(f"Body: {body[:200]}...")
    return True


def main():
    print("Loading tasks...")
    tasks = load_tasks()
    print(f"Loaded {len(tasks)} total tasks")

    high_risk_tasks = filter_high_risk_tasks(tasks)
    print(f"Found {len(high_risk_tasks)} high-risk or security-related tasks")

    if not high_risk_tasks:
        print("No high-risk tasks found. Exiting.")
        return

    print("\nGenerating reviews...")
    reviews = create_review(high_risk_tasks)

    # Create branches and PRs (dry run)
    for review in reviews:
        print(f"\nProcessing task: {review['task_id']} - {review['task_name']}")
        create_branch(review["branch_name"])
        create_pr(review["branch_name"], review["pr_title"], review["pr_body"])

    # Save review to file
    output = {"timestamp": datetime.utcnow().isoformat(), "tasks": reviews}

    os.makedirs(OUTPUT_FILE.parent, exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nReview saved to: {OUTPUT_FILE}")
    print("\nNext steps:")
    print("1. Review the generated highrisk_review.json")
    print("2. Create branches and PRs for each high-risk task")
    print("3. Assign reviewers based on required approvals")
    print("4. Follow the remediation steps in each PR")


if __name__ == "__main__":
    main()
