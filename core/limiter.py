# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime
from typing import Optional


class TokenBucket:
    """
    Advanced token bucket with burst capacity and rate limiting.

    Features:
    - Configurable rate limits (tokens per minute)
    - Burst capacity for handling traffic spikes
    - Automatic token refill based on time passage
    - Thread-safe operations (for single-threaded use)
    """

    def __init__(self, max_per_min: int = 60, burst_capacity: Optional[int] = None):
        """
        Initialize token bucket.

        Args:
            max_per_min: Maximum tokens per minute (sustained rate)
            burst_capacity: Maximum burst capacity (defaults to max_per_min * 2)
        """
        self.rate_per_second = max_per_min / 60.0
        self.max_tokens = burst_capacity if burst_capacity is not None else max_per_min * 2
        self.tokens = float(max_per_min)  # Start with full capacity
        self.last_refill = datetime.utcnow()

        # Statistics for monitoring
        self.total_requests = 0
        self.total_allowed = 0
        self.total_denied = 0
        self.last_denied = None

    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens from the bucket.

        Args:
            tokens: Number of tokens to acquire (default: 1)

        Returns:
            True if tokens were acquired, False if rate limited
        """
        self._refill_tokens()
        self.total_requests += 1

        if self.tokens >= tokens:
            self.tokens -= tokens
            self.total_allowed += 1
            return True
        else:
            self.total_denied += 1
            self.last_denied = datetime.utcnow()
            return False

    def _refill_tokens(self) -> None:
        """Refill tokens based on time passed since last refill."""
        now = datetime.utcnow()
        time_passed = (now - self.last_refill).total_seconds()
        tokens_to_add = time_passed * self.rate_per_second

        if tokens_to_add > 0:
            self.tokens = min(self.max_tokens, self.tokens + tokens_to_add)
            self.last_refill = now

    def get_stats(self) -> dict:
        """Get current bucket statistics."""
        self._refill_tokens()  # Ensure stats are current

        return {
            "current_tokens": round(self.tokens, 2),
            "max_tokens": self.max_tokens,
            "rate_per_second": round(self.rate_per_second, 4),
            "rate_per_minute": round(self.rate_per_second * 60, 2),
            "total_requests": self.total_requests,
            "total_allowed": self.total_allowed,
            "total_denied": self.total_denied,
            "allowance_rate": round(self.total_allowed / max(self.total_requests, 1), 3),
            "last_denied": self.last_denied.isoformat() if self.last_denied else None,
            "time_until_full": self._time_until_full(),
        }

    def _time_until_full(self) -> Optional[float]:
        """Calculate seconds until bucket is full."""
        if self.tokens >= self.max_tokens:
            return 0.0

        tokens_needed = self.max_tokens - self.tokens
        seconds_needed = tokens_needed / self.rate_per_second
        return round(seconds_needed, 2)

    def reset_stats(self) -> None:
        """Reset statistics counters."""
        self.total_requests = 0
        self.total_allowed = 0
        self.total_denied = 0
        self.last_denied = None

    def __repr__(self) -> str:
        """String representation of bucket state."""
        stats = self.get_stats()
        return (
            f"TokenBucket(tokens={stats['current_tokens']}/{stats['max_tokens']}, "
            f"rate={stats['rate_per_minute']}/min, "
            f"allowed={stats['total_allowed']}, denied={stats['total_denied']})"
        )
