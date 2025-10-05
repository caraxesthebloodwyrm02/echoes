"""Custom exceptions for echoe-workspace."""


class EchoeBaseException(Exception):
    """Base exception for all echoe workspace errors."""

    pass


class ConfigurationError(EchoeBaseException):
    """Raised when configuration is invalid or missing."""

    pass


class ValidationError(EchoeBaseException):
    """Raised when data validation fails."""

    pass


class SecurityError(EchoeBaseException):
    """Raised when security checks fail."""

    pass


class ResourceNotFoundError(EchoeBaseException):
    """Raised when a required resource is not found."""

    pass


__all__ = [
    "EchoeBaseException",
    "ConfigurationError",
    "ValidationError",
    "SecurityError",
    "ResourceNotFoundError",
]
