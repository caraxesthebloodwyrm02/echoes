"""
Adaptive rate limiter for managing OpenAI API request rates.
Implements token bucket algorithm with dynamic rate adjustment.
"""

import asyncio
import logging
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

# Import metrics
from .metrics import record_rate_limit_adjustment

logger = logging.getLogger(__name__)


@dataclass
class RateLimitStats:
    """Track rate limiting statistics."""

    total_requests: int = 0
    successful_requests: int = 0
    rate_limited_requests: int = 0
    errors: int = 0
    request_timestamps: deque[float] = field(default_factory=deque)

    def record_success(self):
        """Record a successful request."""
        self.total_requests += 1
        self.successful_requests += 1
        self.request_timestamps.append(time.time())

    def record_rate_limit(self):
        """Record a rate-limited request."""
        self.total_requests += 1
        self.rate_limited_requests += 1

    def record_error(self):
        """Record a failed request."""
        self.total_requests += 1
        self.errors += 1

    def get_success_rate(self, window_seconds: int = 60) -> float:
        """Calculate success rate within a time window."""
        if not self.request_timestamps:
            return 1.0  # Default to 100% success if no data

        now = time.time()
        # Remove timestamps outside the window
        while (
            self.request_timestamps
            and self.request_timestamps[0] < now - window_seconds
        ):
            self.request_timestamps.popleft()

        if not self.request_timestamps:
            return 1.0

        # Calculate success rate in the window
        total_in_window = len(self.request_timestamps)
        successful_in_window = sum(
            1 for _ in self.request_timestamps
        )  # All in window are successful
        return successful_in_window / total_in_window if total_in_window > 0 else 1.0


class AdaptiveRateLimiter:
    """
    Adaptive rate limiter that adjusts request rates based on success patterns.

    Implements a token bucket algorithm with dynamic rate adjustment based on:
    - Success rate of recent requests
    - Rate limit responses from the API
    - Current system load (optional)
    """

    def __init__(
        self,
        initial_rpm: int = 3000,  # Initial requests per minute
        initial_tpm: int = 150000,  # Initial tokens per minute
        min_rpm: int = 100,  # Minimum allowed requests per minute
        max_rpm: int = 10000,  # Maximum allowed requests per minute
        min_tpm: int = 10000,  # Minimum allowed tokens per minute
        max_tpm: int = 200000,  # Maximum allowed tokens per minute
        burst_multiplier: float = 1.5,  # Allow bursts up to this multiple of current rate
        adjustment_interval: float = 60.0,  # How often to adjust rates (seconds)
        success_rate_target: float = 0.95,  # Target success rate (0.0-1.0)
        history_size: int = 1000,  # Number of requests to keep in history
    ):
        # Rate limiting parameters
        self.initial_rpm = initial_rpm
        self.initial_tpm = initial_tpm
        self.min_rpm = min_rpm
        self.max_rpm = max_rpm
        self.min_tpm = min_tpm
        self.max_tpm = max_tpm
        self.burst_multiplier = burst_multiplier
        self.adjustment_interval = adjustment_interval
        self.success_rate_target = success_rate_target
        self.history_size = history_size

        # Current state
        self.current_rpm = initial_rpm
        self.current_tpm = initial_tpm
        self.tokens_per_second = self.current_rpm / 60.0
        self.bucket_capacity = (self.current_rpm / 60.0) * burst_multiplier
        self.tokens = self.bucket_capacity
        self.last_update = time.monotonic()
        self.last_adjustment = time.monotonic()

        # Token usage tracking
        self.tokens_per_second_tpm = self.current_tpm / 60.0
        self.token_bucket_capacity = (self.current_tpm / 60.0) * burst_multiplier
        self.token_bucket = self.token_bucket_capacity

        # Statistics and monitoring
        self.stats = RateLimitStats()
        self.lock = asyncio.Lock()

        # Per-endpoint tracking
        self.endpoint_stats: dict[str, RateLimitStats] = {}

        logger.info(
            f"Initialized AdaptiveRateLimiter with {initial_rpm} RPM and {initial_tpm} TPM "
            f"(min: {min_rpm}-{min_tpm}, max: {max_rpm}-{max_tpm}, burst: {burst_multiplier}x)"
        )

    def _get_endpoint_stats(self, endpoint: str) -> RateLimitStats:
        """Get or create stats for a specific endpoint."""
        if endpoint not in self.endpoint_stats:
            self.endpoint_stats[endpoint] = RateLimitStats()
        return self.endpoint_stats[endpoint]

    async def _update_tokens(self):
        """Update token count based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_update

        if elapsed <= 0:
            return

        # Add tokens based on elapsed time and current rate
        new_tokens = elapsed * self.tokens_per_second
        self.tokens = min(self.bucket_capacity, self.tokens + new_tokens)

        # Add token capacity based on elapsed time and current TPM
        new_token_capacity = elapsed * self.tokens_per_second_tpm
        self.token_bucket = min(
            self.token_bucket_capacity, self.token_bucket + new_token_capacity
        )

        self.last_update = now

        # Periodically adjust rate based on success patterns
        if now - self.last_adjustment >= self.adjustment_interval:
            await self._adjust_rate()
            self.last_adjustment = now

    async def _adjust_rate(self):
        """Adjust rate based on recent success patterns."""
        # Calculate overall success rate
        success_rate = self.stats.get_success_rate()

        # Adjust rate based on success rate
        if success_rate < self.success_rate_target - 0.05:  # Below target
            # Decrease rate more aggressively if we're far from target
            factor = 0.8 if success_rate < self.success_rate_target - 0.15 else 0.9
            new_rpm = max(self.min_rpm, self.current_rpm * factor)

            logger.info(
                f"Decreasing rate from {self.current_rpm:.1f} to {new_rpm:.1f} RPM "
                f"(success rate: {success_rate:.1%} < {self.success_rate_target:.0%} target)"
            )
        elif success_rate > self.success_rate_target + 0.05:  # Above target
            # Increase rate more conservatively
            factor = 1.05  # 5% increase
            new_rpm = min(self.max_rpm, self.current_rpm * factor)

            logger.info(
                f"Increasing rate from {self.current_rpm:.1f} to {new_rpm:.1f} RPM "
                f"(success rate: {success_rate:.1%} > {self.success_rate_target:.0%} target)"
            )
        else:
            # Within target range, no adjustment needed
            return

        # Update rate
        old_rpm = self.current_rpm
        self.current_rpm = new_rpm
        self.tokens_per_second = self.current_rpm / 60.0
        self.bucket_capacity = (self.current_rpm / 60.0) * self.burst_multiplier

        # Record the adjustment in metrics
        record_rate_limit_adjustment(
            old_rate=old_rpm, new_rate=new_rpm, success_rate=success_rate
        )

    async def acquire(
        self,
        tokens: int = 1,
        token_count: int = 0,
        endpoint: str = "default",
        max_wait: float = 10.0,
    ) -> tuple[bool, float]:
        """
        Acquire tokens from the rate limiter.

        Args:
            tokens: Number of request tokens to acquire (1 = 1 request)
            token_count: Number of content tokens to consume
            endpoint: API endpoint being called (for per-endpoint tracking)
            max_wait: Maximum time to wait for tokens (seconds)

        Returns:
            Tuple of (success, wait_time_seconds)
        """
        start_time = time.monotonic()
        timeout = start_time + max_wait

        async with self.lock:
            while True:
                await self._update_tokens()

                # Check if we have enough request tokens
                request_tokens_ok = self.tokens >= tokens

                # Check if we have enough content tokens (if specified)
                content_tokens_ok = (
                    self.token_bucket >= token_count if token_count > 0 else True
                )

                # Check if we have enough tokens for both limits
                if request_tokens_ok and content_tokens_ok:
                    self.tokens -= tokens
                    if token_count > 0:
                        self.token_bucket -= token_count
                    return True, time.monotonic() - start_time

                # Calculate time until next token is available
                now = time.monotonic()

                # Time for request tokens
                request_tokens_needed = tokens - self.tokens
                request_time_needed = (
                    request_tokens_needed / self.tokens_per_second
                    if request_tokens_needed > 0
                    else 0
                )

                # Time for content tokens
                content_tokens_needed = token_count - self.token_bucket
                content_time_needed = (
                    content_tokens_needed / self.tokens_per_second_tpm
                    if content_tokens_needed > 0
                    else 0
                )

                # Use the longer of the two wait times
                time_needed = max(request_time_needed, content_time_needed)

                # Check if we'd exceed the timeout
                if now + time_needed > timeout:
                    return False, time.monotonic() - start_time

                # Wait for tokens to be available
                await asyncio.sleep(min(0.1, time_needed))

    async def record_success(self, endpoint: str = "default", token_count: int = 0):
        """Record a successful API call."""
        async with self.lock:
            self.stats.record_success()
            self._get_endpoint_stats(endpoint).record_success()

    async def record_rate_limit(self, endpoint: str = "default"):
        """Record a rate-limited API call."""
        async with self.lock:
            self.stats.record_rate_limit()
            self._get_endpoint_stats(endpoint).record_rate_limit()

            # Immediately reduce rate on rate limit
            self.current_rpm = max(
                self.min_rpm, min(self.current_rpm * 0.8, self.current_rpm - 100)
            )
            self.current_tpm = max(
                self.min_tpm, min(self.current_tpm * 0.8, self.current_tpm - 10000)
            )
            self.tokens_per_second = self.current_rpm / 60.0
            self.bucket_capacity = (self.current_rpm / 60.0) * self.burst_multiplier
            self.tokens_per_second_tpm = self.current_tpm / 60.0
            self.token_bucket_capacity = (
                self.current_tpm / 60.0
            ) * self.burst_multiplier

            logger.warning(
                f"Rate limited! Reducing rates to {self.current_rpm:.1f} RPM and {self.current_tpm:.0f} TPM"
            )

    async def record_error(self, endpoint: str = "default"):
        """Record a failed API call."""
        async with self.lock:
            self.stats.record_error()
            self._get_endpoint_stats(endpoint).record_error()

    def get_status(self) -> dict[str, Any]:
        """Get current rate limiter status."""
        now = time.monotonic()
        now - self.last_update

        return {
            "current_rpm": self.current_rpm,
            "current_tpm": self.current_tpm,
            "min_rpm": self.min_rpm,
            "max_rpm": self.max_rpm,
            "min_tpm": self.min_tpm,
            "max_tpm": self.max_tpm,
            "tokens_available": self.tokens,
            "tokens_per_second": self.tokens_per_second,
            "bucket_capacity": self.bucket_capacity,
            "token_bucket_available": self.token_bucket,
            "token_bucket_capacity": self.token_bucket_capacity,
            "success_rate": self.stats.get_success_rate(),
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "rate_limited_requests": self.stats.rate_limited_requests,
            "errors": self.stats.errors,
            "requests_in_last_minute": len(
                [t for t in self.stats.request_timestamps if t > now - 60]
            ),
            "endpoints": {
                endpoint: {
                    "total_requests": stats.total_requests,
                    "success_rate": stats.get_success_rate(),
                    "requests_in_last_minute": len(
                        [t for t in stats.request_timestamps if t > now - 60]
                    ),
                }
                for endpoint, stats in self.endpoint_stats.items()
            },
        }


# Global rate limiter instance
_default_rate_limiter: AdaptiveRateLimiter | None = None


def get_default_rate_limiter() -> AdaptiveRateLimiter:
    """Get the global rate limiter instance."""
    global _default_rate_limiter
    if _default_rate_limiter is None:
        _default_rate_limiter = AdaptiveRateLimiter()
    return _default_rate_limiter


def set_default_rate_limiter(rate_limiter: AdaptiveRateLimiter) -> None:
    """Set the global rate limiter instance."""
    global _default_rate_limiter
    _default_rate_limiter = rate_limiter
