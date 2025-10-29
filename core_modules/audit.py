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

import datetime
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from typing import Any, Dict, Optional


@dataclass
class AuditEvent:
    """Structured audit event with GDPR-compliant privacy handling."""

    event_id: str
    timestamp: str
    user_id: str  # Hashed for privacy
    operation: str
    prompt_hash: str  # Hashed prompt content
    response_summary: Dict[str, Any]
    safety_status: str
    ip_hash: Optional[str] = None  # Hashed IP for abuse detection
    user_agent_hash: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def to_ndjson(self) -> str:
        """Convert to NDJSON format."""
        return json.dumps(asdict(self), default=str)


class AuditLogger:
    def __init__(self, log_file="logs/audit.ndjson"):
        # Ensure we have a proper directory path
        log_dir = os.path.dirname(log_file)
        if log_dir:  # Only create directory if there's a path
            os.makedirs(log_dir, exist_ok=True)
        self.log_file = log_file
        self._buffer = []
        self._buffer_size = 10  # Flush every 10 events

    def log_evaluation(
        self,
        user_id: str,
        prompt: str,
        response: Dict[str, Any],
        safety_status: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log a bias evaluation with comprehensive metadata."""

        # GDPR-compliant privacy hashing
        user_hash = self._hash_privacy_data(user_id)
        prompt_hash = self._hash_privacy_data(prompt)
        ip_hash = self._hash_privacy_data(ip_address) if ip_address else None
        ua_hash = self._hash_privacy_data(user_agent) if user_agent else None

        # Create response summary (avoid storing full response for privacy)
        response_summary = {
            "has_bias_score": "bias_score" in response,
            "has_axes": "axes" in response,
            "axes_count": len(response.get("axes", {})),
            "safety_status": safety_status,
            "model": response.get("model", "unknown"),
            "timestamp": response.get("timestamp", datetime.datetime.utcnow().isoformat()),
        }

        # Create audit event
        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.datetime.utcnow().isoformat(),
            user_id=user_hash,
            operation="bias_evaluation",
            prompt_hash=prompt_hash,
            response_summary=response_summary,
            safety_status=safety_status,
            ip_hash=ip_hash,
            user_agent_hash=ua_hash,
            session_id=session_id,
            metadata=metadata or {},
        )

        # Buffer and flush
        self._buffer.append(event)
        if len(self._buffer) >= self._buffer_size:
            self._flush_buffer()

    def log_security_event(
        self,
        event_type: str,
        user_id: str,
        details: Dict[str, Any],
        severity: str = "info",
        ip_address: Optional[str] = None,
    ) -> None:
        """Log security-related events."""

        user_hash = self._hash_privacy_data(user_id)
        ip_hash = self._hash_privacy_data(ip_address) if ip_address else None

        event = AuditEvent(
            event_id=self._generate_event_id(),
            timestamp=datetime.datetime.utcnow().isoformat(),
            user_id=user_hash,
            operation=f"security_{event_type}",
            prompt_hash="",  # Not applicable
            response_summary={"details": details, "severity": severity},
            safety_status="security_event",
            ip_hash=ip_hash,
            metadata={"event_type": event_type, "severity": severity},
        )

        self._buffer.append(event)
        self._flush_buffer()  # Security events flush immediately

    def get_recent_events(self, limit: int = 100) -> list:
        """Retrieve recent audit events for monitoring."""
        if not os.path.exists(self.log_file):
            return []

        events = []
        try:
            with open(self.log_file, "r") as f:
                lines = f.readlines()[-limit:]  # Last N events
                for line in lines:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        except Exception:
            pass

        return events

    def get_security_stats(self, hours: int = 24) -> Dict[str, Any]:
        """Get security statistics for monitoring dashboard."""
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(hours=hours)
        events = self.get_recent_events(1000)

        stats = {
            "total_events": len(events),
            "security_events": 0,
            "rate_limited": 0,
            "blocked_injections": 0,
            "circuit_breaker_trips": 0,
            "time_range": f"{hours} hours",
        }

        for event in events:
            if datetime.datetime.fromisoformat(event["timestamp"]) < cutoff:
                continue

            if event["operation"].startswith("security_"):
                stats["security_events"] += 1

            if event["safety_status"] == "rate_limited":
                stats["rate_limited"] += 1
            elif event["safety_status"] == "input_blocked":
                stats["blocked_injections"] += 1
            elif event["safety_status"] == "circuit_breaker":
                stats["circuit_breaker_trips"] += 1

        return stats

    def _hash_privacy_data(self, data: str) -> str:
        """GDPR-compliant hashing for privacy-sensitive data."""
        if not data:
            return ""
        # Use SHA-256 with salt for privacy
        salt = "echoes_safety_salt"
        return hashlib.sha256(f"{salt}:{data}".encode()).hexdigest()[:16]

    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        return f"evt_{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{hashlib.md5(os.urandom(8)).hexdigest()[:8]}"

    def _flush_buffer(self) -> None:
        """Flush buffered events to disk."""
        if not self._buffer:
            return

        try:
            with open(self.log_file, "a") as f:
                for event in self._buffer:
                    f.write(event.to_ndjson() + "\n")
            self._buffer.clear()
        except Exception as e:
            # Log flushing error (without recursion)
            print(f"Warning: Failed to flush audit buffer: {e}")
            # Keep buffer for retry
            pass

    def __del__(self):
        """Ensure buffer is flushed on destruction."""
        self._flush_buffer()
