"""Tests for the Config class."""

import os
import pytest
from pathlib import Path
from contextlib import contextmanager
from typing import Iterator, Optional

from automation.core.config import Config


@contextmanager
def config_file(content: str, *, suffix: str = ".yaml") -> Iterator[Path]:
    """Create a temporary config file with the given content.

    Args:
        content: The content to write to the file
        suffix: The file extension (default: .yaml)

    Yields:
        Path to the temporary file
    """
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        yield temp_path
    finally:
        try:
            if temp_path.exists():
                temp_path.unlink()
        except Exception as e:
            import logging

            logging.warning(f"Failed to cleanup test file {temp_path}: {e}")


def test_config_loading():
    """Test loading configuration from a YAML file."""
    config_content = """
    framework:
      version: 1.0.0
      tasks:
        security:
          daily: ["task1", "task2"]
    """

    with config_file(config_content) as config_path:
        config = Config(str(config_path))
        assert config.get("framework.version") == "1.0.0"
        assert config.get("framework.tasks.security.daily") == ["task1", "task2"]

        # Test get_section
        tasks = config.get_section("framework.tasks")
        assert tasks == {"security": {"daily": ["task1", "task2"]}}
        assert config["framework.version"] == "1.0.0"

        # Test __contains__
        assert "framework" in config
        assert "framework.version" in config
        assert "framework.tasks" in config
        assert "nonexistent.key" not in config


def test_config_missing_file():
    """Test behavior when config file is missing."""
    config = Config("nonexistent_file.yaml")
    assert config.to_dict() == {}


def test_config_invalid_yaml():
    """Test behavior with invalid YAML content."""
    invalid_yaml = """
    framework:
      version: 1.0.0
      tasks:
        - item1
        - item2: value
          - nested: value
    """

    with config_file(invalid_yaml) as config_path:
        # Should not raise an exception, but return an empty config
        config = Config(str(config_path))
        assert config.to_dict() == {}


def test_config_empty_file():
    """Test behavior with an empty config file."""
    with config_file("") as config_path:
        config = Config(str(config_path))
        assert config.to_dict() == {}
        assert config.get("any.key") is None
        assert config.get("any.key", "default") == "default"


def test_config_reload():
    """Test reloading configuration from file."""
    initial_content = """
    framework:
      version: 1.0.0
    """

    with config_file(initial_content) as config_path:
        # Test initial load
        config = Config(str(config_path))
        assert config.get("framework.version") == "1.0.0"

        # Update with empty content
        with open(config_path, "w") as f:
            f.write("")

        # Reload and verify empty config
        config.reload()
        assert config.to_dict() == {}

        # Update with new version
        new_content = """
        framework:
          version: 2.0.0
        """
        with open(config_path, "w") as f:
            f.write(new_content)

        # Reload and verify new version
        config.reload()
        assert config.get("framework.version") == "2.0.0"

        # Test with invalid YAML
        with open(config_path, "w") as f:
            f.write(
                """
            invalid: yaml:
              - item1
              - item2: value
                - nested: value
            """
            )

        # Reload and verify empty config for invalid YAML
        config.reload()
        assert config.to_dict() == {}
