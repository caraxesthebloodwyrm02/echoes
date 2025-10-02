"""Tests for the Logger class."""

import logging
from unittest.mock import patch

from automation.core.logger import SUCCESS_LEVEL_NUM, AutomationLogger, ColorFormatter


def test_automation_logger_initialization():
    """Test AutomationLogger initialization."""
    # The logger name is fixed as 'automation' in the implementation
    logger = AutomationLogger("test_logger")
    assert isinstance(logger.logger, logging.Logger)
    assert logger.logger.name == "automation"  # Name is fixed in the implementation
    assert logger.logger.level == logging.INFO


def test_automation_logger_singleton():
    """Test that AutomationLogger is a singleton."""
    logger1 = AutomationLogger("test1")
    logger2 = AutomationLogger("test2")
    assert logger1 is logger2
    assert logger1.logger is logger2.logger


def test_automation_logger_methods():
    """Test all logger methods."""
    # Create a real logger instance
    logger = AutomationLogger("test_logger")

    # Test debug
    with patch.object(logger.logger, "debug") as mock_debug:
        logger.debug("debug message")
        mock_debug.assert_called_once_with("debug message")

    # Test info
    with patch.object(logger.logger, "info") as mock_info:
        logger.info("info message")
        mock_info.assert_called_once_with("info message")

    # Test warning
    with patch.object(logger.logger, "warning") as mock_warning:
        logger.warning("warning message")
        mock_warning.assert_called_once_with("warning message")

    # Test error
    with patch.object(logger.logger, "error") as mock_error:
        logger.error("error message")
        mock_error.assert_called_once_with("error message")

    # Test critical
    with patch.object(logger.logger, "critical") as mock_critical:
        logger.critical("critical message")
        mock_critical.assert_called_once_with("critical message")

    # Test success
    with patch.object(logger.logger, "log") as mock_log:
        logger.success("success message")
        from automation.core.logger import SUCCESS_LEVEL_NUM

        mock_log.assert_called_once_with(SUCCESS_LEVEL_NUM, "success message")


def test_color_formatter():
    """Test the ColorFormatter class."""
    formatter = ColorFormatter()

    # Test with a record
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="test message",
        args=(),
        exc_info=None,
    )

    # Just verify it doesn't raise exceptions
    formatted = formatter.format(record)
    assert "test message" in formatted

    # Test with different log levels
    for level in [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.ERROR,
        logging.CRITICAL,
        SUCCESS_LEVEL_NUM,
    ]:
        record.levelno = level
        formatted = formatter.format(record)
        assert "test message" in formatted


def test_color_formatter_no_color():
    """Test ColorFormatter with an unknown log level."""
    formatter = ColorFormatter()

    # Create a record with an unknown log level
    record = logging.LogRecord(
        name="test",
        level=999,  # Unknown level
        pathname="",
        lineno=0,
        msg="test message",
        args=(),
        exc_info=None,
    )

    # Should still format without raising an exception
    formatted = formatter.format(record)
    assert "test message" in formatted

    # Should not contain any color codes for unknown levels
    assert "\x1b" not in formatted, "Unknown levels should not have color codes"

    # Verify the format is correct
    assert " - test - " in formatted
    assert " - test message" in formatted
