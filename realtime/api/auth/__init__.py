"""
Authentication and Authorization Module
Provides JWT-based authentication for the unified API
"""

from .jwt_handler import JWTHandler, create_access_token, verify_token
from .api_keys import APIKeyManager
from .permissions import require_role, Roles

__all__ = [
    'JWTHandler',
    'create_access_token',
    'verify_token',
    'APIKeyManager',
    'require_role',
    'Roles'
]
