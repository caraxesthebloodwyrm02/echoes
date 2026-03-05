"""
Tests for retry utilities.

Tests tenacity integration, exponential backoff, and retry behavior.
"""

from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from tenacity import RetryError

from app.resilience.retry_utils import (
    _log_retry_attempt,
    make_resilient_request,
    resilient_http_call,
    retry_config,
    should_retry_exception,
)


class TestShouldRetryException:
    """Test the should_retry_exception function."""

    def test_should_retry_429_error(self):
        """Test that 429 errors should be retried."""
        exc = httpx.HTTPStatusError(
            "429 Too Many Requests", request=Mock(), response=Mock(status_code=429)
        )
        assert should_retry_exception(exc) is True

    def test_should_retry_5xx_errors(self):
        """Test that 5xx errors should be retried."""
        for status_code in [500, 502, 503, 504]:
            exc = httpx.HTTPStatusError(
                f"{status_code} Server Error",
                request=Mock(),
                response=Mock(status_code=status_code),
            )
            assert should_retry_exception(exc) is True

    def test_should_not_retry_4xx_errors(self):
        """Test that 4xx errors (except 429) should not be retried."""
        for status_code in [400, 401, 403, 404, 422]:
            exc = httpx.HTTPStatusError(
                f"{status_code} Client Error",
                request=Mock(),
                response=Mock(status_code=status_code),
            )
            assert should_retry_exception(exc) is False

    def test_should_retry_connection_errors(self):
        """Test that connection errors should be retried."""
        exc = httpx.ConnectError("Connection failed")
        assert should_retry_exception(exc) is True

    def test_should_retry_timeout_errors(self):
        """Test that timeout errors should be retried."""
        exc = httpx.TimeoutException("Request timed out")
        assert should_retry_exception(exc) is True

    def test_should_not_retry_business_errors(self):
        """Test that business logic errors should not be retried."""
        exc = ValueError("Invalid input")
        assert should_retry_exception(exc) is False

        exc = RuntimeError("Business logic failed")
        assert should_retry_exception(exc) is False


class TestRetryConfig:
    """Test the retry_config decorator."""

    def test_retry_config_decorator(self):
        """Test that retry_config returns a properly configured decorator."""
        decorator = retry_config(max_attempts=3, initial_wait=0.1, max_wait=1.0)

        # Should be a retry decorator
        assert callable(decorator)

        # Test with a function
        @decorator
        def test_func():
            return "success"

        result = test_func()
        assert result == "success"


class TestMakeResilientRequest:
    """Test the make_resilient_request function."""

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_successful_request(self, mock_client_class):
        """Test successful request with no retries needed."""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        response = await make_resilient_request("GET", "https://api.example.com")

        assert response is mock_response
        mock_client.request.assert_called_once_with("GET", "https://api.example.com")

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_retry_on_429(self, mock_client_class):
        """Test retry behavior on 429 error."""
        # Mock client that fails twice then succeeds
        call_count = 0

        def mock_request(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # First two calls fail with 429
                mock_response = Mock()
                mock_response.status_code = 429
                mock_response.headers = {}
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "429 Too Many Requests", request=Mock(), response=mock_response
                )
                return mock_response
            else:
                # Third call succeeds
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.raise_for_status.return_value = None
                return mock_response

        mock_client = AsyncMock()
        mock_client.request.side_effect = mock_request
        mock_client_class.return_value.__aenter__.return_value = mock_client

        response = await make_resilient_request(
            "GET", "https://api.example.com", max_retries=3
        )

        assert response.status_code == 200
        assert mock_client.request.call_count == 3

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_exhaust_retries(self, mock_client_class):
        """Test that retries are exhausted after max attempts."""
        # Mock client that always fails
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {}
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "429 Too Many Requests", request=Mock(), response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with pytest.raises(RetryError):
            await make_resilient_request(
                "GET", "https://api.example.com", max_retries=2
            )

        # Should have tried 2 times (initial + 1 retry)
        assert mock_client.request.call_count == 2

    @pytest.mark.asyncio
    @patch("httpx.AsyncClient")
    async def test_no_retry_on_4xx(self, mock_client_class):
        """Test that 4xx errors (except 429) don't trigger retries."""
        # Mock 404 error
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=Mock(), response=mock_response
        )

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with pytest.raises(httpx.HTTPStatusError):
            await make_resilient_request("GET", "https://api.example.com")

        # Should only be called once (no retries)
        mock_client.request.assert_called_once()


class TestResilientHttpCall:
    """Test the resilient_http_call decorator."""

    def test_decorator_creation(self):
        """Test that resilient_http_call creates proper decorators."""
        decorator = resilient_http_call(method="GET", url="https://api.example.com")

        assert callable(decorator)

        # Test applying to a function
        @decorator
        async def test_func():
            return "success"

        assert callable(test_func)


class TestRetryLogging:
    """Test retry attempt logging."""

    def test_log_retry_attempt_with_exception(self, caplog):
        """Test logging of retry attempts with exceptions."""
        from tenacity import RetryCallState

        # Mock retry state
        mock_outcome = Mock()
        mock_outcome.exception.return_value = Exception("Test error")

        mock_retry_state = Mock(spec=RetryCallState)
        mock_retry_state.attempt_number = 2
        mock_retry_state.outcome = mock_outcome
        mock_retry_state.next_action.sleep = 1.5

        with caplog.at_level("WARNING"):
            _log_retry_attempt(mock_retry_state)

        assert "Retry attempt 2 failed" in caplog.text
        assert "Test error" in caplog.text
        assert "1.5 seconds" in caplog.text

    def test_log_retry_attempt_success(self, caplog):
        """Test logging of successful retry attempts."""
        from tenacity import RetryCallState

        # Mock retry state for success
        mock_outcome = Mock()
        mock_outcome.exception.return_value = None

        mock_retry_state = Mock(spec=RetryCallState)
        mock_retry_state.attempt_number = 1
        mock_retry_state.outcome = mock_outcome

        with caplog.at_level("INFO"):
            _log_retry_attempt(mock_retry_state)

        assert "Retry attempt 1 completed successfully" in caplog.text


class TestPreconfiguredDecorators:
    """Test pre-configured decorator functions."""

    def test_resilient_get_decorator(self):
        """Test the resilient_get decorator."""
        from app.resilience.retry_utils import resilient_get

        decorator = resilient_get("https://api.example.com/data")
        assert callable(decorator)

    def test_resilient_post_decorator(self):
        """Test the resilient_post decorator."""
        from app.resilience.retry_utils import resilient_post

        decorator = resilient_post("https://api.example.com/data")
        assert callable(decorator)

    def test_resilient_put_decorator(self):
        """Test the resilient_put decorator."""
        from app.resilience.retry_utils import resilient_put

        decorator = resilient_put("https://api.example.com/data")
        assert callable(decorator)

    def test_resilient_delete_decorator(self):
        """Test the resilient_delete decorator."""
        from app.resilience.retry_utils import resilient_delete

        decorator = resilient_delete("https://api.example.com/data")
        assert callable(decorator)
