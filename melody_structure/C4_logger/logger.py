import logging

logger = logging.getLogger("automation")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("[automation] %(levelname)s: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class AutomationLogger:
    def log(self, message, level="info"):
        if level == "info":
            logger.info(message)
        elif level == "error":
            logger.error(message)
        elif level == "warning":
            logger.warning(message)
        else:
            logger.debug(message)

    def info(self, msg):
        self.log(msg, "info")

    def error(self, msg):
        self.log(msg, "error")

    def warning(self, msg):
        self.log(msg, "warning")

    def success(self, msg):
        """Convenience success-level log (maps to INFO)."""
        self.log(msg, "info")
