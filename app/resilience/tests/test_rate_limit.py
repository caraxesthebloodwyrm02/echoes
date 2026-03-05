"""
Tests for rate limiting functionality.

Tests SlowApi integration and rate limiting behavior.
"""

from unittest.mock import Mock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.resilience.rate_limit import (
    api_key_limit,
    get_api_key_func,
    setup_rate_limiting,
    strict_limit,
)


class TestRateLimitSetup:
    """Test rate limiting setup and configuration."""

    @patch("app.resilience.rate_limit.get_config")
    def test_setup_without_redis(self, mock_get_config):
        """Test setup with in-memory storage."""
        # Mock config
        mock_config = Mock()
        mock_config.redis.url = None
        mock_config.security.rate_limit_requests = 100
        mock_get_config.return_value = mock_config

        app = FastAPI()
        limiter = setup_rate_limiting(app)

        assert limiter is not None
        assert hasattr(app.state, "limiter")
        assert app.state.limiter is limiter

    @patch("app.resilience.rate_limit.get_config")
    def test_setup_with_redis(self, mock_get_config):
        """Test setup with Redis storage."""
        # Mock config
        mock_config = Mock()
        mock_config.redis.url = "redis://localhost:6379"
        mock_config.security.rate_limit_requests = 100
        mock_get_config.return_value = mock_config

        app = FastAPI()
        limiter = setup_rate_limiting(app)

        assert limiter is not None
        # Check that Redis storage was used
        assert "redis://" in limiter._storage.storage_uri


class TestApiKeyFunc:
    """Test the API key function for rate limiting."""

    def test_api_key_from_authorization_header(self):
        """Test extracting API key from Authorization header."""
        # Mock request with Bearer token
        request = Mock()
        request.headers = {"Authorization": "Bearer test-api-key-123"}

        key = get_api_key_func(request)
        assert key == "api_key:test-api-key-123"

    def test_api_key_from_x_api_key_header(self):
        """Test extracting API key from X-API-Key header."""
        request = Mock()
        request.headers = {"X-API-Key": "test-api-key-456"}

        key = get_api_key_func(request)
        assert key == "api_key:test-api-key-456"

    def test_fallback_to_ip_address(self):
        """Test fallback to IP address when no API key."""
        request = Mock()
        request.headers = {}
        request.client = Mock()
        request.client.host = "192.168.1.100"

        # Mock get_remote_address
        with patch(
            "app.resilience.rate_limit.get_remote_address", return_value="192.168.1.100"
        ):
            key = get_api_key_func(request)
            assert key == "ip:192.168.1.100"

    def test_precedence_authorization_over_x_api_key(self):
        """Test that Authorization header takes precedence over X-API-Key."""
        request = Mock()
        request.headers = {"Authorization": "Bearer auth-key", "X-API-Key": "x-api-key"}

        key = get_api_key_func(request)
        assert key == "api_key:auth-key"


class TestRateLimitDecorators:
    """Test rate limiting decorators."""

    def test_strict_limit_decorator(self):
        """Test the strict_limit decorator."""
        decorator = strict_limit("5/minute")

        # Mock a function
        mock_func = Mock()
        mock_func.__name__ = "test_func"

        # Apply decorator
        decorated_func = decorator(mock_func)

        # The decorated function should have limiter applied
        assert decorated_func is not mock_func
        assert hasattr(decorated_func, "__wrapped__")

    def test_api_key_limit_decorator(self):
        """Test the api_key_limit decorator."""
        decorator = api_key_limit("10/minute")

        mock_func = Mock()
        mock_func.__name__ = "test_func"

        decorated_func = decorator(mock_func)

        assert decorated_func is not mock_func


class TestRateLimitingIntegration:
    """Integration tests for rate limiting behavior."""

    @patch("app.resilience.rate_limit.get_config")
    def test_rate_limiting_works(self, mock_get_config):
        """Test that rate limiting actually blocks requests."""
        # Mock config with very low limit for testing
        mock_config = Mock()
        mock_config.redis.url = None
        mock_config.security.rate_limit_requests = 2  # Only 2 requests per minute
        mock_get_config.return_value = mock_config

        app = FastAPI()
        setup_rate_limiting(app)

        # Add a test endpoint
        @app.get("/test")
        async def test_endpoint():
            return {"message": "ok"}

        client = TestClient(app)

        # First request should succeed
        response1 = client.get("/test")
        assert response1.status_code == 200

        # Second request should succeed
        response2 = client.get("/test")
        assert response2.status_code == 200

        # Third request should be rate limited
        response3 = client.get("/test")
        assert response3.status_code == 429
        assert "Rate limit exceeded" in response3.text

        # Check headers
        assert "X-RateLimit-Remaining" in response3.headers
        assert "Retry-After" in response3.headers

    @patch("app.resilience.rate_limit.get_config")
    def test_api_key_rate_limiting(self, mock_get_config):
        """Test per-API-key rate limiting."""
        mock_config = Mock()
        mock_config.redis.url = None
        mock_config.security.rate_limit_requests = 1
        mock_get_config.return_value = mock_config

        app = FastAPI()
        limiter = setup_rate_limiting(app)

        @app.get("/test")
        @limiter.limit("1/minute", key_func=get_api_key_func)
        async def test_endpoint():
            return {"message": "ok"}

        client = TestClient(app)

        # Request with API key
        headers = {"X-API-Key": "test-key"}

        # First request succeeds
        response1 = client.get("/test", headers=headers)
        assert response1.status_code == 200

        # Second request with same key fails
        response2 = client.get("/test", headers=headers)
        assert response2.status_code == 429

        # Request with different key succeeds
        headers2 = {"X-API-Key": "different-key"}
        response3 = client.get("/test", headers=headers2)
        assert response3.status_code == 200
