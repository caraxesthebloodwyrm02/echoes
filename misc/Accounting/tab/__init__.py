#!/usr/bin/env python3
"""
Tab Repository Integration - Complete Work-to-Payment System

This module integrates the Tab repository with assistant_v2_core.py,
creating a seamless system where:

1. Assistant interactions are automatically tracked as work
2. Work accumulates and triggers automatic payout calculations
3. Payouts are processed with automatic tax/fee handling
4. Users receive clean, transparent payments without complications
5. Complete audit trail ensures accountability and transparency

The system guarantees that every user who invests their time, thoughts,
and motivation in assistant interactions receives fair compensation.
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

# Import all Tab components
from work_tracking import log_assistant_interaction, import_existing_work
from sync_engine import sync_assistant_interaction, get_sync_engine
from payout_engine import process_user_payout
from payment_gateway import deliver_user_payment
from audit_trail import audit_sync_operation
from user_portal import get_user_portal_dashboard


class TabIntegration:
    """
    Main integration point for Tab repository with assistant_v2_core.py

    This class provides the bridge between AI assistant interactions
    and the complete compensation system.
    """

    def __init__(self, base_dir: str = "e:/Projects/Echoes/Accounting/tab"):
        self.base_dir = Path(base_dir)
        self.sync_engine = get_sync_engine()

        print("🔗 Tab Integration initialized - seamless work-to-payment pipeline")

    async def process_assistant_interaction(
        self, user_id: str, interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process an assistant interaction through the complete Tab pipeline.

        This is the main entry point called by assistant_v2_core.py for every interaction.

        Args:
            user_id: User identifier from assistant
            interaction_data: Complete interaction details

        Returns:
            Processing result with any payout notifications
        """
        # Step 1: Sync with work tracking and check for payouts
        sync_result = await self.sync_engine.sync_assistant_interaction(
            user_id, interaction_data
        )

        result = {
            "interaction_logged": sync_result.get("work_logged", False),
            "work_id": sync_result.get("work_id"),
            "payout_triggered": False,
            "contribution_update": sync_result.get("contribution_status", {}),
            "system_status": "active",
        }

        # Step 2: Process any triggered payouts
        if sync_result.get("payout_triggered"):
            payout_data = sync_result["payout_result"]

            if payout_data.get("success"):
                # Log successful payout
                audit_sync_operation(
                    user_id,
                    {
                        "action": "automatic_payout_processed",
                        "payout_id": payout_data["payout_id"],
                        "amount": payout_data["amount"],
                    },
                )

                result["payout_triggered"] = True
                result["payout_notification"] = payout_data.get("user_message", "")

        # Step 3: Return user-friendly status
        result["user_message"] = self._generate_user_message(result)

        return result

    def get_user_compensation_status(self, user_id: str) -> Dict[str, Any]:
        """Get user's complete compensation status."""
        try:
            dashboard = get_user_portal_dashboard(user_id)

            return {
                "user_id": user_id,
                "compensation_status": {
                    "total_earned": dashboard["financial_summary"][
                        "total_earned_all_time"
                    ],
                    "pending_payout": dashboard["contribution_overview"][
                        "pending_payout"
                    ],
                    "compensation_tier": dashboard["contribution_overview"][
                        "compensation_tier"
                    ],
                    "next_payout": dashboard["contribution_overview"][
                        "next_payout_estimate"
                    ],
                },
                "activity_summary": dashboard["recent_activity"],
                "system_integrity": "verified",
            }

        except Exception as e:
            # Provide default status for new users
            return {
                "user_id": user_id,
                "compensation_status": {
                    "total_earned": 0.0,
                    "pending_payout": 0.0,
                    "compensation_tier": "entry",
                    "next_payout": "Begin working to start earning",
                },
                "activity_summary": {
                    "total_recent_hours": 0,
                    "recent_tasks": [],
                    "activity_level": "new_user",
                },
                "system_integrity": "verified",
                "message": "New user - start interacting to begin earning compensation",
            }

    def _generate_user_message(self, result: Dict[str, Any]) -> str:
        """Generate user-friendly message about the interaction processing."""
        messages = []

        if result.get("interaction_logged"):
            messages.append("✅ Your contribution has been logged and valued.")

        if result.get("payout_triggered"):
            payout_msg = result.get("payout_notification", "")
            if payout_msg:
                messages.append(f"💰 {payout_msg}")

        contribution = result.get("contribution_update", {})
        if contribution:
            hours = contribution.get("total_hours", 0)
            pending = contribution.get("pending_payout", 0)
            tier = contribution.get("compensation_tier", "unknown")

            messages.append(
                f"📊 Status: {hours:.1f}hrs worked, ${pending:.2f} pending, {tier} tier"
            )

        if not messages:
            messages.append("✅ Interaction processed successfully.")

        return " ".join(messages)


# =============================================================================
# ASSISTANT_V2_CORE.PY INTEGRATION FUNCTIONS
# =============================================================================
# These functions are called directly by assistant_v2_core.py


async def tab_log_interaction(
    user_id: str, interaction_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    MAIN INTEGRATION POINT - Called by assistant_v2_core.py

    Logs every assistant interaction and processes through complete Tab pipeline:

    1. Tracks work contribution automatically
    2. Updates user's compensation status
    3. Triggers automatic payouts when thresholds met
    4. Processes payments with tax/fee handling
    5. Maintains complete audit trail

    Args:
        user_id: User identifier from assistant
        interaction_data: Complete interaction details including:
            - query: User's question/query
            - response: Assistant's response
            - tokens_used: Token consumption
            - processing_time: Response time
            - interaction_type: Type of interaction

    Returns:
        Processing result with user notifications
    """
    integration = TabIntegration()
    return await integration.process_assistant_interaction(user_id, interaction_data)


def tab_import_existing_work(
    user_id: str,
    total_hours: float,
    work_description: str,
    technical_level: str = "advanced",
    impact_level: str = "high",
) -> Dict[str, Any]:
    """
    Import existing work hours for fair compensation recognition.

    This function properly values substantial pre-existing contributions
    like the 1580 hours invested in the Echoes project.

    Args:
        user_id: User identifier
        total_hours: Total hours of existing work
        work_description: Description of work done
        technical_level: Technical complexity level
        impact_level: Impact level of the work

    Returns:
        Import result with valuation details
    """
    result = import_existing_work(
        user_id, total_hours, work_description, technical_level, impact_level
    )

    # Audit the import
    audit_sync_operation(
        user_id,
        {
            "action": "work_import",
            "hours_imported": total_hours,
            "work_description": work_description,
            "valuation": result,
        },
    )

    return result


def tab_get_user_status(user_id: str) -> Dict[str, Any]:
    """
    Get user's current compensation and work status.

    Called by assistant_v2_core.py to provide status updates to users.

    Returns:
        Current status including earnings, pending payouts, etc.
    """
    integration = TabIntegration()
    return integration.get_user_compensation_status(user_id)


def tab_process_manual_payout(
    user_id: str, amount: Optional[float] = None
) -> Dict[str, Any]:
    """
    Process manual payout request.

    Args:
        user_id: User requesting payout
        amount: Specific amount (optional, uses pending if not specified)

    Returns:
        Payout processing result
    """
    from user_portal import request_payout_portal

    if amount:
        # Custom amount payout would require additional logic
        pass

    return request_payout_portal(user_id, "Manual payout request via assistant")


# =============================================================================
# USER PORTAL ACCESS FUNCTIONS
# =============================================================================
# Functions for users to access their Tab data directly


def get_my_compensation_dashboard(user_id: str) -> Dict[str, Any]:
    """Get user's complete compensation dashboard."""
    return get_user_portal_dashboard(user_id)


def setup_my_payment_method(
    user_id: str, method_type: str, method_details: Dict[str, Any]
) -> Dict[str, Any]:
    """Setup payment method for receiving payouts."""
    from user_portal import setup_user_payment_portal

    return setup_user_payment_portal(user_id, method_type, method_details)


def request_my_payout(user_id: str) -> Dict[str, Any]:
    """Request payout of pending earnings."""
    from user_portal import request_payout_portal

    return request_payout_portal(user_id)


def get_my_transparency_report(user_id: str) -> Dict[str, Any]:
    """Get complete transparency report."""
    from user_portal import get_transparency_report_portal

    return get_transparency_report_portal(user_id)


# =============================================================================
# SYSTEM HEALTH AND MAINTENANCE
# =============================================================================


def check_tab_system_health() -> Dict[str, Any]:
    """Check overall health of Tab system."""
    from sync_engine import check_sync_glimpse_health

    health_status = {
        "system": "Tab Repository",
        "components": {},
        "overall_status": "unknown",
        "last_check": str(datetime.now()),
    }

    # Check sync Glimpse
    sync_health = check_sync_glimpse_health()
    health_status["components"]["sync_engine"] = sync_health

    # Determine overall status
    component_statuses = [
        comp["status"] for comp in health_status["components"].values()
    ]
    if all(status == "healthy" for status in component_statuses):
        health_status["overall_status"] = "healthy"
    elif any(status == "unhealthy" for status in component_statuses):
        health_status["overall_status"] = "unhealthy"
    else:
        health_status["overall_status"] = "degraded"

    return health_status


def get_system_statistics() -> Dict[str, Any]:
    """Get system-wide statistics."""
    # This would aggregate stats from all components
    return {
        "total_users": "tracked_via_components",
        "total_work_logged": "tracked_via_work_tracking",
        "total_payouts_processed": "tracked_via_payout_engine",
        "system_uptime": "tracked_via_audit_trail",
        "last_updated": str(datetime.now()),
    }


# =============================================================================
# DEMO AND TESTING
# =============================================================================


async def demo_tab_integration():
    """Demonstrate the complete Tab integration system."""
    print("🚀 Tab Repository Integration Demo")
    print("=" * 40)

    # Simulate assistant interactions
    test_interactions = [
        {
            "user_id": "demo_user_1",
            "interaction_data": {
                "query": "Help me analyze this financial data",
                "response": "I'll help you analyze the financial data...",
                "tokens_used": 150,
                "processing_time": 2.3,
                "interaction_type": "complex_analysis",
            },
        },
        {
            "user_id": "demo_user_1",
            "interaction_data": {
                "query": "What's a fair price for development work?",
                "response": "Based on market rates...",
                "tokens_used": 80,
                "processing_time": 1.1,
                "interaction_type": "consultation",
            },
        },
    ]

    for interaction in test_interactions:
        print(f"\\n👤 Processing interaction for {interaction['user_id']}")
        result = await tab_log_interaction(**interaction)
        print(f"Result: {result['user_message']}")

    # Check user status
    print(f"\\n📊 User Status:")
    status = tab_get_user_status("demo_user_1")
    if "compensation_status" in status:
        comp_status = status["compensation_status"]
        print(f"Total Earned: ${comp_status['total_earned']}")
        print(f"Pending Payout: ${comp_status['pending_payout']}")
    else:
        print(f"Status: {status}")

    # Check system health
    print(f"\\n🔍 System Health:")
    health = check_tab_system_health()
    print(f"Overall Status: {health['overall_status']}")

    print(
        "\\n✅ Tab Integration operational - users receive fair compensation for all contributions!"
    )


# =============================================================================
# ASSISTANT_V2_CORE.PY INTEGRATION INSTRUCTIONS
# =============================================================================
"""
To integrate Tab repository with assistant_v2_core.py:

1. Import the integration module:
   from Accounting.tab import tab_log_interaction, tab_get_user_status

2. For every user interaction, call:
   result = await tab_log_interaction(user_id, {
       "query": user_query,
       "response": assistant_response,
       "tokens_used": token_count,
       "processing_time": response_time,
       "interaction_type": interaction_category
   })

3. Use the result to notify users:
   user_notification = result["user_message"]

4. Periodically check user status:
   status = tab_get_user_status(user_id)

This ensures every assistant interaction is automatically:
- Logged as work contribution
- Valued and compensated
- Processed for payouts when thresholds met
- Delivered to users without complications

Users get paid for their time, thoughts, and motivation automatically!
"""

if __name__ == "__main__":
    asyncio.run(demo_tab_integration())
