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
Hardened Configuration Loader

Centralizes configuration loading, validation, and management.
Provides a single entry point for all configuration needs.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from src.core.validators import ValidationReport, validate_config

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Custom exception for configuration errors."""

    pass


class ConfigLoader:
    """Centralized configuration management."""

    def __init__(self):
        self.config: Dict[str, Any] = {}
        self._loaded = False
        self._validation_report: Optional[ValidationReport] = None

        # Known configuration files to check
        self._config_files = [
            Path(".env"),
            Path("minicon/.env"),
            Path(".env.unified"),
        ]

        # Required environment keys
        self._required_keys = {
            "OPENAI_API_KEY": "OpenAI API key for AI operations",
            "GITHUB_TOKEN": "GitHub token for repository operations",
        }

        # Optional keys with defaults
        self._optional_keys = {
            "LOG_LEVEL": "INFO",
            "MAX_TOKENS": "1000",
            "TEMPERATURE": "0.7",
            "DATABASE_URL": None,
            "OLLAMA_BASE_URL": "http://localhost:11434",
            "DEBUG": "false",
        }

    def load_config(self, validate: bool = True) -> Dict[str, Any]:
        """Load and validate configuration from all sources.

        Args:
            validate: Whether to validate configuration after loading

        Returns:
            Complete configuration dictionary

        Raises:
            ConfigurationError: If required keys are missing or validation fails
        """
        if self._loaded and not validate:
            return self.config.copy()

        logger.info("Loading configuration from environment and .env files...")

        # Load .env files
        for config_file in self._config_files:
            if config_file.exists():
                logger.debug(f"Loading config from {config_file}")
                load_dotenv(config_file)

        # Build configuration from environment
        self._build_config_from_env()

        # Validate if requested
        if validate:
            self._validation_report = validate_config(self.config)
            if not self._validation_report.is_valid():
                error_msg = "Configuration validation failed:\n"
                for error in self._validation_report.errors:
                    error_msg += f"  - {error}\n"

                logger.error(error_msg)
                raise ConfigurationError(error_msg)

            logger.info("Configuration validation passed")

        self._loaded = True
        logger.info(f"Configuration loaded for {len(self.config)} keys")

        return self.config.copy()

    def _build_config_from_env(self):
        """Build configuration dictionary from environment variables."""
        self.config = {}

        # Load required keys
        for key, description in self._required_keys.items():
            value = os.getenv(key)
            if not value:
                logger.warning(f"Missing required environment variable: {key} ({description})")
                # Don't fail here - let validation handle it
            self.config[key.lower()] = value

        # Load optional keys with defaults
        for key, default in self._optional_keys.items():
            value = os.getenv(key, default)
            # Convert string booleans
            if value and value.lower() in ("true", "false"):
                value = value.lower() == "true"
            # Convert string numbers
            elif value and value.isdigit():
                value = int(value)

            self.config[key.lower()] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        if not self._loaded:
            self.load_config()

        return self.config.get(key.lower(), default)

    def require(self, key: str) -> Any:
        """Get required configuration value.

        Raises:
            ConfigurationError: If key is missing
        """
        value = self.get(key)
        if value is None:
            raise ConfigurationError(f"Required configuration key missing: {key}")
        return value

    def get_validation_report(self) -> Optional[ValidationReport]:
        """Get the last validation report."""
        return self._validation_report

    def reload_config(self):
        """Force reload of configuration."""
        self._loaded = False
        self._validation_report = None
        return self.load_config()

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of configuration status."""
        if not self._loaded:
            self.load_config(validate=False)

        summary = {
            "total_keys": len(self.config),
            "required_keys": len(self._required_keys),
            "optional_keys": len(self._optional_keys),
            "loaded": self._loaded,
        }

        if self._validation_report:
            summary.update(
                {
                    "validation_passed": self._validation_report.is_valid(),
                    "errors": len(self._validation_report.errors),
                    "warnings": len(self._validation_report.warnings),
                }
            )

        return summary


# Global configuration instance
_config_loader = None


def load_config(validate: bool = True) -> Dict[str, Any]:
    """Global configuration loader function.

    This is the single entry point for configuration across the codebase.
    All other modules should use this instead of loading .env directly.

    Args:
        validate: Whether to validate configuration

    Returns:
        Complete configuration dictionary
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()

    return _config_loader.load_config(validate=validate)


def get_config(key: str, default: Any = None) -> Any:
    """Get a configuration value."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()

    return _config_loader.get(key, default)


def require_config(key: str) -> Any:
    """Get a required configuration value."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()

    return _config_loader.require(key)


def get_config_summary() -> Dict[str, Any]:
    """Get configuration summary."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()

    return _config_loader.get_config_summary()


# Backward compatibility - deprecation warnings
def load_env_var_from_files(var_name: str) -> None:
    """DEPRECATED: Use load_config() instead."""
    import warnings

    warnings.warn(
        "load_env_var_from_files() is deprecated. Use load_config() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    # Load minimal config for backward compatibility
    load_dotenv()
    if not os.getenv(var_name):
        for config_file in [Path(".env"), Path("minicon/.env")]:
            if config_file.exists():
                try:
                    lines = config_file.read_text(encoding="utf-8").splitlines()
                    for line in lines:
                        stripped = line.strip()
                        if not stripped or stripped.startswith("#"):
                            continue
                        key, sep, value = stripped.partition("=")
                        if sep and key.strip() == var_name:
                            os.environ[var_name] = value.strip()
                            return
                except:
                    continue


def ensure_required_env_vars() -> None:
    """DEPRECATED: Use load_config() instead."""
    import warnings

    warnings.warn(
        "ensure_required_env_vars() is deprecated. Use load_config() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    required = [
        "OPENAI_API_KEY",
        "OLLAMA_API_KEY",
    ]

    for var in required:
        if not os.getenv(var):
            logger.warning(f"Required environment variable missing: {var}")
