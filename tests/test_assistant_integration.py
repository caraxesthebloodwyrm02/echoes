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

# MIT License
#
# Copyright (c) 2025 Echoes Project

"""
Tests for Assistant Integration system
"""

from datetime import datetime

import pytest

from ai_modules.assistant_integration import (
    AssistantIntegration,
    OpenAIConfig,
    PatternDetector,
)


class TestPatternDetector:
    """Test pattern detection"""

    @pytest.fixture
    def detector(self):
        return PatternDetector()

    def test_detect_infinite_loop(self, detector):
        """Test infinite loop detection"""
        # Should detect
        assert detector.detect_infinite_loop(execution_time_ms=35000, iterations=1500)

        # Should not detect
        assert not detector.detect_infinite_loop(execution_time_ms=5000, iterations=100)

    def test_detect_security_degradation(self, detector):
        """Test security degradation detection"""
        history = [0.95, 0.94, 0.93, 0.92, 0.91, 0.70, 0.68, 0.65]

        assert detector.detect_security_degradation(history)

    def test_detect_quality_degradation(self, detector):
        """Test quality degradation detection"""
        metrics = {
            "test_coverage": 75,
            "avg_complexity": 12,
            "technical_debt_ratio": 0.25,
        }

        assert detector.detect_quality_degradation(metrics)

    def test_detect_trajectory_halt(self, detector):
        """Test trajectory halt detection"""
        progress = [1.0, 2.0, 3.0, 4.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]

        assert detector.detect_trajectory_halt(progress)

    def test_detect_rate_limit_cascade(self, detector):
        """Test rate limit cascade detection"""
        errors = [
            {"error_type": "rate_limit", "timestamp": datetime.now()},
            {"error_type": "rate_limit", "timestamp": datetime.now()},
            {"error_type": "rate_limit", "timestamp": datetime.now()},
        ]

        assert detector.detect_rate_limit_cascade(errors)


class TestAssistantIntegration:
    """Test assistant integration"""

    def test_openai_config_validation(self):
        """Test OpenAI config validation"""
        # Should fail without API key
        with pytest.raises(ValueError):
            OpenAIConfig(api_key="")

        # Should succeed with API key
        config = OpenAIConfig(api_key="test-key")
        assert config.api_key == "test-key"
        assert config.model == "gpt-4o-mini"

    def test_openai_config_extra_forbid(self):
        """Test that extra fields are forbidden"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            OpenAIConfig(api_key="test-key", unknown_field="value")

    def test_assistant_initialization(self):
        """Test assistant initialization"""
        config = OpenAIConfig(api_key="test-key")
        assistant = AssistantIntegration(openai_config=config)

        assert assistant.config.api_key == "test-key"
        assert assistant.detector is not None
        assert assistant.response_history == []

    def test_pattern_processing(self):
        """Test pattern processing"""
        config = OpenAIConfig(api_key="test-key")
        assistant = AssistantIntegration(openai_config=config)

        context = {
            "execution_time_ms": 35000,
            "iterations": 1500,
            "last_checkpoint": "line 42",
            "code_section": "while True: pass",
        }

        # This will fail without real API key, but tests the structure
        try:
            result = assistant.process_pattern("infinite_loop", context)
            assert result["pattern"] == "infinite_loop"
            assert result["severity"] == "CRITICAL"
        except Exception as e:
            # Expected without real API key
            assert "API" in str(e) or "key" in str(e).lower()

    def test_response_history(self):
        """Test response history tracking"""
        config = OpenAIConfig(api_key="test-key")
        assistant = AssistantIntegration(openai_config=config)

        # Manually add to history for testing
        assistant.response_history.append(
            {
                "pattern": "test",
                "severity": "HIGH",
                "timestamp": datetime.now().isoformat(),
            }
        )

        history = assistant.get_response_history()
        assert len(history) == 1
        assert history[0]["pattern"] == "test"


class TestIntegrationScenarios:
    """Test real-world scenarios"""

    def test_infinite_loop_scenario(self):
        """Test infinite loop handling scenario"""
        detector = PatternDetector()

        # Simulate infinite loop
        execution_time = 45000  # 45 seconds
        iterations = 5000

        is_loop = detector.detect_infinite_loop(execution_time, iterations)
        assert is_loop

    def test_security_degradation_scenario(self):
        """Test security degradation scenario"""
        detector = PatternDetector()

        # Simulate security score drop
        history = [0.95] * 5 + [0.70] * 5  # Drop from 95% to 70%

        is_degraded = detector.detect_security_degradation(history)
        assert is_degraded

    def test_quality_degradation_scenario(self):
        """Test quality degradation scenario"""
        detector = PatternDetector()

        metrics = {
            "test_coverage": 60,  # Below 80%
            "avg_complexity": 15,  # Above 10
            "technical_debt_ratio": 0.30,  # Above 20%
        }

        is_degraded = detector.detect_quality_degradation(metrics)
        assert is_degraded

    def test_trajectory_halt_scenario(self):
        """Test trajectory halt scenario"""
        detector = PatternDetector()

        # Simulate no progress
        progress = list(range(1, 6)) + [5] * 10  # Progress stops at 5

        is_halted = detector.detect_trajectory_halt(progress)
        assert is_halted


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
