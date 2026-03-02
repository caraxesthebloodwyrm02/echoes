"""
API Key Management
Handles API key generation, validation, and storage
"""

import hashlib
import json
import secrets
import stat
from pathlib import Path

from src.utils.datetime_utils import utc_now


class APIKeyManager:
    """Manage API keys for authentication"""

    def __init__(self, storage_path: str = "api_keys.json"):
        self.storage_path = Path(storage_path)
        self.keys: dict[str, dict] = self._load_keys()

    def _load_keys(self) -> dict[str, dict]:
        """Load API keys from storage - handle empty files gracefully"""
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
                    content = f.read().strip()
                    if content:
                        return json.loads(content)
            except (OSError, json.JSONDecodeError):
                pass  # Return empty dict on error
        return {}

    def _save_keys(self):
        """Save API keys to storage with restricted file permissions"""
        with open(self.storage_path, "w") as f:
            json.dump(self.keys, f, indent=2)
        self.storage_path.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def _hash_key(self, key: str) -> str:
        """Hash an API key for secure storage"""
        return hashlib.sha256(key.encode()).hexdigest()

    def generate_key(
        self, name: str, role: str = "analyst", platforms: list[str] | None = None
    ) -> str:
        """
        Generate a new API key

        Args:
            name: Descriptive name for the key
            role: User role (admin, researcher, developer, analyst)
            platforms: List of accessible platforms

        Returns:
            Generated API key (store this securely!)
        """
        # Generate a secure random key
        api_key = f"gp_{secrets.token_urlsafe(32)}"
        key_hash = self._hash_key(api_key)

        # Store key metadata
        self.keys[key_hash] = {
            "name": name,
            "role": role,
            "platforms": platforms or ["echoes", "turbo", "glimpse"],
            "created_at": utc_now().isoformat(),
            "last_used": None,
            "active": True,
        }

        self._save_keys()
        return api_key

    def validate_key(self, api_key: str) -> dict | None:
        """
        Validate an API key

        Args:
            api_key: API key to validate

        Returns:
            Key metadata if valid, None otherwise
        """
        key_hash = self._hash_key(api_key)

        if key_hash not in self.keys:
            return None

        key_data = self.keys[key_hash]

        if not key_data.get("active", True):
            return None

        # Update last used timestamp
        key_data["last_used"] = utc_now().isoformat()
        self._save_keys()

        return key_data

    def revoke_key(self, api_key: str) -> bool:
        """
        Revoke an API key

        Args:
            api_key: API key to revoke

        Returns:
            True if revoked, False if not found
        """
        key_hash = self._hash_key(api_key)

        if key_hash in self.keys:
            self.keys[key_hash]["active"] = False
            self._save_keys()
            return True

        return False

    def list_keys(self) -> list[dict]:
        """
        List all API keys (without revealing the actual keys)

        Returns:
            List of key metadata
        """
        return [
            {
                "name": data["name"],
                "role": data["role"],
                "platforms": data["platforms"],
                "created_at": data["created_at"],
                "last_used": data["last_used"],
                "active": data["active"],
            }
            for data in self.keys.values()
        ]
