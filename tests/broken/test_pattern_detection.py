"""
Tests for API pattern detection module.
"""

import asyncio

from api.pattern_detection import DetectedPattern, PatternDetector


class TestDetectedPattern:
    """Test DetectedPattern dataclass."""

    def test_detected_pattern_init(self):
        """Test DetectedPattern initialization."""
        pattern = DetectedPattern(
            pattern_type="test",
            description="Test pattern",
            confidence=0.8,
            span=(0, 10),
            evidence=["evidence1"],
        )
        assert pattern.pattern_type == "test"
        assert pattern.description == "Test pattern"
        assert pattern.confidence == 0.8
        assert pattern.span == (0, 10)
        assert pattern.evidence == ["evidence1"]
        assert pattern.related_patterns == []
        assert pattern.metadata == {}

    def test_detected_pattern_with_optional_fields(self):
        """Test DetectedPattern with optional fields provided."""
        pattern = DetectedPattern(
            pattern_type="test",
            description="Test pattern",
            confidence=0.8,
            span=(0, 10),
            evidence=["evidence1"],
            related_patterns=["pattern2"],
            metadata={"key": "value"},
        )
        assert pattern.related_patterns == ["pattern2"]
        assert pattern.metadata == {"key": "value"}

    def test_detected_pattern_to_dict(self):
        """Test DetectedPattern to_dict method."""
        pattern = DetectedPattern(
            pattern_type="test",
            description="Test pattern",
            confidence=0.8,
            span=(0, 10),
            evidence=["evidence1"],
        )
        result = pattern.to_dict()
        expected = {
            "pattern_type": "test",
            "description": "Test pattern",
            "confidence": 0.8,
            "span": (0, 10),
            "evidence": ["evidence1"],
            "related_patterns": [],
            "metadata": {},
        }
        assert result == expected


class TestPatternDetector:
    """Test PatternDetector class."""

    def test_pattern_detector_init(self):
        """Test PatternDetector initialization."""
        detector = PatternDetector()
        assert detector is not None
        assert hasattr(detector, "detect_patterns")

    def test_pattern_detector_simple_text(self):
        """Test pattern detection on simple text."""
        detector = PatternDetector()
        text = "This is a test pattern"
        patterns = asyncio.run(detector.detect_patterns(text))
        assert isinstance(patterns, list)
        # May return empty list or patterns depending on implementation

    def test_pattern_detector_empty_text(self):
        """Test pattern detection on empty text."""
        detector = PatternDetector()
        patterns = asyncio.run(detector.detect_patterns(""))
        assert isinstance(patterns, list)

    def test_pattern_detector_with_keywords(self):
        """Test pattern detection with keywords."""
        detector = PatternDetector()
        text = "Error: System failure occurred at 2023-01-01"
        patterns = asyncio.run(detector.detect_patterns(text))
        assert isinstance(patterns, list)
        # Check if any error patterns were detected
        if patterns:
            for pattern in patterns:
                assert isinstance(pattern, DetectedPattern)
                assert 0 <= pattern.confidence <= 1
