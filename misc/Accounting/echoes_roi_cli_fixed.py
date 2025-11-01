#!/usr/bin/env python3
# echoes_roi_cli_fixed.py - Fix for YAML currency validation

import json
import sys
import csv
import math
import os
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any, List
import datetime

# Currency formatter (USD by default)
class Money:
    def __init__(self, currency: str = "USD", locale: Optional[str] = "en_US"):
        self.currency = currency.upper() if currency else "USD"
        self.locale = locale

    def format(self, value: float) -> str:
        try:
            import locale
            if self.locale:
                try:
                    locale.setlocale(locale.LC_ALL, self.locale)
                except Exception:
                    pass
            symbol = '$' if self.currency == 'USD' else ''
            return f"{symbol}{value:,.2f}"
        except Exception:
            return f"{value:,.2f}"

@dataclass
class Config:
    # Financials
    avg_hourly_rate: float = 85.0
    # Productivity
    weekly_hours_saved: float = 40.0
    # Quality / risk
    error_reduction_pct: float = 75.0
    avg_cost_per_error_per_fte: float = 15000.0
    # Audits
    audit_prep_hours_saved: float = 30.0
    audits_per_year: float = 4.0
    # Scale
    compliance_team_size: int = 5
    # Contract
    echoes_investment: float = 12000.0
    # Meta
    institution_name: str = "[Bank Name]"
    currency: str = "USD"

def _coerce(val: str):
    s = val.strip()
    if s.lower() in ('true', '1', 'yes', 'y'):
        return True
    if s.lower() in ('false', '0', 'no', 'n'):
        return False
    if s.lower() in ('null', '~', 'none'):
        return None
    try:
        if '.' in s:
            return float(s)
        return int(s)
    except ValueError:
        return s.strip()  # Always strip strings

def _minimal_yaml_load(text: str) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    stack: List[Dict[str, Any]] = [data]
    indent_stack: List[int] = [0]

    for line in text.splitlines():
        stripped = line.rstrip()
        if not stripped or stripped.strip().startswith('#'):
            continue
        # Count leading spaces
        spaces = len(line) - len(line.lstrip(' '))
        
        # Adjust stack for indentation
        while spaces < indent_stack[-1] and len(stack) > 1:
            stack.pop()
            indent_stack.pop()
        parent = stack[-1]

        if ':' in stripped:
            key_part, _, val_part = stripped.partition(':')
            key = key_part.strip()
            val = val_part.strip()
            if val == '':
                # Start a new dict block
                parent[key] = {}
                stack.append(parent[key])
                indent_stack.append(spaces + 2)
            else:
                parent[key] = _coerce(val)
        elif stripped.startswith('- '):
            # List item
            if not isinstance(parent, list):
                # Convert dict to list if needed (simplified)
                parent = parent  # Simplified handling
            item_val = _coerce(stripped[2:].strip())
            if isinstance(parent, list):
                parent.append(item_val)
    return data

def compute_roi(config: Config) -> Dict[str, Any]:
    hours_per_month = 4.33
    monthly_labor = (config.weekly_hours_saved * hours_per_month) * config.avg_hourly_rate
    annual_labor = monthly_labor * 12.0

    error_reduction_savings = (config.compliance_team_size * config.avg_cost_per_error_per_fte) * (max(0.0, min(100.0, config.error_reduction_pct)) / 100.0)
    audit_savings = (config.audit_prep_hours_saved * config.avg_hourly_rate * max(0.0, config.audits_per_year)) / 12.0

    total_monthly_savings = monthly_labor + error_reduction_savings + audit_savings
    net_monthly_benefit = total_monthly_savings - config.echoes_investment

    roi_pct = 0.0
    payback_days = float('inf') if total_monthly_savings <= 0 else (config.echoes_investment / (total_monthly_savings / 30.0))
    if config.echoes_investment > 0:
        roi_pct = (net_monthly_benefit / config.echoes_investment) * 100.0

    res = {
        "inputs": asdict(config),
        "metrics": {
            "hours_per_month": hours_per_month,
            "monthly_labor_savings": monthly_labor,
            "annual_labor_savings": annual_labor,
            "error_reduction_savings": error_reduction_savings,
            "audit_savings": audit_savings,
            "total_monthly_savings": total_monthly_savings,
            "echoes_investment": config.echoes_investment,
            "net_monthly_benefit": net_monthly_benefit,
            "roi_pct": roi_pct,
            "payback_days": payback_days
        },
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return res

def print_report(res: Dict[str, Any], money: Money) -> None:
    i = res["inputs"]
    m = res["metrics"]
    hdr = f"=== ECHOES AI - ROI ANALYSIS ==="
    subtitle = f"For: {i['compliance_team_size']}-Person Compliance Team @ {i['institution_name']}"
    print(hdr)
    print(subtitle)
    print("-" * max(len(hdr), len(subtitle)))
    print("MONTHLY SAVINGS:")
    print(f"- Labor Efficiency: {money.format(m['monthly_labor_savings'])}")
    print(f"- Error Reduction:  {money.format(m['error_reduction_savings'])}")
    print(f"- Audit Preparation: {money.format(m['audit_savings'])}")
    print("")
    print(f"TOTAL MONTHLY SAVINGS: {money.format(m['total_monthly_savings'])}")
    print(f"ECHOES INVESTMENT: {money.format(m['echoes_investment'])}/month")
    print(f"NET MONTHLY BENEFIT: {money.format(m['net_monthly_benefit'])}")
    print("")
    print(f"RETURN ON INVESTMENT: {m['roi_pct']:.0f}%")
    days = m['payback_days']
    days_str = f"{days:.0f} days" if math.isfinite(days) else "N/A"
    print(f"PAYBACK PERIOD: {days_str}")
    print("=" * 50)

def export_json(res: Dict[str, Any], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print(f"✓ Wrote JSON: {path}")

def export_csv(res: Dict[str, Any], path: str) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        m = res["metrics"]
        writer.writerow(["monthly_labor_savings", f"{m['monthly_labor_savings']:.2f}"])
        writer.writerow(["annual_labor_savings", f"{m['annual_labor_savings']:.2f}"])
        writer.writerow(["error_reduction_savings", f"{m['error_reduction_savings']:.2f}"])
        writer.writerow(["audit_savings", f"{m['audit_savings']:.2f}"])
        writer.writerow(["total_monthly_savings", f"{m['total_monthly_savings']:.2f}"])
        writer.writerow(["echoes_investment", f"{m['echoes_investment']:.2f}"])
        writer.writerow(["net_monthly_benefit", f"{m['net_monthly_benefit']:.2f}"])
        writer.writerow(["roi_pct", f"{m['roi_pct']:.2f}"])
        writer.writerow(["payback_days", f"{m['payback_days']:.2f}"])
    print(f"✓ Wrote CSV: {path}")

def read_yaml_config(path: str) -> Dict[str, Any]:
    if path == "-" or path.lower() == "stdin":
        text = sys.stdin.read()
    else:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    return _minimal_yaml_load(text)

def build_config_from_yaml(yaml_path: str) -> Config:
    cfg = Config()
    try:
        data = read_yaml_config(yaml_path)
        if not isinstance(data, dict):
            print(f"WARNING: YAML file didn't contain a dictionary at top level", file=sys.stderr)
            return cfg

        # Safely extract and coerce values
        if "institution_name" in data:
            cfg.institution_name = str(data["institution_name"]).strip() or cfg.institution_name
        if "compliance_team_size" in data:
            cfg.compliance_team_size = int(float(str(data["compliance_team_size"]).strip()))
        if "avg_hourly_rate" in data:
            cfg.avg_hourly_rate = float(str(data["avg_hourly_rate"]).strip())
        if "weekly_hours_saved" in data:
            cfg.weekly_hours_saved = float(str(data["weekly_hours_saved"]).strip())
        if "error_reduction_pct" in data:
            cfg.error_reduction_pct = float(str(data["error_reduction_pct"]).strip())
        if "avg_cost_per_error_per_fte" in data:
            cfg.avg_cost_per_error_per_fte = float(str(data["avg_cost_per_error_per_fte"]).strip())
        if "audit_prep_hours_saved" in data:
            cfg.audit_prep_hours_saved = float(str(data["audit_prep_hours_saved"]).strip())
        if "audits_per_year" in data:
            cfg.audits_per_year = float(str(data["audits_per_year"]).strip())
        if "echoes_investment" in data:
            cfg.echoes_investment = float(str(data["echoes_investment"]).strip())
        if "currency" in data:
            raw_currency = str(data["currency"]).strip()
            # More flexible currency validation
            if raw_currency and len(raw_currency) >= 2:
                cfg.currency = raw_currency.upper()[:3].ljust(3, 'USD')[0:3]  # Safe default
            else:
                cfg.currency = "USD"

    except Exception as e:
        print(f"WARNING: Error parsing YAML config: {e}", file=sys.stderr)
    
    return cfg

def validate_config(cfg: Config) -> List[str]:
    issues: List[str] = []
    
    # More flexible validation
    if cfg.compliance_team_size < 0:
        issues.append("compliance_team_size must be >= 0")
    if cfg.avg_hourly_rate < 0:
        issues.append("avg_hourly_rate must be >= 0")
    if cfg.weekly_hours_saved < 0:
        issues.append("weekly_hours_saved must be >= 0")
    if not (0 <= cfg.error_reduction_pct <= 100):
        issues.append("error_reduction_pct must be between 0 and 100")
    if cfg.avg_cost_per_error_per_fte < 0:
        issues.append("avg_cost_per_error_per_fte must be >= 0")
    if cfg.audit_prep_hours_saved < 0:
        issues.append("audit_prep_hours_saved must be >= 0")
    if cfg.audits_per_year < 0:
        issues.append("audits_per_year must be >= 0")
    if cfg.echoes_investment < 0:
        issues.append("echoes_investment must be >= 0")
    
    # Flexible currency validation - accept 2-3 letter codes and common symbols
    if cfg.currency:
        cur = cfg.currency.upper().strip()
        if len(cur) == 2:  # Common 2-letter codes (USD, EUR, etc.)
            cfg.currency = cur
        elif len(cur) == 3:  # 3-letter codes
            cfg.currency = cur
        elif cur.startswith('$'):  # Dollar symbol
            cfg.currency = "USD"
        elif cur.startswith('€'):  # Euro symbol
            cfg.currency = "EUR"
        elif cur.startswith('£'):  # Pound symbol
            cfg.currency = "GBP"
        else:
            # Default to USD if unclear
            cfg.currency = "USD"
    else:
        cfg.currency = "USD"
        
    return issues

def main(argv: Optional[List[str]] = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Echoes AI - Compliance Automation ROI Calculator (CLI - Fixed)")
    parser.add_argument("--config", dest="config_path", required=False, help="Path to YAML config file or '-' for stdin")
    parser.add_argument("--export-json", dest="export_json", help="Export results to JSON file")
    parser.add_argument("--export-csv", dest="export_csv", help="Export summary to CSV file")
    parser.add_argument("--interactive", dest="interactive", action="store_true", help="Interactive prompts")
    
    args = parser.parse_args(argv)

    if args.config_path:
        cfg = build_config_from_yaml(args.config_path)
    elif args.interactive:
        # Interactive mode
        print("=== Interactive ROI Setup ===")
        def prompt(name: str, default: Any, coerce=float):
            s = input(f"{name} [{default}]: ").strip()
            return coerce(s) if s else default
        def prompt_int(name: str, default: int):
            s = input(f"{name} [{default}]: ").strip()
            return int(s) if s else default
        def prompt_str(name: str, default: str):
            s = input(f"{name} [{default}]: ").strip()
            return s if s else default

        cfg = Config()
        cfg.institution_name = prompt_str("Institution name", cfg.institution_name)
        cfg.compliance_team_size = prompt_int("Compliance team size (FTEs)", cfg.compliance_team_size)
        cfg.avg_hourly_rate = prompt("Loaded cost per hour ($)", cfg.avg_hourly_rate, float)
        cfg.weekly_hours_saved = prompt("Weekly hours saved", cfg.weekly_hours_saved, float)
        cfg.error_reduction_pct = prompt("Error reduction (%)", cfg.error_reduction_pct, float)
        cfg.avg_cost_per_error_per_fte = prompt("Average cost per error per FTE ($)", cfg.avg_cost_per_error_per_fte, float)
        cfg.audit_prep_hours_saved = prompt("Audit prep hours saved per audit", cfg.audit_prep_hours_saved, float)
        cfg.audits_per_year = prompt("Audits per year", cfg.audits_per_year, float)
        cfg.echoes_investment = prompt("Echoes investment ($/month)", cfg.echoes_investment, float)
        cfg.currency = prompt_str("Currency code (USD, EUR, etc.)", cfg.currency)
    else:
        print("Please provide --config <yaml_file>, --interactive, or see --help")
        return 1

    issues = validate_config(cfg)
    if issues:
        for issue in issues:
            print(f"❌ Validation error: {issue}", file=sys.stderr)
        return 2

    print(f"✅ Configuration validated successfully")
    res = compute_roi(cfg)
    money = Money(currency=cfg.currency)
    print()
    print_report(res, money)

    if args.export_json:
        export_json(res, args.export_json)
    if args.export_csv:
        export_csv(res, args.export_csv)

    return 0

if __name__ == "__main__":
    sys.exit(main())
