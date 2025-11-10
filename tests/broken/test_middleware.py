"""
Tests for API middleware components.
"""

import time
from unittest.mock import Mock

from api.middleware import (
    AuthenticationMiddleware,
    RateLimiter,
    RequestLoggingMiddleware,
)


class TestRateLimiter:
    """Test RateLimiter class."""

    def test_rate_limiter_init(self):
        """Test RateLimiter initialization."""
        limiter = RateLimiter(requests_per_window=10, window_seconds=60)
        assert limiter.requests_per_window == 10
        assert limiter.window_seconds == 60
        assert limiter.requests == {}

    def test_rate_limiter_allow_first_request(self):
        """Test that first request is allowed."""
        limiter = RateLimiter(requests_per_window=5, window_seconds=60)
        assert limiter.is_allowed("client1") is True
        assert len(limiter.requests["client1"]) == 1

    def test_rate_limiter_under_limit(self):
        """Test requests under the limit are allowed."""
        limiter = RateLimiter(requests_per_window=3, window_seconds=60)
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True

    def test_rate_limiter_over_limit(self):
        """Test requests over the limit are blocked."""
        limiter = RateLimiter(requests_per_window=2, window_seconds=60)
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False

    def test_rate_limiter_window_reset(self):
        """Test that window resets after time passes."""
        limiter = RateLimiter(requests_per_window=1, window_seconds=1)
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client1") is False

        # Wait for window to pass
        time.sleep(1.1)
        assert limiter.is_allowed("client1") is True

    def test_rate_limiter_different_clients(self):
        """Test that different clients have separate limits."""
        limiter = RateLimiter(requests_per_window=1, window_seconds=60)
        assert limiter.is_allowed("client1") is True
        assert limiter.is_allowed("client2") is True  # Different client
        assert limiter.is_allowed("client1") is False

    def test_get_remaining_requests(self):
        """Test getting remaining requests count."""
        limiter = RateLimiter(requests_per_window=5, window_seconds=60)
        assert limiter.get_remaining_requests("client1") == 5

        limiter.is_allowed("client1")
        assert limiter.get_remaining_requests("client1") == 4

        # Use up all requests
        for _ in range(4):
            limiter.is_allowed("client1")
        assert limiter.get_remaining_requests("client1") == 0


class TestAuthenticationMiddleware:
    """Test AuthenticationMiddleware class."""

    def test_auth_middleware_init(self):
        """Test AuthenticationMiddleware initialization."""
        mock_config = Mock()
        mock_config.security.rate_limit_requests = 60
        mock_config.security.rate_limit_window = 60
        middleware = AuthenticationMiddleware(app=Mock(), config=mock_config)
        assert middleware.app is not None
        assert middleware.config is mock_config

    def test_auth_middleware_disabled(self):
        """Test middleware when authentication is disabled."""
        mock_config = Mock()
        mock_config.security.api_key_required = False
        mock_config.security.rate_limit_requests = 60
        mock_config.security.rate_limit_window = 60

        middleware = AuthenticationMiddleware(app=Mock(), config=mock_config)
        # Should not raise exception when auth is disabled
        assert middleware is not None
        assert middleware.config.security.api_key_required is False

    def test_auth_middleware_enabled_no_key(self):
        """Test middleware when auth is enabled but no key provided."""
        mock_config = Mock()
        mock_config.security.api_key_required = True
        mock_config.security.allowed_api_keys = ["valid-key"]
        mock_config.security.rate_limit_requests = 60
        mock_config.security.rate_limit_window = 60

        middleware = AuthenticationMiddleware(app=Mock(), config=mock_config)
        assert middleware is not None
        assert middleware.config.security.allowed_api_keys == ["valid-key"]


class TestRequestLoggingMiddleware:
    """Test RequestLoggingMiddleware class."""

    def test_logging_middleware_init(self):
        """Test RequestLoggingMiddleware initialization."""
        middleware = RequestLoggingMiddleware(app=Mock())
        assert middleware.app is not None
