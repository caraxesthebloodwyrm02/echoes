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

"""Low-level vector operations (NumPy-only).

All functions are deterministic and side-effect free so they can be safely unit-tested.
"""

from typing import Tuple

import numpy as np
import numpy.typing as npt

# Public API -----------------------------------------------------------------
__all__: Tuple[str, ...] = (
    "normalize",
    "angle_between",
    "compute_efficiency_vector",
)

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def normalize(vector: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
    """Return the unit-length version of *vector* (`np.float64`).

    Raises
    ------
    ValueError
        If *vector* has (near-)zero magnitude.
    """
    vector = np.asarray(vector, dtype=np.float64)
    norm = np.linalg.norm(vector)
    if norm < 1e-12:
        raise ValueError("Cannot normalize the zero vector (||v||=0).")
    return vector / norm


def angle_between(
    v1: npt.NDArray[np.float64],
    v2: npt.NDArray[np.float64],
    *,
    degrees: bool = True,
) -> float:
    """Return the angle between *v1* and *v2*.

    Parameters
    ----------
    v1, v2
        Input vectors (any length > 0).
    degrees
        If ``True`` (default) return angle in degrees, otherwise radians.
    """
    # Normalise to ensure numerical stability
    v1_n = normalize(v1)
    v2_n = normalize(v2)

    dot = float(np.clip(np.dot(v1_n, v2_n), -1.0, 1.0))
    ang = np.arccos(dot)
    return float(np.degrees(ang) if degrees else ang)


def compute_efficiency_vector(
    influence: npt.NDArray[np.float64],
    productivity: npt.NDArray[np.float64],
    creativity: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    """Return the *efficiency* (balance) vector.

    The efficiency vector is the normalised arithmetic mean of the three input
    vectors.
    """
    avg = (normalize(influence) + normalize(productivity) + normalize(creativity)) / 3.0
    return normalize(avg)
