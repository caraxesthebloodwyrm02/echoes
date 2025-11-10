#!/usr/bin/env python3
"""
Echoes Business Analysis CLI

A command-line interface for exploring business opportunities and revenue streams.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.tools.business_analysis import (
    BusinessAnalyzer,
    MarketOpportunity,
    RevenueStream,
)


class BusinessCLI:
    """Command-line interface for business analysis tools."""

    def __init__(self):
        self.analyzer = BusinessAnalyzer()
        self.setup_parser()

    def setup_parser(self):
        """Set up the argument parser."""
        self.parser = argparse.ArgumentParser(
            description="Echoes Business Analysis Tools",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Find market opportunities for AI skills
  python business_cli.py opportunities --skills Python,AI/ML,Data Science --investment 1000-5000
  
  # Identify revenue streams with 20 hours/week availability
  python business_cli.py revenue --skills Python,AI/ML --hours 20 --risk medium
  
  # Get quick wins that can be done in 2 weeks
  python business_cli.py quick-wins --skills Python,Web Development --hours 10 --weeks 2
  
  # Project revenue for multiple streams
  python business_cli.py project --streams '{"name":"Consulting","base_revenue":5000,"growth_rate":0.1}'
            """,
        )

        # Create subparsers for different commands
        subparsers = self.parser.add_subparsers(
            dest="command", help="Command to execute"
        )

        # Opportunities command
        opp_parser = subparsers.add_parser(
            "opportunities", help="Find market opportunities"
        )
        opp_parser.add_argument(
            "--industry", type=str, default="AI/ML", help="Target industry"
        )
        opp_parser.add_argument(
            "--skills", type=str, required=True, help="Comma-separated list of skills"
        )
        opp_parser.add_argument(
            "--investment",
            type=str,
            default="1000-5000",
            help="Investment range (e.g., 1000-5000)",
        )
        opp_parser.add_argument(
            "--months", type=int, default=6, help="Time horizon in months (default: 6)"
        )

        # Revenue streams command
        rev_parser = subparsers.add_parser("revenue", help="Identify revenue streams")
        rev_parser.add_argument(
            "--skills", type=str, required=True, help="Comma-separated list of skills"
        )
        rev_parser.add_argument(
            "--hours", type=int, default=20, help="Weekly hours available (default: 20)"
        )
        rev_parser.add_argument(
            "--risk",
            type=str,
            choices=["low", "medium", "high"],
            default="medium",
            help="Risk tolerance (default: medium)",
        )

        # Projection command
        proj_parser = subparsers.add_parser("project", help="Project revenue")
        proj_parser.add_argument(
            "--streams",
            type=str,
            required=True,
            help="JSON array of stream configurations",
        )
        proj_parser.add_argument(
            "--months",
            type=int,
            default=12,
            help="Number of months to project (default: 12)",
        )
        proj_parser.add_argument(
            "--growth",
            type=float,
            default=0.05,
            help="Monthly growth rate (default: 0.05)",
        )

        # Quick wins command
        quick_parser = subparsers.add_parser("quick-wins", help="Find quick wins")
        quick_parser.add_argument(
            "--skills", type=str, required=True, help="Comma-separated list of skills"
        )
        quick_parser.add_argument(
            "--hours", type=int, default=10, help="Weekly hours available (default: 10)"
        )
        quick_parser.add_argument(
            "--weeks",
            type=int,
            default=2,
            help="Maximum preparation time in weeks (default: 2)",
        )

        # Metrics command
        metrics_parser = subparsers.add_parser(
            "metrics", help="Calculate business metrics"
        )
        metrics_parser.add_argument(
            "--revenue",
            type=float,
            required=True,
            help="Monthly recurring revenue (MRR)",
        )
        metrics_parser.add_argument(
            "--expenses", type=float, required=True, help="Monthly operating expenses"
        )
        metrics_parser.add_argument(
            "--churn",
            type=float,
            default=0.05,
            help="Monthly churn rate (default: 0.05)",
        )
        metrics_parser.add_argument(
            "--cac",
            type=float,
            default=100.0,
            help="Customer acquisition cost (default: 100.0)",
        )
        metrics_parser.add_argument(
            "--acv",
            type=float,
            default=500.0,
            help="Average customer value (default: 500.0)",
        )

    def parse_investment_range(self, investment_str: str) -> Tuple[float, float]:
        """Parse investment range string into min and max values."""
        try:
            min_val, max_val = map(float, investment_str.split("-"))
            return min_val, max_val
        except (ValueError, AttributeError):
            print("Invalid investment range format. Using default: 1000-5000")
            return 1000.0, 5000.0

    def parse_skills(self, skills_str: str) -> List[str]:
        """Parse comma-separated skills string into a list."""
        return [s.strip() for s in skills_str.split(",") if s.strip()]

    def print_markdown(self, title: str, content: Any, level: int = 1):
        """Print content with markdown-style formatting."""
        print(f"\n{'#' * level} {title}\n")
        if isinstance(content, (dict, list)):
            print(json.dumps(content, indent=2, default=str))
        else:
            print(content)

    def run(self):
        """Run the CLI application."""
        args = self.parser.parse_args()

        if not args.command:
            self.parser.print_help()
            return

        try:
            if args.command == "opportunities":
                self.handle_opportunities(args)
            elif args.command == "revenue":
                self.handle_revenue(args)
            elif args.command == "project":
                self.handle_projections(args)
            elif args.command == "quick-wins":
                self.handle_quick_wins(args)
            elif args.command == "metrics":
                self.handle_metrics(args)
        except Exception as e:
            print(f"\n❌ Error: {str(e)}", file=sys.stderr)
            if hasattr(args, "debug") and args.debug:
                import traceback

                traceback.print_exc()

    def handle_opportunities(self, args):
        """Handle the opportunities command."""
        skills = self.parse_skills(args.skills)
        min_inv, max_inv = self.parse_investment_range(args.investment)

        self.print_markdown(
            "🔍 Market Opportunity Analysis",
            {
                "Industry": args.industry,
                "Skills": skills,
                "Investment Range": f"${min_inv:,.2f} - ${max_inv:,.2f}",
                "Time Horizon": f"{args.months} months",
            },
            level=2,
        )

        result = self.analyzer.analyze_market_opportunity(
            industry=args.industry,
            skills=skills,
            investment_range=(min_inv, max_inv),
            time_horizon=args.months,
        )

        self.print_markdown(
            "📊 Opportunities",
            result["opportunities"] or "No matching opportunities found.",
        )

        if result["recommendations"]:
            self.print_markdown("💡 Recommendations", result["recommendations"])

    def handle_revenue(self, args):
        """Handle the revenue command."""
        skills = self.parse_skills(args.skills)

        self.print_markdown(
            "💰 Revenue Stream Analysis",
            {
                "Skills": skills,
                "Weekly Hours": args.hours,
                "Risk Tolerance": args.risk.capitalize(),
            },
            level=2,
        )

        result = self.analyzer.identify_revenue_streams(
            skills=skills, available_hours=args.hours, risk_tolerance=args.risk
        )

        self.print_markdown(
            "📈 Potential Revenue Streams",
            result["revenue_streams"] or "No matching revenue streams found.",
        )

    def handle_projections(self, args):
        """Handle the project command."""
        try:
            streams = json.loads(args.streams)
            if not isinstance(streams, list):
                streams = [streams]
        except json.JSONDecodeError:
            print("Error: Invalid JSON format for streams")
            return

        self.print_markdown(
            "📊 Revenue Projections",
            {
                "Time Frame": f"{args.months} months",
                "Monthly Growth Rate": f"{args.growth * 100:.1f}%",
                "Income Streams": [s.get("name", "Unnamed") for s in streams],
            },
            level=2,
        )

        result = self.analyzer.project_revenue(
            streams=streams, months=args.months, growth_rate=args.growth
        )

        self.print_markdown("📅 Monthly Projections", result["monthly_projections"])
        self.print_markdown(
            "💰 Summary",
            {
                "Total Projected Revenue": f"${result['total_projected_revenue']:,.2f}",
                "Average Monthly Revenue": f"${result['average_monthly_revenue']:,.2f}",
                "Growth Rate": f"{result['growth_rate_percent']:.1f}%",
            },
        )

    def handle_quick_wins(self, args):
        """Handle the quick-wins command."""
        skills = self.parse_skills(args.skills)

        self.print_markdown(
            "⚡ Quick Wins Analysis",
            {
                "Skills": skills,
                "Weekly Hours": args.hours,
                "Max Preparation Time": f"{args.weeks} weeks",
            },
            level=2,
        )

        wins = self.analyzer.identify_quick_wins(
            available_skills=skills,
            available_hours=args.hours,
            max_prep_time=args.weeks,
        )

        if not wins:
            print(
                "\nNo quick wins found with the current criteria. Try adjusting your skills or time constraints."
            )
            return

        for i, win in enumerate(wins, 1):
            self.print_markdown(
                f"🏆 {i}. {win['name']}",
                {
                    "Description": win["description"],
                    "Time to Launch": f"{win['time_to_launch_weeks']} weeks",
                    "Potential Earnings": f"${win['potential_earnings']['min']:,.0f}-${win['potential_earnings']['max']:,.0f}/hour",
                    "Required Skills": ", ".join(win["required_skills"]),
                    "Steps": win.get("steps", []),
                    "Resources": win.get("resources", []),
                },
                level=3,
            )

    def handle_metrics(self, args):
        """Handle the metrics command."""
        self.print_markdown(
            "📊 Business Metrics",
            {
                "Monthly Revenue (MRR)": f"${args.revenue:,.2f}",
                "Monthly Expenses": f"${args.expenses:,.2f}",
                "Monthly Churn Rate": f"{args.churn * 100:.1f}%",
                "Customer Acquisition Cost (CAC)": f"${args.cac:,.2f}",
                "Average Customer Value (ACV)": f"${args.acv:,.2f}",
            },
            level=2,
        )

        metrics = self.analyzer.calculate_business_metrics(
            revenue=args.revenue,
            expenses=args.expenses,
            churn_rate=args.churn,
            customer_acquisition_cost=args.cac,
            average_customer_value=args.acv,
        )

        # Format the metrics for better readability
        formatted_metrics = {
            "💵 Financials": {
                "Gross Profit": f"${metrics['gross_profit']:,.2f}",
                "Profit Margin": f"{metrics['profit_margin_percent']:.1f}%",
            },
            "👥 Customer Metrics": {
                "Customer Lifetime (months)": f"{metrics['customer_lifetime_months']:.1f}",
                "Customer Lifetime Value (LTV)": f"${metrics['customer_lifetime_value']:,.2f}",
                "LTV to CAC Ratio": f"{metrics['ltv_to_cac_ratio']:.2f}",
                "Months to Recover CAC": f"{metrics['months_to_recover_cac']:.1f}",
            },
            "📈 Health Indicators": {
                "Healthy LTV:CAC Ratio (≥3:1)": (
                    "✅ Yes"
                    if metrics["key_metrics"]["healthy_ltv_cac_ratio"]
                    else "❌ No"
                ),
                "Reasonable CAC Payback (≤12 months)": (
                    "✅ Yes"
                    if metrics["key_metrics"]["healthy_months_to_recover_cac"]
                    else "❌ No"
                ),
                "Sustainable Churn Rate (≤10%)": (
                    "✅ Yes"
                    if metrics["key_metrics"]["sustainable_churn_rate"]
                    else "❌ No"
                ),
                "Profitable": (
                    "✅ Yes" if metrics["key_metrics"]["profitable"] else "❌ No"
                ),
            },
        }

        self.print_markdown("📋 Metrics Summary", formatted_metrics)


if __name__ == "__main__":
    try:
        cli = BusinessCLI()
        cli.run()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
        sys.exit(0)
