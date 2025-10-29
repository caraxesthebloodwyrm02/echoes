"""
_constants
======

Constants relevant for the Python implementation.
"""

from __future__ import annotations

import platform
import sys
import sysconfig

import numpy as np

IS64 = sys.maxsize > 2**32

PY310 = sys.version_info >= (3, 10)
PY311 = sys.version_info >= (3, 11)
PY312 = sys.version_info >= (3, 12)
PY314 = sys.version_info >= (3, 14)
PYPY = platform.python_implementation() == "PyPy"
ISMUSL = "musl" in (sysconfig.get_config_var("HOST_GNU_TYPE") or "")
REF_COUNT = 2 if PY311 else 3
WARNING_CHECK_DISABLED = PY314

# Constants for numerical computations
_XMAX = 1e100
_LOGXMAX = np.log(_XMAX)

# Mathematical constants
_XMIN = 1e-323
_LOGXMIN = np.log(_XMIN)
_EULER = 0.5772156649015329  # Euler-Mascheroni constant
_ZETA3 = 1.2020569031595943   # Apery's constant
_SQRT_PI = np.sqrt(np.pi)
_SQRT_2_OVER_PI = np.sqrt(2 / np.pi)
_LOG_PI = np.log(np.pi)
_LOG_SQRT_2_OVER_PI = np.log(np.sqrt(2 / np.pi))


__all__ = [
    "IS64",
    "ISMUSL",
    "PY310",
    "PY311",
    "PY312",
    "PY314",
    "PYPY",
    "_XMAX",
    "_LOGXMAX",
    "_XMIN",
    "_LOGXMIN",
    "_EULER",
    "_ZETA3",
    "_SQRT_PI",
    "_SQRT_2_OVER_PI",
    "_LOG_PI",
    "_LOG_SQRT_2_OVER_PI",
]
