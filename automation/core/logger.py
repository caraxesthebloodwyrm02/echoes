"""Logging for the automation framework."""

import logging
import sys

# Add SUCCESS level (between WARNING and INFO)
SUCCESS_LEVEL_NUM = 25
logging.addLevelName(SUCCESS_LEVEL_NUM, "SUCCESS")


def _success(self, message: str, *args, **kwargs) -> None:
    if self.isEnabledFor(SUCCESS_LEVEL_NUM):
        self._log(SUCCESS_LEVEL_NUM, message, args, **kwargs)


# Add success method to Logger class
# flake8: noqa: B010
setattr(logging.Logger, "success", _success)


class ColorFormatter(logging.Formatter):
    """Custom formatter for colored console output."""

    # ANSI color codes
    GREY = "\x1b[38;21m"
    BLUE = "\x1b[38;5;39m"
    YELLOW = "\x1b[38;5;226m"
    RED = "\x1b[38;5;196m"
    BOLD_RED = "\x1b[31;1m"
    GREEN = "\x1b[38;5;40m"
    RESET = "\x1b[0m"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._colors = {
            logging.DEBUG: self.GREY,
            logging.INFO: self.BLUE,
            logging.WARNING: self.YELLOW,
            logging.ERROR: self.RED,
            logging.CRITICAL: self.BOLD_RED,
            SUCCESS_LEVEL_NUM: self.GREEN,
        }

    def format(self, record):
        """Format the specified record with colors."""
        log_fmt = self._get_format(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

    def _get_format(self, level: int) -> str:
        """Get the format string for the given log level.

        Args:
            level: Logging level (e.g., logging.INFO, logging.ERROR)

        Returns:
            str: Formatted log string with color codes for known levels,
                 plain text for unknown levels
        """
        if level in self._colors:
            color = self._colors[level]
            return f"{color}%(asctime)s - %(name)s - %(levelname)s - " f"%(message)s{self.RESET}"
        # Return plain format for unknown levels
        return "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class AutomationLogger:
    """Logger for automation framework."""

    _instance = None

    def __new__(cls, name: str = "automation"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup_logger(name)
        return cls._instance

    def _setup_logger(self, name: str) -> None:
        """Set up the logger with handlers and formatters."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Prevent adding multiple handlers
        if not self.logger.handlers:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(ColorFormatter())
            self.logger.addHandler(console_handler)

    def debug(self, message: str) -> None:
        """Log a debug message."""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log an info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str) -> None:
        """Log an error message."""
        self.logger.error(message)

    def critical(self, message: str) -> None:
        """Log a critical message."""
        self.logger.critical(message)

    def success(self, message: str) -> None:
        """Log a success message."""
        self.logger.log(SUCCESS_LEVEL_NUM, message)


# Create a default logger instance
log = AutomationLogger()
