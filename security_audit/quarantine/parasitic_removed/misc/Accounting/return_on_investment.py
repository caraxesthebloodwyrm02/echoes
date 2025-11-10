#!/usr/bin/env python3
# echoes_roi_stakeholder.py - Executive ROI Presentation Tool
# Purpose: Generate clean, professional ROI reports for stakeholder meetings

import csv
import datetime
import json
import math
from dataclasses import dataclass


@dataclass
class StakeholderConfig:
    # Financials
    avg_hourly_rate: float = 85.0
    weekly_hours_saved: float = 40.0
    error_reduction_pct: float = 75.0
    avg_cost_per_error_per_fte: float = 15000.0
    audit_prep_hours_saved: float = 30.0
    audits_per_year: float = 4.0
    compliance_team_size: int = 5
    echoes_investment: float = 12000.0
    institution_name: str = "[Bank Name]"
    presenter_name: str = "[Your Name]"
    presentation_date: str = ""


def format_currency(value: float, currency: str = "USD") -> str:
    symbol = "$" if currency.upper() == "USD" else f"{currency.upper()}"
    if currency.upper() != "USD":
        return f"{symbol}{value:,.2f}"
    return f"${value:,.2f}"


def generate_executive_summary(config: StakeholderConfig) -> dict:
    """Generate executive summary with key metrics"""

    # Core calculations
    hours_per_month = 4.33
    monthly_labor = (
        config.weekly_hours_saved * hours_per_month
    ) * config.avg_hourly_rate
    error_reduction_savings = (
        config.compliance_team_size * config.avg_cost_per_error_per_fte
    ) * (config.error_reduction_pct / 100)
    audit_savings = (
        config.audit_prep_hours_saved * config.avg_hourly_rate * config.audits_per_year
    ) / 12

    total_monthly_savings = monthly_labor + error_reduction_savings + audit_savings
    net_monthly_benefit = total_monthly_savings - config.echoes_investment
    roi_pct = (
        (net_monthly_benefit / config.echoes_investment) * 100
        if config.echoes_investment > 0
        else 0
    )
    payback_days = (
        config.echoes_investment / (total_monthly_savings / 30)
        if total_monthly_savings > 0
        else float("inf")
    )

    # Annual projections
    annual_savings = total_monthly_savings * 12
    annual_net_benefit = net_monthly_benefit * 12
    three_year_value = annual_net_benefit * 3

    summary = {
        "executive_overview": {
            "institution": config.institution_name,
            "team_size": config.compliance_team_size,
            "presenter": config.presenter_name,
            "date": config.presentation_date
            or datetime.date.today().strftime("%B %d, %Y"),
        },
        "key_metrics": {
            "total_monthly_savings": total_monthly_savings,
            "monthly_investment": config.echoes_investment,
            "net_monthly_benefit": net_monthly_benefit,
            "roi_percentage": roi_pct,
            "payback_days": payback_days,
            "annual_net_benefit": annual_net_benefit,
            "three_year_value": three_year_value,
        },
        "savings_breakdown": {
            "labor_efficiency": monthly_labor,
            "error_reduction": error_reduction_savings,
            "audit_preparation": audit_savings,
        },
        "implementation": {
            "weeks_to_breakeven": min(52, math.ceil(payback_days / 7))
            if math.isfinite(payback_days)
            else "N/A",
            "recommended_action": "PROCEED - Strong ROI with quick payback"
            if roi_pct > 200 and payback_days < 30
            else "REVIEW - Consider optimization",
        },
    }

    return summary


def print_executive_presentation(summary: dict) -> None:
    """Print professional stakeholder presentation"""

    overview = summary["executive_overview"]
    metrics = summary["key_metrics"]
    savings = summary["savings_breakdown"]
    implementation = summary["implementation"]

    # Header
    print("=" * 80)
    print("🏛️  ECHOES AI - COMPLIANCE AUTOMATION")
    print("📊 EXECUTIVE ROI ANALYSIS")
    print("=" * 80)
    print(f"Institution: {overview['institution']}")
    print(f"Presented by: {overview['presenter']}")
    print(f"Date: {overview['date']}")
    print(f"Compliance Team Size: {overview['team_size']} FTEs")
    print()

    # Key Metrics Dashboard
    print("📈 KEY PERFORMANCE INDICATORS")
    print("-" * 50)
    print(
        f"💰 Total Monthly Savings:    {format_currency(metrics['total_monthly_savings']):>15}"
    )
    print(
        f"💵 Monthly Investment:       {format_currency(metrics['monthly_investment']):>15}"
    )
    print(
        f"✅ Net Monthly Benefit:      {format_currency(metrics['net_monthly_benefit']):>15}"
    )
    print(f"🎯 Return on Investment:     {metrics['roi_percentage']:>14.0f}%")
    print(f"⚡ Payback Period:           {metrics['payback_days']:>14.0f} days")
    print()

    # Savings Breakdown
    print("💡 SAVINGS BREAKDOWN")
    print("-" * 50)
    print(
        f"• Labor Efficiency:          {format_currency(savings['labor_efficiency']):>15}"
    )
    print(
        f"• Error Reduction:           {format_currency(savings['error_reduction']):>15}"
    )
    print(
        f"• Audit Preparation:         {format_currency(savings['audit_preparation']):>15}"
    )
    print()

    # Annual Impact
    print("📅 ANNUAL PROJECTIONS")
    print("-" * 50)
    print(
        f"• Annual Net Benefit:        {format_currency(metrics['annual_net_benefit']):>15}"
    )
    print(
        f"• 3-Year Total Value:        {format_currency(metrics['three_year_value']):>15}"
    )
    print()

    # Recommendation
    print("🎯 STRATEGIC RECOMMENDATION")
    print("-" * 50)
    print(f"Action: {implementation['recommended_action']}")
    print(f"Breakeven: {implementation['weeks_to_breakeven']} weeks")
    print()

    # Talking Points
    print("💬 KEY TALKING POINTS")
    print("-" * 50)
    print(
        "• Immediate ROI: Pays for itself in just {:.0f} days".format(
            metrics["payback_days"]
        )
    )
    print("• Risk Mitigation: 75% reduction in compliance errors")
    print("• Operational Efficiency: 40+ hours saved weekly")
    print("• Audit Readiness: Automated compliance tracking")
    print("• Scalability: Proven in pilot, ready for enterprise deployment")
    print()

    print("=" * 80)
    print("📋 NEXT STEPS:")
    print("  1. Approve $12K/month Echoes AI investment")
    print("  2. Begin enterprise rollout planning")
    print("  3. Establish success metrics and reporting")
    print("=" * 80)


def export_stakeholder_json(summary: dict, filename: str) -> None:
    """Export detailed analysis as JSON for further processing"""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"✅ Detailed analysis exported: {filename}")


def export_executive_csv(summary: dict, filename: str) -> None:
    """Export key metrics as CSV for executive summary tables"""
    metrics = summary["key_metrics"]
    savings = summary["savings_breakdown"]

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value", "Currency"])
        writer.writerow(
            ["Total Monthly Savings", f"{metrics['total_monthly_savings']:.2f}", "USD"]
        )
        writer.writerow(
            ["Monthly Investment", f"{metrics['monthly_investment']:.2f}", "USD"]
        )
        writer.writerow(
            ["Net Monthly Benefit", f"{metrics['net_monthly_benefit']:.2f}", "USD"]
        )
        writer.writerow(["ROI Percentage", f"{metrics['roi_percentage']:.2f}", "%"])
        writer.writerow(["Payback Days", f"{metrics['payback_days']:.2f}", "Days"])
        writer.writerow(
            ["Annual Net Benefit", f"{metrics['annual_net_benefit']:.2f}", "USD"]
        )
        writer.writerow(
            ["Labor Efficiency Savings", f"{savings['labor_efficiency']:.2f}", "USD"]
        )
        writer.writerow(
            ["Error Reduction Savings", f"{savings['error_reduction']:.2f}", "USD"]
        )
        writer.writerow(
            ["Audit Preparation Savings", f"{savings['audit_preparation']:.2f}", "USD"]
        )

    print(f"✅ Executive summary CSV exported: {filename}")


def export_powerpoint_summary(summary: dict, filename: str) -> None:
    """Export PowerPoint-friendly text summary"""
    overview = summary["executive_overview"]
    metrics = summary["key_metrics"]
    savings = summary["savings_breakdown"]

    with open(filename, "w", encoding="utf-8") as f:
        f.write(
            f"""
ECHOES AI - COMPLIANCE AUTOMATION ROI ANALYSIS
{overview['institution']}
Presented by: {overview['presenter']} | {overview['date']}

SLIDE 1: EXECUTIVE SUMMARY
• ROI: {metrics['roi_percentage']:.0f}%
• Payback: {metrics['payback_days']:.0f} days  
• Net Monthly Benefit: ${metrics['net_monthly_benefit']:,.0f}

SLIDE 2: SAVINGS BREAKDOWN
• Labor Efficiency: ${savings['labor_efficiency']:,.0f}/month
• Error Reduction: ${savings['error_reduction']:,.0f}/month  
• Audit Preparation: ${savings['audit_preparation']:,.0f}/month
• Total: ${metrics['total_monthly_savings']:,.0f}/month

SLIDE 3: BUSINESS CASE
• Annual Net Benefit: ${metrics['annual_net_benefit']:,.0f}
• 3-Year Value: ${metrics['three_year_value']:,.0f}
• Risk Reduction: 75% fewer compliance errors

SLIDE 4: RECOMMENDATION
• PROCEED with $12K/month investment
• Begin enterprise deployment
• Establish success metrics

NEXT STEPS:
1. Approve investment
2. Begin rollout planning  
3. Set up reporting dashboard
        """
        )

    print(f"✅ PowerPoint summary exported: {filename}")


def interactive_setup() -> StakeholderConfig:
    """Interactive setup for stakeholder presentation"""
    print("🎯 STAKEHOLDER ROI PRESENTATION SETUP")
    print("=" * 50)

    config = StakeholderConfig()

    # Basic info
    config.institution_name = (
        input("Institution Name [Pilot A Bank]: ").strip() or "Pilot A Bank"
    )
    config.presenter_name = (
        input("Your Name [Echoes AI Team]: ").strip() or "Echoes AI Team"
    )
    config.presentation_date = input("Presentation Date [Today]: ").strip() or ""

    # Financial parameters
    print("\n💰 FINANCIAL PARAMETERS")
    config.compliance_team_size = int(input("Compliance Team Size [5]: ") or "5")
    config.avg_hourly_rate = float(input("Average Hourly Rate ($) [85]: ") or "85")
    config.weekly_hours_saved = float(input("Weekly Hours Saved [40]: ") or "40")
    config.error_reduction_pct = float(input("Error Reduction % [75]: ") or "75")
    config.avg_cost_per_error_per_fte = float(
        input("Cost per Error per FTE ($) [15000]: ") or "15000"
    )
    config.audit_prep_hours_saved = float(
        input("Audit Prep Hours Saved per Audit [30]: ") or "30"
    )
    config.audits_per_year = float(input("Audits per Year [4]: ") or "4")
    config.echoes_investment = float(
        input("Echoes Investment ($/month) [12000]: ") or "12000"
    )

    return config


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Echoes AI - Stakeholder ROI Presentation Tool"
    )
    parser.add_argument(
        "--interactive", action="store_true", help="Interactive setup mode"
    )
    parser.add_argument("--export-json", help="Export detailed analysis as JSON")
    parser.add_argument("--export-csv", help="Export executive summary as CSV")
    parser.add_argument("--export-ppt", help="Export PowerPoint summary as text")
    parser.add_argument("--team-size", type=int, help="Compliance team size")
    parser.add_argument("--hourly", type=float, help="Average hourly rate")
    parser.add_argument("--hours-saved", type=float, help="Weekly hours saved")
    parser.add_argument("--errors-pct", type=float, help="Error reduction percentage")
    parser.add_argument("--investment", type=float, help="Monthly investment")

    args = parser.parse_args()

    # Setup configuration
    if args.interactive:
        config = interactive_setup()
    else:
        config = StakeholderConfig()
        if args.team_size:
            config.compliance_team_size = args.team_size
        if args.hourly:
            config.avg_hourly_rate = args.hourly
        if args.hours_saved:
            config.weekly_hours_saved = args.hours_saved
        if args.errors_pct:
            config.error_reduction_pct = args.errors_pct
        if args.investment:
            config.echoes_investment = args.investment

    # Generate and display executive summary
    summary = generate_executive_summary(config)
    print_executive_presentation(summary)

    # Export options
    if args.export_json:
        export_stakeholder_json(summary, args.export_json)
    if args.export_csv:
        export_executive_csv(summary, args.export_csv)
    if args.export_ppt:
        export_powerpoint_summary(summary, args.export_ppt)

    print("\n🎯 Ready for stakeholder presentation!")
    print("Use --export-ppt to create PowerPoint summary")


if __name__ == "__main__":
    main()
