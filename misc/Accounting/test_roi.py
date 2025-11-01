# Save this as test_roi.py and run: python test_roi.py

# Basic ROI Calculator (no YAML dependency)
compliance_team_size = 5
avg_hourly_rate = 85
weekly_hours_saved = 40
error_reduction_pct = 75
audit_prep_hours_saved = 30
audits_per_year = 4
echoes_investment = 12000

# Calculations
monthly_labor = (weekly_hours_saved * 4.33) * avg_hourly_rate
error_savings = (compliance_team_size * 15000) * (error_reduction_pct/100)
audit_savings = (audit_prep_hours_saved * avg_hourly_rate * audits_per_year) / 12

total_monthly = monthly_labor + error_savings + audit_savings
net_benefit = total_monthly - echoes_investment
roi_pct = (net_benefit / echoes_investment) * 100
payback_days = echoes_investment / (total_monthly/30)

print(f"""
=== ECHOES AI - ROI ANALYSIS ===
For: {compliance_team_size}-Person Compliance Team

MONTHLY SAVINGS:
- Labor Efficiency: ${monthly_labor:,.2f}
- Error Reduction: ${error_savings:,.2f}
- Audit Preparation: ${audit_savings:,.2f}

TOTAL MONTHLY SAVINGS: ${total_monthly:,.2f}
ECHOES INVESTMENT: ${echoes_investment:,.2f}/month
NET MONTHLY BENEFIT: ${net_benefit:,.2f}

RETURN ON INVESTMENT: {roi_pct:.0f}%
PAYBACK PERIOD: {payback_days:.0f} days
============================
""")
