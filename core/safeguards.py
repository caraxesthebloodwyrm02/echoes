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

"""
System safeguards for process locking and mock mode management.
"""

import logging
import os
import platform
from contextlib import contextmanager
from pathlib import Path
from typing import Optional

# Import platform-specific locking mechanism
if platform.system() == "Windows":
    import msvcrt
else:
    import fcntl

# Configure logging
logger = logging.getLogger(__name__)


class ProcessLock:
    """Process-level locking mechanism to prevent parallel execution."""

    def __init__(self, lock_file: str = "echoes.lock"):
        self.lock_file = Path(lock_file)
        self.lock_fd: Optional[int] = None

    @contextmanager
    def acquire(self):
        """
        Acquire a process lock using file locking.

        Raises:
            IOError: If lock cannot be acquired
        """
        try:
            self.lock_fd = os.open(self.lock_file, os.O_CREAT | os.O_RDWR)
            if platform.system() == "Windows":
                msvcrt.locking(self.lock_fd, msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(self.lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            logger.info("🔒 Process lock acquired")
            yield
        except (IOError, OSError) as e:
            logger.error(f"Failed to acquire process lock: {e}")
            raise
        finally:
            if self.lock_fd is not None:
                if platform.system() == "Windows":
                    msvcrt.locking(self.lock_fd, msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(self.lock_fd, fcntl.LOCK_UN)
                os.close(self.lock_fd)
                logger.info("🔓 Process lock released")
                try:
                    self.lock_file.unlink()
                except OSError:
                    pass


class MockManager:
    """Manages mock mode activation and tracking."""

    def __init__(self, mock_log_path: str = "logs/mock.log"):
        self.mock_log_path = Path(mock_log_path)
        self.mock_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Set up mock-specific logger
        self.mock_logger = logging.getLogger("mock_manager")
        handler = logging.FileHandler(self.mock_log_path)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
        self.mock_logger.addHandler(handler)

    def activate_mock_mode(self, reason: str):
        """
        Activate mock mode and log the reason.

        Args:
            reason: Why mock mode was activated
        """
        self.mock_logger.warning(f"Mock mode activated: {reason}")
        return True

    def is_mock_mode_active(self) -> bool:
        """Check if mock mode is currently active."""
        if not self.mock_log_path.exists():
            return False

        # Check last few lines of mock log for recent activations
        try:
            with open(self.mock_log_path, "r") as f:
                last_lines = f.readlines()[-5:]  # Check last 5 lines
                return any("Mock mode activated" in line for line in last_lines)
        except (IOError, IndexError):
            return False
