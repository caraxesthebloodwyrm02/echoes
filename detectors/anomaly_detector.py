"""Sample anomaly detector for demonstration."""

import random
from datetime import datetime
from typing import Any, Dict, Optional

from . import BaseDetector, DetectionResult, DetectionTier


class AnomalyDetector(BaseDetector):
    """Sample detector that detects anomalies based on simple heuristics."""

    def __init__(self, config=None):
        super().__init__("anomaly_detector", config)
        self.baseline_values = [100, 105, 98, 102, 99]  # Sample baseline
        self.detection_count = 0

    def detect(self, data: Any) -> Optional[DetectionResult]:
        """Detect anomalies in the provided data."""
        self.detection_count += 1

        # Simple anomaly detection: check if value deviates significantly
        if isinstance(data, (int, float)):
            value = float(data)
            mean = sum(self.baseline_values) / len(self.baseline_values)
            std_dev = (sum((x - mean) ** 2 for x in self.baseline_values) / len(self.baseline_values)) ** 0.5

            # Check against config thresholds
            deviation = abs(value - mean)
            confidence = min(deviation / (std_dev * 2), 1.0) if std_dev > 0 else 0.0

            if confidence >= self.config.confidence_threshold:
                tier = DetectionTier.BLOCK if confidence > 0.8 else DetectionTier.WARN

                return DetectionResult(
                    detector_name=self.name,
                    tier=tier,
                    confidence=confidence,
                    details={
                        "value": value,
                        "mean": mean,
                        "std_dev": std_dev,
                        "deviation": deviation,
                        "detection_count": self.detection_count
                    },
                    timestamp=datetime.now()
                )

        return None

    def _take_action(self, result: DetectionResult) -> str:
        """Take action based on detection result."""
        if result.tier == DetectionTier.BLOCK:
            return f"Blocked anomalous value: {result.details['value']}"
        elif result.tier == DetectionTier.WARN:
            return f"Warned about anomalous value: {result.details['value']}"
        else:
            return f"Logged anomaly: {result.details['value']}"
