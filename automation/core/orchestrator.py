"""Task orchestration for the automation framework."""

import importlib
from pathlib import Path

from automation.core.config import Config
from automation.core.context import Context
from automation.core.logger import log


class Orchestrator:
    """Orchestrates the execution of automation tasks."""

    def __init__(self, config_path: str | Path):
        """Initialize the orchestrator with a configuration file.

        Args:
            config_path: Path to the configuration file
        """
        self.config = Config(config_path)
        self.context = Context()
        self._tasks: dict[str, dict[str, list[str]]] = {}
        self._load_tasks()

    def _load_tasks(self) -> None:
        """Load task definitions from configuration."""
        self._tasks = self.config.get("framework.tasks", {})

    def get_task_categories(self) -> list[str]:
        """Get available task categories.

        Returns:
            List of task category names
        """
        return list(self._tasks.keys())

    def get_task_frequencies(self, category: str) -> list[str]:
        """Get available frequencies for a task category.

        Args:
            category: Task category name

        Returns:
            List of frequency names (e.g., ['daily', 'weekly'])
        """
        return list(self._tasks.get(category, {}).keys())

    def get_tasks(self, category: str, frequency: str) -> list[str]:
        """Get tasks for a category and frequency.

        Args:
            category: Task category name
            frequency: Task frequency (e.g., 'daily')

        Returns:
            List of task names
        """
        return self._tasks.get(category, {}).get(frequency, [])

    def run_task(self, task_name: str) -> bool:
        """Run a single task by name.

        Args:
            task_name: Name of the task to run

        Returns:
            bool: True if task completed successfully, False otherwise
        """
        try:
            # Import the task module
            module_name = f"automation.tasks.{task_name}"
            module = importlib.import_module(module_name)

            # Run the task
            log.info(f"Running task: {task_name}")
            module.run(self.context)
            log.success(f"Task completed: {task_name}")
            return True

        except ImportError as e:
            log.error(f"Failed to import task '{task_name}': {e}")
            return False
        except Exception as e:
            log.error(f"Error in task '{task_name}': {e}")
            return False

    def run_tasks(
        self, category: str, frequency: str, dry_run: bool = False
    ) -> dict[str, bool]:
        """Run all tasks for a category and frequency.

        Args:
            category: Task category name
            frequency: Task frequency (e.g., 'daily')
            dry_run: If True, tasks should not make any changes

        Returns:
            Dict mapping task names to success status
        """
        self.context.dry_run = dry_run
        task_names = self.get_tasks(category, frequency)

        if not task_names:
            log.warning(f"No tasks found for {category}/{frequency}")
            return {}

        if dry_run:
            log.info("DRY RUN: No changes will be made")

        results = {}
        for task_name in task_names:
            success = self.run_task(task_name)
            results[task_name] = success

        return results

    def run_all(self, dry_run: bool = False) -> dict[str, dict[str, dict[str, bool]]]:
        """Run all tasks for all categories and frequencies.

        Args:
            dry_run: If True, tasks should not make any changes

        Returns:
            Nested dict with results: {category: {frequency: {task: status}}}
        """
        self.context.dry_run = dry_run
        all_results: dict[str, dict[str, dict[str, bool]]] = {}

        for category in self.get_task_categories():
            all_results[category] = {}

            for frequency in self.get_task_frequencies(category):
                results = self.run_tasks(category, frequency, dry_run)
                all_results[category][frequency] = results

        return all_results
