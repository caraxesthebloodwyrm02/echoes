#!/usr/bin/env python3
"""Minimal test of detector system."""

import sys
import os
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
