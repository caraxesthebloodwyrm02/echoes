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

"""Shadow mode runner for detectors."""

import random
import time
from datetime import datetime, timedelta

from detectors import DetectorManager
from detectors.anomaly_detector import AnomalyDetector


def run_shadow_mode(duration_days: int = 7):
    """Run detectors in shadow mode for the specified duration."""
    print(f"Starting shadow mode for {duration_days} days...")

    # Initialize detector manager
    manager = DetectorManager()

    # Register detectors
    anomaly_detector = AnomalyDetector()
    manager.register_detector(anomaly_detector)

    # Enable shadow mode for all detectors
    manager.enable_shadow_mode_all(duration_days)

    # Simulate data processing for the duration
    end_time = datetime.now() + timedelta(days=duration_days)

    print("Shadow mode active. Processing simulated data...")
    print("Press Ctrl+C to stop early")

    try:
        while datetime.now() < end_time:
            # Simulate processing random data
            test_value = random.gauss(100, 10)  # Normal distribution around 100

            # Occasionally inject anomalies
            if random.random() < 0.1:  # 10% chance
                test_value = random.choice([50, 150])  # Clear anomalies

            # Process through detectors
            result = anomaly_detector.process(test_value)

            if result:
                status = "SHADOW" if result.shadow_mode else "LIVE"
                print(
                    f"[{status}] {result.detector_name}: {result.tier.value} "
                    f"(confidence: {result.confidence:.2f}) - {result.action_taken or 'No action'}"
                )

            # Wait a bit between detections
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping shadow mode early...")

    # Show final metrics
    print("\nFinal Metrics:")
    metrics = manager.get_all_metrics()
    for detector_name, detector_metrics in metrics.items():
        print(f"\n{detector_name}:")
        print(f"  Total detections: {detector_metrics['total_detections']}")
        print(f"  By tier: {detector_metrics['by_tier']}")
        print(f"  Actions taken: {detector_metrics['actions_taken']}")
        print(f"  Shadow mode active: {detector_metrics['shadow_mode_active']}")


if __name__ == "__main__":
    run_shadow_mode(7)
