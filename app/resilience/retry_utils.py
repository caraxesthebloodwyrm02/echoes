"""
Retry utilities for outbound API calls using tenacity.

Provides exponential backoff with jitter to prevent thundering herds.
Follows AGENTS.md architecture guidelines for 429 handling.
"""

import logging
from collections.abc import Callable
from functools import wraps
from typing import Any

import httpx
from tenacity import (
    RetryCallState,
    after_log,
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential_jitter,
)

logger = logging.getLogger(__name__)


def retry_config(
    max_attempts: int = 5,
    initial_wait: float = 1.0,
    max_wait: float = 30.0,
    backoff_multiplier: float = 2.0,
) -> Callable:
    """
    Create a tenacity retry decorator with exponential jitter.

    This prevents thundering herds by adding randomness to retry timing.
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential_jitter(
            initial=initial_wait, max=max_wait, exp_base=backoff_multiplier
        ),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        after=after_log(logger, logging.INFO),
        reraise=True,
    )


def should_retry_exception(exception: Exception) -> bool:
    """
    Determine if an exception should trigger a retry.

    Retries on:
    - HTTP 429 (Too Many Requests)
    - HTTP 5xx (Server errors)
    - Connection errors
    - Timeout errors

    Does NOT retry on:
    - HTTP 4xx (Client errors, except 429)
    - Business logic errors
    """
    if isinstance(exception, httpx.HTTPStatusError):
        # Retry on 429 and 5xx
        status_code = exception.response.status_code
        return status_code == 429 or status_code >= 500

    # Retry on connection/timeout errors
    if isinstance(exception, (httpx.ConnectError, httpx.TimeoutException)):
        return True

    return False


def resilient_http_call(method: str = "GET", url: str = "", **kwargs: Any) -> Callable:
    """
    Decorator for resilient HTTP calls with automatic retry logic.

    Usage:
        @resilient_http_call(method="POST", url="https://api.example.com/data")
        async def call_external_api(data: dict):
            # This function will be called with automatic retries
            pass
    """

    def decorator(func: Callable) -> Callable:
        @retry_config()
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                if should_retry_exception(e):
                    logger.warning(f"Retrying {method} {url} after error: {e}")
                    raise  # Re-raise to trigger tenacity retry
                else:
                    logger.error(f"Non-retryable error for {method} {url}: {e}")
                    raise

        return wrapper

    return decorator


async def make_resilient_request(
    method: str,
    url: str,
    max_retries: int = 3,
    timeout: float = 10.0,
    respect_retry_after: bool = True,
    **kwargs: Any,
) -> httpx.Response:
    """
    Make an HTTP request with built-in resilience patterns.

    Automatically handles:
    - Exponential backoff with jitter
    - Retry-After header parsing
    - Proper 429/5xx error handling

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Target URL
        max_retries: Maximum retry attempts
        timeout: Request timeout in seconds
        respect_retry_after: Whether to parse Retry-After headers
        **kwargs: Additional httpx.AsyncClient arguments

    Returns:
        httpx.Response: The successful response

    Raises:
        tenacity.RetryError: If all retries exhausted
        httpx.HTTPStatusError: For non-retryable HTTP errors
    """

    @retry(
        stop=stop_after_attempt(max_retries),
        wait=wait_exponential_jitter(initial=1, max=30),
        retry=should_retry_exception,
        before_sleep=_log_retry_attempt,
        reraise=True,
    )
    async def _make_request() -> httpx.Response:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(method, url, **kwargs)

            # Handle Retry-After header for 429 responses
            if response.status_code == 429 and respect_retry_after:
                retry_after = response.headers.get("Retry-After")
                if retry_after:
                    try:
                        wait_seconds = int(retry_after)
                        logger.warning(
                            f"Server requested wait of {wait_seconds}s via Retry-After"
                        )
                        # Note: tenacity will handle the wait via its wait strategy
                    except ValueError:
                        pass  # Invalid Retry-After value, ignore

            # Raise for status to trigger retries on 429/5xx
            response.raise_for_status()
            return response

    return await _make_request()


def _log_retry_attempt(retry_state: RetryCallState) -> None:
    """Log retry attempts with context."""
    attempt = retry_state.attempt_number
    exception = retry_state.outcome.exception()

    if exception:
        logger.warning(
            f"Retry attempt {attempt} failed: {exception}. "
            f"Next retry in {retry_state.next_action.sleep} seconds"
        )
    else:
        logger.info(f"Retry attempt {attempt} completed successfully")


# Pre-configured decorators for common patterns
def resilient_get(url: str, **kwargs: Any) -> Callable:
    """Decorator for resilient GET requests."""
    return resilient_http_call(method="GET", url=url, **kwargs)


def resilient_post(url: str, **kwargs: Any) -> Callable:
    """Decorator for resilient POST requests."""
    return resilient_http_call(method="POST", url=url, **kwargs)


def resilient_put(url: str, **kwargs: Any) -> Callable:
    """Decorator for resilient PUT requests."""
    return resilient_http_call(method="PUT", url=url, **kwargs)


def resilient_delete(url: str, **kwargs: Any) -> Callable:
    """Decorator for resilient DELETE requests."""
    return resilient_http_call(method="DELETE", url=url, **kwargs)
