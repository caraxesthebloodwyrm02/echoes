"""Timezone-aware datetime utilities.

Replaces deprecated datetime.utcnow() for Python 3.13+ compatibility.
"""

from datetime import datetime, timezone
from typing import Optional


def utc_now() -> datetime:
    """
    Return current UTC time as timezone-aware datetime.
    
    Replaces deprecated datetime.utcnow() for Python 3.13+ compatibility.
    
    Returns:
        datetime: Current UTC time with timezone info
        
    Example:
        >>> from src.utils.datetime_utils import utc_now
        >>> now = utc_now()
        >>> print(now.tzinfo)
        UTC
    """
    return datetime.now(timezone.utc)


def utc_timestamp() -> str:
    """
    Return current UTC time as ISO format string.
    
    Returns:
        str: ISO format timestamp (e.g., "2025-10-22T15:30:45.123456+00:00")
        
    Example:
        >>> from src.utils.datetime_utils import utc_timestamp
        >>> ts = utc_timestamp()
        >>> print(ts)
        2025-10-22T15:30:45.123456+00:00
    """
    return utc_now().isoformat()


def utc_from_timestamp(timestamp: float) -> datetime:
    """
    Create UTC datetime from Unix timestamp.
    
    Args:
        timestamp: Unix timestamp (seconds since epoch)
        
    Returns:
        datetime: Timezone-aware UTC datetime
        
    Example:
        >>> from src.utils.datetime_utils import utc_from_timestamp
        >>> dt = utc_from_timestamp(1698000000)
        >>> print(dt.tzinfo)
        UTC
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)


__all__ = ["utc_now", "utc_timestamp", "utc_from_timestamp"]
