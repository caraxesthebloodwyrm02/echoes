"""Logging configuration for Echoes."""

import logging
import sys
from typing import Optional

__all__ = ["get_logger", "logger"]


def get_logger(
    name: str = None, log_level: int = logging.INFO
) -> logging.Logger:
    """
    Get a configured logger instance.

    Args:
        name: Name of the logger. If None, returns the root logger.
        log_level: Logging level (e.g., logging.INFO, logging.DEBUG)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Prevent adding handlers multiple times
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(handler)

    return logger


# Default logger instance
logger = get_logger(__name__)
