import os
import sys
from pathlib import Path

import pytest

from automation.core.config import Config
from automation.core.context import Context
from automation.core.logger import AutomationLogger
from automation.core.orchestrator import Orchestrator


def test_context_default():
    ctx = Context()
    assert ctx.dry_run is False
    # Check that env is set to a non-empty string
    assert isinstance(ctx.env, str)
    assert len(ctx.env) > 0
    # Check that user is set to a non-empty string
    assert ctx.user is not None


def test_logger_levels(caplog):
    logger = AutomationLogger("test")

    # Clear any existing log records
    caplog.clear()

    # Log messages at different levels
    logger.info("info message")
    logger.error("error message")
    logger.warning("warning message")
    logger.debug("debug message")

    # Check that log messages were captured
    assert any(
        record.levelname == "INFO" and "info message" in record.message
        for record in caplog.records
    )
    assert any(
        record.levelname == "ERROR" and "error message" in record.message
        for record in caplog.records
    )
    assert any(
        record.levelname == "WARNING" and "warning message" in record.message
        for record in caplog.records
    )


def test_config_loader(tmp_path):
    yaml = """
framework:
  version: 1.0.0
  tasks:
    security:
      daily: []
    cleanup:
      monthly: []
    """
    config_file = tmp_path / "test.yaml"
    config_file.write_text(yaml)
    config = Config(str(config_file))
    assert config.get("framework.version") == "1.0.0"


def test_orchestrator_runs(monkeypatch, tmp_path):
    from unittest.mock import MagicMock

    # Create minimal config
    yaml = """
framework:
  version: 1.0.0
  tasks:
    cleanup:
      monthly: ["dummy_task"]
    """
    config_file = tmp_path / "test.yaml"
    config_file.write_text(yaml)

    # Create a mock task module
    mock_task = MagicMock()
    mock_task.run = MagicMock()

    # Mock the import_module function to return our mock task
    def mock_import(module_name):
        if module_name == "automation.tasks.dummy_task":
            return mock_task
        raise ImportError(f"No module named '{module_name}'")

    monkeypatch.setattr("importlib.import_module", mock_import)

    # Create and run the orchestrator
    orch = Orchestrator(str(config_file))
    orch.context.dry_run = True  # Enable dry run to prevent actual execution

    # Run the tasks
    results = orch.run_tasks("cleanup", "monthly")
    assert "dummy_task" in results
    assert results["dummy_task"] is True

    # Verify the task was called
    mock_task.run.assert_called_once_with(orch.context)
