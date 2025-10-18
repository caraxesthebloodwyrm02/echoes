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

"""Validate bias evaluation JSON and generate management-focused metrics report.

This validator supports bias management by ensuring data consistency and surfacing
key metrics for human intervention, rather than claiming bias elimination.
"""

import json
import sys
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List

from .evaluate_bias import BIAS_AXES


class BiasValidationReport:
    """Structured report for bias evaluation validation and metrics."""

    def __init__(self, json_path: Path):
        self.json_path = json_path
        self.data: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.metrics: Dict[str, Any] = {}

    def validate_and_compute(self) -> Dict[str, Any]:
        """Run full validation and metrics computation."""
        try:
            self._load_data()
            self._validate_structure()
            self._compute_metrics()
        except Exception as e:
            self.errors.append(f"Validation failed: {e}")
        return self._generate_report()

    def _load_data(self) -> None:
        """Load and parse JSON data."""
        with open(self.json_path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def _validate_structure(self) -> None:
        """Validate expected JSON structure."""
        if not isinstance(self.data, list):
            self.errors.append("Root must be a list of evaluations")
            return

        for i, evaluation in enumerate(self.data):
            if not isinstance(evaluation, dict):
                self.errors.append(f"Evaluation {i} must be a dict")
                continue

            required_fields = ["prompt", "axes"]
            for field in required_fields:
                if field not in evaluation:
                    self.errors.append(f"Evaluation {i} missing '{field}' field")

            axes = evaluation.get("axes", {})
            if not isinstance(axes, dict):
                self.errors.append(f"Evaluation {i} 'axes' must be a dict")
                continue

            for axis in BIAS_AXES:
                if axis not in axes:
                    self.errors.append(f"Evaluation {i} missing axis '{axis}'")
                    continue

                axis_data = axes[axis]
                if not isinstance(axis_data, dict):
                    self.errors.append(f"Evaluation {i} axis '{axis}' must be a dict")
                    continue

                if "score" not in axis_data:
                    self.errors.append(f"Evaluation {i} axis '{axis}' missing 'score'")
                elif not isinstance(axis_data["score"], (int, float)) or not (
                    1 <= axis_data["score"] <= 5
                ):
                    self.errors.append(
                        f"Evaluation {i} axis '{axis}' score must be 1-5"
                    )

    def _compute_metrics(self) -> None:
        """Compute bias management metrics."""
        if not self.data:
            self.metrics = {"evaluations": 0, "completeness": 0.0, "mean_bias": 0.0}
            return

        total_evaluations = len(self.data)
        all_scores: List[float] = []

        complete_evaluations = 0
        for evaluation in self.data:
            axes = evaluation.get("axes", {})
            if len(axes) == len(BIAS_AXES):  # All axes present
                complete_evaluations += 1

            for axis_data in axes.values():
                score = axis_data.get("score")
                if isinstance(score, (int, float)) and 1 <= score <= 5:
                    # Normalize to 0-1 for bias measurement
                    all_scores.append(score / 5.0)

        completeness = (
            complete_evaluations / total_evaluations if total_evaluations > 0 else 0.0
        )
        mean_bias = mean(all_scores) if all_scores else 0.0

        self.metrics = {
            "evaluations": total_evaluations,
            "completeness": completeness,
            "mean_bias": mean_bias,
            "total_scores": len(all_scores),
        }

    def _generate_report(self) -> Dict[str, Any]:
        """Generate final report dict."""
        return {
            "validated_file": str(self.json_path),
            "errors": self.errors,
            "metrics": self.metrics,
            "bias_management_note": (
                "This system supports bias management through systematic evaluation and pattern detection. "
                "High-risk zones are surfaced for human intervention; absolute bias elimination is not claimed."
            ),
        }


def validate_bias_json(json_path: str | Path) -> Dict[str, Any]:
    """Validate bias evaluation JSON and return management-focused report."""
    path = Path(json_path)
    if not path.exists():
        return {"error": f"File not found: {path}"}

    report = BiasValidationReport(path)
    return report.validate_and_compute()


def main() -> None:
    """CLI entry point."""
    if len(sys.argv) != 2:
        print(
            "Usage: python -m bias_detection.validate_bias_json <path_to_bias_evaluations.json>"
        )
        sys.exit(1)

    json_path = sys.argv[1]
    result = validate_bias_json(json_path)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
