"""
Authentication Routes

Endpoints for user authentication:
- Login
- Logout
- Token refresh
- User profile
"""

from datetime import timedelta

from core.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    LoginRequest,
    TokenResponse,
    User,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse, tags=["Authentication"])
async def login(login_data: LoginRequest):
    """
    Authenticate user and return JWT access token.

    **Demo Credentials:**
    - Username: `admin`, Password: `admin123` (admin role)
    - Username: `user`, Password: `user123` (user role)

    **Security Note:** This is a demo implementation. In production:
    - Use bcrypt/argon2 for password hashing
    - Store users in a database
    - Implement rate limiting
    - Add account lockout after failed attempts
    - Use environment variables for secrets
    """
    user = authenticate_user(login_data.username, login_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )

    return TokenResponse(access_token=access_token, expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60)


@router.post("/auth/logout", tags=["Authentication"])
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout current user.

    In production, implement:
    - Token blacklisting
    - Session revocation
    - Audit logging
    """
    return {"message": f"User {current_user.username} logged out successfully", "status": "ok"}


@router.get("/auth/me", response_model=User, tags=["Authentication"])
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current authenticated user profile.

    Requires valid JWT token in Authorization header:
    `Authorization: Bearer <token>`
    """
    return current_user


@router.get("/auth/verify", tags=["Authentication"])
async def verify_token(current_user: User = Depends(get_current_active_user)):
    """
    Verify if the provided token is valid.

    Returns user information if token is valid.
    """
    return {"valid": True, "username": current_user.username, "role": current_user.role}
