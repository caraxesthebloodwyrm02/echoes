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

"""High-level metrics utilities.

This module defines the :class:`EfficiencySummary` dataclass and the helper
:func:`compute_efficiency_metrics` which aggregate low-level vector operations
into reproducible, numerically-stable metrics.
"""

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np
import numpy.typing as npt

from .vector_ops import (
    angle_between,
    compute_efficiency_vector,
    normalize,
)

__all__: Tuple[str, ...] = (
    "EfficiencySummary",
    "compute_efficiency_metrics",
)

# ---------------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EfficiencySummary:
    """Immutable container for trajectory efficiency metrics.

    All numeric values are stored as ``np.float64`` for consistency.
    """

    # Core vector
    efficiency_vector: npt.NDArray[np.float64]

    # Scalar metrics
    efficiency_score: np.float64
    balance_angle_deg: np.float64

    # Pair-wise angles (deg)
    influence_productivity_deg: np.float64
    influence_creativity_deg: np.float64
    productivity_creativity_deg: np.float64

    # ---------------------------------------------------------------------
    # Validation helpers
    # ---------------------------------------------------------------------

    _RTOL: float = 1e-7  # class-level numeric tolerance

    def __post_init__(self) -> None:  # type: ignore[override]
        if self.efficiency_vector.shape != (3,):
            raise ValueError("efficiency_vector must be 3-D (shape == (3,))")
        # Ensure unit length within rtol
        if not np.isclose(np.linalg.norm(self.efficiency_vector), 1.0, rtol=self._RTOL):
            raise ValueError("efficiency_vector must be normalised (||v||=1)")

        # Validate scalar ranges
        if not -1.0 <= self.efficiency_score <= 1.0:
            raise ValueError("efficiency_score must be in [-1, 1]")
        for name, angle in (
            ("balance_angle_deg", self.balance_angle_deg),
            ("influence_productivity_deg", self.influence_productivity_deg),
            ("influence_creativity_deg", self.influence_creativity_deg),
            ("productivity_creativity_deg", self.productivity_creativity_deg),
        ):
            if not 0.0 <= angle <= 180.0:
                raise ValueError(f"{name} must be in [0°, 180°]")

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, object]:
        """Return a JSON-serialisable representation."""
        return {
            "efficiency_vector": self.efficiency_vector.tolist(),
            "efficiency_score": float(self.efficiency_score),
            "balance_angle_deg": float(self.balance_angle_deg),
            "pairwise_angles_deg": {
                "influence_productivity": float(self.influence_productivity_deg),
                "influence_creativity": float(self.influence_creativity_deg),
                "productivity_creativity": float(self.productivity_creativity_deg),
            },
        }

    # For concise logging / debugging
    def __repr__(self) -> str:  # noqa: D401
        return "EfficiencySummary(score={s:.3f}, balance={b:.2f}°, " "angles=({ip:.2f}, {ic:.2f}, {pc:.2f}))".format(
            s=self.efficiency_score,
            b=self.balance_angle_deg,
            ip=self.influence_productivity_deg,
            ic=self.influence_creativity_deg,
            pc=self.productivity_creativity_deg,
        )


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------


def compute_efficiency_metrics(
    influence: npt.NDArray[np.float64],
    productivity: npt.NDArray[np.float64],
    creativity: npt.NDArray[np.float64],
) -> EfficiencySummary:
    """Compute efficiency metrics given three base vectors.

    All inputs are **copied** and normalised internally. The computation is
    deterministic and satisfies numeric stability requirements via ``np.clip``
    when calculating angles.
    """

    # Normalise base vectors (copy input)
    inf_v = normalize(np.array(influence, dtype=np.float64))
    prod_v = normalize(np.array(productivity, dtype=np.float64))
    crea_v = normalize(np.array(creativity, dtype=np.float64))

    # Efficiency vector
    eff_v = compute_efficiency_vector(inf_v, prod_v, crea_v)

    # Pair-wise angles
    ang_ip = np.float64(angle_between(inf_v, prod_v))
    ang_ic = np.float64(angle_between(inf_v, crea_v))
    ang_pc = np.float64(angle_between(prod_v, crea_v))

    # Aggregate balance
    balance = np.float64((ang_ip + ang_ic + ang_pc) / 3.0)

    # Efficiency score (mean dot-product)
    eff_score = np.float64(
        np.mean(
            [
                np.dot(eff_v, inf_v),
                np.dot(eff_v, prod_v),
                np.dot(eff_v, crea_v),
            ]
        )
    )

    return EfficiencySummary(
        efficiency_vector=eff_v,
        efficiency_score=eff_score,
        balance_angle_deg=balance,
        influence_productivity_deg=ang_ip,
        influence_creativity_deg=ang_ic,
        productivity_creativity_deg=ang_pc,
    )
