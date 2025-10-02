import sys
from automation.core.logger import log
from automation.core.config import ConfigLoader
from automation.core.context import Context
import importlib

class Orchestrator:
    def __init__(self, config_path: str, dry_run: bool = False):
        self.config = ConfigLoader(config_path).config
        self.dry_run = dry_run
        self.context = Context(dry_run=dry_run)

    def run_tasks(self, task_type: str, frequency: str):
        tasks = self.config['framework']['tasks'].get(task_type, {}).get(frequency, [])
        if not tasks:
            log.warning(f"No tasks configured for {task_type} ({frequency})")
            return
        for task_name in tasks:
            try:
                mod = importlib.import_module(f'automation.tasks.{task_name}')
                log.info(f"Running task: {task_name}")
                mod.run(self.context)
                log.success(f"Task {task_name} completed")
            except Exception as e:
                log.error(f"Task {task_name} failed: {e}")

    def run(self, task_type: str, frequency: str):
        log.info(f"Starting automation: {task_type} ({frequency})")
        self.run_tasks(task_type, frequency)
        log.info("Automation complete.")
