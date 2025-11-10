# ----------------------------------------------------------------------
# Cache decorator for utility functions
# ----------------------------------------------------------------------
import functools
import time
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def cached_method(ttl: float | None = None) -> Callable[[F], F]:
    """
    Simple method cache decorator with optional TTL (time-to-live).

    Args:
        ttl: Time-to-live in seconds. If None, cache never expires.

    Usage:
        @cached_method(ttl=60)  # Cache for 60 seconds
        def expensive_operation(self, arg):
            return complex_calculation(arg)
    """

    def decorator(func: F) -> F:
        cache: dict[str, dict[str, Any]] = {}

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Create cache key from function name and arguments
            key = f"{func.__name__}:{hash(str(args) + str(sorted(kwargs.items())))}"

            now = time.time()

            # Check if result is cached and not expired
            if key in cache:
                cached_item = cache[key]
                if ttl is None or (now - cached_item["timestamp"]) < ttl:
                    return cached_item["result"]
                else:
                    # Expired, remove from cache
                    del cache[key]

            # Compute result and cache it
            result = func(*args, **kwargs)
            cache[key] = {"result": result, "timestamp": now}

            return result

        # Add cache management methods
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: {"size": len(cache), "keys": list(cache.keys())}

        return wrapper  # type: ignore

    return decorator
