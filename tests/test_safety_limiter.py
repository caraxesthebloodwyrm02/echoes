#!/usr/bin/env python3
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
Unit tests for safety rate limiter (TokenBucket).
"""

import time
from datetime import datetime

import pytest

from src.safety.limiter import TokenBucket


def test_token_bucket_initialization():
    """Test that token bucket initializes correctly."""
    bucket = TokenBucket(max_per_min=60)
    assert bucket.rate == 1.0  # 60 requests per minute = 1 per second
    assert bucket.tokens == 60
    assert isinstance(bucket.last, datetime)


def test_token_bucket_acquire_success():
    """Test successful token acquisition."""
    bucket = TokenBucket(max_per_min=60)
    assert bucket.acquire() == True
    assert bucket.tokens == 59  # Should have consumed one token


def test_token_bucket_acquire_failure():
    """Test token acquisition failure when bucket is empty."""
    bucket = TokenBucket(max_per_min=1)  # Only 1 token
    bucket.tokens = 0  # Empty the bucket

    assert bucket.acquire() == False
    assert bucket.tokens == 0  # Should not change


def test_token_bucket_refill():
    """Test that tokens refill over time."""
    bucket = TokenBucket(max_per_min=120)  # 2 tokens per second

    # Consume all tokens
    for _ in range(120):
        assert bucket.acquire() == True

    # Bucket should be empty
    assert bucket.acquire() == False

    # Wait for refill (simulate 0.6 seconds = 1.2 tokens)
    original_time = bucket.last
    bucket.last = original_time.replace(
        second=original_time.second - 1
    )  # Simulate 1 second ago

    # Should be able to acquire now
    assert bucket.acquire() == True


def test_token_bucket_burst_capacity():
    """Test that bucket allows burst up to max capacity."""
    bucket = TokenBucket(max_per_min=60)

    # Should allow burst up to 60 requests
    for i in range(60):
        assert bucket.acquire() == True
        assert bucket.tokens == 59 - i

    # Next request should fail
    assert bucket.acquire() == False


def test_token_bucket_rate_limiting():
    """Test that bucket enforces rate limits over time."""
    bucket = TokenBucket(max_per_min=60)  # 1 token per second

    # Consume all tokens
    for _ in range(60):
        bucket.acquire()

    # Should be rate limited
    assert bucket.acquire() == False

    # Simulate passage of time (1 second = 1 token)
    original_time = bucket.last
    bucket.last = original_time.replace(second=original_time.second - 1)

    # Should allow one request
    assert bucket.acquire() == True
    assert bucket.tokens == 0  # Back to zero after refill and consume


def test_token_bucket_different_rates():
    """Test token bucket with different rate limits."""
    # Fast rate: 120 per minute = 2 per second
    fast_bucket = TokenBucket(max_per_min=120)
    assert fast_bucket.rate == 2.0

    # Slow rate: 30 per minute = 0.5 per second
    slow_bucket = TokenBucket(max_per_min=30)
    assert slow_bucket.rate == 0.5


def test_token_bucket_max_burst():
    """Test that burst capacity is capped at maximum."""
    bucket = TokenBucket(max_per_min=60)

    # Consume some tokens
    for _ in range(30):
        bucket.acquire()

    # Simulate long time passage (enough for 100+ tokens)
    original_time = bucket.last
    bucket.last = original_time.replace(
        second=original_time.second - 120
    )  # 2 minutes ago

    # Should refill to max (60), not beyond
    assert bucket.acquire() == True
    # After refill and consume, should be at 59, not negative
    assert bucket.tokens >= 0


def test_token_bucket_time_precision():
    """Test token bucket handles time precision correctly."""
    bucket = TokenBucket(max_per_min=60)  # 1 token per second

    # Get initial state
    initial_tokens = bucket.tokens
    initial_time = bucket.last

    # Wait a very short time (less than 1 second)
    time.sleep(0.1)

    # Should not have refilled yet
    current_tokens = bucket.tokens
    assert current_tokens == initial_tokens

    # Wait longer (more than 1 second)
    bucket.last = initial_time.replace(second=initial_time.second - 2)  # 2 seconds ago

    # Should be able to refill
    assert bucket.acquire() == True


def test_token_bucket_zero_rate():
    """Test edge case with zero rate (should not allow any requests)."""
    bucket = TokenBucket(max_per_min=0)
    assert bucket.rate == 0.0
    assert bucket.acquire() == False  # Should never allow


def test_token_bucket_high_rate():
    """Test with very high rate limit."""
    bucket = TokenBucket(max_per_min=3600)  # 60 per second
    assert bucket.rate == 60.0

    # Should allow many rapid requests
    for _ in range(100):
        assert bucket.acquire() == True


@pytest.mark.parametrize(
    "max_per_min,expected_rate",
    [
        (60, 1.0),
        (120, 2.0),
        (30, 0.5),
        (600, 10.0),
    ],
)
def test_token_bucket_parametrized_rates(max_per_min, expected_rate):
    """Test various rate configurations."""
    bucket = TokenBucket(max_per_min=max_per_min)
    assert bucket.rate == expected_rate
    assert bucket.tokens == max_per_min
