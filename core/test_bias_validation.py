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
Tests for bias validation functionality.

Comprehensive test suite for src/core/validators.py bias validation.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.core.validators import (
    BiasEvaluation,
    ValidationError,
    ValidationReport,
    Validators,
    validate_bias_json,
)


class TestValidationReport:
    """Test ValidationReport class."""

    def test_empty_report(self):
        """Test empty validation report."""
        report = ValidationReport()
        assert report.is_valid()
        assert len(report.errors) == 0
        assert len(report.warnings) == 0
        assert len(report.metrics) == 0

    def test_report_with_errors(self):
        """Test report with errors."""
        report = ValidationReport()
        report.add_error("Test error")
        report.add_warning("Test warning")
        report.set_metric("test_metric", 42)

        assert not report.is_valid()
        assert len(report.errors) == 1
        assert len(report.warnings) == 1
        assert report.metrics["test_metric"] == 42

    def test_summary_generation(self):
        """Test summary generation."""
        report = ValidationReport()
        report.add_error("Error 1")
        report.add_error("Error 2")

        summary = report.summary()
        assert "❌" in summary
        assert "2 errors" in summary

        # Test passing report
        report = ValidationReport()
        summary = report.summary()
        assert "✅" in summary


class TestBiasEvaluation:
    """Test BiasEvaluation Pydantic model."""

    def test_valid_evaluation(self):
        """Test valid bias evaluation."""
        valid_data = {
            "prompt": "Test prompt",
            "axes": {
                "user_invalidation": {"score": 3, "justification": "Test"},
                "escalation": {"score": 2, "justification": "Test"},
                "personal_expression": {"score": 4, "justification": "Test"},
                "asymmetric_coverage": {"score": 1, "justification": "Test"},
                "refusal": {"score": 5, "justification": "Test"},
            },
        }

        evaluation = BiasEvaluation(**valid_data)
        assert evaluation.prompt == "Test prompt"
        assert len(evaluation.axes) == 5

    def test_invalid_score_range(self):
        """Test invalid score range."""
        invalid_data = {
            "prompt": "Test prompt",
            "axes": {
                "user_invalidation": {"score": 6, "justification": "Test"},  # Score > 5
                "escalation": {"score": 0, "justification": "Test"},  # Score < 1
            },
        }

        with pytest.raises(ValidationError):
            BiasEvaluation(**invalid_data)

    def test_missing_axis(self):
        """Test missing bias axis."""
        invalid_data = {
            "prompt": "Test prompt",
            "axes": {
                "user_invalidation": {"score": 3, "justification": "Test"},
                # Missing other required axes
            },
        }

        with pytest.raises(ValidationError):
            BiasEvaluation(**invalid_data)

    def test_missing_score_field(self):
        """Test missing score field."""
        invalid_data = {
            "prompt": "Test prompt",
            "axes": {
                "user_invalidation": {"justification": "Test"},  # Missing score
            },
        }

        with pytest.raises(ValidationError):
            BiasEvaluation(**invalid_data)


class TestBiasJSONValidation:
    """Test bias JSON file validation."""

    def test_valid_bias_json(self):
        """Test validation of valid bias JSON."""
        valid_data = [
            {
                "prompt": "Test prompt 1",
                "axes": {
                    "user_invalidation": {"score": 3, "justification": "Test"},
                    "escalation": {"score": 2, "justification": "Test"},
                    "personal_expression": {"score": 4, "justification": "Test"},
                    "asymmetric_coverage": {"score": 1, "justification": "Test"},
                    "refusal": {"score": 5, "justification": "Test"},
                },
            },
            {
                "prompt": "Test prompt 2",
                "axes": {
                    "user_invalidation": {"score": 2, "justification": "Test"},
                    "escalation": {"score": 3, "justification": "Test"},
                    "personal_expression": {"score": 1, "justification": "Test"},
                    "asymmetric_coverage": {"score": 4, "justification": "Test"},
                    "refusal": {"score": 5, "justification": "Test"},
                },
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_data, f)
            temp_file = f.name

        try:
            report = validate_bias_json(temp_file)
            assert report.is_valid()
            assert report.metrics["total_evaluations"] == 2
            assert report.metrics["complete_evaluations"] == 2
            assert "mean_bias_score" in report.metrics
        finally:
            Path(temp_file).unlink()

    def test_invalid_json_file(self):
        """Test validation of invalid JSON file."""
        invalid_data = [
            {
                "prompt": "Test prompt",
                "axes": {
                    "user_invalidation": {
                        "score": 6,
                        "justification": "Test",
                    },  # Invalid score
                },
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name

        try:
            report = validate_bias_json(temp_file)
            assert not report.is_valid()
            assert len(report.errors) > 0
        finally:
            Path(temp_file).unlink()

    def test_missing_file(self):
        """Test validation of missing file."""
        report = validate_bias_json("nonexistent_file.json")
        assert not report.is_valid()
        assert len(report.errors) > 0
        assert "File not found" in report.errors[0]

    def test_malformed_json(self):
        """Test validation of malformed JSON."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("invalid json content")
            temp_file = f.name

        try:
            report = validate_bias_json(temp_file)
            assert not report.is_valid()
            assert len(report.errors) > 0
        finally:
            Path(temp_file).unlink()

    def test_empty_file(self):
        """Test validation of empty file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_file = f.name

        try:
            report = validate_bias_json(temp_file)
            assert not report.is_valid()
            assert len(report.errors) > 0
        finally:
            Path(temp_file).unlink()

    def test_metrics_calculation(self):
        """Test metrics calculation."""
        valid_data = [
            {
                "prompt": "Test prompt 1",
                "axes": {
                    "user_invalidation": {"score": 3, "justification": "Test"},
                    "escalation": {"score": 2, "justification": "Test"},
                    "personal_expression": {"score": 4, "justification": "Test"},
                    "asymmetric_coverage": {"score": 1, "justification": "Test"},
                    "refusal": {"score": 5, "justification": "Test"},
                },
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(valid_data, f)
            temp_file = f.name

        try:
            report = validate_bias_json(temp_file)
            assert report.is_valid()
            assert report.metrics["total_evaluations"] == 1
            assert report.metrics["complete_evaluations"] == 1
            assert report.metrics["completeness_ratio"] == 1.0
            assert report.metrics["total_scores"] == 5
            assert report.metrics["mean_bias_score"] == 3.0  # (3+2+4+1+5)/5
        finally:
            Path(temp_file).unlink()


class TestGenericValidation:
    """Test generic validation utilities."""

    def test_json_structure_validation(self):
        """Test generic JSON structure validation."""
        schema = {"name": str, "age": int, "items": [{"id": int, "value": str}]}

        valid_data = {"name": "test", "age": 25, "items": [{"id": 1, "value": "item1"}]}

        report = Validators.validate_json_structure(valid_data, schema)
        assert report.is_valid()

        # Test invalid data
        invalid_data = {
            "name": "test",
            "age": "not_a_number",
            "items": [{"id": 1, "value": "item1"}],
        }  # Wrong type

        report = Validators.validate_json_structure(invalid_data, schema)
        assert not report.is_valid()
        assert len(report.errors) > 0

    def test_file_size_validation(self):
        """Test file size validation."""
        # Test with small file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test content")
            temp_file = f.name

        try:
            report = Validators.validate_file_size(temp_file, max_size_mb=1.0)
            assert report.is_valid()
            assert report.metrics["within_limit"] is True
        finally:
            Path(temp_file).unlink()

        # Test with file that's too large (simulate)
        large_content = "x" * (2 * 1024 * 1024)  # 2MB
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write(large_content)
            temp_file = f.name

        try:
            report = Validators.validate_file_size(temp_file, max_size_mb=1.0)
            assert not report.is_valid()
            assert report.metrics["within_limit"] is False
        finally:
            Path(temp_file).unlink()


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""

    def test_partial_bias_evaluation(self):
        """Test handling of partially complete bias evaluations."""
        partial_data = [
            {
                "prompt": "Test prompt",
                "axes": {
                    "user_invalidation": {"score": 3, "justification": "Test"},
                    # Missing some axes
                },
            }
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(partial_data, f)
            temp_file = f.name

        try:
            report = validate_bias_json(temp_file)
            # Should be invalid due to missing axes
            assert not report.is_valid()
        finally:
            Path(temp_file).unlink()

    def test_mixed_valid_invalid_evaluations(self):
        """Test file with mix of valid and invalid evaluations."""
        mixed_data = [
            {
                "prompt": "Valid prompt",
                "axes": {
                    "user_invalidation": {"score": 3, "justification": "Test"},
                    "escalation": {"score": 2, "justification": "Test"},
                    "personal_expression": {"score": 4, "justification": "Test"},
                    "asymmetric_coverage": {"score": 1, "justification": "Test"},
                    "refusal": {"score": 5, "justification": "Test"},
                },
            },
            {
                "prompt": "Invalid prompt",
                "axes": {
                    "user_invalidation": {
                        "score": 6,
                        "justification": "Test",
                    },  # Invalid score
                },
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(mixed_data, f)
            temp_file = f.name

        try:
            report = validate_bias_json(temp_file)
            assert not report.is_valid()
            assert report.metrics["total_evaluations"] == 2
            assert report.metrics["complete_evaluations"] == 1  # Only first is complete
        finally:
            Path(temp_file).unlink()

    @patch(
        "src.core.validators.BIAS_AXES",
        {"test_axis": {"title": "Test Axis", "instruction": "Test instruction"}},
    )
    def test_custom_bias_axes(self):
        """Test validation with custom bias axes."""
        custom_data = {
            "prompt": "Test prompt",
            "axes": {"test_axis": {"score": 3, "justification": "Test"}},
        }

        # This should work if BIAS_AXES is properly mocked
        evaluation = BiasEvaluation(**custom_data)
        assert evaluation.prompt == "Test prompt"
        assert evaluation.axes["test_axis"]["score"] == 3
