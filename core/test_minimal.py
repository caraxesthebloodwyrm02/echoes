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

"""Minimal test of detector system."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from detectors.anomaly_detector import AnomalyDetector


def test_detector():
    """Basic detector test."""
    print("Testing AnomalyDetector...")

    # Create detector with minimal config
    detector = AnomalyDetector()

    # Test normal value
    result = detector.process(100)
    print(f"Normal value (100): {result}")

    # Test anomalous value
    result = detector.process(200)
    print(f"Anomalous value (200): {result}")

    if result:
        print(f"Tier: {result.tier}")
        print(f"Confidence: {result.confidence}")
        print(f"Shadow mode: {result.shadow_mode}")

    print("Test completed!")


if __name__ == "__main__":
    test_detector()
