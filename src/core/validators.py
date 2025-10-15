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
Centralized Validation Module

Consolidates all JSON/schema validation logic from scattered modules.
Provides uniform validation across the codebase with consistent error handling.
"""

import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ValidationError, validator

# Import existing validation logic from bias_detection
try:
    from ai_modules.bias_detection.evaluate_bias import BIAS_AXES
except ImportError:
    BIAS_AXES = {}


class BiasEvaluation(BaseModel):
    """Pydantic model for bias evaluation validation."""

    prompt: str
    axes: Dict[str, Dict[str, Any]]

    @validator("axes")
    def validate_axes(cls, v):
        """Validate bias axes structure."""
        if not isinstance(v, dict):
            raise ValueError("axes must be a dictionary")

        for axis in BIAS_AXES:
            if axis not in v:
                raise ValueError(f"missing required axis: {axis}")

            axis_data = v[axis]
            if not isinstance(axis_data, dict):
                raise ValueError(f"axis {axis} must be a dictionary")

            if "score" not in axis_data:
                raise ValueError(f"axis {axis} missing 'score' field")

            score = axis_data["score"]
            if not isinstance(score, (int, float)) or not (1 <= score <= 5):
                raise ValueError(f"axis {axis} score must be 1-5")

        return v


class ConfigValidation(BaseModel):
    """Pydantic model for configuration validation."""

    openai_api_key: str
    database_url: Optional[str] = None
    log_level: str = "INFO"
    max_tokens: int = 1000
    temperature: float = 0.7

    @validator("log_level")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v.upper()

    @validator("temperature")
    def validate_temperature(cls, v):
        if not (0.0 <= v <= 2.0):
            raise ValueError("temperature must be between 0.0 and 2.0")
        return v


class ValidationError(Exception):
    """Custom validation error with detailed reporting."""

    pass


class ValidationReport:
    """Structured validation report with metrics and errors."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.metrics: Dict[str, Any] = {}

    def add_error(self, message: str):
        """Add a validation error."""
        self.errors.append(message)

    def add_warning(self, message: str):
        """Add a validation warning."""
        self.warnings.append(message)

    def set_metric(self, key: str, value: Any):
        """Set a validation metric."""
        self.metrics[key] = value

    def is_valid(self) -> bool:
        """Check if validation passed."""
        return len(self.errors) == 0

    def summary(self) -> str:
        """Generate a summary of validation results."""
        total_issues = len(self.errors) + len(self.warnings)
        if total_issues == 0:
            return "✅ Validation passed - no issues found"

        summary = f"❌ Validation failed - {len(self.errors)} errors, {len(self.warnings)} warnings"
        if self.metrics:
            summary += f" | Metrics: {self.metrics}"
        return summary


class Validators:
    """Centralized validation utilities."""

    @staticmethod
    def validate_bias_json(json_path: Union[str, Path]) -> ValidationReport:
        """Validate bias evaluation JSON file."""
        report = ValidationReport()
        json_path = Path(json_path)

        if not json_path.exists():
            report.add_error(f"File not found: {json_path}")
            return report

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            report.add_error(f"Invalid JSON format: {e}")
            return report
        except Exception as e:
            report.add_error(f"Error reading file: {e}")
            return report

        if not isinstance(data, list):
            report.add_error("Root must be a list of evaluations")
            return report

        total_scores = []
        complete_evaluations = 0

        for i, evaluation in enumerate(data):
            try:
                # Use Pydantic for strict validation
                validated = BiasEvaluation(**evaluation)
                complete_evaluations += 1

                # Collect scores for metrics
                for axis_data in validated.axes.values():
                    if isinstance(axis_data.get("score"), (int, float)):
                        total_scores.append(axis_data["score"])

            except ValidationError as e:
                for error in e.errors():
                    report.add_error(
                        f"Evaluation {i}: {error['msg']} at {'.'.join(str(x) for x in error['loc'])}"
                    )
            except Exception as e:
                report.add_error(f"Evaluation {i}: Unexpected error: {e}")

        # Calculate metrics
        report.set_metric("total_evaluations", len(data))
        report.set_metric("complete_evaluations", complete_evaluations)
        report.set_metric(
            "completeness_ratio", complete_evaluations / len(data) if data else 0
        )

        if total_scores:
            report.set_metric("mean_bias_score", mean(total_scores))
            report.set_metric("total_scores", len(total_scores))

        return report

    @staticmethod
    def validate_config(config_data: Dict[str, Any]) -> ValidationReport:
        """Validate configuration data."""
        report = ValidationReport()

        try:
            validated = ConfigValidation(**config_data)
            report.set_metric("config_valid", True)
        except ValidationError as e:
            for error in e.errors():
                report.add_error(
                    f"Config validation failed: {error['msg']} at {'.'.join(str(x) for x in error['loc'])}"
                )
        except Exception as e:
            report.add_error(f"Unexpected config validation error: {e}")

        return report

    @staticmethod
    def validate_json_structure(data: Any, schema: Dict[str, Any]) -> ValidationReport:
        """Generic JSON structure validation."""
        report = ValidationReport()

        def _validate_recursive(obj, schema_part, path=""):
            if not isinstance(obj, type(schema_part)):
                report.add_error(
                    f"{path}: Expected {type(schema_part).__name__}, got {type(obj).__name__}"
                )
                return

            if isinstance(schema_part, dict):
                if not isinstance(obj, dict):
                    report.add_error(f"{path}: Expected dict, got {type(obj).__name__}")
                    return

                for key, value in schema_part.items():
                    if key not in obj:
                        report.add_error(f"{path}.{key}: Missing required field")
                    else:
                        _validate_recursive(obj[key], value, f"{path}.{key}")

            elif isinstance(schema_part, list):
                if not isinstance(obj, list):
                    report.add_error(f"{path}: Expected list, got {type(obj).__name__}")
                    return

                if schema_part:  # Non-empty list means validate first item
                    for i, item in enumerate(obj):
                        _validate_recursive(item, schema_part[0], f"{path}[{i}]")

        _validate_recursive(data, schema)
        return report

    @staticmethod
    def validate_file_size(
        file_path: Union[str, Path], max_size_mb: float = 100
    ) -> ValidationReport:
        """Validate file size constraints."""
        report = ValidationReport()
        file_path = Path(file_path)

        if not file_path.exists():
            report.add_error(f"File not found: {file_path}")
            return report

        size_mb = file_path.stat().st_size / (1024 * 1024)

        if size_mb > max_size_mb:
            report.add_error(f"File too large: {size_mb:.2f}MB > {max_size_mb}MB limit")

        report.set_metric("file_size_mb", size_mb)
        report.set_metric("within_limit", size_mb <= max_size_mb)

        return report


# Convenience functions for easy import
def validate_bias_json(json_path: Union[str, Path]) -> ValidationReport:
    """Validate bias evaluation JSON file."""
    return Validators.validate_bias_json(json_path)


def validate_config(config_data: Dict[str, Any]) -> ValidationReport:
    """Validate configuration data."""
    return Validators.validate_config(config_data)


def validate_json_structure(data: Any, schema: Dict[str, Any]) -> ValidationReport:
    """Generic JSON structure validation."""
    return Validators.validate_json_structure(data, schema)


def validate_file_size(
    file_path: Union[str, Path], max_size_mb: float = 100
) -> ValidationReport:
    """Validate file size constraints."""
    return Validators.validate_file_size(file_path, max_size_mb)
