"""
High-Risk Task Review and Execution Script

This script provides a guided workflow for reviewing and executing high-risk tasks
identified by the automation framework. It includes dry-run capabilities, manual
review steps, and safety checks.

Usage:
    python -m automation.scripts.review_high_risk_tasks [--dry-run] [--task TASK_ID]
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

from automation.core.context import Context
from automation.core.logger import log
from automation.core.orchestrator import Orchestrator


class HighRiskTaskHandler:
    def __init__(self, config_path: str | None = None):
        # Use the automation-framework-clean directory as the project root
        self.project_root = Path("e:/Projects/automation-framework-clean")
        if config_path:
            self.config_path = Path(config_path)
        else:
            self.config_path = self.project_root / "config" / "automation.yaml"
        self.tasks_json = self.project_root / "automation" / "reports" / "discover_tasks.json"
        self.orch = Orchestrator(str(self.config_path))
        self.orch.context.dry_run = True  # Default to safe mode
        self.tasks: List[Dict[str, Any]] = []

    def load_tasks(self) -> None:
        """Load tasks from the discovery report."""
        if not self.tasks_json.exists():
            raise FileNotFoundError(f"Task report not found: {self.tasks_json}")
        with open(self.tasks_json, "r") as f:
            self.tasks = json.load(f)

        log.info(f"Loaded {len(self.tasks)} tasks from {self.tasks_json}")

    def dry_run_task(self, task: Dict[str, Any]) -> None:
        """Simulate task execution without making changes."""
        log.info(f"[DRY RUN] Would execute task: {task.get('id')}")
        log.info(f"Action: {task.get('action', 'No action specified')}")
        log.info("No changes were made (dry run mode)")

    def execute_task(self, task: Dict[str, Any]) -> bool:
        """Execute the specified task."""
        task_id = task.get("id")
        log.info(f"Executing task: {task_id}")

        try:
            result = self.orch.execute_task(task_id)
            log.success(f"Successfully executed task: {task_id}")
        except Exception as e:
            log.error(f"Failed to execute task {task_id}: {e}")
            return False

    def show_task_details(self, task: Dict[str, Any]) -> None:
        """Display detailed information about a task."""
        print(f"\n{'=' * 50}")
        print(f"Task ID: {task.get('id', 'N/A')}")
        print(f"Title: {task.get('title', 'N/A')}")
        print(f"Category: {task.get('category', 'N/A')}")
        print(f"Risk Level: {task.get('risk_level', 'N/A')}")
        print(f"Description: {task.get('description', 'No description')}")

        if "files" in task:
            print("\nAffected files:")
            for file_path in task.get("files", []):
                cleaned_path = Path(str(file_path).strip("\"' "))
                if cleaned_path.exists():
                    print(f"  - {cleaned_path} (exists)")
                else:
                    print(f"  [File not found: {cleaned_path}]")


def main():
    parser = argparse.ArgumentParser(description="Review and execute high-risk tasks")
    parser.add_argument("--dry-run", action="store_true", help="Only show what would be done")
    parser.add_argument("--task", help="Specific task ID to run")
    parser.add_argument("--category", help="Filter tasks by category (e.g., 'security')")
    parser.add_argument("--config", default=None, help="Path to automation config file")
    args = parser.parse_args()

    try:
        handler = HighRiskTaskHandler(args.config)
        handler.load_tasks()

        # Get tasks to process
        tasks = [t for t in handler.tasks if t.get("risk_level", "low") == "high"]

        # Filter by category if specified
        if args.category:
            tasks = [t for t in tasks if t.get("category") == args.category]

        # Filter by task ID if specified
        if args.task:
            tasks = [t for t in tasks if t.get("id") == args.task]
            if not tasks:
                log.error(f"No task found with ID: {args.task}")
                return 1

        if not tasks:
            log.info("No high-risk tasks found matching criteria")
            return 0

        log.info(f"Found {len(tasks)} high-risk task(s) to review")

        # Process each task
        for task in tasks:
            try:
                handler.show_task_details(task)

                if args.dry_run:
                    handler.dry_run_task(task)
                else:
                    if handler.execute_task(task):
                        # Run tests after each task if not in dry-run
                        if not handler.run_tests():
                            log.error("Stopping due to test failures")
                            return 1

            except Exception as e:
                log.error(f"Error processing task {task.get('id')}: {e}")
                import traceback

                traceback.print_exc()
                return 1

        return 0

    except Exception as e:
        log.error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
