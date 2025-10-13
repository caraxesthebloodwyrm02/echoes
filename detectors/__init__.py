"""Base detector framework with shadow mode and audit logging."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
import json
import logging
from pathlib import Path
import uuid

from packages.core.config import load_config


class DetectionTier(Enum):
    """Detection severity tiers."""
    INFO = "info"
    WARN = "warn"
    BLOCK = "block"


class DetectorMode(Enum):
    """Detector operating modes."""
    LIVE = "live"  # Take actions
    SHADOW = "shadow"  # Log only, no actions
    DISABLED = "disabled"  # Completely disabled


@dataclass
class DetectionResult:
    """Result of a detection operation."""
    detector_name: str
    tier: DetectionTier
    confidence: float
    details: Dict[str, Any]
    timestamp: datetime
    shadow_mode: bool = False
    approved: bool = False
    action_taken: Optional[str] = None


@dataclass
class PendingApproval:
    """Pending approval for WARN/BLOCK detections."""
    id: str
    detection_result: DetectionResult
    requested_at: datetime
    approved: bool = False
    reviewed_at: Optional[datetime] = None
    reviewer: Optional[str] = None
    notes: Optional[str] = None


class BaseDetector(ABC):
    """Abstract base class for all detectors."""

    def __init__(self, name: str, config=None):
        self.name = name
        self.config = config or load_config()
        self.logger = logging.getLogger(f"detector.{name}")
        self.mode = DetectorMode.LIVE
        self.shadow_start: Optional[datetime] = None
        self.shadow_duration = timedelta(days=7)
        self.pending_approvals: Dict[str, PendingApproval] = {}

        # Setup audit logging
        self.audit_log_path = self.config.logs_dir / "detector_audit.log"
        self._setup_audit_logging()

    def _setup_audit_logging(self):
        """Setup dedicated audit logging."""
        self.audit_logger = logging.getLogger(f"audit.{self.name}")
        self.audit_logger.setLevel(logging.INFO)

        # Remove any existing handlers
        for handler in self.audit_logger.handlers[:]:
            self.audit_logger.removeHandler(handler)

        # Add file handler for audit log
        audit_handler = logging.FileHandler(self.audit_log_path)
        audit_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        self.audit_logger.addHandler(audit_handler)
        self.audit_logger.propagate = False

    def enable_shadow_mode(self, duration_days: int = 7):
        """Enable shadow mode for the specified duration."""
        self.mode = DetectorMode.SHADOW
        self.shadow_start = datetime.now()
        self.shadow_duration = timedelta(days=duration_days)
        self.logger.info(f"Shadow mode enabled for {duration_days} days")

    def disable_shadow_mode(self):
        """Disable shadow mode and return to live mode."""
        self.mode = DetectorMode.LIVE
        self.shadow_start = None
        self.logger.info("Shadow mode disabled, returning to live mode")

    def is_shadow_mode_active(self) -> bool:
        """Check if shadow mode is currently active."""
        if self.mode != DetectorMode.SHADOW or not self.shadow_start:
            return False

        return datetime.now() - self.shadow_start < self.shadow_duration

    @abstractmethod
    def detect(self, data: Any) -> Optional[DetectionResult]:
        """Perform detection on the given data."""
        pass

    def _should_take_action(self, result: DetectionResult) -> bool:
        """Determine if action should be taken based on mode and approval."""
        if self.mode == DetectorMode.DISABLED:
            return False

        if self.mode == DetectorMode.SHADOW:
            return False  # Shadow mode: never take action

        # Live mode: check approval for WARN/BLOCK
        if result.tier in [DetectionTier.WARN, DetectionTier.BLOCK]:
            return result.approved

        return True  # INFO tier always acts in live mode

    def _log_decision(self, result: DetectionResult, action_taken: Optional[str]):
        """Log every decision for audit purposes."""
        audit_entry = {
            "timestamp": result.timestamp.isoformat(),
            "detector": result.detector_name,
            "tier": result.tier.value,
            "confidence": result.confidence,
            "details": result.details,
            "shadow_mode": result.shadow_mode,
            "approved": result.approved,
            "action_taken": action_taken,
            "mode": self.mode.value
        }

        self.audit_logger.info(json.dumps(audit_entry))

    def process(self, data: Any) -> Optional[DetectionResult]:
        """Main processing method that handles detection and action logic."""
        result = self.detect(data)
        if not result:
            return None

        # Update shadow mode status
        result.shadow_mode = self.is_shadow_mode_active()

        # Check if approval is needed for WARN/BLOCK
        if (result.tier in [DetectionTier.WARN, DetectionTier.BLOCK] and
            not result.shadow_mode and
            not result.approved):
            # Create pending approval
            approval_id = str(uuid.uuid4())
            pending = PendingApproval(
                id=approval_id,
                detection_result=result,
                requested_at=datetime.now()
            )
            self.pending_approvals[approval_id] = pending
            self.logger.info(f"Pending approval created: {approval_id} for {result.tier.value}")
            return result  # Return without taking action

        # Determine if action should be taken
        should_act = self._should_take_action(result)
        action_taken = None

        if should_act:
            action_taken = self._take_action(result)
            result.action_taken = action_taken

        # Log the decision
        self._log_decision(result, action_taken)

        return result

    @abstractmethod
    def _take_action(self, result: DetectionResult) -> str:
        """Take the appropriate action based on detection result."""
        pass

    def approve_detection(self, approval_id: str, reviewer: str = "system", notes: str = None) -> bool:
        """Approve a pending detection and take action."""
        if approval_id not in self.pending_approvals:
            self.logger.warning(f"Approval ID not found: {approval_id}")
            return False

        pending = self.pending_approvals[approval_id]
        pending.approved = True
        pending.reviewed_at = datetime.now()
        pending.reviewer = reviewer
        pending.notes = notes

        # Update the detection result
        pending.detection_result.approved = True

        # Take action now that it's approved
        action_taken = self._take_action(pending.detection_result)
        pending.detection_result.action_taken = action_taken

        # Log the decision
        self._log_decision(pending.detection_result, action_taken)

        # Remove from pending
        del self.pending_approvals[approval_id]

        self.logger.info(f"Detection approved and action taken: {approval_id}")
        return True

    def reject_detection(self, approval_id: str, reviewer: str = "system", notes: str = None) -> bool:
        """Reject a pending detection."""
        if approval_id not in self.pending_approvals:
            self.logger.warning(f"Approval ID not found: {approval_id}")
            return False

        pending = self.pending_approvals[approval_id]
        pending.approved = False
        pending.reviewed_at = datetime.now()
        pending.reviewer = reviewer
        pending.notes = notes

        # Log rejection
        rejection_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": "rejection",
            "approval_id": approval_id,
            "detector": pending.detection_result.detector_name,
            "tier": pending.detection_result.tier.value,
            "confidence": pending.detection_result.confidence,
            "reviewer": reviewer,
            "notes": notes
        }
        self.audit_logger.info(json.dumps(rejection_entry))

        # Remove from pending
        del self.pending_approvals[approval_id]

        self.logger.info(f"Detection rejected: {approval_id}")
        return True

    def get_pending_approvals(self) -> List[PendingApproval]:
        """Get list of pending approvals."""
        return list(self.pending_approvals.values())

    def get_metrics(self) -> Dict[str, Any]:
        # Parse audit log for metrics
        metrics = {
            "total_detections": 0,
            "by_tier": {tier.value: 0 for tier in DetectionTier},
            "actions_taken": 0,
            "false_positives": 0,  # Would need manual labeling
            "false_negatives": 0,  # Would need manual labeling
            "shadow_mode_active": self.is_shadow_mode_active()
        }

        if self.audit_log_path.exists():
            try:
                with open(self.audit_log_path, 'r') as f:
                    for line in f:
                        if f"audit.{self.name}" in line:
                            # Parse JSON from log line
                            try:
                                json_start = line.find('{')
                                if json_start >= 0:
                                    entry = json.loads(line[json_start:])
                                    metrics["total_detections"] += 1
                                    metrics["by_tier"][entry["tier"]] += 1
                                    if entry.get("action_taken"):
                                        metrics["actions_taken"] += 1
                            except json.JSONDecodeError:
                                continue
            except Exception as e:
                self.logger.error(f"Error reading audit log: {e}")

        return metrics


class DetectorManager:
    """Manages multiple detectors."""

    def __init__(self, config=None):
        self.config = config or load_config()
        self.detectors: Dict[str, BaseDetector] = {}
        self.logger = logging.getLogger("detector_manager")

    def register_detector(self, detector: BaseDetector):
        """Register a detector."""
        self.detectors[detector.name] = detector
        self.logger.info(f"Registered detector: {detector.name}")

    def enable_shadow_mode_all(self, duration_days: int = 7):
        """Enable shadow mode for all detectors."""
        for detector in self.detectors.values():
            detector.enable_shadow_mode(duration_days)
        self.logger.info(f"Shadow mode enabled for all detectors ({duration_days} days)")

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get metrics for all detectors."""
        return {
            name: detector.get_metrics()
            for name, detector in self.detectors.items()
        }
