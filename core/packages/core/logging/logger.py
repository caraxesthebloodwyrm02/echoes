# core/packages/core/logging/logger.py
"""Simple logger implementation used by core/test_logging.py

Provides setup_logger() which returns a configured logging.Logger.
"""
from __future__ import annotations

import logging
import sys
from typing import Optional

def setup_logger(name: str = "echoes", level: int = logging.INFO) -> logging.Logger:
    """Create and return a logger configured to write to stdout.

    The function is idempotent: repeated calls will not add duplicate handlers.
    """
    logger = logging.getLogger(name)

    # If we've already configured this logger via this helper, return it
    if getattr(logger, "_configured_by_echoes", False):
        return logger

    logger.setLevel(level)

    # Only add a StreamHandler if one isn't already present
    if not any(isinstance(h, logging.StreamHandler) for h in logger.handlers):
        handler = logging.StreamHandler(stream=sys.stdout)
        formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Prevent double propagation to the root logger
    logger.propagate = False
    logger._configured_by_echoes = True
    return logger
