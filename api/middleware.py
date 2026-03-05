"""
Middleware for Echoes API

Provides authentication, rate limiting, and request processing middleware.
"""

import asyncio
import logging
import time

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """Middleware for API key authentication"""

    def __init__(self, app, config):
        super().__init__(app)
        self.config = config

    async def dispatch(self, request: Request, call_next):
        # Skip authentication for health check and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Check if authentication is required
        if not self.config.security.api_key_required:
            # Rate limiting handled by SlowApi
            return await call_next(request)

        # Extract API key
        api_key = self._extract_api_key(request)
        if not api_key:
            logger.warning(
                f"Auth failure: missing API key from {request.client.host if request.client else 'unknown'}"
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "API key required"},
            )

        # Validate API key
        if api_key not in self.config.security.allowed_api_keys:
            logger.warning(
                f"Auth failure: invalid API key from {request.client.host if request.client else 'unknown'}"
            )
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid API key"},
            )

        # Add client info to request state
        request.state.client_id = api_key
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
            logger.info(f"Response time: {process_time:.2f}")
            # Check for errors
            if response.status_code >= 400:
                self.error_count += 1

            return response

        except Exception as e:
            # Log error
            process_time = time.time() - start_time
            self.error_count += 1
            logger.error(f"Request failed after {process_time:.2f}s: {str(e)}")
            # Re-raise exception
            raise


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware for request timeout handling"""

    def __init__(self, app, timeout_seconds: int = 30):
        super().__init__(app)
        self.timeout_seconds = timeout_seconds

    async def dispatch(self, request: Request, call_next):
        try:
            # Create timeout task
            return await asyncio.wait_for(
                call_next(request), timeout=self.timeout_seconds
            )
        except TimeoutError:
            logger.warning(
                f"Request timeout after {self.timeout_seconds}s: {request.method} {request.url.path}"
            )
            return JSONResponse(
                status_code=status.HTTP_408_REQUEST_TIMEOUT,
                content={"error": "Request timeout"},
            )


def setup_middleware(app, config):
    """Setup all middleware for the FastAPI application"""

    # Request timeout
    app.add_middleware(TimeoutMiddleware, timeout_seconds=config.api.request_timeout)

    # Request logging
    app.add_middleware(RequestLoggingMiddleware)

    # Authentication and rate limiting
    app.add_middleware(AuthenticationMiddleware, config=config)

    logger.info("Middleware configured successfully")
    logger.info(
        f"Rate limiting: {config.security.rate_limit_requests} req/{config.security.rate_limit_window}s"
    )
    logger.info(
        f"Authentication: {'Enabled' if config.security.api_key_required else 'Disabled'}"
    )
    logger.info(f"Request timeout: {config.api.request_timeout}s")
