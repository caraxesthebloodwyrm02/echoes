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
Safety module for Echoes platform.

Provides comprehensive safety mechanisms including:
- Input validation and sanitization
- Circuit breaker for fault tolerance
- Audit logging for compliance
- Rate limiting for abuse prevention
- Real-time monitoring and alerts
"""

from .audit import AuditEvent, AuditLogger
from .guards import CircuitBreaker, Prompt, openai_safe_call
from .limiter import TokenBucket
from .monitor import SafetyMonitor, get_safety_monitor, quick_status

__all__ = [
    "Prompt",
    "CircuitBreaker",
    "openai_safe_call",
    "AuditLogger",
    "AuditEvent",
    "TokenBucket",
    "SafetyMonitor",
    "get_safety_monitor",
    "quick_status",
]
