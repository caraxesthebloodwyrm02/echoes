#!/usr/bin/env python3
# echoes_email_generator.py - Email ROI Analysis Generator
# Purpose: Generate professional stakeholder emails from ROI YAML config

import json
import sys
import csv
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import datetime
import math

@dataclass
class EmailConfig:
    # Email Metadata
    email_subject: str = "Echoes AI ROI Analysis - Immediate 5-Day Payback Opportunity"
    email_to: str = "CFO, CTO, Chief Compliance Officer"
    email_from: str = "Sarah Chen, Echoes AI <sarah.chen@echoes.ai>"
    email_date: str = ""
    meeting_request: str = "30-minute decision meeting - This week preferred"
    
    # Institution Details
    institution_name: str = "Pilot A Bank"
    pilot_completed: bool = True
    pilot_duration: str = "8 weeks"
    team_size: int = 5
    
    # Key ROI Metrics
    monthly_savings: float = 71822
    monthly_investment: float = 12000
    net_monthly_benefit: float = 59822
    roi_percentage: float = 499
    payback_days: float = 5
    
    # Financial Breakdown
    labor_efficiency_savings: float = 14722
    error_reduction_savings: float = 56250
    audit_preparation_savings: float = 850
    
    # Decision Framework
    decision_deadline: str = "November 1, 2025"
    contract_duration: str = "12-month minimum"
    rollout_timeline: str = "4-6 weeks"

def load_email_config(yaml_path: str) -> EmailConfig:
    """Load configuration from email YAML file"""
    try:
        import yaml
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except ImportError:
        print("Note: Install PyYAML for full YAML support (pip install pyyaml)")
        # Minimal YAML parsing for email config
        data = {}
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if ':' in line and not line.strip().startswith('#'):
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
        except Exception as e:
            print(f"Warning: Could not parse YAML, using defaults. Error: {e}")

    # Create config object
    config = EmailConfig()
    
    # Email metadata
    config.email_subject = data.get('email_subject', config.email_subject)
    config.email_to = data.get('email_to', config.email_to)
    config.email_from = data.get('email_from', config.email_from)
    config.email_date = data.get('email_date', config.email_date)
    config.meeting_request = data.get('meeting_request', config.meeting_request)
    
    # Institution details
    config.institution_name = data.get('institution_name', config.institution_name)
    config.pilot_completed = data.get('pilot_completed', config.pilot_completed)
    config.pilot_duration = data.get('pilot_duration', config.pilot_duration)
    config.team_size = data.get('team_size', config.team_size)
    
    # ROI metrics
    config.monthly_savings = data.get('monthly_savings', config.monthly_savings)
    config.monthly_investment = data.get('monthly_investment', config.monthly_investment)
    config.net_monthly_benefit = data.get('net_monthly_benefit', config.net_monthly_benefit)
    config.roi_percentage = data.get('roi_percentage', config.roi_percentage)
    config.payback_days = data.get('payback_days', config.payback_days)
    
    # Financial breakdown
    config.labor_efficiency_savings = data.get('labor_efficiency_savings', config.labor_efficiency_savings)
    config.error_reduction_savings = data.get('error_reduction_savings', config.error_reduction_savings)
    config.audit_preparation_savings = data.get('audit_preparation_savings', config.audit_preparation_savings)
    
    # Decision framework
    config.decision_deadline = data.get('decision_deadline', config.decision_deadline)
    config.contract_duration = data.get('contract_duration', config.contract_duration)
    config.rollout_timeline = data.get('rollout_timeline', config.rollout_timeline)
    
    return config

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency for email display"""
    return f"${amount:,.0f}"

def generate_executive_email(config: EmailConfig) -> str:
    """Generate professional stakeholder email"""
    
    # Calculate additional metrics
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
    """Export email in multiple formats"""
    
    email_content = generate_executive_email(config)
    
    # Save as text file
    with open(f"{base_filename}.txt", "w", encoding="utf-8") as f:
        f.write(email_content)
    print(f"✅ Email exported: {base_filename}.txt")
    
    # Save as HTML (for email clients)
    html_content = convert_to_html(email_content)
    with open(f"{base_filename}.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ Email HTML exported: {base_filename}.html")
    
    # Save JSON for data persistence
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
    
    # Export CSV for spreadsheet analysis
    with open(f"{base_filename}_metrics.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Monthly Investment", f"{config.monthly_investment:.2f}"])
        writer.writerow(["Monthly Savings", f"{config.monthly_savings:.2f}"])
        writer.writerow(["Net Monthly Benefit", f"{config.net_monthly_benefit:.2f}"])
        writer.writerow(["ROI Percentage", f"{config.roi_percentage:.2f}"])
        writer.writerow(["Payback Days", f"{config.payback_days:.2f}"])
        writer.writerow(["Annual Net Benefit", f"{config.net_monthly_benefit * 12:.2f}"])
        writer.writerow(["3-Year Value", f"{config.net_monthly_benefit * 36:.2f}"])
    print(f"✅ Email metrics exported: {base_filename}_metrics.csv")

def convert_to_html(email_text: str) -> str:
    """Convert plain text email to HTML format"""
    
    # Convert line breaks to HTML paragraphs
    lines = email_text.split('\n')
    html_lines = []
    
    for line in lines:
        line = line.strip()
        if not line:
            html_lines.append('<br>')
        elif line.startswith('SUBJECT:'):
            html_lines.append(f'<h2 style="color: #2c5aa0; margin-bottom: 10px;">{line}</h2>')
        elif line.startswith('•'):
            html_lines.append(f'<li style="margin-bottom: 5px;">{line[1:].strip()}</li>')
        elif '│' in line and '─' in line:
            # Table row - convert to simple HTML table
            html_lines.append('<table border="1" style="border-collapse: collapse; margin: 10px 0;">')
        elif line.startswith('┌'):
            continue  # Skip table borders
        elif line.startswith('└'):
            html_lines.append('</table>')
        elif '|' in line and not line.startswith('│'):
            # Table data
            cells = [cell.strip() for cell in line.split('│') if cell.strip()]
            if len(cells) >= 2:
                html_lines.append(f'<tr><td style="padding: 8px; border: 1px solid #ccc;">{cells[0]}</td><td style="padding: 8px; border: 1px solid #ccc; text-align: right;">{cells[1]}</td></tr>')
        elif line.startswith('✓'):
            html_lines.append(f'<p style="color: #28a745; margin-bottom: 8px;">{line}</p>')
        else:
            html_lines.append(f'<p style="margin-bottom: 10px;">{line}</p>')
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Echoes AI ROI Analysis</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            .header {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
            .metrics {{ background-color: #e9ecef; padding: 15px; border-radius: 5px; }}
            .cta {{ background-color: #d4edda; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        {''.join(html_lines)}
    </body>
    </html>
    """
    
    return html_content

def interactive_email_setup() -> EmailConfig:
    """Interactive setup for email configuration"""
    print("📧 EMAIL STAKEHOLDER ROI SETUP")
    print("=" * 50)
    
    config = EmailConfig()
    
    # Email details
    config.institution_name = input("Institution Name [Pilot A Bank]: ") or "Pilot A Bank"
    config.email_to = input("Email To (recipients) [CFO, CTO, Chief Compliance Officer]: ") or "CFO, CTO, Chief Compliance Officer"
    config.email_from = input("Email From [Sarah Chen, Echoes AI <sarah.chen@echoes.ai>]: ") or "Sarah Chen, Echoes AI <sarah.chen@echoes.ai>"
    
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
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Echoes AI - Email ROI Stakeholder Generator")
    parser.add_argument("--config", help="YAML configuration file")
    parser.add_argument("--interactive", action="store_true", help="Interactive email setup")
    parser.add_argument("--output", default="stakeholder_email", help="Output filename base")
    
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        config = load_email_config(args.config)
        print(f"✅ Loaded configuration from: {args.config}")
    elif args.interactive:
        config = interactive_email_setup()
    else:
        print("Please specify --config <yaml_file> or --interactive")
        return 1
    
    # Generate email
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
    print(f"Files created: {args.output}.txt, {args.output}.html, {args.output}_data.json, {args.output}_metrics.csv")

if __name__ == "__main__":
    main()
