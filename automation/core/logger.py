"""Automation Logger - Colored logging with SUCCESS level for automation framework."""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Colored log formatter with SUCCESS level support."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'SUCCESS': '\033[92m',   # Bright Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[91m',  # Bright Red
    }
    RESET = '\033[0m'

    def format(self, record):
        # Add SUCCESS level if not already defined
        if not hasattr(record, 'levelno') or record.levelno == 25:  # Custom SUCCESS level
            record.levelno = 25
            record.levelname = 'SUCCESS'

        # Apply color
        color = self.COLORS.get(record.levelname, '')
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
        logging.addLevelName(25, 'SUCCESS')

        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)

        # Create formatter
        formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)

    def success(self, message: str):
        """Log success message."""
        self.logger.log(25, message)  # SUCCESS level

    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)

    def critical(self, message: str):
        """Log critical message."""
        self.logger.critical(message)

    def set_level(self, level: int):
        """Set logging level."""
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)


# Global instance for easy access
automation_logger = AutomationLogger()
