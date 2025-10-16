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
Core utility functions for rate-limiting and API interaction management.
"""

import logging
import random
import time
from typing import Callable, TypeVar

from openai import RateLimitError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T")

"""
Core utility functions for rate-limiting and API interaction management.
"""
import logging
from typing import TypeVar

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

T = TypeVar("T")


def rate_limit_safe_call(func: Callable[[], T], retries: int = 5) -> T:
    """
    Execute a function with rate-limit awareness and exponential backoff.

    Args:
        func: The function to execute
        retries: Maximum number of retry attempts (default: 5)

    Returns:
        The result of the function execution

    Raises:
        RateLimitError: If rate limit is hit after all retries
    """
    for attempt in range(retries):
        try:
            return func()
        except RateLimitError:
            if attempt == retries - 1:
                logger.error(
                    "❌ Rate limit exceeded after all retries, switching to mock mode"
                )
                return {"mock": True}

            sleep_time = (2**attempt) + random.uniform(0, 1)
            logger.warning(f"⚠️ Rate limit hit, retrying in {sleep_time:.2f}s...")
            time.sleep(sleep_time)

    raise RateLimitError("Rate limit exceeded after maximum retries")
