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
Task execution system with phase-based orchestration and isolated error handling.
"""

import logging
from pathlib import Path
from typing import Any, Dict

# Set up logging with file handlers
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add file handlers
execution_handler = logging.FileHandler(log_dir / "execution.log")
error_handler = logging.FileHandler(log_dir / "error.log")
mock_handler = logging.FileHandler(log_dir / "mock.log")

# Set formats
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
execution_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)
mock_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(execution_handler)
logger.addHandler(error_handler)
logger.addHandler(mock_handler)


class TaskExecutor:
    """Manages phase-based task execution with error isolation."""

    def __init__(self):
        self.current_phase = None

    def execute_phase(self, phase: Dict[str, Any]) -> bool:
        """
        Execute all tasks in a given phase with error isolation.

        Args:
            phase: Dictionary containing phase information and tasks

        Returns:
            bool: True if phase completed successfully, False otherwise
        """
        self.current_phase = phase
        logger.info(f"🚀 Starting phase: {phase['name']}")

        success = True
        for task in phase.get("tasks", []):
            try:
                self._run_task(task)
            except Exception as e:
                success = False
                logger.error(f"Task {task['id']} failed: {str(e)}")
                continue

        status = "✅" if success else "⚠️"
        logger.info(f"{status} Phase {phase['phase']} completed")
        return success

    def _run_task(self, task: Dict[str, Any]):
        """
        Execute a single task with logging.

        Args:
            task: Dictionary containing task details
        """
        task_id = task.get("id", "unknown")
        logger.info(f"Starting task {task_id}: {task.get('instruction', '')}")

        # Execute commands
        for cmd in task.get("commands", []):
            if isinstance(cmd, str):
                logger.info(f"Executing command: {cmd}")
                # Command execution logic here

        logger.info(f"Task {task_id} completed")
