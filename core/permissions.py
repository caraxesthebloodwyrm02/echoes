"""
Role-Based Access Control (RBAC)
Defines roles and permission decorators
"""

from enum import Enum
from functools import wraps
from typing import List, Callable
from fastapi import HTTPException, status


class Roles(str, Enum):
    """User roles with hierarchical permissions"""

    ADMIN = "admin"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    ANALYST = "analyst"


# Role hierarchy (higher roles inherit lower role permissions)
ROLE_HIERARCHY = {
    Roles.ADMIN: [Roles.ADMIN, Roles.RESEARCHER, Roles.DEVELOPER, Roles.ANALYST],
    Roles.RESEARCHER: [Roles.RESEARCHER, Roles.ANALYST],
    Roles.DEVELOPER: [Roles.DEVELOPER, Roles.ANALYST],
    Roles.ANALYST: [Roles.ANALYST],
}


# Platform access by role
PLATFORM_ACCESS = {
    Roles.ADMIN: ["echoes", "turbo", "glimpse"],
    Roles.RESEARCHER: ["glimpse", "turbo"],  # read-only turbo
    Roles.DEVELOPER: ["echoes", "glimpse"],  # read-only glimpse
    Roles.ANALYST: ["echoes", "turbo", "glimpse"],  # read-only all
}


def has_permission(user_role: str, required_role: str) -> bool:
    """
    Check if user role has required permission

    Args:
        user_role: User's role
        required_role: Required role for operation

    Returns:
        True if user has permission
    """
    try:
        user_role_enum = Roles(user_role)
        required_role_enum = Roles(required_role)
        return required_role_enum in ROLE_HIERARCHY.get(user_role_enum, [])
    except ValueError:
        return False


def can_access_platform(user_role: str, platform: str) -> bool:
    """
    Check if user can access a platform

    Args:
        user_role: User's role
        platform: Platform name (echoes, turbo, glimpse)

    Returns:
        True if user can access platform
    """
    try:
        user_role_enum = Roles(user_role)
        return platform in PLATFORM_ACCESS.get(user_role_enum, [])
    except ValueError:
        return False


def require_role(required_roles: List[str]):
    """
    Decorator to require specific roles for endpoint access

    Args:
        required_roles: List of roles that can access the endpoint

    Example:
        @require_role([Roles.ADMIN, Roles.RESEARCHER])
        async def sensitive_endpoint():
            pass
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user from request context
            # This would typically come from JWT token or API key validation
            user_role = kwargs.get("user_role") or kwargs.get("current_user", {}).get("role")

            if not user_role:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

            # Check if user has any of the required roles
            has_access = any(has_permission(user_role, required_role) for required_role in required_roles)

            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required roles: {required_roles}",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def require_platform_access(platform: str):
    """
    Decorator to require access to a specific platform

    Args:
        platform: Platform name (echoes, turbo, glimpse)

    Example:
        @require_platform_access("glimpse")
        async def glimpse_endpoint():
            pass
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_role = kwargs.get("user_role") or kwargs.get("current_user", {}).get("role")

            if not user_role:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

            if not can_access_platform(user_role, platform):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail=f"Access to platform '{platform}' denied"
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator
