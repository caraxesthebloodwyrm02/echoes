"""
Caching helpers for Glimpse, tuned for OpenAI API responses.
Provides prompt-aware keying, TTL/LRU eviction, and optional persistence.
"""
import hashlib
import json
import logging
import time
from collections import OrderedDict
from typing import Any

# Import metrics
from .metrics import record_cache_hit, record_cache_miss, update_cache_size

logger = logging.getLogger(__name__)


class PromptCache:
    """
    LRU cache with TTL for OpenAI prompt/response pairs.
    Keys are deterministic hashes of prompt components.
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._hits = 0
        self._misses = 0

    @staticmethod
    def _hash_prompt(
        messages: list[dict], model: str, temperature: float, max_tokens: int | None
    ) -> str:
        """Create a deterministic SHA-256 hash for the request."""
        payload = {
            "messages": messages,
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode()).hexdigest()

    async def get(
        self,
        messages: list[dict],
        model: str,
        temperature: float,
        max_tokens: int | None,
    ) -> Any | None:
        """Return cached response if available and not expired."""
        key = self._hash_prompt(messages, model, temperature, max_tokens)
        entry = self._cache.get(key)

        # Update metrics
        if entry is None:
            self._misses += 1
            record_cache_miss()
            return None

        result, timestamp = entry
        if time.time() - timestamp > self.ttl_seconds:
            # Expired - remove from cache and count as miss
            self._cache.pop(key, None)  # Safe pop with default
            self._misses += 1
            record_cache_miss()
            update_cache_size(len(self._cache))
            return None

        # Cache hit - update LRU and metrics
        self._cache.move_to_end(key)
        self._hits += 1
        record_cache_hit()
        return result

    async def set(
        self,
        messages: list[dict],
        model: str,
        temperature: float,
        max_tokens: int | None,
        response: Any,
    ) -> None:
        """Cache the response with LRU eviction."""
        key = self._hash_prompt(messages, model, temperature, max_tokens)
        now = time.time()

        # Check if key already exists to avoid unnecessary evictions
        if key in self._cache:
            self._cache[key] = (response, now)
            self._cache.move_to_end(key)
            update_cache_size(len(self._cache))
            return

        # Evict oldest if over capacity
        while len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)

        self._cache[key] = (response, now)
        update_cache_size(len(self._cache))

    def get_hit_rate(self) -> float:
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    async def clear(self) -> None:
        """Clear all entries and reset metrics."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        update_cache_size(0)  # Update metrics to reflect empty cache


# Global cache instance (can be swapped or configured)
_default_cache: PromptCache | None = None


def get_default_cache() -> PromptCache:
    """Return a shared PromptCache instance."""
    global _default_cache
    if _default_cache is None:
        # Increased defaults for higher repetition workloads
        _default_cache = PromptCache(max_size=2000, ttl_seconds=7200)
    return _default_cache


# Decorator to auto-cache any async function that matches the signature
def cached_openai_call(cache: PromptCache | None = None, skip_cache: bool = False):
    """
    Decorator for async OpenAI call functions with caching.

    Args:
        cache: Optional PromptCache instance. If None, uses default cache.
        skip_cache: If True, bypasses the cache entirely (useful for testing or forcing fresh responses).
    """

    def decorator(func):
        async def wrapper(
            messages: list[dict],
            model: str,
            temperature: float,
            max_tokens: int | None = None,
            **kwargs,
        ) -> Any:
            # Skip cache if requested or temperature > 0 (non-deterministic)
            if skip_cache or temperature > 0:
                logger.debug(
                    "cache_bypass",
                    extra={
                        "reason": "skip_cache=True"
                        if skip_cache
                        else "temperature > 0",
                        "model": model,
                        "temperature": temperature,
                    },
                )
                return await func(messages, model, temperature, max_tokens, **kwargs)

            # Get cache instance
            cache_instance = cache or get_default_cache()

            # Try cache lookup
            cached = await cache_instance.get(messages, model, temperature, max_tokens)
            if cached is not None:
                logger.debug(
                    "cache_hit",
                    extra={
                        "model": model,
                        "messages_len": len(messages),
                        "cache_size": len(cache_instance._cache),  # type: ignore
                    },
                )
                return cached

            # Cache miss - call the function and cache the result
            time.perf_counter()
            try:
                result = await func(messages, model, temperature, max_tokens, **kwargs)

                # Only cache successful responses
                if result is not None:
                    await cache_instance.set(
                        messages, model, temperature, max_tokens, result
                    )

                return result

            except Exception as e:
                logger.error(
                    "cache_miss_error",
                    extra={
                        "error": str(e),
                        "model": model,
                        "messages_len": len(messages),
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                    exc_info=True,
                )
                raise

        return wrapper

    return decorator


# Example usage:
# @cached_openai_call()
# async def my_chat_completion(messages, model, temperature, max_tokens, **kwargs):
#     # actual OpenAI call here
#     return await client.chat.completions.create(...)
