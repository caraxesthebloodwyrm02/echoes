"""Tests for the Orchestrator class."""

from typing import Any, Dict, List
from unittest.mock import patch

from automation.core.context import Context
from automation.core.orchestrator import Orchestrator


def test_orchestrator_initialization():
    """Test orchestrator initialization."""
    # Create orchestrator with a dummy config path
    orchestrator = Orchestrator("dummy_config.yaml")

    # Verify the orchestrator was initialized correctly
    assert isinstance(orchestrator.context, Context)
    assert orchestrator._tasks == {}
    assert orchestrator.config is not None
    assert orchestrator.context.dry_run is False


@patch("automation.core.orchestrator.Orchestrator.run_task")
@patch("automation.core.orchestrator.Orchestrator.get_tasks")
def test_run_tasks(mock_get_tasks, mock_run_task, caplog):
    """Test running tasks."""
    # Setup test tasks
    task_list = ["test_task1", "test_task2"]

    # Mock get_tasks to return our test tasks
    mock_get_tasks.return_value = task_list

    # Mock run_task to return True for all tasks
    mock_run_task.side_effect = lambda x: True

    # Create orchestrator with a dummy config path
    orchestrator = Orchestrator("dummy_config.yaml")

    # Run the tasks
    results = orchestrator.run_tasks("security", "daily")

    # Verify the results
    assert results == {"test_task1": True, "test_task2": True}

    # Verify run_task was called for each task
    assert mock_run_task.call_count == 2
    assert mock_run_task.call_args_list[0][0][0] == "test_task1"
    assert mock_run_task.call_args_list[1][0][0] == "test_task2"

    # Verify get_tasks was called with the correct arguments
    mock_get_tasks.assert_called_once_with("security", "daily")
    assert mock_run_task.call_args_list[1][0][0] == "test_task2"


def test_get_task_categories():
    """Test getting task categories."""
    # Create orchestrator with a dummy config path
    orchestrator = Orchestrator("dummy_config.yaml")

    # Manually set the _tasks dictionary
    test_tasks: Dict[str, Dict[str, Any]] = {
        "security": {},
        "cleanup": {},
        "maintenance": {},
    }
    orchestrator._tasks = test_tasks

    # Test getting categories
    categories = orchestrator.get_task_categories()

    # Verify the results
    assert set(categories) == {"security", "cleanup", "maintenance"}


def test_get_task_frequencies():
    """Test getting task frequencies for a category."""
    # Create orchestrator with a dummy config path
    orchestrator = Orchestrator("dummy_config.yaml")

    # Manually set the _tasks dictionary
    test_tasks: Dict[str, Dict[str, List[str]]] = {
        "security": {"daily": [], "weekly": [], "monthly": []}
    }
    orchestrator._tasks = test_tasks

    # Test getting frequencies
    frequencies = orchestrator.get_task_frequencies("security")

    # Verify the results
    assert set(frequencies) == {"daily", "weekly", "monthly"}


def test_get_tasks():
    """Test getting tasks for a category and frequency."""
    # Create orchestrator with a dummy config path
    orchestrator = Orchestrator("dummy_config.yaml")

    # Manually set the _tasks dictionary
    test_tasks: Dict[str, Dict[str, List[str]]] = {
        "security": {"daily": ["task1", "task2"], "weekly": ["task3"]}
    }
    orchestrator._tasks = test_tasks

    # Test daily tasks
    daily_tasks = orchestrator.get_tasks("security", "daily")
    assert daily_tasks == ["task1", "task2"]

    # Test weekly tasks
    weekly_tasks = orchestrator.get_tasks("security", "weekly")
    assert weekly_tasks == ["task3"]


@patch("importlib.import_module")
def test_run_task_error_handling(mock_import, caplog):
    """Test error handling in run_task."""
    # Create an instance of Orchestrator with a dummy config path
    orchestrator = Orchestrator("dummy_config.yaml")

    # Mock import to raise an exception
    mock_import.side_effect = ImportError("Test import error")

    # Run the task that will fail to import
    result = orchestrator.run_task("nonexistent_task")

    # Verify the result is False and the error was logged
    assert result is False
    assert "Failed to import task 'nonexistent_task'" in caplog.text

    # The actual error message is included in the log
    assert "Test import error" in caplog.text

    # Verify import_module was called with the correct module path
    mock_import.assert_called_once_with("automation.tasks.nonexistent_task")
