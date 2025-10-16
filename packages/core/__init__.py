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
