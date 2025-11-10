"""
Echoes AI Exceptions

This module provides custom exception classes for the Echoes AI Multi-Agent System.
"""

import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class EchoesException(Exception):
    """Base exception for Echoes AI."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ConfigurationError(EchoesException):
    """Configuration related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message, error_code="CONFIG_ERROR", status_code=500, details=details
        )


class ValidationError(EchoesException):
    """Validation related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class AuthenticationError(EchoesException):
    """Authentication related errors."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message, error_code="AUTH_ERROR", status_code=401, details=details
        )


class AuthorizationError(EchoesException):
    """Authorization related errors."""

    def __init__(
        self, message: str = "Access denied", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details,
        )


class NotFoundError(EchoesException):
    """Resource not found errors."""

    def __init__(
        self, message: str = "Resource not found", details: dict[str, Any] | None = None
    ):
        super().__init__(
            message=message, error_code="NOT_FOUND", status_code=404, details=details
        )


class RateLimitError(EchoesException):
    """Rate limiting errors."""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details,
        )


class AIServiceError(EchoesException):
    """AI service related errors."""

    def __init__(
        self,
        message: str,
        service: str = "unknown",
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        details["service"] = service
        super().__init__(
            message=message,
            error_code="AI_SERVICE_ERROR",
            status_code=502,
            details=details,
        )


class DatabaseError(EchoesException):
    """Database related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            status_code=500,
            details=details,
        )


class WorkflowError(EchoesException):
    """Workflow related errors."""

    def __init__(
        self,
        message: str,
        workflow_id: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        if workflow_id:
            details["workflow_id"] = workflow_id
        super().__init__(
            message=message,
            error_code="WORKFLOW_ERROR",
            status_code=500,
            details=details,
        )


class AgentError(EchoesException):
    """Agent related errors."""

    def __init__(
        self,
        message: str,
        agent_id: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        details = details or {}
        if agent_id:
            details["agent_id"] = agent_id
        super().__init__(
            message=message, error_code="AGENT_ERROR", status_code=500, details=details
        )


class MediaError(EchoesException):
    """Media processing related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message, error_code="MEDIA_ERROR", status_code=500, details=details
        )


# Exception handlers
async def echoes_exception_handler(request: Request, exc: EchoesException):
    """Handle Echoes AI exceptions."""
    logger.error(f"EchoesException: {exc.message}", extra={"details": exc.details})

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "type": exc.__class__.__name__,
            }
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions."""
    logger.warning(f"HTTPException: {exc.status_code} - {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": str(exc.detail),
                "type": "HTTPException",
            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation exceptions."""
    logger.warning(f"ValidationException: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": {"errors": exc.errors()},
                "type": "RequestValidationError",
            }
        },
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal error occurred",
                "type": "InternalServerError",
            }
        },
    )


def setup_exception_handlers(app):
    """Set up exception handlers for the FastAPI application."""
    app.add_exception_handler(EchoesException, echoes_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)


# Error response utilities
def create_error_response(
    message: str,
    error_code: str | None = None,
    status_code: int = 500,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standardized error response."""
    return {
        "error": {
            "code": error_code or "UNKNOWN_ERROR",
            "message": message,
            "details": details or {},
            "type": "Error",
        }
    }


def create_success_response(
    data: Any, message: str = "Success", details: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Create a standardized success response."""
    return {"success": True, "message": message, "data": data, "details": details or {}}
