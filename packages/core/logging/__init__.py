"""Unified logging configuration."""

import logging
import sys
from pathlib import Path
from typing import Optional

from rich.logging import RichHandler


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with workspace config."""
    return logging.getLogger(f"echoe.{name}")


def configure_logging(level: str = "INFO", log_file: Optional[Path] = None, rich_output: bool = True) -> None:
    """
    Configure logging for the workspace.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for log output
        rich_output: Use Rich library for pretty terminal output
    """
    handlers = []

    # Console handler
    if rich_output:
        handlers.append(RichHandler(rich_tracebacks=True))
    else:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        handlers.append(console_handler)

    # File handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        handlers.append(file_handler)

    # Configure root logger
    logging.basicConfig(level=getattr(logging, level.upper()), handlers=handlers, force=True)


__all__ = ["get_logger", "configure_logging"]
