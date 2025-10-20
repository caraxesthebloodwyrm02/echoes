#!/usr/bin/env python3
"""
Simple test runner for authentication system
Runs without pytest if needed
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def run_manual_tests():
    """Run tests manually without pytest"""
    print("=" * 70)
    print("AUTHENTICATION SYSTEM - MANUAL TEST RUNNER")
    print("=" * 70)

    try:
        # Test 1: JWT Handler
        print("\n[TEST 1] JWT Token Handler")
        from api.auth.jwt_handler import JWTHandler

        handler = JWTHandler(secret_key="test-secret")
        token = handler.create_access_token({"sub": "test_user", "role": "admin"})
        payload = handler.verify_token(token)

        assert payload["sub"] == "test_user"
        assert payload["role"] == "admin"
        assert payload["type"] == "access"
        print("  ✅ JWT token creation and verification: PASSED")

        # Test 2: Refresh Token
        print("\n[TEST 2] Refresh Token")
        refresh_token = handler.create_refresh_token({"sub": "test_user", "role": "admin"})
        new_access = handler.refresh_access_token(refresh_token)
        new_payload = handler.verify_token(new_access)

        assert new_payload["sub"] == "test_user"
        assert new_payload["type"] == "access"
        print("  ✅ Refresh token workflow: PASSED")

    except ImportError as e:
        print(f"  ❌ FAILED: Missing dependency - {e}")
        print("  💡 Install with: pip install PyJWT")
        return False
    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

    try:
        # Test 3: API Key Manager
        print("\n[TEST 3] API Key Manager")
        from api.auth.api_keys import APIKeyManager
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            temp_path = f.name

        manager = APIKeyManager(storage_path=temp_path)
        api_key = manager.generate_key(name="Test Key", role="researcher")

        assert api_key.startswith("gp_")
        print("  ✅ API key generation: PASSED")

        key_data = manager.validate_key(api_key)
        assert key_data is not None
        assert key_data["name"] == "Test Key"
        assert key_data["role"] == "researcher"
        print("  ✅ API key validation: PASSED")

        manager.revoke_key(api_key)
        assert manager.validate_key(api_key) is None
        print("  ✅ API key revocation: PASSED")

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

    try:
        # Test 4: Permissions
        print("\n[TEST 4] Role-Based Access Control")
        from api.auth.permissions import Roles, has_permission, can_access_platform

        # Test role hierarchy
        assert has_permission(Roles.ADMIN, Roles.ADMIN)
        assert has_permission(Roles.ADMIN, Roles.RESEARCHER)
        assert not has_permission(Roles.ANALYST, Roles.ADMIN)
        print("  ✅ Role hierarchy: PASSED")

        # Test platform access
        assert can_access_platform(Roles.ADMIN, "echoes")
        assert can_access_platform(Roles.RESEARCHER, "glimpse")
        assert not can_access_platform(Roles.RESEARCHER, "echoes")
        print("  ✅ Platform access control: PASSED")

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

    try:
        # Test 5: Rate Limiter
        print("\n[TEST 5] Rate Limiter")
        from api.middleware.rate_limiter import TokenBucketRateLimiter

        limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1.0)

        # Should allow first request
        assert limiter.allow_request("client1", cost=1.0)
        print("  ✅ Rate limiter initialization: PASSED")

        # Exhaust tokens
        for _ in range(9):
            limiter.allow_request("client1", cost=1.0)

        # Should deny when exhausted
        assert not limiter.allow_request("client1", cost=1.0)
        print("  ✅ Rate limiting enforcement: PASSED")

    except Exception as e:
        print(f"  ❌ FAILED: {e}")
        return False

    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED!")
    print("=" * 70)
    print("\nAuthentication system is fully operational:")
    print("  • JWT token generation and validation")
    print("  • API key management")
    print("  • Role-based access control")
    print("  • Rate limiting")
    print("\n" + "=" * 70)

    return True


if __name__ == "__main__":
    try:
        # Try to run with pytest if available
        import pytest

        print("Running tests with pytest...\n")
        sys.exit(pytest.main(["tests/test_auth_system.py", "-v", "--tb=short", "-s"]))
    except ImportError:
        print("pytest not found, running manual tests...\n")
        success = run_manual_tests()
        sys.exit(0 if success else 1)
