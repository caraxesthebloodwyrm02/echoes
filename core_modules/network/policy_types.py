"""Policy types and data structures."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import os


def _env(key: str, default: str = "") -> str:
    """Get environment variable with default."""
    return os.getenv(key, default)


def _parse_bool(value: Optional[str], default: bool) -> bool:
    """Parse boolean from string value."""
    if value is None:
        return default
    val = value.strip().lower()
    if val in ("1", "true", "yes", "on"):
        return True
    if val in ("0", "false", "no", "off"):
        return False
    return default


@dataclass(frozen=True)
class PolicyConfig:
    """Policy configuration loaded from environment."""

    enforce: bool
    allowlist: tuple[str, ...]
    log_level: int
    log_format: str
    otel_enable: bool
    otel_exporter: str
    otel_endpoint: str
    prom_enable: bool
    ci_fail_on_blocked: bool
    ci_allow_disable: bool
    ci_fail_on_drift: bool


@dataclass(frozen=True)
class PolicyEvent:
    """A policy decision event for metrics/logging."""

    ts: int
    action: str  # ALLOW or DENY
    host: str
    reason: str


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str
    matched_token: Optional[str] = None


def load_config() -> PolicyConfig:
    """Load policy configuration from environment variables."""
    enforce = _parse_bool(_env("EGRESS_ENFORCE", None), True)

    allowlist_str = _env("EGRESS_ALLOWLIST", "openai").strip()
    allowlist = tuple()
    if allowlist_str:
        allowlist = tuple(
            token.strip().lower() for token in allowlist_str.split(",") if token.strip()
        )

    log_level_str = _env("EGRESS_LOG", "1").strip()
    try:
        log_level = int(log_level_str)
    except ValueError:
        log_level = 1
    log_level = max(0, min(2, log_level))

    log_format = _env("EGRESS_LOG_FORMAT", "text").strip().lower()
    if log_format not in ("text", "json"):
        log_format = "text"

    otel_enable = _parse_bool(_env("EGRESS_OTEL_ENABLE", None), False)
    otel_exporter = _env("EGRESS_OTEL_EXPORTER", "http").strip().lower()
    if otel_exporter not in ("http", "grpc"):
        otel_exporter = "http"
    otel_endpoint = _env("EGRESS_OTEL_ENDPOINT", "http://localhost:4318").strip()

    prom_enable = _parse_bool(_env("EGRESS_PROM_ENABLE", None), False)
    ci_fail_on_blocked = _parse_bool(_env("EGRESS_CI_FAIL_ON_BLOCKED", None), False)
    ci_allow_disable = _parse_bool(_env("EGRESS_CI_ALLOW_DISABLE", None), False)
    ci_fail_on_drift = _parse_bool(_env("EGRESS_CI_FAIL_ON_DRIFT", None), False)

    return PolicyConfig(
        enforce=enforce,
        allowlist=allowlist,
        log_level=log_level,
        log_format=log_format,
        otel_enable=otel_enable,
        otel_exporter=otel_exporter,
        otel_endpoint=otel_endpoint,
        prom_enable=prom_enable,
        ci_fail_on_blocked=ci_fail_on_blocked,
        ci_allow_disable=ci_allow_disable,
        ci_fail_on_drift=ci_fail_on_drift,
    )
