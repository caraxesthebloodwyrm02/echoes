"""Custom exceptions for echoe-workspace."""


class EchoeBaseException(Exception):
    """Base exception for all echoe workspace errors."""


class ConfigurationError(EchoeBaseException):
    """Raised when configuration is invalid or missing."""


class ValidationError(EchoeBaseException):
    """Raised when data validation fails."""


class SecurityError(EchoeBaseException):
    """Raised when security checks fail."""


class ResourceNotFoundError(EchoeBaseException):
    """Raised when a required resource is not found."""


__all__ = [
    "EchoeBaseException",
    "ConfigurationError",
    "ValidationError",
    "SecurityError",
    "ResourceNotFoundError",
]
