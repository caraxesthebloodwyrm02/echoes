"""
Echoes AI Middleware

This module provides middleware components for the Echoes AI Multi-Agent System.
"""

import logging
import time
import uuid

import redis.asyncio as redis
from fastapi import HTTPException, Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.middleware.base import (BaseHTTPMiddleware,
                                       RequestResponseEndpoint)

from .config import Settings
from .exceptions import RateLimitError

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Add unique request ID to each request."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Log request and response information."""

    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "request_id": getattr(request.state, "request_id", None),
            },
        )

        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} - {response.status_code}",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": process_time,
                "request_id": getattr(request.state, "request_id", None),
            },
        )

        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to responses."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers[
                "Strict-Transport-Security"
            ] = "max-age=31536000; includeSubDomains"

        return response


class MetricsMiddleware(BaseHTTPMiddleware):
    """Collect metrics for requests."""

    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not self.settings.metrics_enabled:
            return await call_next(request)

        start_time = time.time()

        try:
            response = await call_next(request)

            # Update metrics
            self.request_count += 1
            process_time = time.time() - start_time
            self.total_response_time += process_time

            # Log metrics (in production, you'd send to Prometheus)
            if self.settings.debug:
                logger.info(
                    f"Metrics: requests={self.request_count}, avg_response_time={self.total_response_time / self.request_count:.3f}s"
                )

            return response

        except Exception as e:
            self.error_count += 1
            logger.error(f"Request failed: {e}")
            raise


class CacheMiddleware(BaseHTTPMiddleware):
    """Simple response caching middleware."""

    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings
        self.redis_client: redis.Redis | None = None
        self.cache_ttl = settings.cache_ttl

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if not self.settings.cache_enabled:
            return await call_next(request)

        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)

        # Generate cache key
        cache_key = f"cache:{request.url.path}:{str(request.query_params)}"

        # Try to get from cache
        try:
            if not self.redis_client:
                self.redis_client = redis.from_url(self.settings.redis_url)

            cached_response = await self.redis_client.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for {cache_key}")
                return Response(
                    content=cached_response,
                    media_type="application/json",
                    headers={"X-Cache": "HIT"},
                )
        except Exception as e:
            logger.warning(f"Cache error: {e}")

        # Get fresh response
        response = await call_next(request)

        # Cache successful responses
        if response.status_code == 200:
            try:
                await self.redis_client.setex(cache_key, self.cache_ttl, response.body)
                response.headers["X-Cache"] = "MISS"
            except Exception as e:
                logger.warning(f"Cache set error: {e}")

        return response


class APIKeyMiddleware(BaseHTTPMiddleware):
    """API key authentication middleware."""

    def __init__(self, app, settings: Settings):
        super().__init__(app)
        self.settings = settings
        self.api_keys = settings.api_keys if hasattr(settings, "api_keys") else []

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip API key check for health endpoints and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Check API key
        api_key = request.headers.get("X-API-Key")
        if not api_key or api_key not in self.api_keys:
            raise HTTPException(status_code=401, detail="Invalid or missing API key")

        return await call_next(request)


# Rate limiting handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded errors."""
    raise RateLimitError(
        message=f"Rate limit exceeded: {exc.detail}",
        details={"limit": exc.detail, "retry_after": "60"},
    )


def setup_middleware(app, settings: Settings):
    """Set up all middleware for the application."""

    # Add request ID middleware
    app.add_middleware(RequestIDMiddleware)

    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # Add logging middleware
    app.add_middleware(LoggingMiddleware, settings=settings)

    # Add metrics middleware
    app.add_middleware(MetricsMiddleware, settings=settings)

    # Add cache middleware
    app.add_middleware(CacheMiddleware, settings=settings)

    # Add rate limiting
    if settings.rate_limit_enabled:
        app.state.limiter = limiter
        app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # Add API key middleware if enabled
    if hasattr(settings, "require_api_key") and settings.require_api_key:
        app.add_middleware(APIKeyMiddleware, settings=settings)


# Middleware utilities
def get_request_id(request: Request) -> str | None:
    """Get the request ID from the request state."""
    return getattr(request.state, "request_id", None)


def get_client_ip(request: Request) -> str | None:
    """Get the client IP address."""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


def get_user_agent(request: Request) -> str | None:
    """Get the user agent from the request."""
    return request.headers.get("User-Agent")
