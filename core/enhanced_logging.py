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

# Logging configuration for enhanced monitoring
import logging
import sys
from pathlib import Path

# Setup logging paths
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def setup_logger(name, log_file, level=logging.INFO):
    """Function to setup a custom logger"""
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    # Also log to console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Setup individual loggers
integration_logger = setup_logger("integration", LOG_DIR / "integration.log")
performance_logger = setup_logger("performance", LOG_DIR / "performance.log")
error_logger = setup_logger("error", LOG_DIR / "error.log", level=logging.ERROR)


def log_performance_metrics():
    """Log performance metrics"""
    try:
        import psutil

        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        performance_logger.info(
            f"System Metrics - CPU: {cpu_percent}%, "
            f"Memory Used: {memory.percent}%, "
            f"Available: {memory.available / (1024 * 1024 * 1024):.2f}GB"
        )

        # Process specific metrics
        for proc in psutil.process_iter(["name", "cpu_percent", "memory_percent"]):
            if "codeium" in proc.info["name"].lower() or "windsurf" in proc.info["name"].lower():
                performance_logger.info(
                    f"Process: {proc.info['name']}, "
                    f"CPU: {proc.info['cpu_percent']}%, "
                    f"Memory: {proc.info['memory_percent']}%"
                )
    except Exception:
        error_logger.exception("Error logging performance metrics")
