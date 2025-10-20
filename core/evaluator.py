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

from __future__ import annotations

"""Trajectory efficiency evaluator.

Contains rule-based classification of an `EfficiencySummary` into
``Aligned`` / ``Imbalanced`` / ``Fragmented`` categories according to the
specifications provided by the research team.
"""

from typing import Dict, Tuple

from .metrics import EfficiencySummary

__all__: Tuple[str, ...] = (
    "classify",
    "DEFAULT_THRESHOLDS",
)

# ---------------------------------------------------------------------------
# Threshold configuration (can be tuned externally)
# ---------------------------------------------------------------------------

DEFAULT_THRESHOLDS = {
    "aligned_score": 0.7,  # |score| >= 0.7
    "imbalanced_score": 0.3,  # 0.3 <= |score| < 0.7
    "synergy_balance_deg": 90.0,  # balance < 90° -> synergy
    "imbalanced_upper_deg": 120.0,  # 90°–120° -> imbalanced range
}

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def classify(
    summary: EfficiencySummary,
    *,
    thresholds: Dict[str, float] | None = None,
) -> Dict[str, str]:
    """Return classification label & reason for an *EfficiencySummary*.

    The returned dict has keys ``label`` and ``reason`` suitable for JSON
    serialisation.
    """
    th = {**DEFAULT_THRESHOLDS, **(thresholds or {})}

    score_abs = abs(summary.efficiency_score)
    balance = summary.balance_angle_deg

    # Determine primary label
    if score_abs >= th["aligned_score"] and balance < th["synergy_balance_deg"]:
        label = "Aligned"
        reason = "|score| >= {:.2f} and balance_angle < {:.0f}°".format(th["aligned_score"], th["synergy_balance_deg"])
    elif (score_abs >= th["imbalanced_score"] and score_abs < th["aligned_score"]) or (
        th["synergy_balance_deg"] <= balance <= th["imbalanced_upper_deg"]
    ):
        label = "Imbalanced"
        reason = "efficiency_score between {:.1f} and {:.1f} or " "balance_angle between {:.0f}° and {:.0f}°".format(
            th["imbalanced_score"],
            th["aligned_score"],
            th["synergy_balance_deg"],
            th["imbalanced_upper_deg"],
        )
    else:
        label = "Fragmented"
        # Fragmented occurs when score < imbalanced_score or balance > upper
        if score_abs < th["imbalanced_score"]:
            reason = "|score| < {:.2f}".format(th["imbalanced_score"])
        else:
            reason = "balance_angle > {:.0f}°".format(th["imbalanced_upper_deg"])

    return {
        "label": label,
        "reason": reason,
    }
