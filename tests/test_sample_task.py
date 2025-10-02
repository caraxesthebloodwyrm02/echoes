"""Tests for the sample task."""

from pathlib import Path
from unittest.mock import patch

import pytest

from automation.core.context import Context
from automation.tasks.sample_task import run


@pytest.fixture
def mock_context(tmp_path):
    """Create a mock context for testing."""
    context = Context()
    context.extra["target_dir"] = str(tmp_path)
    return context


def test_sample_task_dry_run(mock_context):
    """Test sample task in dry run mode."""
    mock_context.dry_run = True
    run(mock_context)
    # Check that no file was created in dry run mode
    assert not (Path(mock_context.extra["target_dir"]) / "sample.txt").exists()


def test_sample_task_confirmation_rejected(mock_context):
    """Test sample task when user rejects confirmation."""
    mock_context.confirmed = False
    with patch.object(mock_context, "require_confirmation", return_value=False):
        run(mock_context)
        # Check that no file was created when confirmation is rejected
        assert not (Path(mock_context.extra["target_dir"]) / "sample.txt").exists()


def test_sample_task_confirmation_accepted(mock_context):
    """Test sample task when user accepts confirmation."""
    mock_context.confirmed = False
    with patch.object(mock_context, "require_confirmation", return_value=True):
        run(mock_context)
        # Check that file was created when confirmation is accepted
        sample_file = Path(mock_context.extra["target_dir"]) / "sample.txt"
        assert sample_file.exists()
        assert (
            sample_file.read_text() == "This is a sample file created by the automation framework."
        )


def test_sample_task_no_confirmation_needed(mock_context):
    """Test sample task when confirmation is not needed."""
    mock_context.confirmed = True
    run(mock_context)
    # Check that file was created without asking for confirmation
    sample_file = Path(mock_context.extra["target_dir"]) / "sample.txt"
    assert sample_file.exists()
    assert sample_file.read_text() == "This is a sample file created by the automation framework."


def test_sample_task_default_directory(tmp_path):
    """Test sample task using default directory."""
    context = Context()
    context.confirmed = True  # Skip confirmation
    with patch("os.getcwd", return_value=str(tmp_path)):
        run(context)
        # Check that file was created in the current working directory
        sample_file = Path(tmp_path) / "sample.txt"
        assert sample_file.exists()


def test_sample_task_error_handling(mock_context):
    """Test sample task error handling."""
    mock_context.confirmed = True  # Skip confirmation

    # Mock write_text to raise an error
    def mock_write_text(content):
        raise PermissionError("Permission denied")

    with patch.object(Path, "write_text", side_effect=mock_write_text):
        # Test that the task handles the permission error
        with pytest.raises(PermissionError):
            run(mock_context)
