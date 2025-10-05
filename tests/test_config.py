"""
Tests for configuration modules.
"""

import json
import os
import pytest


class TestConfigFiles:
    """Tests for configuration file loading and validation."""

    def test_quality_config_loads(self):
        """Test that quality config loads as valid JSON."""
        config_path = "config/quality_config.json"
        assert os.path.exists(config_path), f"Config file {config_path} not found"

        with open(config_path, "r") as f:
            config = json.load(f)

        # Validate required fields
        required_fields = ["min_maintainability", "max_complexity", "min_pylint_score"]
        for field in required_fields:
            assert field in config, f"Required field {field} missing from quality config"

    def test_automation_config_loads(self):
        """Test that automation config loads as valid JSON."""
        config_path = "config/automation_config.json"
        assert os.path.exists(config_path), f"Config file {config_path} not found"

        with open(config_path, "r") as f:
            config = json.load(f)

        assert "framework" in config, "Framework section missing from automation config"

    def test_guardrails_config_loads(self):
        """Test that guardrails metrics config loads as valid JSON."""
        config_path = "config/guardrails_metrics.json"
        assert os.path.exists(config_path), f"Config file {config_path} not found"

        with open(config_path, "r") as f:
            config = json.load(f)

        assert "metrics" in config, "Metrics section missing from guardrails config"
        assert isinstance(config["metrics"], list), "Metrics should be a list"

    def test_pending_reviews_config_loads(self):
        """Test that pending reviews config loads as valid JSON."""
        config_path = "config/pending_reviews.json"
        assert os.path.exists(config_path), f"Config file {config_path} not found"

        with open(config_path, "r") as f:
            config = json.load(f)

        assert isinstance(config, list), "Pending reviews should be a list"


class TestConfigValidation:
    """Tests for configuration validation logic."""

    def test_config_paths_exist(self):
        """Test that all config files exist."""
        config_files = [
            "config/quality_config.json",
            "config/automation_config.json",
            "config/guardrails_metrics.json",
            "config/pending_reviews.json",
            "config/quality_config.json",
        ]

        for config_file in config_files:
            assert os.path.exists(config_file), f"Config file {config_file} not found"

    def test_memory_config_valid(self):
        """Test that memory.json is valid."""
        memory_path = "memory.json"
        assert os.path.exists(memory_path), "memory.json not found"

        with open(memory_path, "r") as f:
            memory = json.load(f)

        assert "entities" in memory, "Entities section missing from memory"
        assert "relations" in memory, "Relations section missing from memory"
