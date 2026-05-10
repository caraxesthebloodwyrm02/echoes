"""
Structured Logging Configuration for Echoes.

Provides production-grade structured logging using structlog,
configured for JSON output in production and colored console in development.

Usage:
    from api.logging_structured import get_logger

    logger = get_logger(__name__)
    logger.info("user_login", user_id="123", ip="127.0.0.1")
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def redact_telemetry_processor(
    logger: Any,
    method_name: str,
    event_dict: dict[str, Any],
) -> dict[str, Any]:
    """
    Structlog processor: recursively scrub secrets/PII from event payloads.

    Delegates to ``tools.security.advanced_routine.sanitize_mapping`` so telemetry
    shares the same policy as CLI scans.
    """

    from tools.security.advanced_routine import RoutineMode, sanitize_mapping

    out = sanitize_mapping(event_dict, RoutineMode.ADVANCED)
    if isinstance(out, dict):
        return out
    return event_dict


def configure_structured_logging(
    environment: str = "development",
    log_level: str = "INFO",
    json_output: bool | None = None,
) -> None:
    """
    Configure structlog for Echoes.

    Args:
        environment: Current environment (development, production, testing)
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_output: Force JSON output. If None, auto-detect based on environment.
    """
    if json_output is None:
        json_output = environment.lower() in ("production", "staging")

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if json_output:
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ]
        logging.basicConfig(
            format="%(message)s",
            stream=sys.stdout,
            level=getattr(logging, log_level.upper(), logging.INFO),
        )
    else:
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]
        logging.basicConfig(
            format="%(levelname)s %(name)s: %(message)s",
            stream=sys.stdout,
            level=getattr(logging, log_level.upper(), logging.INFO),
        )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def bind_context(**context: Any) -> None:
    """Bind context variables included in all subsequent log entries."""
    structlog.contextvars.bind_contextvars(**context)


def clear_context() -> None:
    """Clear all bound context variables."""
    structlog.contextvars.clear_contextvars()


_configured = False


def ensure_configured() -> None:
    """Ensure logging is configured (idempotent)."""
    global _configured
    if not _configured:
        import os

        env = os.getenv("ENVIRONMENT", "development")
        log_level = os.getenv("LOG_LEVEL", "INFO")
        configure_structured_logging(environment=env, log_level=log_level)
        _configured = True


__all__ = [
    "configure_structured_logging",
    "get_logger",
    "bind_context",
    "clear_context",
    "ensure_configured",
    "redact_telemetry_processor",
]
