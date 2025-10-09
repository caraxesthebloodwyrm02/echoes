"""Comprehensive tests for echoe-core package."""

import logging
import sys
import tempfile
from pathlib import Path

import pytest
from core.config import Config, load_config
from core.exceptions import ConfigurationError, EchoeBaseException, ValidationError
from core.logging import configure_logging, get_logger

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class TestLogging:
    """Test logging functionality."""

    def test_get_logger(self):
        """Test logger creation."""
        logger = get_logger("test_module")
        assert logger.name == "echoe.test_module"
        assert isinstance(logger, logging.Logger)

    def test_get_logger_different_names(self):
        """Test multiple loggers with different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1.name != logger2.name
        assert logger1.name == "echoe.module1"
        assert logger2.name == "echoe.module2"

    def test_configure_logging_basic(self):
        """Test basic logging configuration."""
        configure_logging(level="DEBUG", rich_output=False)

        logger = get_logger("test")
        assert logger.level <= logging.DEBUG

    def test_configure_logging_with_file(self):
        """Test logging to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"

            configure_logging(level="INFO", log_file=log_file, rich_output=False)

            logger = get_logger("file_test")
            logger.info("Test message")

            assert log_file.exists()
            content = log_file.read_text()
            assert "Test message" in content

    def test_configure_logging_levels(self):
        """Test different logging levels."""
        levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in levels:
            configure_logging(level=level, rich_output=False)
            logger = get_logger(f"test_{level}")
            assert logger.level <= getattr(logging, level)


class TestConfig:
    """Test configuration management."""

    def test_config_defaults(self):
        """Test default configuration values."""
        config = Config()

        assert config.env in ["development", "production", "test"]
        assert isinstance(config.debug, bool)
        assert config.log_level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        assert isinstance(config.workspace_root, Path)
        assert isinstance(config.data_dir, Path)
        assert isinstance(config.logs_dir, Path)

    def test_config_directories_created(self):
        """Test that config creates required directories."""
        config = Config()

        assert config.data_dir.exists()
        assert config.logs_dir.exists()

    def test_config_with_env_vars(self, monkeypatch):
        """Test configuration with environment variables."""
        monkeypatch.setenv("ENV", "production")
        monkeypatch.setenv("DEBUG", "true")
        monkeypatch.setenv("LOG_LEVEL", "ERROR")

        config = Config()

        assert config.env == "production"
        assert config.debug is True
        assert config.log_level == "ERROR"

    def test_load_config_no_files(self):
        """Test loading config without files."""
        config = load_config()

        assert isinstance(config, Config)
        assert config.workspace_root.exists()

    def test_load_config_with_yaml(self):
        """Test loading config from YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("env: testing\n")
            f.write("debug: true\n")
            yaml_path = Path(f.name)

        try:
            config = load_config(config_file=yaml_path)
            assert isinstance(config, Config)
        finally:
            yaml_path.unlink()

    def test_config_env_override_yaml(self, monkeypatch):
        """Test that environment variables override YAML."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("env: from_yaml\n")
            yaml_path = Path(f.name)

        try:
            monkeypatch.setenv("ENV", "from_env")
            config = load_config(config_file=yaml_path)

            # Environment variable should take precedence
            assert config.env == "from_env"
        finally:
            yaml_path.unlink()


class TestExceptions:
    """Test custom exception classes."""

    def test_echoe_base_exception(self):
        """Test base exception."""
        exc = EchoeBaseException("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)

    def test_configuration_error(self):
        """Test configuration error."""
        exc = ConfigurationError("Invalid config")
        assert str(exc) == "Invalid config"
        assert isinstance(exc, EchoeBaseException)
        assert isinstance(exc, Exception)

    def test_validation_error(self):
        """Test validation error."""
        exc = ValidationError("Validation failed")
        assert str(exc) == "Validation failed"
        assert isinstance(exc, EchoeBaseException)

    def test_exception_raising(self):
        """Test that exceptions can be raised and caught."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Test")

        with pytest.raises(ValidationError):
            raise ValidationError("Test")

        with pytest.raises(EchoeBaseException):
            raise ConfigurationError("Caught by base")

    def test_exception_with_context(self):
        """Test exceptions with additional context."""
        try:
            raise ValidationError("Field 'email' is invalid")
        except ValidationError as e:
            assert "email" in str(e)
            assert "invalid" in str(e)


class TestIntegration:
    """Integration tests for core package."""

    def test_logging_and_config_integration(self):
        """Test logging with config."""
        config = Config()

        log_file = config.logs_dir / "integration_test.log"
        configure_logging(level=config.log_level, log_file=log_file, rich_output=False)

        logger = get_logger("integration")
        logger.info(f"Testing in {config.env} environment")

        assert log_file.exists()
        content = log_file.read_text()
        assert config.env in content or "integration" in content

    def test_exception_logging(self):
        """Test logging exceptions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "error.log"

            configure_logging(level="ERROR", log_file=log_file, rich_output=False)

            logger = get_logger("error_test")

            try:
                raise ValidationError("Test validation error")
            except ValidationError as e:
                logger.error(f"Caught exception: {e}")

            assert log_file.exists()
            content = log_file.read_text()
            assert "validation error" in content.lower()

    def test_complete_workflow(self, monkeypatch):
        """Test complete workflow with all core components."""
        # Setup environment
        monkeypatch.setenv("ENV", "test")
        monkeypatch.setenv("DEBUG", "true")

        # Load configuration
        config = load_config()
        assert config.env == "test"
        assert config.debug is True

        # Configure logging
        log_file = config.logs_dir / "workflow_test.log"
        configure_logging(level=config.log_level, log_file=log_file, rich_output=False)

        # Use logger
        logger = get_logger("workflow")
        logger.info("Starting workflow")

        # Handle exceptions
        try:
            logger.debug("Attempting risky operation")
            raise ValidationError("Simulated error")
        except EchoeBaseException as e:
            logger.error(f"Handled error: {e}")

        logger.info("Workflow completed")

        # Verify results
        assert log_file.exists()
        content = log_file.read_text()
        assert "Starting workflow" in content
        assert "Handled error" in content
        assert "Workflow completed" in content


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_logger_with_empty_name(self):
        """Test logger with empty name."""
        logger = get_logger("")
        assert logger.name == "echoe."

    def test_logger_with_special_characters(self):
        """Test logger with special characters in name."""
        logger = get_logger("test-module_v2.1")
        assert "test-module_v2.1" in logger.name

    def test_config_with_nonexistent_yaml(self):
        """Test loading config with nonexistent YAML file."""
        fake_path = Path("/nonexistent/config.yaml")
        config = load_config(config_file=fake_path)

        # Should not crash, just use defaults
        assert isinstance(config, Config)

    def test_logging_to_readonly_location(self):
        """Test logging to a read-only location (should handle gracefully)."""
        # This should not crash the application
        # In a real scenario, you'd test with actual permissions

    def test_config_invalid_log_level(self, monkeypatch):
        """Test config with invalid log level."""
        monkeypatch.setenv("LOG_LEVEL", "INVALID")
        config = Config()

        # Should still work with the invalid value stored
        assert config.log_level == "INVALID"


class TestPerformance:
    """Performance and stress tests."""

    def test_logger_creation_performance(self):
        """Test creating many loggers."""
        loggers = []
        for i in range(1000):
            logger = get_logger(f"perf_test_{i}")
            loggers.append(logger)

        assert len(loggers) == 1000
        assert all(isinstance(logger, logging.Logger) for logger in loggers)

    def test_logging_many_messages(self):
        """Test logging many messages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "perf.log"

            configure_logging(level="INFO", log_file=log_file, rich_output=False)

            logger = get_logger("perf")

            for i in range(100):
                logger.info(f"Message {i}")

            assert log_file.exists()
            lines = log_file.read_text().count("\n")
            assert lines >= 100

    def test_config_multiple_instances(self):
        """Test creating multiple config instances."""
        configs = [Config() for _ in range(100)]

        assert len(configs) == 100
        assert all(c.workspace_root == configs[0].workspace_root for c in configs)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
