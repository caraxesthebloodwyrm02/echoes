# test_logger.py
from core.packages.core.logging import get_logger, logger


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
    import logging

    test_logger()
