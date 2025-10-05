"""Alert management system."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from packages.core import get_logger

logger = get_logger("monitoring.alerts")


@dataclass
class Alert:
    """Alert data structure."""

    name: str
    severity: str  # "info", "warning", "critical"
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]


class AlertManager:
    """Manages alerts and notifications."""

    def __init__(self) -> None:
        self.logger = logger
        self.alerts: List[Alert] = []
        self.handlers: Dict[str, Callable[[Alert], None]] = {}

    def register_handler(self, name: str, handler: Callable[[Alert], None]) -> None:
        """Register an alert handler."""
        self.handlers[name] = handler
        self.logger.info(f"Registered alert handler: {name}")

    def send_alert(self, alert: Alert) -> None:
        """Send an alert to all registered handlers."""
        self.alerts.append(alert)
        self.logger.info(f"Alert: [{alert.severity}] {alert.name} - {alert.message}")

        for handler_name, handler in self.handlers.items():
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler '{handler_name}' failed: {e}")

    def create_alert(
        self, name: str, severity: str, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Alert:
        """Create and send an alert."""
        alert = Alert(
            name=name,
            severity=severity,
            message=message,
            timestamp=datetime.now(),
            metadata=metadata or {},
        )

        self.send_alert(alert)
        return alert


__all__ = ["Alert", "AlertManager"]
