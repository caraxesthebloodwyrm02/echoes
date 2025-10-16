# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
