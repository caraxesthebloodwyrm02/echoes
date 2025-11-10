"""
OpenAI API wrapper with latency logging, async client, and retry/backoff.
Intended to be imported by samplers or performance optimizer modules.
"""

import asyncio
import time
import random
import logging
from contextlib import asynccontextmanager
from typing import Any, Callable, Optional, Dict, Tuple
import openai
from openai import OpenAIError, RateLimitError

# Handle PermissionError compatibility across OpenAI versions
try:
    from openai import PermissionDeniedError as OpenAIPermissionError
except ImportError:
    # Fallback for older versions
    try:
        OpenAIPermissionError = openai.PermissionError
    except AttributeError:
        # Create a fallback exception class
        class OpenAIPermissionError(Exception):
            pass


# Import metrics and rate limiter
from .metrics import (
    record_openai_request,
    record_openai_tokens,
    record_rate_limit_delay,
    record_rate_limit_rejection,
    record_rate_limit_wait_time,
    record_rate_limit_metrics,
)
from .rate_limiter import get_default_rate_limiter, AdaptiveRateLimiter

logger = logging.getLogger(__name__)


@asynccontextmanager
async def log_latency(label: str, payload: Dict[str, Any]):
    """Async context manager to log request latency with metadata."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        logger.info(
            "openai_call",
            extra={
                "label": label,
                "elapsed_seconds": elapsed,
                "payload": payload,
            },
        )
        # Optional: record to PerformanceMetrics if available
        try:
            from .performance_optimizer import PerformanceOptimizer

            # Attempt to get a shared optimizer instance if one exists
            # This is a soft integration; no hard dependency required
        except Exception:
            pass


async def call_with_backoff(
    fn: Callable,
    max_attempts: int = 5,
    base_delay: float = 0.5,
    max_delay: float = 60.0,
    endpoint: str = "unknown",
    rate_limiter: Optional[AdaptiveRateLimiter] = None,
    **kwargs,  # OpenAI API parameters go here
) -> Tuple[Any, Dict[str, Any]]:
    """
    Call an async function with exponential backoff on RateLimitError.
    OpenAI API parameters should be passed as kwargs.
    Returns a tuple of (result, metadata) or raises RuntimeError after max_attempts.
    """
    rate_limiter = rate_limiter or get_default_rate_limiter()
    last_error = None

    # Extract model for logging/metrics
    model = kwargs.get("model", "unknown")

    for attempt in range(1, max_attempts + 1):
        start_time = time.perf_counter()
        status_code = 200

        # Apply rate limiting
        if attempt == 1:  # Only rate limit on first attempt
            try:
                # Try to acquire a token with a reasonable timeout
                # Estimate token usage for rate limiting (rough estimate)
                estimated_tokens = getattr(
                    kwargs.get("messages", [{}])[0], "get", lambda k, d=0: d
                )("estimated_tokens", 0)
                if not estimated_tokens and "messages" in kwargs:
                    # Rough estimate: ~4 tokens per message word
                    message_text = str(kwargs["messages"])
                    estimated_tokens = len(message_text.split()) * 4

                acquired, wait_time = await rate_limiter.acquire(
                    endpoint=endpoint,
                    token_count=min(
                        estimated_tokens, rate_limiter.current_tpm // 60
                    ),  # Cap at 1 second worth
                    max_wait=30.0,  # Allow up to 30 seconds for rate limiting
                )

                if not acquired:
                    # We couldn't get a token within the timeout
                    record_rate_limit_rejection(endpoint)
                    raise RuntimeError(
                        f"Rate limit exceeded for {endpoint} - max wait time reached"
                    )

                # Record the time we spent waiting for rate limiting
                if wait_time > 0.001:  # Only record if we actually waited
                    record_rate_limit_delay(endpoint)
                    record_rate_limit_wait_time(wait_time, endpoint)

            except asyncio.TimeoutError:
                record_rate_limit_rejection(endpoint)
                raise RuntimeError(f"Rate limit acquisition timed out for {endpoint}")

        try:
            try:
                # Call the function with all kwargs (OpenAI API parameters)
                result = await fn(**kwargs)

                # Record success
                duration = time.perf_counter() - start_time
                record_openai_request(
                    endpoint=endpoint,
                    model=model,
                    duration=duration,
                    status_code=status_code,
                )

                # Extract token usage if available
                usage = getattr(result, "usage", {})
                if hasattr(usage, "prompt_tokens") and hasattr(
                    usage, "completion_tokens"
                ):
                    record_openai_tokens(
                        prompt_tokens=usage.prompt_tokens,
                        completion_tokens=usage.completion_tokens,
                        model=model,
                    )

                # Record successful request in rate limiter with actual token consumption
                actual_tokens = (
                    usage.total_tokens
                    if hasattr(usage, "total_tokens")
                    else estimated_tokens
                )
                await rate_limiter.record_success(endpoint, token_count=actual_tokens)

                # Update rate limiter metrics
                status = rate_limiter.get_status()
                record_rate_limit_metrics(
                    endpoint=endpoint,
                    tokens_available=status["tokens_available"],
                    bucket_capacity=status["bucket_capacity"],
                    requests_per_minute=status["current_rpm"],
                )

                return result, {
                    "attempts": attempt,
                    "duration": duration,
                    "status": "success",
                    "usage": {
                        "prompt_tokens": getattr(usage, "prompt_tokens", 0),
                        "completion_tokens": getattr(usage, "completion_tokens", 0),
                        "total_tokens": getattr(usage, "total_tokens", 0),
                    },
                    "rate_limit_info": {
                        "rpm": status["current_rpm"],
                        "success_rate": status["success_rate"],
                    },
                }

            except Exception as e:
                # Record failure in rate limiter
                if isinstance(e, openai.RateLimitError) or (
                    hasattr(e, "status_code") and e.status_code == 429
                ):
                    await rate_limiter.record_rate_limit(endpoint)
                    record_rate_limit_rejection(endpoint)
                else:
                    await rate_limiter.record_error(endpoint)

                # Re-raise the exception to be handled by the outer try/except
                raise

        except RateLimitError as e:
            status_code = 429
            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            jitter = random.uniform(0, delay / 2)
            wait = delay + jitter
            last_error = e

            logger.warning(
                "openai_rate_limit_retry",
                extra={
                    "attempt": attempt,
                    "max_attempts": max_attempts,
                    "wait_seconds": wait,
                    "error": str(e),
                    "endpoint": endpoint,
                    "model": model,
                    "current_rpm": rate_limiter.current_rpm if rate_limiter else None,
                },
            )

            # Record the rate limit delay
            record_rate_limit_delay(endpoint)

            # Record the failed attempt
            duration = time.perf_counter() - start_time
            record_openai_request(
                endpoint=endpoint,
                model=model,
                duration=duration,
                status_code=status_code,
            )

            # Use the rate limiter's backoff if available, otherwise use default
            if rate_limiter:
                # The rate limiter's record_rate_limit was already called in the inner try/except
                await asyncio.sleep(wait)
            else:
                # Fallback to default behavior if no rate limiter
                record_rate_limit_delay(endpoint)
                await asyncio.sleep(wait)

        except OpenAIError as e:
            last_error = e
            status_code = getattr(e, "status_code", 500)

            # Record the failed attempt
            duration = time.perf_counter() - start_time
            record_openai_request(
                endpoint=endpoint,
                model=model,
                duration=duration,
                status_code=status_code,
            )

            if attempt < max_attempts:
                logger.warning(
                    "openai_error_retry",
                    extra={
                        "attempt": attempt,
                        "max_attempts": max_attempts,
                        "error": str(e),
                        "endpoint": endpoint,
                        "model": model,
                        "status_code": status_code,
                    },
                )
                await asyncio.sleep(base_delay)
                continue
            else:
                logger.error(
                    "openai_error_max_retries",
                    extra={
                        "error": str(e),
                        "endpoint": endpoint,
                        "model": model,
                        "status_code": status_code,
                        "max_attempts": max_attempts,
                    },
                    exc_info=True,
                )
                raise

    # If we get here, all retries were exhausted
    record_rate_limit_rejection()
    logger.error(
        "openai_max_retries_exceeded",
        extra={
            "endpoint": endpoint,
            "model": model,
            "max_attempts": max_attempts,
            "last_error": str(last_error) if last_error else "Unknown error",
        },
    )
    raise RuntimeError(
        f"Max retries ({max_attempts}) exceeded for OpenAI call to {endpoint}."
    )


# Example async client wrapper
class AsyncOpenAIClient:
    """
    Thin async wrapper around OpenAI client with built-in latency logging,
    adaptive rate limiting, and exponential backoff.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limiter: Optional[AdaptiveRateLimiter] = None,
    ):
        self._client = openai.AsyncOpenAI(api_key=api_key)
        self._rate_limiter = rate_limiter or get_default_rate_limiter()

    async def chat_completion(
        self,
        messages: list[dict],
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        rate_limiter: Optional[AdaptiveRateLimiter] = None,
        **kwargs,
    ) -> dict:
        """Make an async chat completion request with automatic retries and metrics."""
        # Use the provided rate limiter or fall back to the instance one
        current_rate_limiter = rate_limiter or self._rate_limiter

        try:
            result, metadata = await call_with_backoff(
                self._client.chat.completions.create,
                endpoint="chat/completions",
                rate_limiter=current_rate_limiter,
                # OpenAI API parameters
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )
            return result.model_dump() if hasattr(result, "model_dump") else result

        except Exception as e:
            logger.error(
                "openai_chat_completion_error",
                extra={
                    "error": str(e),
                    "model": model,
                    "messages_count": len(messages),
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                exc_info=True,
            )
            raise

    async def embeddings(
        self,
        input: str | list[str],
        model: str = "text-embedding-3-small",
        **extra_kwargs,
    ) -> dict:
        """Async embeddings.create with latency and retry."""

        async def _call():
            async with log_latency(
                "embeddings", {"model": model, "input": input, **extra_kwargs}
            ):
                response = await self._client.embeddings.create(
                    model=model, input=input, **extra_kwargs
                )
                return (
                    response.model_dump()
                    if hasattr(response, "model_dump")
                    else response
                )

        return await call_with_backoff(_call, endpoint="embeddings")


# Convenience global client (can be replaced or configured)
_default_client: Optional[AsyncOpenAIClient] = None


def get_default_client() -> AsyncOpenAIClient:
    """Return a shared AsyncOpenAIClient instance."""
    global _default_client
    if _default_client is None:
        _default_client = AsyncOpenAIClient()
    return _default_client


# Example usage in a sampler:
#
# from glimpse.openai_wrapper import get_default_client
# client = get_default_client()
# resp = await client.chat_completion(messages=[{"role":"user","content":"Hi"}])
# content = resp["choices"][0]["message"]["content"]
