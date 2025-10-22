#!/usr/bin/env python3
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
Tests for configuration loader functionality.

Comprehensive test suite for src/config/loader.py
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config.loader import (
    ConfigLoader,
    ConfigurationError,
    get_config,
    get_config_summary,
    load_config,
    require_config,
)


class TestConfigLoader:
    """Test ConfigLoader class."""

    def test_empty_config_loader(self):
        """Test empty config loader initialization."""
        loader = ConfigLoader()
        assert len(loader.config) == 0
        assert not loader._loaded

    def test_config_loading_without_validation(self):
        """Test loading config without validation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            loader = ConfigLoader()
            config = loader.load_config(validate=False)

            assert "openai_api_key" in config
            assert config["openai_api_key"] == "test-key"
            assert loader._loaded is True

    def test_config_loading_with_validation(self):
        """Test loading config with validation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "LOG_LEVEL": "DEBUG"}):
            loader = ConfigLoader()
            config = loader.load_config(validate=True)

            assert "openai_api_key" in config
            assert "log_level" in config
            assert config["log_level"] == "DEBUG"

    def test_missing_required_keys(self):
        """Test handling of missing required keys."""
        with patch.dict(os.environ, {}, clear=True):
            loader = ConfigLoader()

            with pytest.raises(ConfigurationError):
                loader.load_config(validate=True)

    def test_optional_keys_with_defaults(self):
        """Test optional keys with defaults."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            loader = ConfigLoader()
            config = loader.load_config(validate=False)

            assert config["log_level"] == "INFO"
            assert config["max_tokens"] == "1000"
            assert config["temperature"] == "0.7"
            assert config["database_url"] is None

    def test_config_get_methods(self):
        """Test config getter methods."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            loader = ConfigLoader()
            loader.load_config(validate=False)

            # Test get method
            assert loader.get("openai_api_key") == "test-key"
            assert loader.get("nonexistent", "default") == "default"

            # Test require method
            assert loader.require("openai_api_key") == "test-key"

            # Test require with missing key
            with pytest.raises(ConfigurationError):
                loader.require("nonexistent_key")

    def test_config_reload(self):
        """Test config reload functionality."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            loader = ConfigLoader()

            # Load initial config
            config1 = loader.load_config(validate=False)
            assert config1["openai_api_key"] == "test-key"

            # Change environment and reload
            with patch.dict(os.environ, {"OPENAI_API_KEY": "new-key"}):
                config2 = loader.reload_config()
                assert config2["openai_api_key"] == "new-key"

    def test_config_summary(self):
        """Test config summary generation."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            loader = ConfigLoader()
            summary = loader.get_config_summary()

            assert summary["total_keys"] > 0
            assert summary["required_keys"] == 2  # OPENAI_API_KEY and GITHUB_TOKEN
            assert summary["optional_keys"] == 7
            assert not summary["loaded"]


class TestGlobalConfigFunctions:
    """Test global configuration functions."""

    def test_global_load_config(self):
        """Test global load_config function."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            config = load_config(validate=False)
            assert "openai_api_key" in config
            assert config["openai_api_key"] == "test-key"

    def test_global_get_config(self):
        """Test global get_config function."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            load_config(validate=False)  # Initialize global loader
            assert get_config("openai_api_key") == "test-key"
            assert get_config("nonexistent", "default") == "default"

    def test_global_require_config(self):
        """Test global require_config function."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            load_config(validate=False)  # Initialize global loader
            assert require_config("openai_api_key") == "test-key"

            with pytest.raises(ConfigurationError):
                require_config("nonexistent_key")

    def test_global_config_summary(self):
        """Test global config summary function."""
        summary = get_config_summary()
        assert isinstance(summary, dict)
        assert "total_keys" in summary


class TestEnvFileLoading:
    """Test .env file loading functionality."""

    def test_env_file_loading(self):
        """Test loading from .env files."""
        # Create temporary .env file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("OPENAI_API_KEY=test-key-from-file\n")
            f.write("LOG_LEVEL=DEBUG\n")
            temp_env = f.name

        try:
            # Mock the config files list to include our temp file
            with patch.object(ConfigLoader, "_config_files", [Path(temp_env)]):
                with patch.dict(os.environ, {}, clear=True):
                    loader = ConfigLoader()
                    config = loader.load_config(validate=False)

                    assert config["openai_api_key"] == "test-key-from-file"
                    assert config["log_level"] == "DEBUG"

        finally:
            Path(temp_env).unlink()

    def test_multiple_env_files(self):
        """Test loading from multiple .env files."""
        # Create two .env files with different keys
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f1:
            f1.write("OPENAI_API_KEY=key-from-file1\n")
            temp_env1 = f1.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f2:
            f2.write("GITHUB_TOKEN=token-from-file2\n")
            temp_env2 = f2.name

        try:
            with patch.object(ConfigLoader, "_config_files", [Path(temp_env1), Path(temp_env2)]):
                with patch.dict(os.environ, {}, clear=True):
                    loader = ConfigLoader()
                    config = loader.load_config(validate=False)

                    # Should load from both files (later files override earlier)
                    assert config["openai_api_key"] == "key-from-file1"
                    assert config["github_token"] == "token-from-file2"

        finally:
            Path(temp_env1).unlink()
            Path(temp_env2).unlink()

    def test_env_file_precedence(self):
        """Test .env file precedence over environment."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("OPENAI_API_KEY=file-key\n")
            temp_env = f.name

        try:
            # Set environment variable
            original_env = os.environ.get("OPENAI_API_KEY")
            os.environ["OPENAI_API_KEY"] = "env-key"

            with patch.object(ConfigLoader, "_config_files", [Path(temp_env)]):
                loader = ConfigLoader()
                config = loader.load_config(validate=False)

                # Environment should take precedence
                assert config["openai_api_key"] == "env-key"

            # Restore original environment
            if original_env is None:
                os.environ.pop("OPENAI_API_KEY", None)
            else:
                os.environ["OPENAI_API_KEY"] = original_env

        finally:
            Path(temp_env).unlink()


class TestTypeConversion:
    """Test type conversion in configuration."""

    def test_boolean_conversion(self):
        """Test boolean value conversion."""
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "test-key", "DEBUG": "true", "TEMPERATURE": "false"},
        ):
            loader = ConfigLoader()
            config = loader.load_config(validate=False)

            assert config["debug"] is True
            assert config["temperature"] is False

    def test_numeric_conversion(self):
        """Test numeric value conversion."""
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "test-key", "MAX_TOKENS": "1500", "TEMPERATURE": "0.8"},
        ):
            loader = ConfigLoader()
            config = loader.load_config(validate=False)

            assert config["max_tokens"] == 1500
            assert config["temperature"] == 0.8


class TestErrorHandling:
    """Test error handling in configuration loading."""

    def test_invalid_log_level(self):
        """Test invalid log level handling."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "LOG_LEVEL": "INVALID_LEVEL"}):
            loader = ConfigLoader()

            with pytest.raises(ConfigurationError):
                loader.load_config(validate=True)

    def test_invalid_temperature(self):
        """Test invalid temperature handling."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key", "TEMPERATURE": "2.5"}):  # Out of range
            loader = ConfigLoader()

            with pytest.raises(ConfigurationError):
                loader.load_config(validate=True)

    def test_malformed_env_file(self):
        """Test handling of malformed .env files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
            f.write("INVALID_LINE_FORMAT\n")  # Missing =
            f.write("OPENAI_API_KEY=test-key\n")
            temp_env = f.name

        try:
            with patch.object(ConfigLoader, "_config_files", [Path(temp_env)]):
                loader = ConfigLoader()
                # Should not crash, just skip invalid lines
                config = loader.load_config(validate=False)
                assert config["openai_api_key"] == "test-key"

        finally:
            Path(temp_env).unlink()


class TestBackwardCompatibility:
    """Test backward compatibility functions."""

    def test_deprecated_functions_warning(self):
        """Test that deprecated functions issue warnings."""
        with patch("src.config.loader.logger") as mock_logger:
            from src.config.loader import load_env_var_from_files

            with patch.dict(os.environ, {}, clear=True):
                load_env_var_from_files("OPENAI_API_KEY")

            # Should have been called with warning
            mock_logger.warning.assert_called()

    def test_ensure_required_env_vars_deprecation(self):
        """Test deprecated ensure_required_env_vars function."""
        with patch("src.config.loader.logger") as mock_logger:
            from src.config.loader import ensure_required_env_vars

            ensure_required_env_vars()

            # Should have been called with warning
            mock_logger.warning.assert_called()


class TestIntegrationScenarios:
    """Test integration scenarios."""

    def test_full_config_lifecycle(self):
        """Test complete config lifecycle."""
        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": "test-key", "LOG_LEVEL": "DEBUG", "MAX_TOKENS": "2000"},
        ):
            # Load config
            load_config(validate=True)

            # Use global getters
            assert get_config("openai_api_key") == "test-key"
            assert get_config("log_level") == "DEBUG"
            assert get_config("max_tokens") == 2000

            # Test required config
            assert require_config("openai_api_key") == "test-key"

            # Test summary
            summary = get_config_summary()
            assert summary["loaded"] is True
            assert summary["validation_passed"] is True

    def test_config_with_missing_required(self):
        """Test config loading with missing required keys."""
        with patch.dict(os.environ, {}, clear=True):
            loader = ConfigLoader()

            with pytest.raises(ConfigurationError):
                loader.load_config(validate=True)

            # Should still work without validation
            config = loader.load_config(validate=False)
            assert config["openai_api_key"] is None
