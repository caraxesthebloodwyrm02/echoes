"""
Rate limiting implementation for FastAPI using SlowApi.

Provides inbound rate limiting with Redis backend for distributed deployments.
Follows AGENTS.md architecture guidelines for 429 handling.
"""

import hashlib
import logging
from collections.abc import Callable

from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from api.config import get_config

logger = logging.getLogger(__name__)

_limiter: Limiter | None = None


def get_api_key_func(request: Request) -> str:
    """
    Key function that prioritizes API key over IP address.

    This prevents unfair rate limiting where legitimate API key users
    get blocked due to shared IP addresses (corporate networks, etc.).
    Uses SHA-256 hash of API keys to avoid storing raw credentials in Redis.
    """
    # Try Authorization header first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        key = auth_header[7:]
        return f"api_key:{hashlib.sha256(key.encode()).hexdigest()[:32]}"

    # Try X-API-Key header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{hashlib.sha256(api_key.encode()).hexdigest()[:32]}"

    # Fall back to IP address with prefix
    return f"ip:{get_remote_address(request)}"


def setup_rate_limiting(app: FastAPI) -> Limiter:
    """
    Setup SlowApi rate limiting for the FastAPI application.

    Returns the limiter instance for use in decorators or custom logic.
    """
    config = get_config()

    # Initialize limiter with Redis storage for distributed deployments
    storage_uri = None
    if config.redis.url:
        # slowapi expects a storage URI string; pass directly
        storage_uri = config.redis.url

    limiter = Limiter(
        key_func=get_api_key_func,
        default_limits=[f"{config.security.rate_limit_requests}/minute"],
        storage_uri=storage_uri,
    )

    # Add rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Store limiter on app for access in routes
    app.state.limiter = limiter
    global _limiter
    _limiter = limiter

    logger.info("Rate limiting configured with SlowApi")
    logger.info(f"Default limits: {limiter._default_limits}")
    logger.info(f"Storage: {'Redis' if config.redis.url else 'In-memory'}")

    return limiter


# Pre-configured limit decorators for common use cases
def strict_limit(limit: str) -> Callable:
    """
    Decorator for strict rate limiting (e.g., authentication endpoints).

    Usage:
        @app.post("/auth/login")
        @strict_limit("5/minute")
        async def login():
            ...
    """

    def decorator(func: Callable) -> Callable:
        if _limiter is None:
            raise RuntimeError(
                "Limiter not initialized. Call setup_rate_limiting first."
            )
        return _limiter.limit(limit)(func)

    return decorator


def api_key_limit(limit: str) -> Callable:
    """
    Decorator that enforces per-API-key rate limiting.

    Falls back to IP-based limiting if no API key provided.
    """

    def decorator(func: Callable) -> Callable:
        if _limiter is None:
            raise RuntimeError(
                "Limiter not initialized. Call setup_rate_limiting first."
            )
        return _limiter.limit(limit, key_func=get_api_key_func)(func)

    return decorator
