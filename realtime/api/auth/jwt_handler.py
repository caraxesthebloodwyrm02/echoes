"""
JWT Token Handler
Manages JWT token generation, validation, and refresh
"""

import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import jwt
from jwt.exceptions import InvalidTokenError


class JWTHandler:
    """Handle JWT token operations"""
    
    def __init__(self, secret_key: Optional[str] = None, algorithm: str = "HS256"):
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = algorithm
        self.access_token_expire_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    def create_access_token(
        self, 
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token
        
        Args:
            data: Payload data to encode
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """
        Create a JWT refresh token
        
        Args:
            data: Payload data to encode
            
        Returns:
            Encoded JWT refresh token string
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except InvalidTokenError as e:
            raise InvalidTokenError(f"Token validation failed: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Generate a new access token from a refresh token
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            New access token
            
        Raises:
            InvalidTokenError: If refresh token is invalid
        """
        payload = self.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise InvalidTokenError("Invalid token type")
        
        # Create new access token with user data
        user_data = {
            "sub": payload.get("sub"),
            "role": payload.get("role"),
            "platforms": payload.get("platforms", [])
        }
        
        return self.create_access_token(user_data)


# Convenience functions
_jwt_handler = JWTHandler()


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create an access token (convenience function)"""
    return _jwt_handler.create_access_token(data, expires_delta)


def create_refresh_token(data: Dict[str, Any]) -> str:
    """Create a refresh token (convenience function)"""
    return _jwt_handler.create_refresh_token(data)


def verify_token(token: str) -> Dict[str, Any]:
    """Verify a token (convenience function)"""
    return _jwt_handler.verify_token(token)


def refresh_access_token(refresh_token: str) -> str:
    """Refresh an access token (convenience function)"""
    return _jwt_handler.refresh_access_token(refresh_token)
