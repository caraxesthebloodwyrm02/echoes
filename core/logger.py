import logging
import sys
from typing import Optional

# Add SUCCESS level
logging.addLevelName(25, 'SUCCESS')

class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[90m',
        'INFO': '\033[97m',
        'SUCCESS': '\033[92m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'RESET': '\033[0m',
    }
    def format(self, record):
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        msg = super().format(record)
        return f"{color}{msg}{self.COLORS['RESET']}"

class AutomationLogger:
    def __init__(self, name: str = "automation"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = ColorFormatter('[%(asctime)s] [%(levelname)s] %(message)s', "%Y-%m-%d %H:%M:%S")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def info(self, msg):
        self.logger.info(msg)
    
    def success(self, msg):
        self.logger.log(25, msg)  # SUCCESS level
    
    def warning(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)
    
    def debug(self, msg):
        self.logger.debug(msg)

log = AutomationLogger()
