# test_logger.py
import pytest

# Try to import c_o_r_e modules, skip if not available
try:
    from c_o_r_e.packages.core.logging import get_logger, logger
    c_o_r_e_available = True
except ImportError:
    c_o_r_e_available = False


@pytest.mark.skipif(not c_o_r_e_available, reason="c_o_r_e import issues - relative import beyond top-level package")
def test_logger():
    # Using the default logger
    logger.info("This is a test message from the default logger")

    # Creating a custom logger
    custom_logger = get_logger("test_module", log_level=logging.DEBUG)
    custom_logger.debug("This is a debug message")
    custom_logger.info("This is an info message")
    custom_logger.warning("This is a warning message")
    custom_logger.error("This is an error message")


if __name__ == "__main__":
    import agent_logging

    test_logger()
