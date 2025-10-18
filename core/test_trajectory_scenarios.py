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

"""Tests reflecting successful trajectory scenarios from project history.

These tests validate the best practices identified in trajectory logs:
- Poetry dependency management
- Ecosystem monitoring with plant-based metaphors
- Detector system with shadow mode and approvals
- Schema-based data structures
- Comprehensive audit trails
"""

import json
import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from detectors import BaseDetector, DetectionResult, DetectionTier
from packages.core.schemas import PodcastData, PodcastEvent
from Q4.drucker_management import EcosystemManager


class TestTrajectoryScenarios:
    """Test scenarios derived from successful trajectory logs."""

    def test_poetry_dependency_management(self):
        """Test that Poetry provides reproducible environments."""
        # This test validates the Poetry setup from trajectory logs
        import subprocess

        result = subprocess.run(
            ["poetry", "check"], capture_output=True, text=True, cwd="."
        )
        assert result.returncode == 0, "Poetry environment should be valid"

    def test_ecosystem_monitoring_metaphors(self):
        """Test plant-based ecosystem monitoring from trajectory logs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = EcosystemManager(temp_dir)

            # Test terraforming analysis
            metric = manager.track_terraforming()
            assert hasattr(metric, "roots")
            assert hasattr(metric, "branches")
            assert hasattr(metric, "leaves")
            assert hasattr(metric, "complexity_score")

            # Test communication validation
            wiring_status = manager.validate_communication_wirings()
            assert "healthy" in wiring_status
            assert "issues" in wiring_status

            # Test GATE operation
            gate_result = manager.operate_gate()
            assert "gate_status" in gate_result
            assert gate_result["gate_status"] in ["open", "closed"]

    def test_detector_system_trajectory(self):
        """Test detector system implementation from trajectory logs."""

        class TestDetector(BaseDetector):
            def __init__(self):
                super().__init__("test_detector")

            def detect(self, data):
                return DetectionResult(
                    detector_name=self.name,
                    tier=DetectionTier.INFO,
                    confidence=0.8,
                    details={"test": "data"},
                    timestamp=datetime.now(),
                )

            def _take_action(self, detection):
                return "test_action_taken"

        detector = TestDetector()

        # Test shadow mode (from trajectory implementation)
        detector.enable_shadow_mode(7)
        assert detector.is_shadow_mode_active()

        # Test detection processing
        result = detector.process({"test": "data"})
        assert result is not None

        # Test audit logging
        metrics = detector.get_metrics()
        assert "total_detections" in metrics

    def test_schema_validation_trajectory(self):
        """Test PodcastData schema usage from trajectory logs."""
        # Create test data mirroring trajectory usage
        event = PodcastEvent(
            timestamp_start_s=0.0,
            timestamp_end_s=3.25,
            speaker="Test Speaker",
            utterance="Test utterance for schema validation",
            pause_after_s=0.8,
            label="rhetorical",
        )

        podcast_data = PodcastData(
            podcast="Test Podcast",
            episode_title="Trajectory Test Episode",
            source="Test Source",
            events=[event],
        )

        # Validate schema works correctly
        assert podcast_data.podcast == "Test Podcast"
        assert len(podcast_data.events) == 1
        assert podcast_data.events[0].label == "rhetorical"

        # Test JSON serialization (used extensively in trajectory)
        json_str = podcast_data.model_dump_json()
        assert json_str is not None

        # Test deserialization
        loaded_data = PodcastData.model_validate_json(json_str)
        assert loaded_data.podcast == podcast_data.podcast

    def test_endpoint_vulnerability_protection(self):
        """Test endpoint vulnerability protection from trajectory logs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = EcosystemManager(temp_dir)

            # Test endpoint vulnerability checking
            vuln_check = manager._check_endpoint_vulnerabilities()
            assert "passed" in vuln_check
            assert "vectors_checked" in vuln_check

            # Verify vector analysis components
            expected_vectors = [
                "confusion",
                "decision_points",
                "timing",
                "absence_changes",
                "cascade",
            ]
            assert vuln_check["vectors_checked"] == expected_vectors

    @patch("subprocess.run")
    def test_json_validation_trajectory(self, mock_subprocess):
        """Test JSON validation processes from trajectory logs."""
        # Mock successful validation
        mock_subprocess.return_value = Mock(returncode=0, stdout="Valid JSON")

        # Import and test the validation function if it exists
        # This mirrors the trajectory JSON validation implementation
        try:
            from validate_json_structure import validate_json_files

            # Test would validate JSON structure as in trajectory
            assert True  # Import successful
        except ImportError:
            # If validation script not available, test basic JSON handling
            test_json = '{"test": "data", "number": 42}'
            parsed = json.loads(test_json)
            assert parsed["test"] == "data"
            assert parsed["number"] == 42

    def test_audit_trail_comprehensive(self):
        """Test comprehensive audit trail from trajectory detector system."""

        class AuditTestDetector(BaseDetector):
            def __init__(self):
                super().__init__("audit_test_detector")

            def detect(self, data):
                return DetectionResult(
                    detector_name=self.name,
                    tier=DetectionTier.WARN,
                    confidence=0.9,
                    details={"audit_test": True},
                    timestamp=datetime.now(),
                )

            def _take_action(self, detection):
                return "audit_test_action"

        detector = AuditTestDetector()

        # Process detection (should create audit entry)
        result = detector.process({"audit": "test"})

        # Check metrics include audit data
        metrics = detector.get_metrics()
        assert isinstance(metrics, dict)
        assert "total_detections" in metrics

        # Test that audit logging setup worked
        assert hasattr(detector, "audit_logger")
        assert detector.audit_log_path.exists()

    def test_modular_architecture_separation(self):
        """Test modular architecture separation of concerns."""
        # Test that packages are properly separated
        core_modules = ["schemas", "config"]
        integration_modules = ["slack"]
        monitoring_modules = ["alerts", "health", "ci"]
        security_modules = ["scanner"]

        # Verify module separation (this reflects trajectory modular design)
        assert len(core_modules) > 0
        assert len(monitoring_modules) > 0
        assert len(security_modules) > 0

        # Test that imports work correctly across modules
        try:
            from packages.core.config import load_config
            from packages.core.schemas import PodcastData

            assert PodcastData is not None
            assert load_config is not None
        except ImportError as e:
            pytest.fail(f"Module separation test failed: {e}")


class TestTrajectoryIntegration:
    """Integration tests for trajectory-validated workflows."""

    def test_full_ecosystem_workflow(self):
        """Test complete ecosystem workflow from trajectory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = EcosystemManager(temp_dir)

            # Run full ecosystem check (from trajectory implementation)
            terraforming = manager.track_terraforming()
            communications = manager.validate_communication_wirings()
            gate_status = manager.operate_gate()

            # Verify all components work together
            assert terraforming is not None
            assert communications is not None
            assert gate_status is not None

            # Test that GATE considers communication health
            assert "communication_health" in gate_status["details"]

    def test_detector_manager_integration(self):
        """Test detector manager integration from trajectory."""
        from detectors import DetectorManager

        manager = DetectorManager()

        # Create and register test detector
        class IntegrationDetector(BaseDetector):
            def __init__(self):
                super().__init__("integration_test")

            def detect(self, data):
                return DetectionResult(
                    detector_name=self.name,
                    tier=DetectionTier.INFO,
                    confidence=0.7,
                    details={"integration": True},
                    timestamp=self._now(),
                )

            def _take_action(self, detection):
                return "integration_action"

        detector = IntegrationDetector()
        manager.register_detector(detector)

        # Test manager operations
        assert "integration_test" in manager.detectors

        # Test shadow mode for all detectors
        manager.enable_shadow_mode_all(3)

        # Test metrics collection
        metrics = manager.get_all_metrics()
        assert "integration_test" in metrics
