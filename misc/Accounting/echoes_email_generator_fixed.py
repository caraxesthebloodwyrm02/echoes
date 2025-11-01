#!/usr/bin/env python3
# echoes_email_generator_fixed.py - Email ROI Analysis Generator (Production Ready)

import json
import sys
import csv
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
import datetime
import math

@dataclass
class EmailConfig:
    email_subject: str = "Echoes AI ROI Analysis - Immediate 5-Day Payback Opportunity"
    email_to: List[str] = None
    email_from: str = "Sarah Chen, Echoes AI <sarah.chen@echoes.ai>"
    email_date: str = ""
    meeting_request: str = "30-minute decision meeting - This week preferred"
    institution_name: str = "Pilot A Bank"
    pilot_completed: bool = True
    pilot_duration: str = "8 weeks"
    team_size: int = 5
    monthly_savings: float = 71822
    monthly_investment: float = 12000
    net_monthly_benefit: float = 59822
    roi_percentage: float = 499
    payback_days: float = 5
    labor_efficiency_savings: float = 14722
    error_reduction_savings: float = 56250
    audit_preparation_savings: float = 850
    decision_deadline: str = "November 1, 2025"
    contract_duration: str = "12-month minimum"
    rollout_timeline: str = "4-6 weeks"

def __post_init__(self):
    if self.email_to is None:
        self.email_to = ["CFO@bank.com", "CTO@bank.com", "Chief.Compliance@bank.com"]

def load_email_config(yaml_path: str) -> EmailConfig:
    """Load configuration from email YAML file"""
    config = EmailConfig()
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Simple YAML parsing for email config
        data = {}
        for line in content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                try:
                    if '.' in val:
                        data[key] = float(val)
                    elif val.isdigit():
                        data[key] = int(val)
                    elif val.lower() in ('true', 'false'):
                        data[key] = val.lower() == 'true'
                    else:
                        data[key] = val
                except:
                    data[key] = val
        
        # Apply loaded values
        config.email_subject = data.get('email_subject', config.email_subject)
        
        # Handle email_to as list or string
        email_to_data = data.get('email_to', config.email_to)
        if isinstance(email_to_data, list):
            config.email_to = email_to_data
        elif isinstance(email_to_data, str):
            # Parse comma-separated email list
            config.email_to = [email.strip() for email in email_to_data.split(',')]
        
        config.email_from = data.get('email_from', config.email_from)
        config.email_date = data.get('email_date', config.email_date)
        config.meeting_request = data.get('meeting_request', config.meeting_request)
        config.institution_name = data.get('institution_name', config.institution_name)
        config.pilot_completed = data.get('pilot_completed', config.pilot_completed)
        config.pilot_duration = data.get('pilot_duration', config.pilot_duration)
        config.team_size = data.get('team_size', config.team_size)
        config.monthly_savings = data.get('monthly_savings', config.monthly_savings)
        config.monthly_investment = data.get('monthly_investment', config.monthly_investment)
        config.net_monthly_benefit = data.get('net_monthly_benefit', config.net_monthly_benefit)
        config.roi_percentage = data.get('roi_percentage', config.roi_percentage)
        config.payback_days = data.get('payback_days', config.payback_days)
        config.labor_efficiency_savings = data.get('labor_efficiency_savings', config.labor_efficiency_savings)
        config.error_reduction_savings = data.get('error_reduction_savings', config.error_reduction_savings)
        config.audit_preparation_savings = data.get('audit_preparation_savings', config.audit_preparation_savings)
        config.decision_deadline = data.get('decision_deadline', config.decision_deadline)
        config.contract_duration = data.get('contract_duration', config.contract_duration)
        config.rollout_timeline = data.get('rollout_timeline', config.rollout_timeline)
        
    except Exception as e:
        print(f"Warning: Could not parse YAML file: {e}")
        print("Using default configuration")
    
    return config

def format_currency(amount: float, currency: str = "USD") -> str:
    return f"${amount:,.0f}"

def format_email_recipients(email_list: List[str]) -> str:
    """Format email recipients for display"""
    if len(email_list) == 1:
        return email_list[0]
    elif len(email_list) == 2:
        return f"{email_list[0]} and {email_list[1]}"
    else:
        return ", ".join(email_list[:-1]) + f", and {email_list[-1]}"

def generate_executive_email(config: EmailConfig) -> str:
    annual_net_benefit = config.net_monthly_benefit * 12
    three_year_value = annual_net_benefit * 3
    total_monthly_savings = config.labor_efficiency_savings + config.error_reduction_savings + config.audit_preparation_savings
    
    # Format recipients for email
    recipients_display = format_email_recipients(config.email_to)
    
    email_content = f"""
SUBJECT: {config.email_subject}

To: {recipients_display}
From: {config.email_from}
Date: {config.email_date or datetime.date.today().strftime("%B %d, %Y")}
Meeting Request: {config.meeting_request}

Dear {recipients_display},

Our {config.pilot_duration} pilot with your {config.team_size}-person compliance team has delivered exceptional results. Echoes AI automation pays for itself in just {config.payback_days:.0f} days and generates {format_currency(config.net_monthly_benefit)} net monthly benefit - a {config.roi_percentage:.0f}% ROI.

KEY RESULTS:
• Immediate ROI: {config.payback_days:.0f}-day payback period
• Labor Efficiency: {format_currency(config.labor_efficiency_savings)}/month savings  
• Error Reduction: 75% fewer compliance violations
• Audit Readiness: 30+ hours saved per audit
• Risk Mitigation: Automated compliance monitoring

FINANCIAL IMPACT SUMMARY:
┌─────────────────────────────────────────┐
│ Monthly Investment:      {format_currency(config.monthly_investment):>10}│
│ Monthly Savings:         {format_currency(total_monthly_savings):>10}│
│ Net Monthly Benefit:     {format_currency(config.net_monthly_benefit):>10}│
│ Annual Net Benefit:      {format_currency(annual_net_benefit):>10}│
│ 3-Year Value:            {format_currency(three_year_value):>10}│
│ Return on Investment:    {config.roi_percentage:>9.0f}%│
│ Payback Period:          {config.payback_days:>9.0f} days│
└─────────────────────────────────────────┘

SAVINGS BREAKDOWN:
• Labor Efficiency:       {format_currency(config.labor_efficiency_savings)}/month
• Error Reduction:        {format_currency(config.error_reduction_savings)}/month  
• Audit Preparation:      {format_currency(config.audit_preparation_savings)}/month

WHAT THIS MEANS FOR {config.institution_name.upper()}:
✓ Investment pays for itself in {config.payback_days:.0f} days
✓ {format_currency(config.net_monthly_benefit)} monthly net benefit after investment
✓ {format_currency(annual_net_benefit)} annual net benefit vs {format_currency(config.monthly_investment * 12)} investment
✓ Proven results from {config.pilot_duration} pilot with your team

RECOMMENDATION:
Proceed with {format_currency(config.monthly_investment)}/month Echoes AI investment for immediate {config.payback_days:.0f}-day payback.

NEXT STEPS:
1. Approve investment (instant ROI with {config.payback_days:.0f}-day payback)
2. Schedule {config.meeting_request}
3. Begin {config.rollout_timeline} enterprise rollout planning
4. Execute {config.contract_duration} contract

DECISION TIMELINE:
• Decision Deadline: {config.decision_deadline}
• Contract Duration: {config.contract_duration}
• Rollout Timeline: {config.rollout_timeline}

Would you be available for a brief meeting this week to discuss next steps? I'm confident this represents an exceptional opportunity to capture immediate ROI while strengthening your compliance operations.

Best regards,

Sarah Chen
Echoes AI - Compliance Automation
📧 sarah.chen@echoes.ai
📱 [Phone Number]

P.S. Pilot results and technical documentation available upon request.
    """
    
    return email_content.strip()

def export_email_files(config: EmailConfig, base_filename: str = "stakeholder_email") -> None:
    email_content = generate_executive_email(config)
    
    # Save as text file
    with open(f"{base_filename}.txt", "w", encoding="utf-8") as f:
        f.write(email_content)
    print(f"✅ Email exported: {base_filename}.txt")
    
    # Save JSON with UTC timestamp fix
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    email_data = {
        "subject": config.email_subject,
        "to": config.email_to,
        "from": config.email_from,
        "body": email_content,
        "timestamp": timestamp,
        "metrics": {
            "monthly_savings": config.monthly_savings,
            "monthly_investment": config.monthly_investment,
            "net_monthly_benefit": config.net_monthly_benefit,
            "roi_percentage": config.roi_percentage,
            "payback_days": config.payback_days
        }
    }
    
    with open(f"{base_filename}_data.json", "w", encoding="utf-8") as f:
        json.dump(email_data, f, indent=2, ensure_ascii=False)
    print(f"✅ Email data exported: {base_filename}_data.json")

def interactive_setup() -> EmailConfig:
    """Interactive setup for email configuration"""
    print("📧 INTERACTIVE EMAIL ROI SETUP")
    print("=" * 50)
    
    config = EmailConfig()
    
    # Email details
    config.institution_name = input("Institution Name [Pilot A Bank]: ").strip() or "Pilot A Bank"
    
    # Email recipients
    recipient_input = input("Email recipients (comma-separated) [CFO@bank.com, CTO@bank.com, Chief.Compliance@bank.com]: ").strip()
    if recipient_input:
        config.email_to = [email.strip() for email in recipient_input.split(',')]
    
    config.email_from = input("Email From [Sarah Chen, Echoes AI <sarah.chen@echoes.ai>]: ").strip() or "Sarah Chen, Echoes AI <sarah.chen@echoes.ai>"
    
    # ROI metrics
    config.team_size = int(input("Team Size (FTEs) [5]: ") or "5")
    config.monthly_savings = float(input("Monthly Savings ($) [71822]: ") or "71822")
    config.monthly_investment = float(input("Monthly Investment ($) [12000]: ") or "12000")
    config.net_monthly_benefit = config.monthly_savings - config.monthly_investment
    config.payback_days = config.monthly_investment / (config.monthly_savings / 30)
    config.roi_percentage = (config.net_monthly_benefit / config.monthly_investment) * 100
    
    # Financial breakdown
    config.labor_efficiency_savings = float(input("Labor Efficiency Savings ($) [14722]: ") or "14722")
    config.error_reduction_savings = float(input("Error Reduction Savings ($) [56250]: ") or "56250")
    config.audit_preparation_savings = float(input("Audit Preparation Savings ($) [850]: ") or "850")
    
    return config

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Echoes AI - Email ROI Stakeholder Generator (Production)")
    parser.add_argument("--config", help="YAML configuration file")
    parser.add_argument("--output", default="stakeholder_email", help="Output filename base")
    parser.add_argument("--interactive", action="store_true", help="Interactive setup mode")
    
    args = parser.parse_args()
    
    if args.config and args.interactive:
        print("Error: Cannot use both --config and --interactive")
        return 1
    
    # Load configuration
    if args.config:
        config = load_email_config(args.config)
        print(f"✅ Loaded configuration from: {args.config}")
    elif args.interactive:
        config = interactive_setup()
    else:
        print("Please specify --config <yaml_file> or --interactive")
        return 1
    
    print("\n📧 GENERATING STAKEHOLDER EMAIL...")
    email_content = generate_executive_email(config)
    
    # Display email
    print("\n" + "="*60)
    print("📧 EMAIL PREVIEW")
    print("="*60)
    print(email_content)
    print("="*60)
    
    # Export files
    export_email_files(config, args.output)
    
    print(f"\n🎯 Ready to send stakeholder email!")
    print(f"Files created: {args.output}.txt, {args.output}_data.json")

if __name__ == "__main__":
    main()
