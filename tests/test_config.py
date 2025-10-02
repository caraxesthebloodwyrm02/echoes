"""Tests for the Config class."""

import os
import tempfile
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from automation.core.config import Config


def test_config_loading():
    """Test loading configuration from a YAML file."""
    # Create a temporary config file
    config_content = """
    framework:
      version: 1.0.0
      tasks:
        security:
          daily: ["task1", "task2"]
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        temp_path = f.name

    try:
        config = Config(temp_path)
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
        assert "nonexistent.key" not in config  # Check using the __contains__ method

        # Test to_dict
        config_dict = config.to_dict()
        assert "framework" in config_dict
        assert "version" in config_dict["framework"]
        assert "tasks" in config_dict["framework"]
        assert config_dict["framework"]["version"] == "1.0.0"

    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


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

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(invalid_yaml)
        temp_path = f.name

    try:
        # Should not raise an exception, but return an empty config
        config = Config(temp_path)
        assert config.to_dict() == {}
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_config_empty_file():
    """Test behavior with an empty config file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write("")
        temp_path = f.name

    try:
        config = Config(temp_path)
        assert config.to_dict() == {}
        assert config.get("any.key") is None
        assert config.get("any.key", "default") == "default"
    finally:
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def test_config_reload():
    """Test reloading configuration from file."""
    # Initial config
    config_content = """
    framework:
      version: 1.0.0
    """

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(config_content)
        temp_path = f.name

    try:
        # Test initial load
        config = Config(temp_path)
        assert config.get("framework.version") == "1.0.0"

        # Update the config file
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(
                """
            framework:
              version: 2.0.0
            """
            )

        # Reload and verify
        config.reload()
        assert config.get("framework.version") == "2.0.0"

        # Test with invalid YAML - should not raise an exception
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(
                """
            invalid: yaml:
              - item1
              - item2: value
                - nested: value
            """
            )

        config.reload()
        assert config.to_dict() == {}

    finally:
        # Clean up the temporary file
        if os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except Exception as e:
                print(f"Error cleaning up temporary file {temp_path}: {e}")
