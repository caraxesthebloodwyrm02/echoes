"""Timezone-aware datetime utilities.

Replaces deprecated datetime.utcnow() for Python 3.13+ compatibility.
"""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(UTC)


def utc_timestamp() -> str:
    """Return current UTC time as ISO format string."""
    return utc_now().isoformat()


def utc_from_timestamp(timestamp: float) -> datetime:
    """Create UTC datetime from Unix timestamp."""
    return datetime.fromtimestamp(timestamp, tz=UTC)


__all__ = ["utc_now", "utc_timestamp", "utc_from_timestamp"]
