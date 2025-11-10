#!/usr/bin/env python3
"""
User Portal - Tab Repository

User-friendly interface for managing work tracking, payouts, and payments.
Provides complete transparency and control over compensation process.

Features:
- Work history and contribution tracking
- Payment method management
- Payout status and history
- Transparency reports and compliance status
- Easy setup and configuration
"""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from audit_trail import get_user_compliance_status
from payment_gateway import get_user_payment_status, setup_user_payment_method
from payout_engine import get_user_payment_history
# Import Tab components
from work_tracking import WorkTracker


class UserPortal:
    """
    User portal for complete compensation management.

    Gives users full visibility and control over:
    - Their work contributions and value
    - Payment methods and preferences
    - Payout history and status
    - Compliance and transparency
    """

    def __init__(self, base_dir: str = "e:/Projects/Echoes/Accounting/tab"):
        self.base_dir = Path(base_dir)
        self.portal_dir = self.base_dir / "user_portal"
        self.data_dir = self.portal_dir / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.work_tracker = WorkTracker(str(self.base_dir))

        print("✅ User Portal initialized - complete user compensation control")

    def get_user_dashboard(self, user_id: str) -> dict[str, Any]:
        """
        Get complete user dashboard with all compensation information.

        Args:
            user_id: User identifier

        Returns:
            Comprehensive dashboard data
        """
        # Get work and contribution data
        contribution_summary = self.work_tracker.get_user_contribution_summary(user_id)

        # Get payout history
        payout_history = get_user_payment_history(user_id)

        # Get payment status
        payment_status = get_user_payment_status(user_id)

        # Get compliance status
        compliance_status = get_user_compliance_status(user_id)

        # Calculate pending payout
        pending_amount = self._calculate_pending_payout(
            contribution_summary, payout_history
        )

        # Get next payout estimate
        next_payout = self._estimate_next_payout(contribution_summary)

        dashboard = {
            "user_id": user_id,
            "last_updated": datetime.now(UTC).isoformat(),
            "contribution_overview": {
                "total_hours_worked": contribution_summary["total_time_invested_hours"],
                "contribution_score": contribution_summary["contribution_score"],
                "compensation_tier": contribution_summary["compensation_eligibility"][
                    "tier"
                ],
                "hourly_rate_range": contribution_summary["compensation_eligibility"][
                    "hourly_rate_range_usd"
                ],
                "pending_payout": pending_amount,
                "next_payout_estimate": next_payout,
            },
            "financial_summary": {
                "total_earned_all_time": payout_history["total_earned"],
                "total_payouts_received": payout_history["total_payouts"],
                "average_payout_amount": payout_history["average_payout"],
                "pending_amount": pending_amount,
                "estimated_annual_earnings": self._calculate_annual_projection(
                    contribution_summary
                ),
            },
            "payment_methods": {
                "total_methods": payment_status["payment_methods"],
                "available_methods": payment_status["available_methods"],
                "setup_complete": payment_status["payment_methods"] > 0,
            },
            "compliance_status": {
                "compliance_score": compliance_status["compliance_score"],
                "audit_integrity": compliance_status["audit_integrity"][
                    "integrity_status"
                ],
                "key_findings": compliance_status["key_findings"],
                "recommendations": compliance_status["recommendations"],
            },
            "recent_activity": {
                "recent_payouts": payout_history["recent_payouts"][:3],
                "work_summary": self._get_recent_work_summary(user_id),
            },
            "quick_actions": self._generate_quick_actions(
                user_id, contribution_summary, payment_status
            ),
        }

        return dashboard

    def setup_payment_method(
        self, user_id: str, method_type: str, method_details: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Easy setup of payment methods through the portal.

        Args:
            user_id: User identifier
            method_type: Payment method type
            method_details: Method-specific details

        Returns:
            Setup result
        """
        try:
            method_id = setup_user_payment_method(user_id, method_type, method_details)

            return {
                "success": True,
                "method_id": method_id,
                "method_type": method_type,
                "message": f"✅ {method_type.title()} payment method added successfully!",
                "next_steps": [
                    "Your payment method is now active",
                    "Future payouts will be sent automatically",
                    "Check your dashboard for payout status",
                ],
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "❌ Failed to add payment method. Please check your details and try again.",
                "troubleshooting": [
                    "Verify all required fields are provided",
                    "Check payment method details for accuracy",
                    "Contact support if issues persist",
                ],
            }

    def request_manual_payout(self, user_id: str, reason: str = "") -> dict[str, Any]:
        """
        Request manual payout for accumulated work.

        Args:
            user_id: User identifier
            reason: Reason for manual payout request

        Returns:
            Payout request result
        """
        contribution_summary = self.work_tracker.get_user_contribution_summary(user_id)
        payout_history = get_user_payment_history(user_id)

        pending_amount = self._calculate_pending_payout(
            contribution_summary, payout_history
        )

        if pending_amount < 50.0:  # Minimum payout threshold
            return {
                "success": False,
                "message": f"❌ Insufficient funds for payout. Minimum payout is $50. Current pending: ${pending_amount:.2f}",
                "pending_amount": pending_amount,
                "minimum_required": 50.0,
                "suggested_wait": "Continue working to accumulate more earnings",
            }

        # Check if payment method is set up
        payment_status = get_user_payment_status(user_id)
        if payment_status["payment_methods"] == 0:
            return {
                "success": False,
                "message": "❌ No payment method configured. Please set up a payment method first.",
                "setup_required": True,
                "pending_amount": pending_amount,
            }

        # Process manual payout
        from payout_engine import process_user_payout

        result = process_user_payout(
            user_id=user_id,
            work_amount=pending_amount,
            jurisdiction="US",
            payment_method="bank_transfer",
        )

        if result["success"]:
            return {
                "success": True,
                "payout_id": result["payout_id"],
                "amount": result["amount_paid"],
                "message": result["user_message"],
                "processing_time": result["processing_time"],
                "next_steps": [
                    "Monitor payout status in your dashboard",
                    "Check your payment method for delivery confirmation",
                    "New work will continue accumulating for future payouts",
                ],
            }
        else:
            return {
                "success": False,
                "message": f"❌ Payout failed: {result.get('error', 'Unknown error')}",
                "troubleshooting": [
                    "Verify payment method details",
                    "Check account balance/limits",
                    "Contact support for assistance",
                ],
            }

    def generate_transparency_report(self, user_id: str) -> dict[str, Any]:
        """Generate complete transparency report for the user."""
        dashboard = self.get_user_dashboard(user_id)

        # Add detailed breakdowns
        work_history = self.work_tracker.get_user_work_history(user_id, limit=50)

        report = {
            "user_id": user_id,
            "generated_at": datetime.now(UTC).isoformat(),
            "period": "All time",
            "executive_summary": {
                "total_contribution_hours": dashboard["contribution_overview"][
                    "total_hours_worked"
                ],
                "total_earned": dashboard["financial_summary"]["total_earned_all_time"],
                "current_pending": dashboard["contribution_overview"]["pending_payout"],
                "compensation_tier": dashboard["contribution_overview"][
                    "compensation_tier"
                ],
                "compliance_score": dashboard["compliance_status"]["compliance_score"],
            },
            "contribution_breakdown": {
                "work_history": [
                    {
                        "date": entry.timestamp[:10],
                        "task": entry.task_type,
                        "hours": entry.time_invested_minutes / 60,
                        "quality": entry.quality_rating,
                        "value_generated": self._calculate_work_value(entry),
                    }
                    for entry in work_history
                ],
                "skill_development": dashboard["contribution_overview"],
                "impact_metrics": self._calculate_impact_metrics(work_history),
            },
            "financial_transparency": {
                "earnings_breakdown": dashboard["financial_summary"],
                "tax_information": {
                    "tax_responsibility": "Handled automatically by system",
                    "jurisdiction": "US (default)",
                    "transparency": "All tax calculations visible in payout reports",
                    "user_burden": "Zero - system manages all tax complexities",
                },
                "fee_structure": {
                    "platform_fee": "5% - System maintenance and development",
                    "payment_processing": "2.9% - Third-party payment services",
                    "taxes": "Automatic - Based on jurisdiction and income type",
                    "transparency": "All fees disclosed before any deductions",
                },
            },
            "payment_methods": dashboard["payment_methods"],
            "compliance_audit": dashboard["compliance_status"],
            "system_guarantees": {
                "payment_guarantee": "All legitimate work contributions are compensated",
                "transparency_guarantee": "Complete visibility into all calculations and fees",
                "fairness_guarantee": "Consistent application of rates and rules",
                "privacy_guarantee": "Work and payment data kept secure and private",
                "support_guarantee": "Full assistance for any questions or issues",
            },
            "user_responsibilities": {
                "accurate_reporting": "Log work honestly and completely",
                "payment_method_setup": "Maintain active payment methods",
                "compliance": "Follow platform guidelines and terms",
                "communication": "Report any issues or discrepancies promptly",
            },
        }

        return report

    def _calculate_pending_payout(
        self, contribution_summary: dict[str, Any], payout_history: dict[str, Any]
    ) -> float:
        """Calculate pending payout amount."""
        # Use compensation eligibility to determine rate
        eligibility = contribution_summary["compensation_eligibility"]
        hourly_rate_range = eligibility["hourly_rate_range_usd"]
        average_hourly_rate = (hourly_rate_range[0] + hourly_rate_range[1]) / 2

        total_hours = contribution_summary["total_time_invested_hours"]
        gross_amount = total_hours * average_hourly_rate

        # Subtract previous payouts
        total_paid = payout_history["total_earned"]

        return max(0, gross_amount - total_paid)

    def _estimate_next_payout(
        self, contribution_summary: dict[str, Any]
    ) -> dict[str, Any]:
        """Estimate when next automatic payout will occur."""
        total_hours = contribution_summary["total_time_invested_hours"]
        hours_needed = 40 - total_hours  # Auto payout at 40 hours

        if hours_needed <= 0:
            return {"trigger": "immediate", "reason": "Hours threshold reached"}

        # Estimate based on historical activity (assume 5 hours/week)
        weeks_needed = hours_needed / 5

        return {
            "trigger": "estimated",
            "hours_needed": hours_needed,
            "estimated_weeks": weeks_needed,
            "estimated_date": f"In approximately {weeks_needed:.1f} weeks",
        }

    def _calculate_annual_projection(
        self, contribution_summary: dict[str, Any]
    ) -> float:
        """Calculate annual earnings projection."""
        total_hours = contribution_summary["total_time_invested_hours"]
        eligibility = contribution_summary["compensation_eligibility"]
        hourly_rate_range = eligibility["hourly_rate_range_usd"]
        average_hourly_rate = (hourly_rate_range[0] + hourly_rate_range[1]) / 2

        # Project annual hours (assume 10 hours/week * 50 weeks)
        annual_hours = 500
        annual_earnings = annual_hours * average_hourly_rate

        return annual_earnings

    def _get_recent_work_summary(self, user_id: str) -> dict[str, Any]:
        """Get summary of recent work activity."""
        work_history = self.work_tracker.get_user_work_history(user_id, limit=10)

        if not work_history:
            return {
                "total_recent_hours": 0,
                "recent_tasks": [],
                "activity_level": "none",
            }

        total_hours = sum(entry.time_invested_minutes for entry in work_history) / 60
        task_types = list(set(entry.task_type for entry in work_history))

        return {
            "total_recent_hours": round(total_hours, 1),
            "recent_tasks": task_types,
            "activity_level": "high"
            if total_hours > 20
            else "moderate"
            if total_hours > 10
            else "low",
        }

    def _generate_quick_actions(
        self,
        user_id: str,
        contribution_summary: dict[str, Any],
        payment_status: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Generate quick actions based on user status."""
        actions = []

        # Payment method setup
        if payment_status["payment_methods"] == 0:
            actions.append(
                {
                    "action": "setup_payment_method",
                    "title": "Set Up Payment Method",
                    "description": "Add a payment method to receive payouts",
                    "priority": "high",
                    "cta": "Add Payment Method",
                }
            )

        # Manual payout request
        pending_amount = contribution_summary.get("pending_amount", 0)
        if pending_amount >= 50.0:
            actions.append(
                {
                    "action": "request_payout",
                    "title": "Request Payout",
                    "description": f"Request payout for ${pending_amount:.2f} pending earnings",
                    "priority": "medium",
                    "cta": "Request Payout",
                }
            )

        # View transparency report
        actions.append(
            {
                "action": "view_transparency_report",
                "title": "View Transparency Report",
                "description": "See complete breakdown of earnings and fees",
                "priority": "low",
                "cta": "View Report",
            }
        )

        return actions

    def _calculate_work_value(self, work_entry) -> float:
        """Calculate the monetary value of a work entry."""
        # Simplified calculation
        hours = work_entry.time_invested_minutes / 60
        # Assume $50/hour base rate adjusted by quality
        base_rate = 50.0
        quality_multiplier = (
            work_entry.quality_rating / 7.0
        )  # Normalize to 7-point scale
        return hours * base_rate * quality_multiplier

    def _calculate_impact_metrics(self, work_history: list) -> dict[str, Any]:
        """Calculate impact metrics from work history."""
        if not work_history:
            return {"total_impact": 0, "average_quality": 0, "consistency_score": 0}

        total_impact = sum(self._calculate_work_value(entry) for entry in work_history)
        average_quality = sum(entry.quality_rating for entry in work_history) / len(
            work_history
        )

        # Consistency score based on quality variance
        qualities = [entry.quality_rating for entry in work_history]
        mean_quality = sum(qualities) / len(qualities)
        variance = sum((q - mean_quality) ** 2 for q in qualities) / len(qualities)
        consistency_score = max(0, 10 - variance)  # Lower variance = higher consistency

        return {
            "total_impact": round(total_impact, 2),
            "average_quality": round(average_quality, 1),
            "consistency_score": round(consistency_score, 1),
            "total_entries": len(work_history),
        }


# Portal access functions
def get_user_portal_dashboard(user_id: str) -> dict[str, Any]:
    """Get user's portal dashboard."""
    portal = UserPortal()
    return portal.get_user_dashboard(user_id)


def setup_user_payment_portal(
    user_id: str, method_type: str, method_details: dict[str, Any]
) -> dict[str, Any]:
    """Setup payment method through portal."""
    portal = UserPortal()
    return portal.setup_payment_method(user_id, method_type, method_details)


def request_payout_portal(user_id: str, reason: str = "") -> dict[str, Any]:
    """Request payout through portal."""
    portal = UserPortal()
    return portal.request_manual_payout(user_id, reason)


def get_transparency_report_portal(user_id: str) -> dict[str, Any]:
    """Get transparency report through portal."""
    portal = UserPortal()
    return portal.generate_transparency_report(user_id)


if __name__ == "__main__":
    # Demo the user portal
    portal = UserPortal()

    print("User Portal Demo")
    print("=" * 30)

    # Demo dashboard for a user
    dashboard = portal.get_user_dashboard("demo_user")
    print("Dashboard Overview:")
    print(f"  Total Hours: {dashboard['contribution_overview']['total_hours_worked']}")
    print(f"  Total Earned: ${dashboard['financial_summary']['total_earned_all_time']}")
    print(f"  Pending Payout: ${dashboard['contribution_overview']['pending_payout']}")
    print(f"  Payment Methods: {dashboard['payment_methods']['total_methods']}")

    print("\\n✅ User Portal operational - complete user control and transparency!")
