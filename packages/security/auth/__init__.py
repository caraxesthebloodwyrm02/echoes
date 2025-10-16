# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Authentication and authorization utilities."""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import jwt
from cryptography.fernet import Fernet

from packages.core import get_logger

logger = get_logger("security.auth")


class AuthManager:
    def __init__(self, secret_key: Optional[str] = None) -> None:
        self.logger = logger
        self.secret_key = secret_key or "dev-secret-key-change-in-production"
        self.cipher_suite = Fernet(Fernet.generate_key())

    def generate_token(
        self, user_id: str, permissions: List[str], expires_in: int = 3600
    ) -> str:
        """
        Generate JWT token for user.

        Args:
            user_id: User identifier
            permissions: List of user permissions
            expires_in: Token expiration time in seconds

        Returns:
            JWT token string
        """
        payload = {
            "user_id": user_id,
            "permissions": permissions,
            "exp": datetime.utcnow() + timedelta(seconds=expires_in),
            "iat": datetime.utcnow(),
        }

        token = jwt.encode(payload, self.secret_key, algorithm="HS256")
        self.logger.info(f"Generated token for user: {user_id}")

        return token

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token.

        Args:
            token: JWT token to verify

        Returns:
            Token payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token")

        return None

    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        encrypted = self.cipher_suite.encrypt(data.encode())
        return encrypted.decode()

    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        decrypted = self.cipher_suite.decrypt(encrypted_data.encode())
        return decrypted.decode()


__all__ = ["AuthManager"]
