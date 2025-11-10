"""
Caching utilities for performance optimization.
"""

import functools
from typing import Any, Dict, Optional
import time
from collections import OrderedDict


class SimpleLRUCache:
    """Simple LRU cache implementation for method results."""

    def __init__(self, max_size: int = 100, ttl_seconds: Optional[int] = None):
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.cache: OrderedDict = OrderedDict()
        self.timestamps: Dict[Any, float] = {}

    def get(self, key: Any) -> Any:
        """Get value from cache if it exists and hasn't expired."""
        if key not in self.cache:
            return None

        # Check TTL if configured
        if self.ttl and key in self.timestamps:
            if time.time() - self.timestamps[key] > self.ttl:
                del self.cache[key]
                del self.timestamps[key]
                return None

        # Move to end (most recently used)
        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key: Any, value: Any) -> None:
        """Set value in cache."""
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.max_size:
            # Remove least recently used
            oldest_key, _ = self.cache.popitem(last=False)
            if oldest_key in self.timestamps:
                del self.timestamps[oldest_key]

        self.cache[key] = value
        self.timestamps[key] = time.time()

    def clear(self) -> None:
        """Clear all cached items."""
        self.cache.clear()
        self.timestamps.clear()


def cached_method(max_size: int = 50, ttl_seconds: Optional[int] = None):
    """Decorator for caching method results."""

    def decorator(func):
        cache = SimpleLRUCache(max_size, ttl_seconds)

        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            # Create cache key from method name and arguments
            key = (func.__name__, args, tuple(sorted(kwargs.items())))

            # Try to get from cache
            cached_result = cache.get(key)
            if cached_result is not None:
                return cached_result

            # Execute method and cache result
            result = func(self, *args, **kwargs)
            cache.set(key, result)
            return result

        # Add cache management methods
        wrapper.cache = cache
        wrapper.clear_cache = cache.clear

        return wrapper

    return decorator
