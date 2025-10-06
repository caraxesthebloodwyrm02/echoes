"""
Authentication Module for AI Advisor

Implements JWT-based authentication with:
- User login/logout
- Token generation and validation
- Password hashing
- Role-based access control
"""

import hashlib
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Security configuration
# Prefer environment variable for stable tokens across processes
SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()


class User(BaseModel):
    username: str
    email: str
    role: str = "user"
    disabled: bool = False


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# In-memory user store (replace with database in production)
users_db: Dict[str, Dict[str, Any]] = {
    "admin": {
        "username": "admin",
        "email": "admin@ai-advisor.com",
        "hashed_password": hashlib.sha256("admin123".encode()).hexdigest(),  # DEMO ONLY
        "role": "admin",
        "disabled": False,
    },
    "user": {
        "username": "user",
        "email": "user@ai-advisor.com",
        "hashed_password": hashlib.sha256("user123".encode()).hexdigest(),  # DEMO ONLY
        "role": "user",
        "disabled": False,
    },
}


def hash_password(password: str) -> str:
    """Hash password using SHA-256 (use bcrypt/argon2 in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(plain_password) == hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create access token (simple demo, not real JWT).

    Uses '|' as delimiter and epoch seconds for expiration to avoid parsing issues.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    exp_epoch = int(expire.timestamp())

    # Simple token generation (use PyJWT in production)
    token = f"{to_encode['sub']}|{to_encode['role']}|{exp_epoch}|{SECRET_KEY[:16]}"
    return token


def decode_token(token: str) -> TokenData:
    """Decode and validate demo token"""
    try:
        parts = token.split("|")
        if len(parts) != 4:
            raise ValueError("Invalid token format")

        username, role, exp_epoch_str, key_part = parts

        # Validate key part
        if key_part != SECRET_KEY[:16]:
            raise ValueError("Invalid token signature")

        # Check expiration
        exp_epoch = int(exp_epoch_str)
        if exp_epoch < int(datetime.utcnow().timestamp()):
            raise ValueError("Token expired")

        return TokenData(username=username, role=role)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current authenticated user from token"""
    token = credentials.credentials
    token_data = decode_token(token)

    if token_data.username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_dict = users_db.get(token_data.username)
    if user_dict is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return User(**user_dict)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Verify user is active"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(required_role: str):
    """Dependency to require specific role"""

    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required role: {required_role}",
            )
        return current_user

    return role_checker


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate user with username and password"""
    user_dict = users_db.get(username)
    if not user_dict:
        return None
    if not verify_password(password, user_dict["hashed_password"]):
        return None
    return User(**user_dict)
