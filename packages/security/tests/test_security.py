"""Tests for security package."""

import tempfile
from pathlib import Path


from packages.security import AuthManager, QuantumShield, VulnerabilityScanner


def test_vulnerability_scanner():
    """Test vulnerability scanner basic functionality."""
    scanner = VulnerabilityScanner()

    # Test with empty requirements file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("# Empty requirements file\n")
        temp_path = Path(f.name)

    # Should not crash
    vulnerabilities = scanner.scan_dependencies(temp_path)
    assert isinstance(vulnerabilities, list)

    temp_path.unlink()


def test_auth_manager():
    """Test authentication manager."""
    auth = AuthManager("test-secret-key")

    # Test token generation and verification
    token = auth.generate_token("test_user", ["read", "write"])
    assert isinstance(token, str)

    payload = auth.verify_token(token)
    assert payload is not None
    assert payload["user_id"] == "test_user"
    assert payload["permissions"] == ["read", "write"]


def test_quantum_shield():
    """Test quantum shield encryption."""
    shield = QuantumShield()

    # Test key generation
    key = shield.generate_secure_key()
    assert len(key) == 64  # 32 bytes * 2 (hex)

    # Test coordinate encryption
    fernet_key, salt = shield.create_fernet_key("test_password")
    encrypted = shield.encrypt_coordinates(40.7128, -74.0060, fernet_key)
    assert isinstance(encrypted, str)

    # Test decryption
    lat, lng = shield.decrypt_coordinates(encrypted, fernet_key)
    assert abs(lat - 40.7128) < 0.0001
    assert abs(lng - (-74.0060)) < 0.0001

    # Test hashing
    hash1 = shield.hash_data("test_data")
    hash2 = shield.hash_data("test_data")
    assert hash1 == hash2  # Same input = same hash

    hash3 = shield.hash_data("test_data", "salt")
    assert hash1 != hash3  # Different with salt
