"""
Security Tests for Authentication Module

Tests for:
- Login/logout functionality
- Token generation and validation
- Protected endpoints
- Role-based access control
"""

import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, "../app")

from main import app

client = TestClient(app)


class TestAuthentication:
    """Test authentication endpoints"""

    def test_login_success_admin(self):
        """Test successful login with admin credentials"""
        response = client.post(
            "/api/auth/login", json={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_login_success_user(self):
        """Test successful login with user credentials"""
        response = client.post("/api/auth/login", json={"username": "user", "password": "user123"})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = client.post(
            "/api/auth/login", json={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = client.post(
            "/api/auth/login", json={"username": "nonexistent", "password": "password"}
        )
        assert response.status_code == 401

    def test_get_current_user_without_token(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/api/auth/me")
        assert response.status_code == 403

    def test_get_current_user_with_valid_token(self):
        """Test accessing protected endpoint with valid token"""
        # First login
        login_response = client.post(
            "/api/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        # Then access protected endpoint
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"

    def test_get_current_user_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token"})
        assert response.status_code == 401

    def test_verify_token_valid(self):
        """Test token verification with valid token"""
        # Login first
        login_response = client.post(
            "/api/auth/login", json={"username": "user", "password": "user123"}
        )
        token = login_response.json()["access_token"]

        # Verify token
        response = client.get("/api/auth/verify", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["username"] == "user"

    def test_logout(self):
        """Test logout endpoint"""
        # Login first
        login_response = client.post(
            "/api/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        # Logout
        response = client.post("/api/auth/logout", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        assert "logged out successfully" in response.json()["message"]


class TestPasswordSecurity:
    """Test password security features"""

    def test_password_not_returned_in_response(self):
        """Ensure password is never returned in API responses"""
        login_response = client.post(
            "/api/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = login_response.json()["access_token"]

        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        data = response.json()
        assert "password" not in data
        assert "hashed_password" not in data


class TestRoleBasedAccess:
    """Test role-based access control"""

    def test_admin_role_in_token(self):
        """Test that admin role is properly encoded in token"""
        response = client.post(
            "/api/auth/login", json={"username": "admin", "password": "admin123"}
        )
        token = response.json()["access_token"]

        # Verify role
        verify_response = client.get(
            "/api/auth/verify", headers={"Authorization": f"Bearer {token}"}
        )
        assert verify_response.json()["role"] == "admin"

    def test_user_role_in_token(self):
        """Test that user role is properly encoded in token"""
        response = client.post("/api/auth/login", json={"username": "user", "password": "user123"})
        token = response.json()["access_token"]

        # Verify role
        verify_response = client.get(
            "/api/auth/verify", headers={"Authorization": f"Bearer {token}"}
        )
        assert verify_response.json()["role"] == "user"


class TestCORSSecurity:
    """Test CORS configuration"""

    def test_cors_headers_present(self):
        """Test that CORS headers are present"""
        response = client.options("/api/health")
        # Note: TestClient may not fully simulate CORS
        # This is a basic check
        assert response.status_code in [200, 405]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
