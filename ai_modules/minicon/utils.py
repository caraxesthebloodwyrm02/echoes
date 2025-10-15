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

from __future__ import annotations

import random
import signal
import time
from contextlib import contextmanager
from functools import wraps
from threading import Timer
from typing import Any, Callable, Iterable, Optional, Type, TypeVar
from urllib.parse import urlparse

T = TypeVar("T")


def is_valid_youtube_url(url: str) -> bool:
    """Return ``True`` when *url* looks like a valid YouTube link."""
    if not isinstance(url, str) or not url:
        return False
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    hostname = parsed.hostname or ""
    if hostname.startswith("www."):
        hostname = hostname[4:]
    return hostname in {"youtube.com", "youtu.be"}


def retry(
    *,
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    backoff_factor: float = 2.0,
    jitter_seconds: float = 0.0,
    retry_exceptions: Iterable[Type[BaseException]] = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator providing exponential back-off retry semantics."""

    allowed_exceptions = tuple(retry_exceptions)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempts_remaining = max(1, max_attempts)
            current_delay = max(0.0, delay_seconds)
            while True:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions:
                    attempts_remaining -= 1
                    if attempts_remaining <= 0:
                        raise
                    if current_delay > 0:
                        jitter = random.uniform(0, max(0.0, jitter_seconds))
                        time.sleep(current_delay + jitter)
                        current_delay *= max(1.0, backoff_factor)

        return wrapper

    return decorator


@contextmanager
def timeout(seconds: Optional[float]) -> Iterable[None]:
    """Context manager raising ``TimeoutError`` when block exceeds *seconds*."""

    if seconds is None or seconds <= 0:
        yield
        return

    has_alarm = hasattr(signal, "SIGALRM")
    timer: Optional[Timer] = None
    start = time.perf_counter()

    def _raise_timeout() -> None:
        raise TimeoutError(f"Operation timed out after {seconds} seconds")

    if has_alarm:
        previous_handler = signal.getsignal(signal.SIGALRM)

        def _handle_alarm(signum: int, frame: Any) -> None:  # pragma: no cover - system
            raise TimeoutError(f"Operation timed out after {seconds} seconds")

        try:
            signal.signal(signal.SIGALRM, _handle_alarm)
            signal.setitimer(signal.ITIMER_REAL, seconds)
            yield
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
            signal.signal(signal.SIGALRM, previous_handler)
    else:
        timer = Timer(seconds, _raise_timeout)
        timer.start()
        try:
            yield
        finally:
            elapsed = time.perf_counter() - start
            timer.cancel()
            if elapsed > seconds:
                raise TimeoutError(f"Operation timed out after {seconds} seconds")


__all__ = ["is_valid_youtube_url", "retry", "timeout"]
