"""
Logger Setup for Monitoring and Logging
Provides a configured logger instance
"""

import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

def setup_logger(name: str = "default_logger", log_file: str = "application.log") -> logging.Logger:
    """Set up a logger with JSON formatting and file rotation"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    log_path = Path(log_file)
    file_handler = RotatingFileHandler(log_path, maxBytes=1048576, backupCount=5)
    file_handler.setLevel(logging.INFO)
    
    # JSON formatter (simple implementation)
    formatter = logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
    file_handler.setFormatter(formatter)
    
    # Console handler for debug
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
