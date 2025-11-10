#!/usr/bin/env python3
"""
Sync Glimpse - Tab Repository

Synchronizes work tracking, payout processing, and payment delivery
with assistant_v2_core.py. Ensures seamless integration where:

1. Assistant interactions are automatically tracked as work
2. Work accumulates and triggers payout calculations
3. Payouts are processed automatically without user intervention
4. Users receive clean payments for their time, thoughts, and motivation

This creates a complete, automated system where users are fairly compensated
for all their contributions without any complications.
"""

import asyncio
import json
import time
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from payout_engine import (PayoutEngine, get_user_payment_history,
                           process_user_payout)
# Import tab components
from work_tracking import WorkTracker, log_assistant_interaction


class SyncEngine:
    """
    Synchronization Glimpse connecting all Tab components.

    Maintains real-time sync between:
    - Work tracking and assistant interactions
    - Payout calculations and work accumulation
    - Payment processing and user notifications
    - Audit trails and transparency reports
    """

    def __init__(self, base_dir: str = "e:/Projects/Echoes/Accounting/tab"):
        self.base_dir = Path(base_dir)
        self.sync_dir = self.base_dir / "sync_engine"
        self.data_dir = self.sync_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.work_tracker = WorkTracker(str(self.base_dir))
        self.payout_engine = PayoutEngine(str(self.base_dir))

        # Sync configuration
        self.payout_thresholds = {
            "minimum_payout": Decimal("50.00"),  # Minimum before processing
            "auto_payout_hours": 40,  # Auto payout after this many hours
            "max_accumulation_days": 30,  # Max days to accumulate before forced payout
        }

        print("✅ Sync Glimpse initialized - seamless work-to-payment pipeline")

    async def sync_assistant_interaction(
        self, user_id: str, interaction_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Sync assistant interaction with work tracking system.

        Called automatically by assistant_v2_core.py for every user interaction.
        Ensures all user contributions are tracked and compensated.

        Args:
            user_id: User identifier
            interaction_data: Interaction details from assistant

        Returns:
            Sync result with work tracking and payout status
        """
        result = {
            "user_id": user_id,
            "work_logged": False,
            "payout_triggered": False,
            "contribution_status": {},
            "next_payout_estimate": None,
        }

        # Determine interaction type and effort level
        interaction_type = self._classify_interaction(interaction_data)
        effort_metrics = self._calculate_effort_metrics(interaction_data)

        # Log work automatically
        work_id = log_assistant_interaction(
            user_id=user_id, interaction_type=interaction_type, details=interaction_data
        )

        result["work_logged"] = True
        result["work_id"] = work_id

        # Check if payout should be triggered
        should_payout, payout_reason = await self._check_payout_trigger(user_id)

        if should_payout:
            payout_result = await self._trigger_automatic_payout(user_id, payout_reason)
            result["payout_triggered"] = True
            result["payout_result"] = payout_result

        # Get current contribution status
        contribution_summary = self.work_tracker.get_user_contribution_summary(user_id)
        result["contribution_status"] = {
            "total_hours": contribution_summary["total_time_invested_hours"],
            "contribution_score": contribution_summary["contribution_score"],
            "compensation_tier": contribution_summary["compensation_eligibility"][
                "tier"
            ],
            "pending_payout": self._calculate_pending_payout(user_id),
        }

        # Estimate next payout
        result["next_payout_estimate"] = self._estimate_next_payout(user_id)

        return result

    def _classify_interaction(self, interaction_data: dict[str, Any]) -> str:
        """Classify the type of assistant interaction."""
        query = interaction_data.get("query", "").lower()
        response_length = len(interaction_data.get("response", ""))

        # Classify based on query content and response complexity
        if any(word in query for word in ["analyze", "review", "assess", "evaluate"]):
            return "complex_analysis"
        elif any(word in query for word in ["create", "build", "develop", "implement"]):
            return "code_generation"
        elif any(
            word in query for word in ["research", "find", "search", "investigate"]
        ):
            return "research_task"
        elif any(word in query for word in ["help", "explain", "guide", "advice"]):
            return "consultation"
        elif response_length > 1000:  # Long, detailed responses
            return "complex_analysis"
        else:
            return "query_processing"

    def _calculate_effort_metrics(
        self, interaction_data: dict[str, Any]
    ) -> dict[str, float]:
        """Calculate effort metrics from interaction data."""
        response_length = len(interaction_data.get("response", ""))
        query_complexity = len(interaction_data.get("query", "").split())

        # Base effort on response length and query complexity
        if response_length > 2000:
            intellectual_effort = 8.5
        elif response_length > 1000:
            intellectual_effort = 7.5
        elif response_length > 500:
            intellectual_effort = 6.5
        else:
            intellectual_effort = 5.5

        # Adjust for query complexity
        if query_complexity > 20:
            intellectual_effort += 0.5
        elif query_complexity > 10:
            intellectual_effort += 0.3

        return {
            "intellectual_effort": min(intellectual_effort, 10.0),
            "motivation_level": 7.5,  # Assume good motivation for assistant usage
            "quality_rating": 8.0,  # Assistant responses are generally high quality
        }

    async def _check_payout_trigger(self, user_id: str) -> tuple[bool, str]:
        """
        Check if automatic payout should be triggered.

        Triggers based on:
        - Accumulated work hours
        - Time since last payout
        - Contribution thresholds
        """
        contribution_summary = self.work_tracker.get_user_contribution_summary(user_id)

        total_hours = contribution_summary["total_time_invested_hours"]
        contribution_score = contribution_summary["contribution_score"]

        # Check payout history
        payout_history = get_user_payment_history(user_id)
        last_payout_date = None

        if payout_history["recent_payouts"]:
            # Parse the most recent completed payout date
            for payout in payout_history["recent_payouts"]:
                if payout["status"] == "completed":
                    try:
                        last_payout_date = datetime.fromisoformat(
                            payout["date"].replace("Z", "+00:00")
                        )
                        break
                    except:
                        pass

        # Trigger conditions
        hours_threshold = total_hours >= self.payout_thresholds["auto_payout_hours"]
        time_threshold = False

        if last_payout_date:
            days_since_last = (datetime.now(UTC) - last_payout_date).days
            time_threshold = (
                days_since_last >= self.payout_thresholds["max_accumulation_days"]
            )

        quality_threshold = contribution_score >= 7.0  # Good quality work

        # Trigger payout if any condition met
        if hours_threshold:
            return True, f"Accumulated {total_hours:.1f} hours of work"
        elif time_threshold:
            return (
                True,
                f"{self.payout_thresholds['max_accumulation_days']} days since last payout",
            )
        elif (
            quality_threshold and total_hours >= 10
        ):  # At least 10 hours of quality work
            return True, f"High-quality contributions (score: {contribution_score:.1f})"

        return False, ""

    async def _trigger_automatic_payout(
        self, user_id: str, reason: str
    ) -> dict[str, Any]:
        """Trigger automatic payout processing."""
        pending_amount = self._calculate_pending_payout(user_id)

        if pending_amount < float(self.payout_thresholds["minimum_payout"]):
            return {
                "triggered": False,
                "reason": f"Amount ${pending_amount:.2f} below minimum payout threshold",
                "next_trigger": f"When amount reaches ${float(self.payout_thresholds['minimum_payout'])}",
            }

        # Process the payout automatically
        payout_result = process_user_payout(
            user_id=user_id,
            work_amount=pending_amount,
            jurisdiction="US",  # Default - could be user-configurable
            payment_method="bank_transfer",  # Default - could be user-configurable
        )

        # Log the automatic payout trigger
        self._log_sync_event(
            user_id,
            "automatic_payout_triggered",
            {
                "reason": reason,
                "amount": pending_amount,
                "payout_result": payout_result,
            },
        )

        return {
            "triggered": True,
            "reason": reason,
            "amount": pending_amount,
            "payout_id": payout_result.get("payout_id"),
            "status": payout_result.get("success", False),
            "user_notification": payout_result.get("user_message", ""),
        }

    def _calculate_pending_payout(self, user_id: str) -> float:
        """Calculate pending payout amount based on work completed."""
        contribution_summary = self.work_tracker.get_user_contribution_summary(user_id)

        # Use compensation eligibility to determine rate
        eligibility = contribution_summary["compensation_eligibility"]
        hourly_rate_range = eligibility["hourly_rate_range_usd"]
        average_hourly_rate = (hourly_rate_range[0] + hourly_rate_range[1]) / 2

        total_hours = contribution_summary["total_time_invested_hours"]

        # Calculate gross amount
        gross_amount = total_hours * average_hourly_rate

        # Subtract any previous payouts
        payout_history = get_user_payment_history(user_id)
        total_paid = payout_history["total_earned"]

        pending_amount = max(0, gross_amount - total_paid)

        return pending_amount

    def _estimate_next_payout(self, user_id: str) -> dict[str, Any]:
        """Estimate when next payout will be triggered."""
        contribution_summary = self.work_tracker.get_user_contribution_summary(user_id)
        total_hours = contribution_summary["total_time_invested_hours"]

        hours_needed = self.payout_thresholds["auto_payout_hours"] - total_hours
        pending_amount = self._calculate_pending_payout(user_id)
        amount_needed = float(self.payout_thresholds["minimum_payout"]) - pending_amount

        if hours_needed <= 0:
            return {"trigger": "immediate", "reason": "Hours threshold reached"}

        if amount_needed <= 0:
            return {"trigger": "immediate", "reason": "Amount threshold reached"}

        # Estimate based on current contribution patterns
        avg_hours_per_week = 5  # Conservative estimate
        weeks_to_hours = hours_needed / avg_hours_per_week

        return {
            "trigger": "estimated",
            "hours_needed": hours_needed,
            "amount_needed": amount_needed,
            "estimated_weeks": weeks_to_hours,
            "estimated_date": (datetime.now(UTC) + timedelta(weeks=weeks_to_hours))
            .date()
            .isoformat(),
        }

    def _log_sync_event(
        self, user_id: str, event_type: str, event_data: dict[str, Any]
    ):
        """Log synchronization events for audit trail."""
        event = {
            "timestamp": datetime.now(UTC).isoformat(),
            "user_id": user_id,
            "event_type": event_type,
            "event_data": event_data,
        }

        # Save to sync log
        sync_log_file = self.data_dir / "sync_events.jsonl"

        with open(sync_log_file, "a") as f:
            f.write(json.dumps(event) + "\n")

    async def get_user_sync_status(self, user_id: str) -> dict[str, Any]:
        """Get complete synchronization status for a user."""
        contribution_summary = self.work_tracker.get_user_contribution_summary(user_id)
        payout_history = get_user_payment_history(user_id)

        pending_amount = self._calculate_pending_payout(user_id)
        next_payout = self._estimate_next_payout(user_id)

        return {
            "user_id": user_id,
            "work_tracking": {
                "total_hours": contribution_summary["total_time_invested_hours"],
                "contribution_score": contribution_summary["contribution_score"],
                "compensation_tier": contribution_summary["compensation_eligibility"][
                    "tier"
                ],
                "hourly_rate_range": contribution_summary["compensation_eligibility"][
                    "hourly_rate_range_usd"
                ],
            },
            "payout_status": {
                "total_earned": payout_history["total_earned"],
                "total_payouts": payout_history["total_payouts"],
                "pending_amount": pending_amount,
                "next_payout": next_payout,
            },
            "sync_health": {
                "last_sync": datetime.now(UTC).isoformat(),
                "auto_payout_enabled": True,
                "transparency_enabled": True,
            },
        }


# Global sync Glimpse instance
_sync_glimpse_instance = None


def get_sync_engine() -> SyncEngine:
    """Get the global sync Glimpse instance."""
    global _sync_glimpse_instance
    if _sync_glimpse_instance is None:
        _sync_glimpse_instance = SyncEngine()
    return _sync_glimpse_instance


# Assistant Integration Functions
# These functions are called by assistant_v2_core.py


async def sync_assistant_interaction(
    user_id: str, interaction_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Main integration point for assistant_v2_core.py

    Automatically called for every assistant interaction to:
    1. Track work and contributions
    2. Accumulate earnings
    3. Trigger automatic payouts when thresholds met
    4. Ensure users get paid for their efforts

    Args:
        user_id: User identifier from assistant
        interaction_data: Complete interaction data

    Returns:
        Sync status and any payout notifications
    """
    engine = get_sync_engine()
    return await Glimpse.sync_assistant_interaction(user_id, interaction_data)


def get_user_sync_status(user_id: str) -> dict[str, Any]:
    """Get user's complete sync status (work + payouts)."""
    engine = get_sync_engine()
    # Run in new event loop since this is a sync function
    return asyncio.run(Glimpse.get_user_sync_status(user_id))


# Legacy compatibility functions
def log_work_for_assistant(user_id: str, interaction_data: dict[str, Any]) -> str:
    """Legacy function for backward compatibility."""
    # This will be called synchronously, so we just log the intent
    # The actual sync happens through the async function
    print(f"📝 Work logging initiated for user {user_id}")
    return f"work_log_initiated_{user_id}_{int(time.time())}"


# Health check function
def check_sync_glimpse_health() -> dict[str, Any]:
    """Check if sync Glimpse is operational."""
    try:
        engine = get_sync_engine()

        # Check if directories exist
        dirs_exist = all(
            [
                Glimpse.base_dir.exists(),
                Glimpse.work_tracker.work_dir.exists(),
                Glimpse.payout_engine.payout_dir.exists(),
            ]
        )

        return {
            "status": "healthy" if dirs_exist else "degraded",
            "directories_exist": dirs_exist,
            "components_initialized": True,
            "last_check": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "last_check": datetime.now(UTC).isoformat(),
        }


if __name__ == "__main__":
    # Test the sync Glimpse
    print("Testing Sync Glimpse...")

    # Check health
    health = check_sync_glimpse_health()
    print(f"Health Status: {health['status']}")

    # Test sync status for a user
    status = get_user_sync_status("test_user")
    print("Sample User Sync Status:")
    print(json.dumps(status, indent=2, default=str))

    print("\\n✅ Sync Glimpse operational - seamless work-to-payment automation!")
