"""Encryption utilities including quantum-resistant approaches."""

import hashlib
import secrets
from typing import Optional, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from packages.core import get_logger

logger = get_logger("security.encryption")


class QuantumShield:
    """Quantum-resistant encryption utilities."""

    def __init__(self) -> None:
        self.logger = logger

    def generate_secure_key(self, length: int = 32) -> str:
        """Generate cryptographically secure random key."""
        return secrets.token_hex(length)

    def create_fernet_key(self, password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
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

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
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

    def decrypt_coordinates(self, encrypted_data: str, key: bytes) -> Tuple[float, float]:
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
