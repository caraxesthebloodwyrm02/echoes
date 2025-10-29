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

# MIT License
# Copyright (c) 2025 Echoes Project

"""
Security - Encryption, credential management, authentication
"""

import getpass
import logging
from typing import Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

try:
    import keyring

    KEYRING_AVAILABLE = True
except ImportError:
    KEYRING_AVAILABLE = False

logger = logging.getLogger(__name__)


class Encryption:
    """
    Data encryption using cryptography
    Fernet symmetric encryption with key derivation
    """

    def __init__(self, password: Optional[str] = None):
        self.logger = logging.getLogger(__name__)

        if password:
            self.key = self._derive_key(password)
        else:
            # Generate random key
            self.key = Fernet.generate_key()

        self.cipher = Fernet(self.key)

    @staticmethod
    def _derive_key(password: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password"""
        if salt is None:
            salt = b"system_orchestrator_salt"  # In production, use random salt

        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return kdf.derive(password.encode())

    def encrypt(self, data: str) -> bytes:
        """Encrypt string data"""
        try:
            return self.cipher.encrypt(data.encode())
        except Exception as e:
            self.logger.error(f"Encryption failed: {e}")
            raise

    def decrypt(self, encrypted_data: bytes) -> str:
        """Decrypt data to string"""
        try:
            return self.cipher.decrypt(encrypted_data).decode()
        except Exception as e:
            self.logger.error(f"Decryption failed: {e}")
            raise

    def encrypt_file(self, file_path: str, output_path: Optional[str] = None):
        """Encrypt a file"""
        try:
            with open(file_path, "rb") as f:
                data = f.read()

            encrypted = self.cipher.encrypt(data)

            output = output_path or f"{file_path}.encrypted"
            with open(output, "wb") as f:
                f.write(encrypted)

            self.logger.info(f"File encrypted: {output}")
        except Exception as e:
            self.logger.error(f"File encryption failed: {e}")
            raise

    def decrypt_file(self, encrypted_path: str, output_path: Optional[str] = None):
        """Decrypt a file"""
        try:
            with open(encrypted_path, "rb") as f:
                encrypted_data = f.read()

            decrypted = self.cipher.decrypt(encrypted_data)

            output = output_path or encrypted_path.replace(".encrypted", "")
            with open(output, "wb") as f:
                f.write(decrypted)

            self.logger.info(f"File decrypted: {output}")
        except Exception as e:
            self.logger.error(f"File decryption failed: {e}")
            raise


class CredentialManager:
    """
    Secure credential storage
    Uses keyring (Windows Credential Manager) or fallback to encrypted file
    """

    def __init__(self, use_system_keyring: bool = True):
        self.logger = logging.getLogger(__name__)
        self.use_system_keyring = use_system_keyring and KEYRING_AVAILABLE

        if not self.use_system_keyring:
            self.logger.warning("Keyring not available, using encrypted file storage")
            self.encryption = Encryption()
            self._credentials = {}

    def store(self, service: str, username: str, password: str):
        """Store credential"""
        if self.use_system_keyring:
            try:
                keyring.set_password(service, username, password)
                self.logger.info(f"Credential stored in keyring: {service}")
            except Exception as e:
                self.logger.error(f"Failed to store credential: {e}")
        else:
            # Fallback: encrypted storage
            key = f"{service}:{username}"
            self._credentials[key] = self.encryption.encrypt(password)
            self.logger.info(f"Credential stored (encrypted): {service}")

    def retrieve(self, service: str, username: str) -> Optional[str]:
        """Retrieve credential"""
        if self.use_system_keyring:
            try:
                password = keyring.get_password(service, username)
                if password:
                    self.logger.debug(f"Credential retrieved from keyring: {service}")
                return password
            except Exception as e:
                self.logger.error(f"Failed to retrieve credential: {e}")
                return None
        else:
            # Fallback: decrypt from storage
            key = f"{service}:{username}"
            if key in self._credentials:
                password = self.encryption.decrypt(self._credentials[key])
                self.logger.debug(f"Credential retrieved (decrypted): {service}")
                return password
            return None

    def delete(self, service: str, username: str):
        """Delete credential"""
        if self.use_system_keyring:
            try:
                keyring.delete_password(service, username)
                self.logger.info(f"Credential deleted from keyring: {service}")
            except Exception as e:
                self.logger.error(f"Failed to delete credential: {e}")
        else:
            key = f"{service}:{username}"
            if key in self._credentials:
                del self._credentials[key]
                self.logger.info(f"Credential deleted (encrypted): {service}")


class InteractiveAuth:
    """Interactive authentication with getpass"""

    @staticmethod
    def prompt_password(prompt: str = "Enter password: ") -> str:
        """Securely prompt for password"""
        return getpass.getpass(prompt)

    @staticmethod
    def prompt_username(prompt: str = "Enter username: ") -> str:
        """Prompt for username"""
        return input(prompt)

    @staticmethod
    def authenticate(service: str, credential_manager: CredentialManager) -> bool:
        """Interactive authentication flow"""
        username = InteractiveAuth.prompt_username()
        password = InteractiveAuth.prompt_password()

        # Store for future use
        credential_manager.store(service, username, password)

        return True


__all__ = ["Encryption", "CredentialManager", "InteractiveAuth"]
