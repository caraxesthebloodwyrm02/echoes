"""
Enhanced Accounting module - Mock implementation for assistant functionality.

Provides enhanced accounting and value tracking for the Echoes assistant.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class ValueType(Enum):
    """Types of values that can be tracked."""

    MONETARY = "monetary"
    COGNITIVE = "cognitive"
    TEMPORAL = "temporal"
    SOCIAL = "social"
    KNOWLEDGE = "knowledge"


class AccountingPeriod(Enum):
    """Accounting periods."""

    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class ValueEntry:
    """Represents a value entry in the accounting system."""

    id: str
    value_type: ValueType
    amount: float
    unit: str
    description: str
    timestamp: datetime = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class EnhancedAccountingSystem:
    """Enhanced accounting system for tracking various value types."""

    def __init__(self):
        self.entries: list[ValueEntry] = []
        self.balances: dict[ValueType, float] = dict.fromkeys(ValueType, 0.0)
        self.period = AccountingPeriod.REAL_TIME

    def record_value(
        self,
        value_type: ValueType,
        amount: float,
        unit: str,
        description: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Record a value entry."""
        import uuid

        entry = ValueEntry(
            id=str(uuid.uuid4()),
            value_type=value_type,
            amount=amount,
            unit=unit,
            description=description,
            metadata=metadata,
        )

        self.entries.append(entry)
        self.balances[value_type] += amount

        return entry.id

    def get_balance(self, value_type: ValueType) -> float:
        """Get balance for a specific value type."""
        return self.balances.get(value_type, 0.0)

    def get_entries_by_type(self, value_type: ValueType) -> list[ValueEntry]:
        """Get all entries of a specific type."""
        return [entry for entry in self.entries if entry.value_type == value_type]

    def get_entries_in_period(self, start: datetime, end: datetime) -> list[ValueEntry]:
        """Get entries within a time period."""
        return [entry for entry in self.entries if start <= entry.timestamp <= end]

    def calculate_roi(self, value_type: ValueType) -> dict[str, float]:
        """Calculate simple ROI for a value type."""
        entries = self.get_entries_by_type(value_type)
        if not entries:
            return {"roi": 0.0, "total_invested": 0.0, "total_returned": 0.0}

        invested = sum(e.amount for e in entries if e.amount < 0)
        returned = sum(e.amount for e in entries if e.amount > 0)

        if invested == 0:
            return {
                "roi": float("inf"),
                "total_invested": 0.0,
                "total_returned": returned,
            }

        roi = (returned - invested) / invested * 100
        return {"roi": roi, "total_invested": abs(invested), "total_returned": returned}

    def generate_report(self, period: AccountingPeriod | None = None) -> dict[str, Any]:
        """Generate accounting report."""
        report_period = period or self.period

        # Calculate statistics
        stats = {}
        for value_type in ValueType:
            entries = self.get_entries_by_type(value_type)
            if entries:
                stats[value_type.value] = {
                    "count": len(entries),
                    "total": sum(e.amount for e in entries),
                    "average": sum(e.amount for e in entries) / len(entries),
                    "balance": self.get_balance(value_type),
                    "roi": self.calculate_roi(value_type),
                }

        return {
            "period": report_period.value,
            "generated_at": datetime.now().isoformat(),
            "total_entries": len(self.entries),
            "value_types": stats,
        }

    def set_period(self, period: AccountingPeriod):
        """Set accounting period."""
        self.period = period

    def clear_old_entries(self, days: int = 30):
        """Clear entries older than specified days."""
        cutoff = datetime.now() - datetime.timedelta(days=days)
        self.entries = [e for e in self.entries if e.timestamp > cutoff]

        # Recalculate balances
        self.balances = dict.fromkeys(ValueType, 0.0)
        for entry in self.entries:
            self.balances[entry.value_type] += entry.amount


# Global instance
_accounting = EnhancedAccountingSystem()


def get_enhanced_accounting() -> EnhancedAccountingSystem:
    """Get the global enhanced accounting system."""
    return _accounting


# Export symbols for backward compatibility
__all__ = [
    "get_enhanced_accounting",
    "ValueType",
    "AccountingPeriod",
    "ValueEntry",
    "EnhancedAccountingSystem",
]
