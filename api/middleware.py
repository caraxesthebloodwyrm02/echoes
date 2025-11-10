"""
Middleware for Echoes API

Provides authentication, rate limiting, and request processing middleware.
"""

import asyncio
import logging
import time
from collections import defaultdict

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self, requests_per_window: int = 60, window_seconds: int = 60):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests: dict[str, list] = defaultdict(list)

    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for the client"""
        now = time.time()
        client_requests = self.requests[client_id]

        # Remove old requests outside the window
        client_requests[:] = [
            req_time
            for req_time in client_requests
            if now - req_time < self.window_seconds
        ]

        # Check if under limit
        if len(client_requests) < self.requests_per_window:
            client_requests.append(now)
            return True

        return False

    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for the client"""
        now = time.time()
        client_requests = self.requests[client_id]

        # Clean old requests
        client_requests[:] = [
            req_time
            for req_time in client_requests
            if now - req_time < self.window_seconds
        ]

        return max(0, self.requests_per_window - len(client_requests))

    def get_reset_time(self, client_id: str) -> float:
        """Get time until rate limit resets for the client"""
        client_requests = self.requests[client_id]
        if not client_requests:
            return 0

        now = time.time()
        oldest_request = min(client_requests)
        return max(0, self.window_seconds - (now - oldest_request))


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for API key authentication"""

    def __init__(self, app, config):
        super().__init__(app)
        self.config = config
        self.rate_limiter = RateLimiter(
            requests_per_window=config.security.rate_limit_requests,
            window_seconds=config.security.rate_limit_window,
        )

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for health check and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Check if authentication is required
        if not self.config.security.api_key_required:
            # Still apply rate limiting if no auth required
            client_id = self._get_client_id(request)
            if not self.rate_limiter.is_allowed(client_id):
                return self._rate_limit_response(client_id)

            return await call_next(request)

        # Extract API key
        api_key = self._extract_api_key(request)
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "API key required"},
            )

        # Validate API key
        if api_key not in self.config.security.allowed_api_keys:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid API key"},
            )

        # Apply rate limiting
        client_id = api_key  # Use API key as client identifier
        if not self.rate_limiter.is_allowed(client_id):
            return self._rate_limit_response(client_id)

        # Add client info to request state
        request.state.client_id = client_id
        request.state.api_key = api_key

        # Continue with request
        response = await call_next(request)
        return response

    def _extract_api_key(self, request: Request) -> str | None:
        """Extract API key from request"""
        # Try Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix

        # Try X-API-Key header
        api_key_header = request.headers.get("X-API-Key")
        if api_key_header:
            return api_key_header

        # Try query parameter
        api_key_param = request.query_params.get("api_key")
        if api_key_param:
            return api_key_param

        return None

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting"""
        # Try to get from API key first
        api_key = self._extract_api_key(request)
        if api_key:
            return api_key

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    def _rate_limit_response(self, client_id: str):
        """Generate rate limit exceeded response"""
        remaining = self.rate_limiter.get_remaining_requests(client_id)
        reset_time = self.rate_limiter.get_reset_time(client_id)

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": "Rate limit exceeded",
                "remaining_requests": remaining,
                "reset_in_seconds": int(reset_time),
                "retry_after": int(reset_time),
            },
            headers={
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(int(time.time() + reset_time)),
                "Retry-After": str(int(reset_time)),
            },
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and monitoring"""

    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Increment request count
        self.request_count += 1

        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}"
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate processing time
            process_time = time.time() - start_time

            # Log response
            logger.info("Response time: %.2f", process_time)
            # Check for errors
            if response.status_code >= 400:
                self.error_count += 1

            return response

        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            self.error_count += 1
            logger.error("Request failed after %.2f seconds: %s", process_time, str(e))
            # Re-raise exception
            raise


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware for request timeout handling"""

    def __init__(self, app, timeout_seconds: int = 30):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds

    async def dispatch(self, request: Request, call_next):
        try:
            return await asyncio.wait_for(
                call_next(request), timeout=self.timeout_seconds
            )
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                content={"detail": "Request timeout"},
            )
            return JSONResponse(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                content={"error": "Request timeout"},
            )


def setup_middleware(app: ASGIApp, config) -> None:
    """Setup all middleware for the FastAPI application"""
    # Add authentication middleware
    app.add_middleware(
        AuthenticationMiddleware,
        config=config,
    )

    # Add request logging middleware
    app.add_middleware(
        RequestLoggingMiddleware,
    )

    # Add timeout middleware
    app.add_middleware(
        TimeoutMiddleware,
        timeout_seconds=config.api.request_timeout,
    )

    logger.info("Middleware configured successfully")
    logger.info(
        "Rate limiting: %d req/%ds",
        config.security.rate_limit_requests,
        config.security.rate_limit_window,
    )
    logger.info(
        "Authentication: %s",
        "Enabled" if config.security.api_key_required else "Disabled",
    )
    logger.info("Request timeout: %ds", config.api.request_timeout)
