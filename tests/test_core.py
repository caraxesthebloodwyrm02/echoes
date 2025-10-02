import os
import pytest
from automation.core.context import Context
from automation.core.logger import AutomationLogger
from automation.core.config import ConfigLoader
from automation.core.orchestrator import Orchestrator


def test_context_default():
    ctx = Context()
    assert ctx.dry_run is False
    assert ctx.env in ("development", os.getenv('ENVIRONMENT'))
    assert ctx.user

def test_logger_levels(capfd):
    logger = AutomationLogger("test")
    logger.info("info")
    logger.error("error")
    logger.warning("warn")
    logger.debug("debug")
    out, _ = capfd.readouterr()
    assert "info" in out and "error" in out and "warn" in out

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
    loader = ConfigLoader(str(config_file))
    assert loader.get('framework')['version'] == '1.0.0'


def test_orchestrator_runs(monkeypatch, tmp_path):
    # Create minimal config
    yaml = """
framework:
  version: 1.0.0
  tasks:
    cleanup:
      monthly: ["_dummy_task"]
    """
    config_file = tmp_path / "test.yaml"
    config_file.write_text(yaml)
    # Dummy task
    dummy_dir = tmp_path / "automation" / "tasks"
    dummy_dir.mkdir(parents=True, exist_ok=True)
    dummy_task = dummy_dir / "_dummy_task.py"
    dummy_task.write_text("def run(context): print('dummy ran')\n")
    monkeypatch.syspath_prepend(str(tmp_path))
    orch = Orchestrator(str(config_file), dry_run=True)
    orch.run("cleanup", "monthly")
