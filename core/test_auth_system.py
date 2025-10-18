"""
Tests for Authentication and Authorization System
"""

import pytest
import time
from datetime import timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.auth.jwt_handler import JWTHandler, create_access_token, verify_token
from api.auth.api_keys import APIKeyManager
from api.auth.permissions import Roles, has_permission, can_access_platform
from jwt.exceptions import InvalidTokenError


class TestJWTHandler:
    """Test JWT token operations"""
    
    def test_jwt_handler_initialization(self):
        """Test JWT handler can be initialized"""
        handler = JWTHandler(secret_key="test-secret")
        assert handler.secret_key == "test-secret"
        assert handler.algorithm == "HS256"
    
    def test_create_access_token(self):
        """Test access token creation"""
        handler = JWTHandler(secret_key="test-secret")
        token = handler.create_access_token({"sub": "user123", "role": "admin"})
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_valid_token(self):
        """Test verification of valid token"""
        handler = JWTHandler(secret_key="test-secret")
        token = handler.create_access_token({"sub": "user123", "role": "admin"})
        payload = handler.verify_token(token)
        
        assert payload["sub"] == "user123"
        assert payload["role"] == "admin"
        assert payload["type"] == "access"
        assert "exp" in payload
        assert "iat" in payload
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        handler = JWTHandler(secret_key="test-secret")
        
        with pytest.raises(InvalidTokenError):
            handler.verify_token("invalid.token.here")
    
    def test_expired_token(self):
        """Test expired token raises error"""
        handler = JWTHandler(secret_key="test-secret")
        token = handler.create_access_token(
            {"sub": "user123"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        with pytest.raises(InvalidTokenError):
            handler.verify_token(token)
    
    def test_create_refresh_token(self):
        """Test refresh token creation"""
        handler = JWTHandler(secret_key="test-secret")
        token = handler.create_refresh_token({"sub": "user123", "role": "admin"})
        payload = handler.verify_token(token)
        
        assert payload["type"] == "refresh"
        assert payload["sub"] == "user123"
    
    def test_refresh_access_token(self):
        """Test refreshing access token"""
        handler = JWTHandler(secret_key="test-secret")
        refresh_token = handler.create_refresh_token({
            "sub": "user123",
            "role": "admin",
            "platforms": ["echoes", "turbo"]
        })
        
        new_access_token = handler.refresh_access_token(refresh_token)
        payload = handler.verify_token(new_access_token)
        
        assert payload["type"] == "access"
        assert payload["sub"] == "user123"
        assert payload["role"] == "admin"
    
    def test_convenience_functions(self):
        """Test module-level convenience functions"""
        token = create_access_token({"sub": "user123"})
        payload = verify_token(token)
        assert payload["sub"] == "user123"


class TestAPIKeyManager:
    """Test API key management"""
    
    @pytest.fixture
    def temp_storage(self, tmp_path):
        """Create temporary storage for API keys"""
        return str(tmp_path / "test_api_keys.json")
    
    def test_api_key_manager_initialization(self, temp_storage):
        """Test API key manager initialization"""
        manager = APIKeyManager(storage_path=temp_storage)
        assert manager.storage_path == Path(temp_storage)
        assert isinstance(manager.keys, dict)
    
    def test_generate_api_key(self, temp_storage):
        """Test API key generation"""
        manager = APIKeyManager(storage_path=temp_storage)
        api_key = manager.generate_key(
            name="Test Key",
            role="researcher",
            platforms=["glimpse", "turbo"]
        )
        
        assert api_key.startswith("gp_")
        assert len(api_key) > 10
    
    def test_validate_api_key(self, temp_storage):
        """Test API key validation"""
        manager = APIKeyManager(storage_path=temp_storage)
        api_key = manager.generate_key(name="Test Key", role="admin")
        
        key_data = manager.validate_key(api_key)
        assert key_data is not None
        assert key_data["name"] == "Test Key"
        assert key_data["role"] == "admin"
        assert key_data["active"] is True
    
    def test_validate_invalid_key(self, temp_storage):
        """Test validation of invalid key"""
        manager = APIKeyManager(storage_path=temp_storage)
        key_data = manager.validate_key("invalid_key")
        assert key_data is None
    
    def test_revoke_api_key(self, temp_storage):
        """Test API key revocation"""
        manager = APIKeyManager(storage_path=temp_storage)
        api_key = manager.generate_key(name="Test Key")
        
        # Revoke the key
        result = manager.revoke_key(api_key)
        assert result is True
        
        # Validation should fail
        key_data = manager.validate_key(api_key)
        assert key_data is None
    
    def test_list_api_keys(self, temp_storage):
        """Test listing API keys"""
        manager = APIKeyManager(storage_path=temp_storage)
        manager.generate_key(name="Key 1", role="admin")
        manager.generate_key(name="Key 2", role="researcher")
        
        keys = manager.list_keys()
        assert len(keys) == 2
        assert keys[0]["name"] in ["Key 1", "Key 2"]
        assert keys[1]["name"] in ["Key 1", "Key 2"]
    
    def test_key_persistence(self, temp_storage):
        """Test API keys persist across instances"""
        manager1 = APIKeyManager(storage_path=temp_storage)
        api_key = manager1.generate_key(name="Persistent Key")
        
        # Create new manager instance
        manager2 = APIKeyManager(storage_path=temp_storage)
        key_data = manager2.validate_key(api_key)
        
        assert key_data is not None
        assert key_data["name"] == "Persistent Key"


class TestPermissions:
    """Test role-based access control"""
    
    def test_role_hierarchy(self):
        """Test role hierarchy permissions"""
        # Admin has all permissions
        assert has_permission(Roles.ADMIN, Roles.ADMIN)
        assert has_permission(Roles.ADMIN, Roles.RESEARCHER)
        assert has_permission(Roles.ADMIN, Roles.DEVELOPER)
        assert has_permission(Roles.ADMIN, Roles.ANALYST)
        
        # Researcher has researcher and analyst permissions
        assert has_permission(Roles.RESEARCHER, Roles.RESEARCHER)
        assert has_permission(Roles.RESEARCHER, Roles.ANALYST)
        assert not has_permission(Roles.RESEARCHER, Roles.ADMIN)
        assert not has_permission(Roles.RESEARCHER, Roles.DEVELOPER)
        
        # Developer has developer and analyst permissions
        assert has_permission(Roles.DEVELOPER, Roles.DEVELOPER)
        assert has_permission(Roles.DEVELOPER, Roles.ANALYST)
        assert not has_permission(Roles.DEVELOPER, Roles.ADMIN)
        assert not has_permission(Roles.DEVELOPER, Roles.RESEARCHER)
        
        # Analyst only has analyst permissions
        assert has_permission(Roles.ANALYST, Roles.ANALYST)
        assert not has_permission(Roles.ANALYST, Roles.ADMIN)
        assert not has_permission(Roles.ANALYST, Roles.RESEARCHER)
        assert not has_permission(Roles.ANALYST, Roles.DEVELOPER)
    
    def test_platform_access(self):
        """Test platform access by role"""
        # Admin has access to all platforms
        assert can_access_platform(Roles.ADMIN, "echoes")
        assert can_access_platform(Roles.ADMIN, "turbo")
        assert can_access_platform(Roles.ADMIN, "glimpse")
        
        # Researcher has access to glimpse and turbo
        assert can_access_platform(Roles.RESEARCHER, "glimpse")
        assert can_access_platform(Roles.RESEARCHER, "turbo")
        assert not can_access_platform(Roles.RESEARCHER, "echoes")
        
        # Developer has access to echoes and glimpse
        assert can_access_platform(Roles.DEVELOPER, "echoes")
        assert can_access_platform(Roles.DEVELOPER, "glimpse")
        assert not can_access_platform(Roles.DEVELOPER, "turbo")
        
        # Analyst has read-only access to all
        assert can_access_platform(Roles.ANALYST, "echoes")
        assert can_access_platform(Roles.ANALYST, "turbo")
        assert can_access_platform(Roles.ANALYST, "glimpse")


class TestIntegrationScenarios:
    """Test complete authentication workflows"""
    
    @pytest.fixture
    def temp_storage(self, tmp_path):
        return str(tmp_path / "integration_keys.json")
    
    def test_complete_jwt_workflow(self):
        """Test complete JWT authentication workflow"""
        handler = JWTHandler(secret_key="integration-test")
        
        # 1. Create access and refresh tokens
        user_data = {
            "sub": "user123",
            "role": "researcher",
            "platforms": ["glimpse", "turbo"]
        }
        access_token = handler.create_access_token(user_data)
        refresh_token = handler.create_refresh_token(user_data)
        
        # 2. Verify access token
        payload = handler.verify_token(access_token)
        assert payload["sub"] == "user123"
        assert payload["role"] == "researcher"
        
        # 3. Refresh access token
        new_access_token = handler.refresh_access_token(refresh_token)
        new_payload = handler.verify_token(new_access_token)
        assert new_payload["sub"] == "user123"
    
    def test_complete_api_key_workflow(self, temp_storage):
        """Test complete API key workflow"""
        manager = APIKeyManager(storage_path=temp_storage)
        
        # 1. Generate key for researcher
        api_key = manager.generate_key(
            name="Research Team",
            role="researcher",
            platforms=["glimpse", "turbo"]
        )
        
        # 2. Validate key
        key_data = manager.validate_key(api_key)
        assert key_data["role"] == "researcher"
        
        # 3. Check permissions
        assert can_access_platform(key_data["role"], "glimpse")
        assert can_access_platform(key_data["role"], "turbo")
        assert not can_access_platform(key_data["role"], "echoes")
        
        # 4. Revoke key
        manager.revoke_key(api_key)
        assert manager.validate_key(api_key) is None


def test_auth_system_summary():
    """Summary test showing all auth components work together"""
    print("\n" + "=" * 60)
    print("AUTHENTICATION SYSTEM SUMMARY")
    print("=" * 60)
    
    # JWT Handler
    handler = JWTHandler(secret_key="test")
    token = handler.create_access_token({"sub": "test_user", "role": "admin"})
    payload = handler.verify_token(token)
    print(f"\n✅ JWT Handler: Token created and verified")
    print(f"   User: {payload['sub']}, Role: {payload['role']}")
    
    # API Key Manager
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
        temp_path = f.name
    
    manager = APIKeyManager(storage_path=temp_path)
    api_key = manager.generate_key(name="Test", role="researcher")
    key_data = manager.validate_key(api_key)
    print(f"\n✅ API Key Manager: Key generated and validated")
    print(f"   Name: {key_data['name']}, Role: {key_data['role']}")
    
    # Permissions
    print(f"\n✅ Permissions System:")
    print(f"   Admin can access all platforms: {can_access_platform(Roles.ADMIN, 'echoes')}")
    print(f"   Researcher can access glimpse: {can_access_platform(Roles.RESEARCHER, 'glimpse')}")
    print(f"   Developer can access echoes: {can_access_platform(Roles.DEVELOPER, 'echoes')}")
    
    print("\n" + "=" * 60)
    print("All authentication components operational!")
    print("=" * 60)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
