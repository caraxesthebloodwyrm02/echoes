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

"""Automation Logger - Colored logging with SUCCESS level for automation framework."""

import logging
import sys

# Import privacy filter
try:
    from packages.security.privacy_filter import PrivacyFilter

    privacy_filter = PrivacyFilter()
except ImportError:
    # Fallback if privacy filter not available
    privacy_filter = None


class ColoredFormatter(logging.Formatter):
    """Colored log formatter with SUCCESS level support."""

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "SUCCESS": "\033[92m",  # Bright Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[91m",  # Bright Red
    }
    RESET = "\033[0m"

    def format(self, record):
        # Add SUCCESS level if not already defined
        if (
            not hasattr(record, "levelno") or record.levelno == 25
        ):  # Custom SUCCESS level
            record.levelno = 25
            record.levelname = "SUCCESS"

        # Apply color
        color = self.COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{self.RESET}"

        return super().format(record)


class AutomationLogger:
    """Colored logger for automation framework with SUCCESS level."""

    def __init__(self, name: str = "automation", level: int = logging.INFO):
        self.logger = logging.getLogger(name)

        # Prevent duplicate handlers
        if self.logger.handlers:
            return

        self.logger.setLevel(level)

        # Add SUCCESS level
        logging.addLevelName(25, "SUCCESS")

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Create formatter
        formatter = ColoredFormatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def _filter_message(self, message: str) -> str:
        """Apply privacy filtering to log messages if available."""
        if privacy_filter:
            return privacy_filter.mask(message)
        return message

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(self._filter_message(message))

    def info(self, message: str):
        """Log info message."""
        self.logger.info(self._filter_message(message))

    def success(self, message: str):
        """Log success message."""
        self.logger.log(25, self._filter_message(message))  # SUCCESS level

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(self._filter_message(message))

    def error(self, message: str):
        """Log error message."""
        self.logger.error(self._filter_message(message))

    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(self._filter_message(message))

    def set_level(self, level: int):
        """Set logging level."""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)


# Global instance for easy access
automation_logger = AutomationLogger()
