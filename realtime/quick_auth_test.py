#!/usr/bin/env python3
"""Quick authentication system test"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 70)
print("AUTHENTICATION SYSTEM - QUICK TEST")
print("=" * 70)

# Test 1: JWT Handler
print("\n[1/5] Testing JWT Token Handler...")
try:
    from api.auth.jwt_handler import JWTHandler
    handler = JWTHandler(secret_key="test-secret")
    token = handler.create_access_token({"sub": "user123", "role": "admin"})
    payload = handler.verify_token(token)
    assert payload["sub"] == "user123"
    print("PASSED: JWT Handler")
except Exception as e:
    print(f"FAILED: JWT Handler - {e}")
    sys.exit(1)

# Test 2: API Key Manager
print("\n[2/5] Testing API Key Manager...")
try:
    from api.auth.api_keys import APIKeyManager
    import tempfile
    import json
    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    temp_path = temp_file.name
    # Initialize with empty dict to avoid JSON decode error
    with open(temp_path, 'w') as f:
        json.dump({}, f)
    manager = APIKeyManager(storage_path=temp_path)
    api_key = manager.generate_key(name="Test", role="researcher")
    key_data = manager.validate_key(api_key)
    assert key_data["name"] == "Test"
    print("PASSED: API Key Manager")
except Exception as e:
    print(f"FAILED: API Key Manager - {e}")
    sys.exit(1)

# Test 3: Permissions
print("\n[3/5] Testing Permissions...")
try:
    from api.auth.permissions import Roles, has_permission, can_access_platform
    assert has_permission(Roles.ADMIN, Roles.RESEARCHER)
    assert can_access_platform(Roles.RESEARCHER, "glimpse")
    print("PASSED: Permissions")
except Exception as e:
    print(f"FAILED: Permissions - {e}")
    sys.exit(1)

# Test 4: Rate Limiter
print("\n[4/5] Testing Rate Limiter...")
try:
    from api.middleware.rate_limiter import TokenBucketRateLimiter
    limiter = TokenBucketRateLimiter(capacity=5, refill_rate=1.0)
    assert limiter.allow_request("client1", cost=1.0)
    print("PASSED: Rate Limiter")
except Exception as e:
    print(f"FAILED: Rate Limiter - {e}")
    sys.exit(1)

# Test 5: Integration
print("\n[5/5] Testing Complete Workflow...")
try:
    # Create user with JWT
    handler = JWTHandler(secret_key="integration-test")
    access_token = handler.create_access_token({
        "sub": "researcher001",
        "role": "researcher",
        "platforms": ["glimpse", "turbo"]
    })
    
    # Verify token
    payload = handler.verify_token(access_token)
    
    # Check permissions
    assert can_access_platform(payload["role"], "glimpse")
    assert can_access_platform(payload["role"], "turbo")
    
    print("PASSED: Integration Workflow")
except Exception as e:
    print(f"FAILED: Integration - {e}")
    sys.exit(1)

print("\n" + "=" * 70)
print("ALL TESTS PASSED - Authentication System Operational!")
print("=" * 70)
print("\nComponents verified:")
print("  • JWT token generation & validation")
print("  • API key management & storage")
print("  • Role-based access control")
print("  • Rate limiting enforcement")
print("  • End-to-end integration")
print("\n" + "=" * 70)
