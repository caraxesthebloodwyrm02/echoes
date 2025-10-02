"""Automation script for creating PRs from high-risk tasks."""

import json
import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
log = logging.getLogger(__name__)


@dataclass
class TaskDefinition:
    """Structure for a high-risk task."""

    task_id: str
    task_name: str
    category: str
    severity: str
    description: str
    suggested_fix: str
    files: list[str]
    branch_name: str
    pr_title: str
    pr_body: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskDefinition":
        """Create TaskDefinition from JSON data."""
        branch_name = f"automation/highrisk/{data['task_id']}"
        pr_title = f"[HIGH-RISK] {data['task_name']} — {data['task_id']}"

        pr_body = f"""## Task: {data['task_name']} ({data['task_id']})

**Category:** {data['category']}
**Severity:** {data['severity']}

### Description
{data['description']}

### Suggested Fix
{data['suggested_fix']}

### Affected Files
{chr(10).join([f"- `{f}`" for f in data['files']])}

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
"""
        return cls(
            task_id=data["task_id"],
            task_name=data["task_name"],
            category=data["category"],
            severity=data["severity"],
            description=data["description"],
            suggested_fix=data["suggested_fix"],
            files=data["files"],
            branch_name=branch_name,
            pr_title=pr_title,
            pr_body=pr_body,
        )


def run_git_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess:
    """Run a git command and return the result.

    Args:
        cmd: Command list starting with 'git'
        check: Whether to raise on non-zero exit

    Returns:
        CompletedProcess instance
    """
    log.debug(f"Running git command: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        log.error(f"Git command failed: {e}")
        log.error(f"Error output: {e.stderr}")
        raise


def load_tasks(task_file: Path) -> list[TaskDefinition]:
    """Load and filter high-risk tasks from JSON.

    Args:
        task_file: Path to highrisk_review.json

    Returns:
        List of TaskDefinition objects
    """
    try:
        with open(task_file, encoding="utf-8") as f:
            data = json.load(f)

        tasks = []
        for task in data["tasks"]:
            if task["severity"] == "high" or task["category"] == "security":
                tasks.append(TaskDefinition.from_dict(task))

        return tasks
    except Exception as e:
        log.error(f"Failed to load tasks: {e}")
        raise


def create_branch_for_task(task: TaskDefinition, dry_run: bool = True) -> bool:
    """Create and push a branch for the given task.

    Args:
        task: TaskDefinition object
        dry_run: If True, only print commands

    Returns:
        bool: True if successful
    """
    try:
        if dry_run:
            log.info(f"[DRY RUN] Would create branch: {task.branch_name}")
            log.info(f"[DRY RUN] PR Title: {task.pr_title}")
            log.info(f"[DRY RUN] Files to review: {', '.join(task.files)}")
            return True

        # Fetch and create branch from main
        run_git_command(["git", "fetch", "origin", "main"])
        run_git_command(["git", "checkout", "-b", task.branch_name, "origin/main"])

        # Create PR body file
        pr_body_path = Path(f"tmp_pr_body_{task.task_id}.md")
        pr_body_path.write_text(task.pr_body, encoding="utf-8")

        # Add and commit PR body
        run_git_command(["git", "add", str(pr_body_path)])
        run_git_command(
            [
                "git",
                "commit",
                "-m",
                f"[HIGH-RISK][{task.task_id}] Initialize PR for {task.task_name}",
            ]
        )

        # Push branch
        run_git_command(["git", "push", "-u", "origin", task.branch_name])

        log.info(f"Successfully created branch: {task.branch_name}")
        log.info(f"PR Title: {task.pr_title}")
        log.info(f"PR body saved to: {pr_body_path}")

        return True

    except Exception as e:
        log.error(f"Failed to create branch for task {task.task_id}: {e}")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Automate high-risk task PR creation")
    parser.add_argument(
        "--dry-run", action="store_true", help="Print commands without executing"
    )
    args = parser.parse_args()

    task_file = Path("automation/reports/highrisk_review.json")
    if not task_file.exists():
        log.error(f"Task file not found: {task_file}")
        sys.exit(1)

    try:
        tasks = load_tasks(task_file)
        log.info(f"Found {len(tasks)} high-risk/security tasks")

        for task in tasks:
            log.info(f"\nProcessing task: {task.task_id}")
            success = create_branch_for_task(task, dry_run=args.dry_run)
            if not success:
                log.error(f"Failed to process task {task.task_id}")
                continue

    except Exception as e:
        log.error(f"Script failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
