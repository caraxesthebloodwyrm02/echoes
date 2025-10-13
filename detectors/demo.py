#!/usr/bin/env python3
"""Demo script showing detector system functionality."""

import random
from datetime import datetime

from detectors import DetectorManager
from detectors.anomaly_detector import AnomalyDetector


def demo_basic_detection():
    """Demonstrate basic detection functionality."""
    print("=== Basic Detection Demo ===")

    manager = DetectorManager()
    detector = AnomalyDetector()
    manager.register_detector(detector)

    # Test normal values
    print("\nTesting normal values:")
    for i in range(3):
        value = random.gauss(100, 5)  # Normal distribution
        result = detector.process(value)
        if result:
            print(f"  Value: {value:.1f} -> {result.tier.value} (confidence: {result.confidence:.2f})")

    # Test anomalous values
    print("\nTesting anomalous values:")
    anomalous_values = [50, 150, 200, 10]
    for value in anomalous_values:
        result = detector.process(value)
        if result:
            print(f"  Value: {value} -> {result.tier.value} (confidence: {result.confidence:.2f})")
            if result.tier in ['warn', 'block']:
                print("    ^^^ Would require approval in live mode ^^^")


def demo_shadow_mode():
    """Demonstrate shadow mode functionality."""
    print("\n=== Shadow Mode Demo ===")

    detector = AnomalyDetector()
    detector.enable_shadow_mode(duration_days=1)  # Short duration for demo

    print("Shadow mode enabled for 1 day")

    # Process anomalous value in shadow mode
    result = detector.process(200)  # Clear anomaly
    if result:
        print(f"Shadow mode result: {result.tier.value} (shadow: {result.shadow_mode})")
        print(f"Action taken: {result.action_taken or 'None (shadow mode)'}")

    print(f"Shadow mode active: {detector.is_shadow_mode_active()}")


def demo_approvals():
    """Demonstrate approval workflow."""
    print("\n=== Approval Workflow Demo ===")

    detector = AnomalyDetector()
    detector.mode = detector.mode.LIVE  # Ensure live mode

    # Process value that should trigger WARN/BLOCK
    result = detector.process(180)  # Should trigger detection
    if result:
        print(f"Detection result: {result.tier.value}")
        print(f"Approved: {result.approved}")
        print(f"Action taken: {result.action_taken or 'None (pending approval)'}")

    # Check pending approvals
    pending = detector.get_pending_approvals()
    print(f"\nPending approvals: {len(pending)}")
    for approval in pending:
        print(f"  ID: {approval.id}")
        print(f"  Tier: {approval.detection_result.tier.value}")
        print(f"  Requested: {approval.requested_at}")

        # Approve it
        success = detector.approve_detection(approval.id, reviewer="demo_user", notes="Approved for demo")
        print(f"  Approved: {success}")

        if success:
            print(f"  Action taken after approval: {approval.detection_result.action_taken}")


def demo_metrics():
    """Demonstrate metrics collection."""
    print("\n=== Metrics Demo ===")

    manager = DetectorManager()
    detector = AnomalyDetector()
    manager.register_detector(detector)

    # Generate some test data
    for _ in range(10):
        value = random.gauss(100, 15)  # Wider distribution to trigger some detections
        detector.process(value)

    # Get metrics
    metrics = manager.get_all_metrics()
    for detector_name, detector_metrics in metrics.items():
        print(f"\n{detector_name} Metrics:")
        print(f"  Total detections: {detector_metrics['total_detections']}")
        print(f"  By tier: {detector_metrics['by_tier']}")
        print(f"  Actions taken: {detector_metrics['actions_taken']}")
        print(f"  Shadow mode: {detector_metrics['shadow_mode_active']}")


if __name__ == "__main__":
    print("Detector System Demo")
    print("=" * 50)

    demo_basic_detection()
    demo_shadow_mode()
    demo_approvals()
    demo_metrics()

    print("\n" + "=" * 50)
    print("Demo complete!")
    print("\nTo run shadow mode for 7 days: python detectors/shadow_runner.py")
    print("To view dashboard: python detectors/dashboard.py")
