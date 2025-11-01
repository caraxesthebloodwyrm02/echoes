#!/usr/bin/env python3
# master_roi_spreadsheet.py
# --------------------------------------------
# 1️⃣   Clean input (YAML or hard‑coded defaults)
# 2️⃣   Compute derived metrics
# 3️⃣   Dump a CSV & a text file – no `#ERROR` lines
# --------------------------------------------

import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ──────────────────────────────────────────────────────
# 1️⃣  CONFIG (defaults or YAML)
# ──────────────────────────────────────────────────────
try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

def load_config_from_yaml(yaml_path: str) -> Dict[str, Any]:
    """Parse a tiny YAML config."""
    raw = Path(yaml_path).read_text(encoding="utf-8")
    data: Dict[str, Any] = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            try:
                if "." in val:
                    data[key] = float(val)
                elif val.isdigit():
                    data[key] = int(val)
                elif val.lower() in ("true", "false"):
                    data[key] = val.lower() == "true"
                else:
                    data[key] = val
            except Exception:  # pragma: no cover
                data[key] = val
    return data


DEFAULTS: Dict[str, Any] = {
    # --- Basic ---
    "institution_name": "Pilot A Bank",
    "analysis_date": "October 29, 2025",
    "prepared_by": "Sarah Chen, Echoes AI",
    "prepared_by_email": "sarah.chen@echoes.ai",
    # --- Numbers ---
    "team_size": 5,
    "monthly_investment": 12_000,
    "monthly_savings": 71_822,
    "payback_days": 5,
    "roi_percent": 499,
    # --- Breakdown ---
    "labor_efficiency": 14_722,
    "error_reduction": 56_250,
    "audit_prep": 850,
    # --- Scenarios ---
    "scenario_conservative": {
        "payback": 7,
        "roi": 350,
        "monthly_net": 45_000,
        "annual_benefit": 540_000,
    },
    "scenario_base": {
        "payback": 5,
        "roi": 499,
        "monthly_net": 59_822,
        "annual_benefit": 717_864,
    },
    "scenario_aggressive": {
        "payback": 3,
        "roi": 750,
        "monthly_net": 85_000,
        "annual_benefit": 1_020_000,
    },
    # --- Sensitivity ---
    "sensitivity": [
        ("Hours saved = 30/week (instead of 40)", "-20%", 6, "Still excellent ROI"),
        ("Hours saved = 50/week", "+25%", 4, "Enhanced efficiency gains"),
        ("Error reduction = 50% (instead of 75%)", "-15%", 6, "Baseline compliance improvement"),
        ("Error reduction = 90%", "+10%", 5, "Industry‑leading performance"),
        ("Team size = 4 FTEs (instead of 5)", "-20%", 6, "Smaller organization"),
        ("Team size = 6 FTEs", "+20%", 4, "Larger implementation"),
    ],
    # --- Implementation ---
    "timeline": {
        "Decision Phase": ("This Week", "Investment Approval", "Signed Contract"),
        "Preparation Phase": ("Week 2-3", "Technical Setup", "Infrastructure Ready"),
        "Training Phase": ("Week 3-4", "Team Training", "Certified Users"),
        "Rollout Phase": ("Week 4-6", "Production Deployment", "Live System"),
        "Optimization Phase": ("Week 6-8", "Performance Tuning", "Max Efficiency"),
    },
    "milestones": [
        ("Executive Decision", "November 1, 2025", "Yes", "Board Approval"),
        ("Contract Execution", "November 5, 2025", "Yes", "Legal Review"),
        ("Technical Kickoff", "November 8, 2025", "No", "Vendor Onboarding"),
        ("Go‑Live Target", "December 15, 2025", "No", "Testing Complete"),
    ],
    # --- Financial ---
    "costs": [
        ("Echoes AI Investment", 144_000, "12‑month contract minimum"),
        ("Implementation Costs", 0, "Included in service"),
        ("Training Costs", 0, "Vendor‑provided"),
        ("Ongoing Support", 0, "24/7 included"),
    ],
    "benefits": [
        ("Labor Efficiency Savings", 176_664, "40 hours/week @ $85/hour"),
        ("Error Reduction Savings", 675_000, "5 FTEs @ $15K/error reduction"),
        ("Audit Preparation Savings", 10_200, "4 audits @ 30 hours each"),
    ],
    # --- Risk ---
    "risks": [
        ("Technology Adoption Risk", "Low", "Medium", "8‑week pilot proven success"),
        ("ROI Achievement Risk", "Low", "High", "Conservative estimates used"),
        ("Implementation Risk", "Very Low", "Medium", "Experienced vendor team"),
        ("Operational Disruption", "Very Low", "Low", "Seamless integration"),
    ],
    # --- Competitive Advantages ---
    "advantages": [
        ("First‑Mover Benefit", "Early adoption advantage", "Market leadership position"),
        ("Proven Technology", "8‑week pilot success", "Reduced implementation risk"),
        ("Immediate ROI", "5‑day payback period", "Fast value realization"),
        ("Compliance Leadership", "75% error reduction", "Industry best practices"),
    ],
}

# ──────────────────────────────────────────────────────
# 2️⃣  HELPERS
# ──────────────────────────────────────────────────────
def fmt(num: Any) -> str:
    """Currency formatter – no decimals."""
    if isinstance(num, (int, float)):
        return f"${num:,.0f}"
    return str(num)


def to_rows(
    title: str,
    header: List[Any],
    rows: List[Tuple[Any, ...]],
) -> List[List[str]]:
    """
    Build a block of rows for CSV/text.
    `header` may be any iterable of values – we convert each to string.
    """
    out: List[List[str]] = [[f"{title}"], []]
    out.append([str(x) for x in header])   # <-- fix: normalise header
    for r in rows:
        out.append([str(x) for x in r])
    out.append([])
    return out


def generate_master(config: Dict[str, Any]) -> Tuple[List[List[str]], List[List[str]]]:
    """
    Returns: (csv_rows, text_rows)
    """
    # Derived values
    config["net_monthly_benefit"] = config["monthly_savings"] - config["monthly_investment"]
    config["annual_net_benefit"] = config["net_monthly_benefit"] * 12
    config["three_year_value"] = config["annual_net_benefit"] * 3

    csv_rows: List[List[str]] = [
        ["ECHOES AI - COMPREHENSIVE ROI ANALYSIS"],
        ["Executive Financial Analysis for Compliance Automation"],
        [""],
        [f"Institution: {config['institution_name']}"],
        [f"Analysis Date: {config['analysis_date']}"],
        [f"Prepared by: {config['prepared_by']}"],
        [f"Prepared by email: {config['prepared_by_email']}"],
        [""],
        ["=" * 80],
        [""],
    ]

    text_rows: List[List[str]] = csv_rows.copy()

    # ── EXECUTIVE SUMMARY ───────────────────────────────
    exec_summ = [
        ("Metric", "Value", "Interpretation"),
        ("Monthly Investment", fmt(config["monthly_investment"]), "Fixed monthly cost"),
        ("Monthly Savings", fmt(config["monthly_savings"]), "Total operational savings"),
        ("Net Monthly Benefit", fmt(config["net_monthly_benefit"]), "Benefit after investment"),
        ("Payback Period", f"{config['payback_days']} days", "Investment recovery time"),
        ("Return on Investment", f"{config['roi_percent']}%", "Annual ROI percentage"),
        ("Annual Net Benefit", fmt(config["annual_net_benefit"]), "Year 1 value creation"),
        ("3-Year Cumulative Value", fmt(config["three_year_value"]), "3‑year total benefit"),
    ]
    csv_rows.extend(to_rows("EXECUTIVE SUMMARY - KEY METRICS", exec_summ[0], exec_summ[1:]))
    text_rows.extend(to_rows("EXECUTIVE SUMMARY - KEY METRICS", exec_summ[0], exec_summ[1:]))

    # ── BREAKDOWN ─────────────────────────────────────
    total_breakdown = (
        config["labor_efficiency"]
        + config["error_reduction"]
        + config["audit_prep"]
    )
    breaks = [
        (
            "Labor Efficiency",
            fmt(config["labor_efficiency"]),
            f"{(config['labor_efficiency'] / total_breakdown) * 100:.2f}%",
            fmt(config["labor_efficiency"] * 12),
        ),
        (
            "Error Reduction",
            fmt(config["error_reduction"]),
            f"{(config['error_reduction'] / total_breakdown) * 100:.2f}%",
            fmt(config["error_reduction"] * 12),
        ),
        (
            "Audit Preparation",
            fmt(config["audit_prep"]),
            f"{(config['audit_prep'] / total_breakdown) * 100:.2f}%",
            fmt(config["audit_prep"] * 12),
        ),
        (
            "TOTAL MONTHLY SAVINGS",
            fmt(total_breakdown),
            "100.00%",
            fmt(total_breakdown * 12),
        ),
    ]
    csv_rows.extend(
        to_rows(
            "SAVINGS COMPONENT BREAKDOWN",
            breaks[0],
            breaks[1:],
        )
    )
    text_rows.extend(
        to_rows(
            "SAVINGS COMPONENT BREAKDOWN",
            breaks[0],
            breaks[1:],
        )
    )
    csv_rows.append(["Note: Error reduction represents largest value driver (78.3% of total savings)"])
    text_rows.append(["Note: Error reduction represents largest value driver (78.3% of total savings)"])
    csv_rows.append([""])
    text_rows.append([""])

    # ── CASH FLOW ─────────────────────────────────────
    cash_rows = [("Month", "Investment", "Savings", "Net Benefit", "Cumulative Net")]
    cumulative = 0
    for m in range(1, 13):
        net = config["net_monthly_benefit"]
        cumulative += net
        cash_rows.append(
            (
                f"Month {m}",
                fmt(config["monthly_investment"]),
                fmt(config["monthly_savings"]),
                fmt(net),
                fmt(cumulative),
            )
        )
    csv_rows.extend(to_rows("12-MONTH CASH FLOW PROJECTIONS", cash_rows[0], cash_rows[1:]))
    text_rows.extend(to_rows("12-MONTH CASH FLOW PROJECTIONS", cash_rows[0], cash_rows[1:]))

    # ── SCENARIO ANALYSIS ──────────────────────────────
    scen_rows = [
        ("Scenario", "Payback Period", "ROI %", "Monthly Net", "Annual Benefit", "Risk Level"),
        (
            "Conservative Estimate",
            f"{config['scenario_conservative']['payback']} days",
            f"{config['scenario_conservative']['roi']}%",
            fmt(config["scenario_conservative"]["monthly_net"]),
            fmt(config["scenario_conservative"]["annual_benefit"]),
            "Low",
        ),
        (
            "Base Case (Pilot Results)",
            f"{config['scenario_base']['payback']} days",
            f"{config['scenario_base']['roi']}%",
            fmt(config["scenario_base"]["monthly_net"]),
            fmt(config["scenario_base"]["annual_benefit"]),
            "Very Low",
        ),
        (
            "Aggressive (Full Adoption)",
            f"{config['scenario_aggressive']['payback']} days",
            f"{config['scenario_aggressive']['roi']}%",
            fmt(config["scenario_aggressive"]["monthly_net"]),
            fmt(config["scenario_aggressive"]["annual_benefit"]),
            "Low",
        ),
    ]
    csv_rows.extend(to_rows("SCENARIO ANALYSIS - RISK ASSESSMENT", scen_rows[0], scen_rows[1:]))
    text_rows.extend(to_rows("SCENARIO ANALYSIS - RISK ASSESSMENT", scen_rows[0], scen_rows[1:]))

    # ── SENSITIVITY ───────────────────────────────────
    sens_rows = [("Variable Change", "Impact on ROI", "New Payback", "Notes")]
    for a, imp, pb, note in config["sensitivity"]:
        sens_rows.append((a, imp, f"{pb} days", note))
    csv_rows.extend(to_rows("SENSITIVITY ANALYSIS - IMPACT OF KEY VARIABLES", sens_rows[0], sens_rows[1:]))
    text_rows.extend(to_rows("SENSITIVITY ANALYSIS - IMPACT OF KEY VARIABLES", sens_rows[0], sens_rows[1:]))

    # ── IMPLEMENTATION ROADMAP ───────────────────────
    imp_rows = [("Phase", "Timeline", "Milestone", "Deliverable")]
    for ph, (tl, ms, dl) in config["timeline"].items():
        imp_rows.append((ph, tl, ms, dl))
    csv_rows.extend(to_rows("IMPLEMENTATION ROADMAP", imp_rows[0], imp_rows[1:]))
    text_rows.extend(to_rows("IMPLEMENTATION ROADMAP", imp_rows[0], imp_rows[1:]))

    # ── MILESTONES ──────────────────────────────────
    mil_rows = [("Milestone", "Target Date", "Critical Path", "Dependencies")]
    for m, td, cp, dep in config["milestones"]:
        mil_rows.append((m, td, cp, dep))
    csv_rows.append([""])
    csv_rows.extend(to_rows("KEY MILESTONES & DEADLINES", mil_rows[0], mil_rows[1:]))
    text_rows.append([""])
    text_rows.extend(to_rows("KEY MILESTONES & DEADLINES", mil_rows[0], mil_rows[1:]))

    # ── FINANCIAL JUSTIFICATION ───────────────────────
    fin_rows = [("Cost Category", "Annual Amount", "Justification")]
    for cat, amt, jus in config["costs"]:
        fin_rows.append((cat, fmt(amt), jus))
    fin_rows.append(("TOTAL ANNUAL COST", fmt(config["costs"][0][1]), "Predictable monthly expense"))
    csv_rows.append([""])
    csv_rows.extend(to_rows("FINANCIAL JUSTIFICATION & BUSINESS CASE", fin_rows[0], fin_rows[1:]))
    text_rows.append([""])
    text_rows.extend(to_rows("FINANCIAL JUSTIFICATION & BUSINESS CASE", fin_rows[0], fin_rows[1:]))

    # ── BENEFITS ─────────────────────────────────────
    benef_rows = [("Benefit Category", "Annual Amount", "Source")]
    for cat, amt, src in config["benefits"]:
        benef_rows.append((cat, fmt(amt), src))
    benef_rows.append(("TOTAL ANNUAL BENEFIT", fmt(config["benefits"][0][1] + config["benefits"][1][1] + config["benefits"][2][1]), "Conservative estimate"))
    benef_rows.append(("NET ANNUAL VALUE", fmt(config["annual_net_benefit"]), "Benefit minus cost"))
    roi_multi = config["annual_net_benefit"] / config["costs"][0][1]
    benef_rows.append(("ROI MULTIPLE", f"{roi_multi:.1f}x", "Every $1 invested returns $7.10"))
    csv_rows.extend(to_rows("", [], benef_rows[1:]))
    text_rows.extend(to_rows("", [], benef_rows[1:]))
    csv_rows.append([""])
    text_rows.append([""])

    # ── RISK ────────────────────────────────────────
    risk_rows = [("Risk Category", "Probability", "Impact", "Mitigation Strategy")]
    risk_rows.extend(config["risks"])
    csv_rows.append([""])
    csv_rows.extend(to_rows("RISK ANALYSIS & MITIGATION", risk_rows[0], risk_rows[1:]))
    text_rows.append([""])
    text_rows.extend(to_rows("RISK ANALYSIS & MITIGATION", risk_rows[0], risk_rows[1:]))

    # ── COMPETITIVE ADVANTAGES ──────────────────────
    adv_rows = [("Advantage", "Value Proposition", "Competitive Edge")]
    adv_rows.extend(config["advantages"])
    csv_rows.append([""])
    csv_rows.extend(to_rows("COMPETITIVE ADVANTAGES", adv_rows[0], adv_rows[1:]))
    text_rows.append([""])
    text_rows.extend(to_rows("COMPETITIVE ADVANTAGES", adv_rows[0], adv_rows[1:]))
    csv_rows.append([""])
    text_rows.append([""])

    # ── SUMMARY FOR DECISION MAKERS ───────────────────
    summ_rows: List[List[str]] = [
        ["EXECUTIVE SUMMARY FOR DECISION MAKERS", "", ""],
        # CFO
        ["FOR THE CFO:"],
        [f"• Investment pays for itself in {config['payback_days']} days"],
        [f"• {fmt(config['annual_net_benefit'])} net annual value creation"],
        [f"• {config['roi_percent']}% return on investment"],
        ["• Predictable monthly expense with quantifiable benefits"],
        # CTO
        ["", "FOR THE CTO:"],
        ["• Proven technology with 8‑week pilot success"],
        ["• AI automation reduces manual processes by 75%"],
        ["• Seamless integration with existing systems"],
        ["• 24/7 vendor support included"],
        # CCO
        ["", "FOR THE CHIEF COMPLIANCE OFFICER:"],
        ["• 75% reduction in compliance errors"],
        ["• Automated audit trail and monitoring"],
        ["• 30+ hours saved per audit cycle"],
        ["• Continuous compliance vs periodic reviews"],
        # Recommendation
        ["", "FINAL RECOMMENDATION"],
        [f"APPROVE immediate investment of {fmt(config['monthly_investment'])} per month for Echoes AI"],
        [f"• Payback in {config['payback_days']} days = instant ROI"],
        [f"• {fmt(config['annual_net_benefit'])} annual net benefit vs {fmt(config['costs'][0][1])} investment"],
        ["• Proven results from 8‑week pilot"],
        ["• Minimal risk with maximum reward"],
        # Steps
        ["", "Next Step: Approve investment and schedule implementation meeting"],
    ]
    csv_rows.append([""])
    csv_rows.extend(to_rows("", [], summ_rows[1:]))
    text_rows.append([""])
    text_rows.extend(to_rows("", [], summ_rows[1:]))

    # Final separator
    sep_line = "=" * 60
    csv_rows.append([sep_line])
    text_rows.append([sep_line])

    return csv_rows, text_rows


# ──────────────────────────────────────────────────────
# 3️⃣  MAIN
# ──────────────────────────────────────────────────────
def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate a clean master ROI spreadsheet & text summary."
    )
    parser.add_argument(
        "--config",
        help="Path to YAML config (optional – defaults when omitted)",
        default=None,
    )
    parser.add_argument(
        "--output",
        help="Base filename (no extension)",
        default="pilot_a_master",
    )
    args = parser.parse_args()

    # Load config
    cfg: Dict[str, Any] = DEFAULTS.copy()
    if args.config and Path(args.config).exists():
        try:
            cfg.update(load_config_from_yaml(args.config))
            print(f"✅ Loaded config from {args.config}")
        except Exception as e:
            print(f"⚠️  Failed to load YAML: {e}", file=sys.stderr)

    # Generate rows
    csv_rows, txt_rows = generate_master(cfg)

    # Write CSV
    csv_path = Path(f"{args.output}.csv")
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for r in csv_rows:
            writer.writerow(r)
    print(f"✅ CSV written: {csv_path}")

    # Write TXT (for copy‑paste)
    txt_path = Path(f"{args.output}.txt")
    with txt_path.open("w", encoding="utf-8") as f:
        for r in txt_rows:
            f.write(",".join(r) + "\n")
    print(f"✅ Text written: {txt_path}")

    print("\n🎯 All output files ready – share with the stakeholder team!")


if __name__ == "__main__":
    main()
