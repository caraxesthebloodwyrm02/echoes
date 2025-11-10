"""
Security Framework for Echoes AI System
Implements multi-layer security with encryption, access control, audit logging, and threat detection.
"""

import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import threading
from functools import wraps
import os

# Configure security logger
security_logger = logging.getLogger("echoes.security")
security_logger.setLevel(logging.INFO)


class SecurityEvent(Enum):
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "config_change"
    THREAT_DETECTED = "threat_detected"
    ENCRYPTION_ERROR = "encryption_error"
    AUDIT_FAILURE = "audit_failure"

    def __str__(self) -> str:
        return self.value


@dataclass
class SecurityIncident:
    """Represents a security incident for logging and analysis."""

    timestamp: str
    event_type: SecurityEvent
    severity: str  # "low", "medium", "high", "critical"
    user_id: Optional[str]
    resource: str
    action: str
    details: Dict[str, Any]
    source_ip: Optional[str] = None
    user_agent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["event_type"] = str(self.event_type)
        return result


class EncryptionLayer:
    """Handles encryption/decryption operations with multiple algorithms."""

    def __init__(self, key: Optional[bytes] = None):
        try:
            from cryptography.fernet import Fernet

            self.fernet = Fernet
            self.key = key or Fernet.generate_key()
        except ImportError:
            security_logger.warning(
                "cryptography not available, using basic encryption"
            )
            self.fernet = None
            self.key = key or os.urandom(32)

    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        if self.fernet:
            f = self.fernet(self.key)
            return f.encrypt(data.encode()).decode()
        else:
            # Fallback basic encryption
            return self._basic_encrypt(data)

    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if self.fernet:
            f = self.fernet(self.key)
            return f.decrypt(encrypted_data.encode()).decode()
        else:
            return self._basic_decrypt(encrypted_data)

    def _basic_encrypt(self, data: str) -> str:
        """Basic XOR encryption fallback."""
        key_bytes = self.key
        data_bytes = data.encode()
        encrypted = bytearray()
        for i, byte in enumerate(data_bytes):
            encrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        return encrypted.hex()

    def _basic_decrypt(self, encrypted_data: str) -> str:
        """Basic XOR decryption fallback."""
        key_bytes = self.key
        encrypted_bytes = bytearray.fromhex(encrypted_data)
        decrypted = bytearray()
        for i, byte in enumerate(encrypted_bytes):
            decrypted.append(byte ^ key_bytes[i % len(key_bytes)])
        return decrypted.decode()


class AccessControl:
    """Manages user permissions and access control."""

    def __init__(self):
        self.roles: Dict[str, List[str]] = {
            "admin": ["*"],  # All permissions
            "user": ["read", "write", "execute"],
            "viewer": ["read"],
            "auditor": ["read", "audit"],
        }

        self.user_roles: Dict[str, str] = {}
        self.permissions: Dict[str, Callable] = {}

    def assign_role(self, user_id: str, role: str):
        """Assign a role to a user."""
        if role not in self.roles:
            raise ValueError(f"Unknown role: {role}")
        self.user_roles[user_id] = role

    def has_permission(self, user_id: str, permission: str) -> bool:
        """Check if user has specific permission."""
        role = self.user_roles.get(user_id, "viewer")
        role_permissions = self.roles.get(role, [])

        return "*" in role_permissions or permission in role_permissions

    def add_permission_check(self, resource: str, check_func: Callable):
        """Add custom permission check for a resource."""
        self.permissions[resource] = check_func

    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        """Comprehensive access check."""
        # Basic role-based check
        if not self.has_permission(user_id, action):
            return False

        # Custom permission check if exists
        if resource in self.permissions:
            return self.permissions[resource](user_id, action)

        return True


class AuditLogger:
    """Handles security event logging and audit trails."""

    def __init__(self, log_path: str = "logs/security_audit.log"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()

    def log_event(self, incident: SecurityIncident):
        """Log a security event."""
        with self._lock:
            try:

                def _json_default(value: Any):
                    if isinstance(value, Enum):
                        return value.value
                    if isinstance(value, (datetime, datetime.date)):
                        return value.isoformat()
                    if isinstance(value, Path):
                        return str(value)
                    if isinstance(value, set):
                        return list(value)
                    if hasattr(value, "to_dict") and callable(value.to_dict):
                        return value.to_dict()
                    return str(value)

                event_data = incident.to_dict()
                serialized = json.dumps(
                    event_data,
                    default=_json_default,
                    ensure_ascii=False,
                )

                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(serialized)
                    f.write("\n")

                # Also log to Python logger
                security_logger.info(
                    f"Security event: {incident.event_type.value} - {incident.severity}"
                )

            except Exception as e:
                security_logger.error(f"Failed to log security event: {e}")

    def get_events(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[SecurityEvent] = None,
        since: Optional[float] = None,
    ) -> List[SecurityIncident]:
        """Retrieve audit events with optional filtering."""
        events = []
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        event = SecurityIncident(**data)

                        # Apply filters
                        if user_id and event.user_id != user_id:
                            continue
                        if event_type and event.event_type != event_type:
                            continue
                        if (
                            since
                            and datetime.fromisoformat(event.timestamp).timestamp()
                            < since
                        ):
                            continue

                        events.append(event)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            pass

        return events


class ThreatDetection:
    """Detects potential security threats and anomalies."""

    def __init__(self):
        self.suspicious_patterns = {
            "sql_injection": [
                r";\s*DROP\s+TABLE",
                r";\s*DELETE\s+FROM",
                r"UNION\s+SELECT",
                r"--",
                r"/\*.*\*/",
            ],
            "path_traversal": [r"\.\./", r"\.\.\\", r"%2e%2e%2f", r"%2e%2e%5c"],
            "script_injection": [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"eval\s*\(",
            ],
        }

    def is_safe(self, data: Any) -> bool:
        """Check if input data appears safe."""
        if isinstance(data, str):
            return self._check_string_safety(data)
        elif isinstance(data, dict):
            return all(self.is_safe(v) for v in data.values())
        elif isinstance(data, list):
            return all(self.is_safe(item) for item in data)
        return True

    def _check_string_safety(self, text: str) -> bool:
        """Check string for suspicious patterns."""
        text_lower = text.lower()
        for category, patterns in self.suspicious_patterns.items():
            for pattern in patterns:
                import re

                if re.search(pattern, text_lower, re.IGNORECASE):
                    security_logger.warning(f"Suspicious pattern detected: {category}")
                    return False
        return True

    def detect_anomaly(self, user_activity: List[Dict]) -> Optional[str]:
        """Detect anomalous user behavior."""
        if len(user_activity) < 10:
            return None

        # Check for rapid-fire requests
        timestamps = [item.get("timestamp") for item in user_activity[-10:]]
        if len(timestamps) >= 2:
            time_diffs = []
            for i in range(1, len(timestamps)):
                try:
                    t1 = datetime.fromisoformat(timestamps[i - 1])
                    t2 = datetime.fromisoformat(timestamps[i])
                    time_diffs.append((t2 - t1).total_seconds())
                except:
                    continue

            avg_interval = sum(time_diffs) / len(time_diffs) if time_diffs else 0
            if avg_interval < 0.1:  # Less than 100ms between requests
                return "high_frequency_requests"

        return None


class RateLimiter:
    """Implements rate limiting for API endpoints."""

    def __init__(self):
        self.requests: Dict[str, List[float]] = {}
        self.limits = {
            "default": {"requests": 100, "window": 60},  # 100 req/minute
            "strict": {"requests": 10, "window": 60},  # 10 req/minute
            "lenient": {"requests": 1000, "window": 60},  # 1000 req/minute
        }

    def exceeded(self, user_id: str, limit_type: str = "default") -> bool:
        """Check if rate limit exceeded."""
        now = time.time()
        limit = self.limits.get(limit_type, self.limits["default"])

        if user_id not in self.requests:
            self.requests[user_id] = []

        # Clean old requests
        self.requests[user_id] = [
            ts for ts in self.requests[user_id] if now - ts < limit["window"]
        ]

        # Check limit
        if len(self.requests[user_id]) >= limit["requests"]:
            return True

        # Add current request
        self.requests[user_id].append(now)
        return False


class SecurityManager:
    """Central security management system."""

    def __init__(self):
        self.encryption = EncryptionLayer()
        self.access_control = AccessControl()
        self.audit_logger = AuditLogger()
        self.threat_detection = ThreatDetection()
        self.rate_limiter = RateLimiter()

        # Set up default roles
        self.access_control.assign_role("system", "admin")

    def validate_operation(
        self, user_id: str, operation: str, data: Any = None, source_ip: str = None
    ) -> bool:
        """Zero-trust validation for operations."""

        # Rate limiting check
        if self.rate_limiter.exceeded(user_id):
            self._log_incident(
                SecurityEvent.AUTHENTICATION,
                "medium",
                user_id,
                "rate_limit",
                operation,
                {"reason": "rate_limit_exceeded"},
                source_ip,
            )
            return False

        # Threat detection
        if data and not self.threat_detection.is_safe(data):
            self._log_incident(
                SecurityEvent.THREAT_DETECTED,
                "high",
                user_id,
                "threat_detection",
                operation,
                {"reason": "suspicious_input"},
                source_ip,
            )
            return False

        # Access control
        if not self.access_control.check_access(
            user_id, operation.split(".")[0], operation.split(".")[-1]
        ):
            self._log_incident(
                SecurityEvent.AUTHORIZATION,
                "medium",
                user_id,
                "access_denied",
                operation,
                {"reason": "insufficient_permissions"},
                source_ip,
            )
            return False

        # Log successful validation
        self._log_incident(
            SecurityEvent.AUTHENTICATION,
            "low",
            user_id,
            "validation_passed",
            operation,
            {"status": "approved"},
            source_ip,
        )

        return True

    def _log_incident(
        self,
        event_type: SecurityEvent,
        severity: str,
        user_id: str,
        resource: str,
        action: str,
        details: Dict[str, Any],
        source_ip: str = None,
    ):
        """Log a security incident."""
        incident = SecurityIncident(
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            resource=resource,
            action=action,
            details=details,
            source_ip=source_ip,
        )
        self.audit_logger.log_event(incident)

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.encryption.encrypt(data)

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self.encryption.decrypt(encrypted_data)

    def get_audit_trail(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[SecurityEvent] = None,
        hours: int = 24,
    ) -> List[SecurityIncident]:
        """Get audit trail for specified criteria."""
        since = time.time() - (hours * 3600)
        return self.audit_logger.get_events(user_id, event_type, since)

    def security_health_check(self) -> Dict[str, Any]:
        """Perform security health check."""
        return {
            "encryption_status": "operational" if self.encryption else "degraded",
            "audit_logging": "operational" if self.audit_logger else "failed",
            "threat_detection": "operational" if self.threat_detection else "failed",
            "access_control": "operational" if self.access_control else "failed",
            "rate_limiting": "operational" if self.rate_limiter else "failed",
            "recent_incidents": len(self.get_audit_trail(hours=1)),
        }


# Global security manager instance
security_manager = SecurityManager()


def secure_operation(operation_name: str):
    """Decorator for securing operations."""

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user_id from kwargs or args (assuming it's passed)
            user_id = kwargs.get(
                "user_id", getattr(args[0] if args else None, "user_id", "anonymous")
            )

            if not security_manager.validate_operation(user_id, operation_name, kwargs):
                raise PermissionError(
                    f"Security validation failed for operation: {operation_name}"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
