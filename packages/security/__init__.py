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
echoe-security: Security utilities for echoe-workspace.

Consolidates security functionality from:
- Root project's src/security
- Project 3's security modules
- Project 6's quantum_shield
"""

__version__ = "0.1.0"

from .auth import AuthManager
from .encryption import QuantumShield
from .privacy_filter import PrivacyFilter
from .privacy_middleware import PrivacyMiddleware
from .privacy_scanner import PrivacyScanner
from .scanning import CodeReviewer, VulnerabilityScanner

__all__ = [
    "VulnerabilityScanner",
    "CodeReviewer",
    "AuthManager",
    "QuantumShield",
    "PrivacyFilter",
    "PrivacyMiddleware",
    "PrivacyScanner",
]
