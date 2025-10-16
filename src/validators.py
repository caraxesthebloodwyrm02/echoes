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

"""Schema validation for trajectory analysis artifacts.

Strict type enforcement and structural validation for JSON outputs.
"""

from __future__ import annotations

from typing import Any, Dict


def validate_schema(data: Dict[str, Any], strict: bool = True) -> bool:
    """Validate analysis JSON against expected schema.

    Parameters
    ----------
    data
        Analysis JSON data
    strict
        If True, enforce strict type checking

    Returns
    -------
    bool
        True if valid, False otherwise
    """
    # Required top-level keys
    required_keys = ["timestamp", "seed", "vectors", "metrics", "classification"]

    for key in required_keys:
        if key not in data:
            if strict:
                raise ValueError(f"Missing required key: {key}")
            return False

    # Validate vectors
    vector_keys = ["influence", "productivity", "creativity", "efficiency"]
    vectors = data.get("vectors", {})

    for vkey in vector_keys:
        if vkey not in vectors:
            if strict:
                raise ValueError(f"Missing vector: {vkey}")
            return False

        vec = vectors[vkey]
        if not isinstance(vec, list) or len(vec) != 3:
            if strict:
                raise ValueError(f"Vector {vkey} must be 3-element list")
            return False

        # Check all elements are numeric
        if not all(isinstance(x, (int, float)) for x in vec):
            if strict:
                raise ValueError(f"Vector {vkey} contains non-numeric values")
            return False

    # Validate metrics
    metrics = data.get("metrics", {})
    required_metrics = ["efficiency_score", "balance_angle_deg", "pairwise_angles_deg"]

    for mkey in required_metrics:
        if mkey not in metrics:
            if strict:
                raise ValueError(f"Missing metric: {mkey}")
            return False

    # Validate efficiency_score range
    score = metrics.get("efficiency_score")
    if not isinstance(score, (int, float)) or not -1.0 <= score <= 1.0:
        if strict:
            raise ValueError(f"efficiency_score must be in [-1, 1], got {score}")
        return False

    # Validate balance_angle_deg range
    balance = metrics.get("balance_angle_deg")
    if not isinstance(balance, (int, float)) or not 0.0 <= balance <= 180.0:
        if strict:
            raise ValueError(f"balance_angle_deg must be in [0, 180], got {balance}")
        return False

    # Validate pairwise angles
    pairwise = metrics.get("pairwise_angles_deg", {})
    required_angles = [
        "influence_productivity",
        "influence_creativity",
        "productivity_creativity",
    ]

    for akey in required_angles:
        if akey not in pairwise:
            if strict:
                raise ValueError(f"Missing pairwise angle: {akey}")
            return False

        angle = pairwise[akey]
        if not isinstance(angle, (int, float)) or not 0.0 <= angle <= 180.0:
            if strict:
                raise ValueError(f"Angle {akey} must be in [0, 180], got {angle}")
            return False

    # Validate classification
    classification = data.get("classification", {})
    if "label" not in classification or "reason" not in classification:
        if strict:
            raise ValueError("Classification must have 'label' and 'reason'")
        return False

    # Validate label is one of expected values
    valid_labels = ["Aligned", "Imbalanced", "Fragmented"]
    if classification["label"] not in valid_labels:
        if strict:
            raise ValueError(f"Invalid label: {classification['label']}")
        return False

    # Validate seed
    seed = data.get("seed")
    if not isinstance(seed, int):
        if strict:
            raise ValueError(f"seed must be integer, got {type(seed)}")
        return False

    return True


def validate_numeric_reproducibility(
    data1: Dict[str, Any], data2: Dict[str, Any], rtol: float = 1e-7
) -> bool:
    """Validate that two analysis outputs are numerically identical.

    Parameters
    ----------
    data1, data2
        Analysis JSON data to compare
    rtol
        Relative tolerance for numeric comparison

    Returns
    -------
    bool
        True if outputs match within tolerance
    """
    import numpy as np

    # Compare seeds
    if data1.get("seed") != data2.get("seed"):
        return False

    # Compare vectors
    for vkey in ["influence", "productivity", "creativity", "efficiency"]:
        vec1 = np.array(data1["vectors"][vkey])
        vec2 = np.array(data2["vectors"][vkey])

        if not np.allclose(vec1, vec2, rtol=rtol):
            return False

    # Compare metrics
    metrics1 = data1["metrics"]
    metrics2 = data2["metrics"]

    if not np.isclose(
        metrics1["efficiency_score"], metrics2["efficiency_score"], rtol=rtol
    ):
        return False

    if not np.isclose(
        metrics1["balance_angle_deg"], metrics2["balance_angle_deg"], rtol=rtol
    ):
        return False

    # Compare pairwise angles
    for akey in [
        "influence_productivity",
        "influence_creativity",
        "productivity_creativity",
    ]:
        angle1 = metrics1["pairwise_angles_deg"][akey]
        angle2 = metrics2["pairwise_angles_deg"][akey]

        if not np.isclose(angle1, angle2, rtol=rtol):
            return False

    # Compare classification
    if data1["classification"]["label"] != data2["classification"]["label"]:
        return False

    return True
