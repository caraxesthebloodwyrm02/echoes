"""
echoe-core: Shared utilities for echoe-workspace.

Provides common functionality used across all applications:
- Logging configuration and utilities
- Configuration management
- Custom exceptions
- General utilities (file ops, date/time, etc.)
- HTTP request helpers
"""

__version__ = "0.1.0"

from .logging import get_logger, configure_logging
from .config import load_config, Config
from .exceptions import (
    EchoeBaseException,
    ConfigurationError,
    ValidationError,
)

__all__ = [
    "get_logger",
    "configure_logging",
    "load_config",
    "Config",
    "EchoeBaseException",
    "ConfigurationError",
    "ValidationError",
]
