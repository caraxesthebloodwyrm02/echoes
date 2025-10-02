"""Tests for the Context class."""

from unittest.mock import patch

from automation.core.context import Context


def test_context_default():
    """Test default context initialization."""
    ctx = Context()
    assert ctx.dry_run is False
    assert ctx.user is not None
    assert ctx.env in ("dev", "staging", "prod")  # Default from environment or 'dev'
    assert ctx.confirmed is False
    assert isinstance(ctx.extra, dict)
    assert len(ctx.extra) == 0


@patch("os.getenv")
def test_context_environment_vars(mock_getenv):
    """Test context initialization with environment variables."""
    # Mock environment variables
    mock_getenv.side_effect = lambda k, d=None: {
        "USERNAME": "testuser",
        "ENVIRONMENT": "staging",
    }.get(k, d)

    ctx = Context()
    assert ctx.user == "testuser"
    assert ctx.env == "staging"


def test_context_custom_values():
    """Test context with custom values."""
    extra_data = {"key": "value"}
    ctx = Context(
        dry_run=True,
        user="testuser",
        env="testing",
        confirmed=True,
        extra=extra_data.copy(),
    )
    assert ctx.dry_run is True
    assert ctx.user == "testuser"
    assert ctx.env == "testing"
    assert ctx.confirmed is True
    assert ctx.extra == extra_data


def test_require_confirmation_dry_run():
    """Test require_confirmation in dry-run mode."""
    with patch("builtins.input") as mock_input:
        ctx = Context(dry_run=True)
        result = ctx.require_confirmation("Test prompt")
        assert result is True  # Should return True in dry-run
        assert ctx.confirmed is False  # Should not modify confirmed in dry-run
        mock_input.assert_not_called()  # Should not prompt in dry-run


def test_require_confirmation_user_accepts():
    """Test require_confirmation when user accepts."""
    with patch("builtins.input", return_value="y"):
        ctx = Context()
        assert ctx.require_confirmation("Test prompt") is True
        assert ctx.confirmed is True


def test_require_confirmation_user_rejects():
    """Test require_confirmation when user rejects."""
    with patch("builtins.input", return_value="n"):
        ctx = Context()
        assert ctx.require_confirmation("Test prompt") is False
        assert ctx.confirmed is False


def test_require_confirmation_case_insensitive():
    """Test require_confirmation is case insensitive."""
    with patch("builtins.input", return_value="Y"):
        ctx = Context()
        assert ctx.require_confirmation("Test prompt") is True
        assert ctx.confirmed is True
