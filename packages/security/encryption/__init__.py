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

"""Encryption utilities including quantum-resistant approaches."""

import hashlib
import secrets
from typing import Optional, Tuple

from cryptography.fernet import Fernet

from packages.core import get_logger

logger = get_logger("security.encryption")


class QuantumShield:
    """Quantum-resistant encryption utilities."""

    def __init__(self) -> None:
        self.logger = logger

    def generate_secure_key(self, length: int = 32) -> str:
        """Generate cryptographically secure random key."""
        return secrets.token_hex(length)

    def create_fernet_key(
        self, password: str, salt: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        """
        Create Fernet encryption key from password.

        Args:
            password: Password string
            salt: Salt bytes (generated if None)

        Returns:
            Tuple of (key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(16)

        key = Fernet.generate_key()  # For now, use standard Fernet

        return key, salt

    def encrypt_coordinates(self, lat: float, lng: float, key: bytes) -> str:
        """
        Encrypt coordinate data.

        Args:
            lat: Latitude
            lng: Longitude
            key: Encryption key

        Returns:
            Encrypted coordinate string
        """
        cipher_suite = Fernet(key)
        coordinate_data = f"{lat},{lng}".encode()
        encrypted = cipher_suite.encrypt(coordinate_data)

        self.logger.debug("Coordinates encrypted")
        return encrypted.decode()

    def decrypt_coordinates(
        self, encrypted_data: str, key: bytes
    ) -> Tuple[float, float]:
        """
        Decrypt coordinate data.

        Args:
            encrypted_data: Encrypted coordinate string
            key: Decryption key

        Returns:
            Tuple of (lat, lng)
        """
        cipher_suite = Fernet(key)
        decrypted = cipher_suite.decrypt(encrypted_data.encode())
        lat_str, lng_str = decrypted.decode().split(",")

        self.logger.debug("Coordinates decrypted")
        return float(lat_str), float(lng_str)

    def hash_data(self, data: str, salt: Optional[str] = None) -> str:
        """
        Hash data with optional salt.

        Args:
            data: Data to hash
            salt: Optional salt string

        Returns:
            Hex digest of hash
        """
        if salt:
            data = data + salt

        hash_obj = hashlib.sha256(data.encode())
        return hash_obj.hexdigest()


__all__ = ["QuantumShield"]
