#!/usr/bin/env python3
# echoes_email_generator.py - Email ROI Analysis Generator
import json
import sys
import csv
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import datetime
import math

@dataclass
class EmailConfig:
    email_subject: str = "Echoes AI ROI Analysis - Immediate 5-Day Payback Opportunity"
    email_to: str = "CFO, CTO, Chief Compliance Officer"
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
        config.email_to = data.get('email_to', config.email_to)
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

def generate_executive_email(config: EmailConfig) -> str:
    annual_net_benefit = config.net_monthly_benefit * 12
    three_year_value = annual_net_benefit * 3
    total_monthly_savings = config.labor_efficiency_savings + config.error_reduction_savings + config.audit_preparation_savings
    
    email_content = f"""
SUBJECT: {config.email_subject}

To: {config.email_to}
From: {config.email_from}
Date: {config.email_date or datetime.date.today().strftime("%B %d, %Y")}
Meeting Request: {config.meeting_request}

Dear {config.email_to},

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
    
    # Save JSON
    email_data = {
        "subject": config.email_subject,
        "to": config.email_to,
        "from": config.email_from,
        "body": email_content,
        "timestamp": datetime.datetime.utcnow().isoformat(),
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

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Echoes AI - Email ROI Stakeholder Generator")
    parser.add_argument("--config", help="YAML configuration file")
    parser.add_argument("--output", default="stakeholder_email", help="Output filename base")
    args = parser.parse_args()
    
    if not args.config:
        print("Please specify --config <yaml_file>")
        return 1
    
    config = load_email_config(args.config)
    print(f"✅ Loaded configuration from: {args.config}")
    
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
