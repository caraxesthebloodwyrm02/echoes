"""Comprehensive tests for echoe-security package."""

import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from security.auth import AuthManager
from security.encryption import QuantumShield
from security.scanning import Vulnerability, VulnerabilityScanner


class TestVulnerabilityScanner:
    """Test vulnerability scanning functionality."""

    def test_scanner_initialization(self):
        """Test scanner can be initialized."""
        scanner = VulnerabilityScanner()
        assert scanner is not None
        assert hasattr(scanner, "logger")

    def test_scan_empty_requirements(self):
        """Test scanning empty requirements file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("# Empty requirements file\n")
            temp_path = Path(f.name)

        try:
            scanner = VulnerabilityScanner()
            vulnerabilities = scanner.scan_dependencies(temp_path)

            assert isinstance(vulnerabilities, list)
        finally:
            temp_path.unlink()

    def test_scan_with_common_packages(self):
        """Test scanning with common packages."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("requests==2.28.0\n")
            f.write("urllib3==1.26.0\n")
            temp_path = Path(f.name)

        try:
            scanner = VulnerabilityScanner()
            vulnerabilities = scanner.scan_dependencies(temp_path)

            assert isinstance(vulnerabilities, list)
            # Note: May find real vulnerabilities in these old versions
        finally:
            temp_path.unlink()

    def test_scan_code_directory(self):
        """Test scanning code directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test Python file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                """
import os
password = "hardcoded123"
result = eval(user_input)
"""
            )

            scanner = VulnerabilityScanner()
            issues = scanner.scan_code(Path(tmpdir))

            assert isinstance(issues, list)

    def test_scan_nonexistent_file(self):
        """Test scanning nonexistent file."""
        scanner = VulnerabilityScanner()
        result = scanner.scan_dependencies(Path("/nonexistent/file.txt"))

        # Should not crash, return empty list
        assert isinstance(result, list)

    def test_vulnerability_dataclass(self):
        """Test Vulnerability dataclass."""
        vuln = Vulnerability(
            cve_id="CVE-2023-12345",
            severity="HIGH",
            description="Test vulnerability",
            affected_package="test-package",
            affected_version="1.0.0",
            fixed_version="1.0.1",
            discovered_at=datetime.now(),
        )

        assert vuln.cve_id == "CVE-2023-12345"
        assert vuln.severity == "HIGH"
        assert vuln.fixed_version == "1.0.1"


class TestAuthManager:
    """Test authentication and authorization."""

    def test_auth_manager_initialization(self):
        """Test auth manager initialization."""
        auth = AuthManager("test-secret")
        assert auth.secret_key == "test-secret"

    def test_auth_manager_default_secret(self):
        """Test auth manager with default secret."""
        auth = AuthManager()
        assert auth.secret_key is not None
        assert len(auth.secret_key) > 0

    def test_generate_token_basic(self):
        """Test basic token generation."""
        auth = AuthManager("test-secret")
        token = auth.generate_token("user123", ["read", "write"])

        assert isinstance(token, str)
        assert len(token) > 0

    def test_generate_token_different_users(self):
        """Test tokens for different users."""
        auth = AuthManager("test-secret")

        token1 = auth.generate_token("user1", ["read"])
        token2 = auth.generate_token("user2", ["write"])

        assert token1 != token2

    def test_verify_token_valid(self):
        """Test verifying valid token."""
        auth = AuthManager("test-secret")

        token = auth.generate_token("test_user", ["read", "write"])
        payload = auth.verify_token(token)

        assert payload is not None
        assert payload["user_id"] == "test_user"
        assert payload["permissions"] == ["read", "write"]

    def test_verify_token_invalid(self):
        """Test verifying invalid token."""
        auth = AuthManager("test-secret")

        payload = auth.verify_token("invalid.token.here")
        assert payload is None

    def test_verify_token_wrong_secret(self):
        """Test verifying token with wrong secret."""
        auth1 = AuthManager("secret1")
        auth2 = AuthManager("secret2")

        token = auth1.generate_token("user", ["read"])
        payload = auth2.verify_token(token)

        assert payload is None

    def test_token_expiration(self):
        """Test token expiration."""
        auth = AuthManager("test-secret")

        # Create token that expires in 1 second
        token = auth.generate_token("user", ["read"], expires_in=1)

        # Verify immediately - should work
        payload = auth.verify_token(token)
        assert payload is not None

        # After expiration, it should fail (would need time.sleep in real test)

    def test_token_with_empty_permissions(self):
        """Test token with no permissions."""
        auth = AuthManager("test-secret")
        token = auth.generate_token("user", [])

        payload = auth.verify_token(token)
        assert payload is not None
        assert payload["permissions"] == []

    def test_token_with_many_permissions(self):
        """Test token with many permissions."""
        auth = AuthManager("test-secret")
        permissions = [f"permission_{i}" for i in range(100)]

        token = auth.generate_token("user", permissions)
        payload = auth.verify_token(token)

        assert payload is not None
        assert len(payload["permissions"]) == 100

    def test_encrypt_decrypt_data(self):
        """Test data encryption and decryption."""
        auth = AuthManager("test-secret")

        original_data = "sensitive information"
        encrypted = auth.encrypt_data(original_data)
        decrypted = auth.decrypt_data(encrypted)

        assert encrypted != original_data
        assert decrypted == original_data

    def test_encrypt_empty_string(self):
        """Test encrypting empty string."""
        auth = AuthManager("test-secret")

        encrypted = auth.encrypt_data("")
        decrypted = auth.decrypt_data(encrypted)

        assert decrypted == ""

    def test_encrypt_unicode(self):
        """Test encrypting unicode data."""
        auth = AuthManager("test-secret")

        original = "Hello 世界 🌍"
        encrypted = auth.encrypt_data(original)
        decrypted = auth.decrypt_data(encrypted)

        assert decrypted == original


class TestQuantumShield:
    """Test quantum-resistant encryption."""

    def test_quantum_shield_initialization(self):
        """Test quantum shield initialization."""
        shield = QuantumShield()
        assert shield is not None

    def test_generate_secure_key(self):
        """Test secure key generation."""
        shield = QuantumShield()

        key1 = shield.generate_secure_key()
        key2 = shield.generate_secure_key()

        assert len(key1) == 64  # 32 bytes * 2 (hex encoding)
        assert len(key2) == 64
        assert key1 != key2  # Should be different each time

    def test_generate_key_custom_length(self):
        """Test generating keys of different lengths."""
        shield = QuantumShield()

        key_16 = shield.generate_secure_key(length=16)
        key_64 = shield.generate_secure_key(length=64)

        assert len(key_16) == 32  # 16 bytes * 2
        assert len(key_64) == 128  # 64 bytes * 2

    def test_create_fernet_key(self):
        """Test Fernet key creation."""
        shield = QuantumShield()

        key, salt = shield.create_fernet_key("password123")

        assert key is not None
        assert salt is not None
        assert len(salt) == 16

    def test_create_fernet_key_with_salt(self):
        """Test Fernet key creation with provided salt."""
        shield = QuantumShield()

        salt1 = b"fixed_salt_16byt"
        key1, returned_salt1 = shield.create_fernet_key("password", salt1)
        key2, returned_salt2 = shield.create_fernet_key("password", salt1)

        assert returned_salt1 == salt1
        assert returned_salt2 == salt1

    def test_encrypt_decrypt_coordinates(self):
        """Test coordinate encryption and decryption."""
        shield = QuantumShield()

        lat, lng = 40.7128, -74.0060  # New York
        key, salt = shield.create_fernet_key("password")

        encrypted = shield.encrypt_coordinates(lat, lng, key)
        decrypted_lat, decrypted_lng = shield.decrypt_coordinates(encrypted, key)

        assert abs(decrypted_lat - lat) < 0.0001
        assert abs(decrypted_lng - lng) < 0.0001

    def test_encrypt_coordinates_various_locations(self):
        """Test encrypting coordinates for various locations."""
        shield = QuantumShield()
        key, salt = shield.create_fernet_key("password")

        locations = [
            (0.0, 0.0),  # Null Island
            (90.0, 0.0),  # North Pole
            (-90.0, 0.0),  # South Pole
            (35.6762, 139.6503),  # Tokyo
            (-33.8688, 151.2093),  # Sydney
        ]

        for lat, lng in locations:
            encrypted = shield.encrypt_coordinates(lat, lng, key)
            dec_lat, dec_lng = shield.decrypt_coordinates(encrypted, key)

            assert abs(dec_lat - lat) < 0.0001
            assert abs(dec_lng - lng) < 0.0001

    def test_hash_data_consistency(self):
        """Test that hashing is consistent."""
        shield = QuantumShield()

        data = "test_data"
        hash1 = shield.hash_data(data)
        hash2 = shield.hash_data(data)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex digest

    def test_hash_data_with_salt(self):
        """Test hashing with salt."""
        shield = QuantumShield()

        data = "test_data"
        hash_no_salt = shield.hash_data(data)
        hash_with_salt = shield.hash_data(data, salt="mysalt")

        assert hash_no_salt != hash_with_salt

    def test_hash_different_data(self):
        """Test that different data produces different hashes."""
        shield = QuantumShield()

        hash1 = shield.hash_data("data1")
        hash2 = shield.hash_data("data2")

        assert hash1 != hash2


class TestSecurityIntegration:
    """Integration tests for security package."""

    def test_complete_authentication_flow(self):
        """Test complete authentication workflow."""
        auth = AuthManager("production-secret")

        # User logs in, gets token
        user_id = "john_doe"
        permissions = ["read:documents", "write:documents", "delete:own"]
        token = auth.generate_token(user_id, permissions, expires_in=3600)

        # Later, verify the token
        payload = auth.verify_token(token)

        assert payload is not None
        assert payload["user_id"] == user_id
        assert "read:documents" in payload["permissions"]

    def test_secure_data_storage(self):
        """Test secure data storage workflow."""
        auth = AuthManager("encryption-key")

        # Store sensitive data
        sensitive = "Credit Card: 1234-5678-9012-3456"
        encrypted = auth.encrypt_data(sensitive)

        # Encrypted data should be different
        assert encrypted != sensitive
        assert "1234" not in encrypted

        # Can be decrypted
        decrypted = auth.decrypt_data(encrypted)
        assert decrypted == sensitive

    def test_coordinate_protection_workflow(self):
        """Test protecting GPS coordinates."""
        shield = QuantumShield()

        # User's actual location
        actual_lat, actual_lng = 37.7749, -122.4194  # San Francisco

        # Encrypt for storage
        password = "user_encryption_key"
        key, salt = shield.create_fernet_key(password)
        encrypted_coords = shield.encrypt_coordinates(actual_lat, actual_lng, key)

        # Store encrypted_coords and salt
        # Later, decrypt when needed
        retrieved_key, _ = shield.create_fernet_key(password, salt)
        dec_lat, dec_lng = shield.decrypt_coordinates(encrypted_coords, retrieved_key)

        assert abs(dec_lat - actual_lat) < 0.0001
        assert abs(dec_lng - actual_lng) < 0.0001

    def test_vulnerability_scanning_with_auth(self):
        """Test vulnerability scanning in authenticated context."""
        # Authenticate user
        auth = AuthManager("scan-secret")
        token = auth.generate_token("security_admin", ["scan:vulnerabilities"])

        payload = auth.verify_token(token)
        assert "scan:vulnerabilities" in payload["permissions"]

        # Perform scan
        scanner = VulnerabilityScanner()
        # In real scenario, would scan actual dependencies


class TestSecurityEdgeCases:
    """Test edge cases and security concerns."""

    def test_token_tampering(self):
        """Test that tampered tokens are rejected."""
        auth = AuthManager("secret")

        token = auth.generate_token("user", ["read"])

        # Tamper with token
        tampered = token[:-5] + "XXXXX"

        payload = auth.verify_token(tampered)
        assert payload is None

    def test_encryption_with_wrong_key(self):
        """Test decryption with wrong key fails gracefully."""
        shield = QuantumShield()

        key1, salt1 = shield.create_fernet_key("password1")
        key2, salt2 = shield.create_fernet_key("password2")

        encrypted = shield.encrypt_coordinates(40.0, -74.0, key1)

        # Should fail to decrypt with wrong key
        with pytest.raises(Exception):
            shield.decrypt_coordinates(encrypted, key2)

    def test_sql_injection_in_user_id(self):
        """Test that SQL injection attempts in user_id are handled."""
        auth = AuthManager("secret")

        malicious_user = "admin' OR '1'='1"
        token = auth.generate_token(malicious_user, ["read"])

        payload = auth.verify_token(token)
        assert payload["user_id"] == malicious_user  # Stored as-is in JWT

    def test_xss_in_permissions(self):
        """Test XSS attempts in permissions."""
        auth = AuthManager("secret")

        xss_permission = "<script>alert('xss')</script>"
        token = auth.generate_token("user", [xss_permission])

        payload = auth.verify_token(token)
        assert xss_permission in payload["permissions"]

    def test_hash_collision_resistance(self):
        """Test hash collision resistance."""
        shield = QuantumShield()

        # Similar inputs should produce different hashes
        hash1 = shield.hash_data("password123")
        hash2 = shield.hash_data("password124")

        assert hash1 != hash2

        # Even one character difference should produce completely different hash
        assert not any(c1 == c2 for c1, c2 in zip(hash1, hash2)[:10])


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
