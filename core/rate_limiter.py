"""
Rate Limiting Middleware
Prevents API abuse by limiting requests per client
"""

import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm
    """

    def __init__(self, app, requests_per_minute: int = 60, requests_per_hour: int = 1000):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Storage: {client_id: [(timestamp, count)]}
        self.minute_window: Dict[str, list] = defaultdict(list)
        self.hour_window: Dict[str, list] = defaultdict(list)

    def _get_client_id(self, request: Request) -> str:
        """
        Extract client identifier from request
        Priority: API key > JWT token > IP address
        """
        # Check for API key
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key[:16]}"  # Use first 16 chars

        # Check for JWT token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            return f"jwt:{token[:16]}"

        # Fallback to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    def _clean_old_requests(self, window: Dict[str, list], max_age: float):
        """Remove requests older than max_age seconds"""
        current_time = time.time()
        for client_id in list(window.keys()):
            window[client_id] = [(ts, count) for ts, count in window[client_id] if current_time - ts < max_age]
            if not window[client_id]:
                del window[client_id]

    def _check_rate_limit(
        self, client_id: str, window: Dict[str, list], limit: int, window_seconds: int
    ) -> Tuple[bool, int, int]:
        """
        Check if client has exceeded rate limit

        Returns:
            (is_allowed, current_count, limit)
        """
        current_time = time.time()

        # Clean old requests
        window[client_id] = [(ts, count) for ts, count in window[client_id] if current_time - ts < window_seconds]

        # Count requests in window
        current_count = sum(count for _, count in window[client_id])

        if current_count >= limit:
            return False, current_count, limit

        # Add current request
        window[client_id].append((current_time, 1))

        return True, current_count + 1, limit

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""

        # Skip rate limiting for health check
        if request.url.path == "/health":
            return await call_next(request)

        client_id = self._get_client_id(request)

        # Check minute limit
        minute_allowed, minute_count, minute_limit = self._check_rate_limit(
            client_id, self.minute_window, self.requests_per_minute, 60
        )

        if not minute_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {minute_count}/{minute_limit} requests per minute",
                headers={"Retry-After": "60"},
            )

        # Check hour limit
        hour_allowed, hour_count, hour_limit = self._check_rate_limit(
            client_id, self.hour_window, self.requests_per_hour, 3600
        )

        if not hour_allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded: {hour_count}/{hour_limit} requests per hour",
                headers={"Retry-After": "3600"},
            )

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(self.requests_per_minute - minute_count)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(self.requests_per_hour - hour_count)

        return response


class TokenBucketRateLimiter:
    """
    Alternative rate limiter using token bucket algorithm
    More flexible for burst traffic
    """

    def __init__(self, capacity: int = 100, refill_rate: float = 10.0):
        """
        Args:
            capacity: Maximum tokens in bucket
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.buckets: Dict[str, Tuple[float, float]] = {}  # {client_id: (tokens, last_update)}

    def _refill_bucket(self, client_id: str) -> float:
        """Refill tokens based on time elapsed"""
        current_time = time.time()

        if client_id not in self.buckets:
            self.buckets[client_id] = (self.capacity, current_time)
            return self.capacity

        tokens, last_update = self.buckets[client_id]
        time_elapsed = current_time - last_update

        # Add tokens based on refill rate
        new_tokens = min(self.capacity, tokens + (time_elapsed * self.refill_rate))
        self.buckets[client_id] = (new_tokens, current_time)

        return new_tokens

    def allow_request(self, client_id: str, cost: float = 1.0) -> bool:
        """
        Check if request is allowed

        Args:
            client_id: Client identifier
            cost: Token cost of this request

        Returns:
            True if request allowed
        """
        tokens = self._refill_bucket(client_id)

        if tokens >= cost:
            self.buckets[client_id] = (tokens - cost, time.time())
            return True

        return False
