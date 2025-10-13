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

from .config import Config, load_config
from .exceptions import ConfigurationError, EchoeBaseException, ValidationError
from .logging import configure_logging, get_logger
from .schemas import CacheEntry, PodcastData, PodcastEvent, PromptTemplate

__all__ = [
    "get_logger",
    "configure_logging",
    "load_config",
    "Config",
    "EchoeBaseException",
    "ConfigurationError",
    "ValidationError",
    "PodcastEvent",
    "PodcastData",
    "PromptTemplate",
    "CacheEntry",
]
