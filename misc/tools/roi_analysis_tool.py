"""
ROI Analysis Tool for EchoesAssistantV2

Generates comprehensive ROI analysis packages including stakeholder emails,
spreadsheets, CSV data, and executive reports for converting pilots into enterprise contracts.
"""

import json
import csv
import yaml
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict

from .base import BaseTool, ToolResult


@dataclass
class ROIMetrics:
    """Core ROI calculation results."""

    monthly_investment: float
    monthly_savings: float
    net_monthly_benefit: float
    payback_days: float
    roi_percentage: float
    annual_net_benefit: float
    three_year_value: float
    savings_breakdown: Dict[str, float]


@dataclass
class StakeholderConfig:
    """Stakeholder-specific configuration."""

    institution_name: str
    email_subject: str
    email_to: List[str]
    email_from: str
    team_size: int
    decision_deadline: str
    contract_duration: str
    rollout_timeline: str
    stakeholder_priorities: Dict[str, str]


class ROIAnalysisTool(BaseTool):
    """
    Comprehensive ROI analysis generation tool for EchoesAssistantV2.

    Generates complete ROI analysis packages including:
    - Stakeholder email configurations (YAML)
    - Financial spreadsheets (CSV format)
    - Executive reports (text/markdown)
    - Raw data exports (CSV)
    """

    def __init__(self) -> None:
        super().__init__(
            "generate_roi_analysis",
            "Generate comprehensive ROI analysis with email configs, spreadsheets, and reports",
        )

        # Template storage
        self.templates = self._load_templates()

    def _load_templates(self) -> Dict[str, Any]:
        """Load ROI analysis templates."""
        return {
            "email_config": {
                "email_subject": "Echoes AI ROI Analysis - {payback_days}-Day Payback Opportunity",
                "email_from": "Sarah Chen, Echoes AI <sarah.chen@echoes.ai>",
                "decision_deadline": "November 1, 2025",
                "contract_duration": "12-month minimum",
                "rollout_timeline": "4-6 weeks",
                "meeting_request": "30-minute decision meeting - This week preferred",
            },
            "stakeholder_priorities": {
                "CFO": "Investment pays for itself in {payback_days} days - ${annual_net:,.0f} annual net benefit",
                "CTO": "{error_reduction:.0f}% reduction in compliance errors with AI automation",
                "CCO": "Automated audit trails eliminate manual review cycles",
            },
            "executive_summary": """# Echoes AI ROI Analysis - Executive Summary

## Institution: {institution_name}
## Date: {analysis_date}
## Prepared by: Sarah Chen, Echoes AI

### Key Financial Metrics
- **Monthly Investment**: ${monthly_investment:,.0f}
- **Monthly Savings**: ${monthly_savings:,.0f}
- **Net Monthly Benefit**: ${net_monthly_benefit:,.0f}
- **Payback Period**: {payback_days:.0f} days
- **ROI**: {roi_percentage:.0f}%

### Annual Impact
- **Year 1 Net Benefit**: ${annual_net_benefit:,.0f}
- **3-Year Cumulative Value**: ${three_year_value:,.0f}

### Savings Breakdown
{breakdown_text}

### Next Steps
1. Schedule 30-minute decision meeting this week
2. Review pilot results and implementation timeline
3. Approve investment by {decision_deadline}
4. Begin rollout within {rollout_timeline}

**Contact**: Sarah Chen, Echoes AI - sarah.chen@echoes.ai
""",
        }

    def __call__(
        self,
        business_type: str,
        analysis_data: Dict[str, Any],
        stakeholder_info: Dict[str, Any],
        output_formats: List[str] = None,
        customization_level: str = "comprehensive",
    ) -> ToolResult:
        """
        Generate comprehensive ROI analysis package.

        Args:
            business_type: Type of business (financial, healthcare, etc.)
            analysis_data: Core business metrics and parameters
            stakeholder_info: Information about stakeholders and institution
            output_formats: Desired output formats (yaml, csv, spreadsheet, report)
            customization_level: Level of customization (basic, standard, comprehensive)

        Returns:
            ToolResult with generated files and metadata
        """
        try:
            if output_formats is None:
                output_formats = ["yaml", "csv", "spreadsheet", "report"]

            # Phase 1: Data Validation & Preparation
            validated_data = self._validate_and_process_data(
                analysis_data, stakeholder_info
            )

            # Phase 2: Calculate Financial Metrics
            roi_metrics = self._calculate_financial_metrics(validated_data)

            # Phase 3: Generate Stakeholder Configuration
            stakeholder_config = self._generate_stakeholder_config(
                business_type, validated_data, stakeholder_info, customization_level
            )

            # Phase 4: Generate All Requested Formats
            generated_files = {}
            for format_type in output_formats:
                generated_files[format_type] = self._generate_format(
                    format_type, roi_metrics, stakeholder_config, validated_data
                )

            # Phase 5: Package Results
            result = {
                "success": True,
                "business_type": business_type,
                "customization_level": customization_level,
                "generated_files": generated_files,
                "roi_metrics": asdict(roi_metrics),
                "stakeholder_config": asdict(stakeholder_config),
                "timestamp": datetime.now().isoformat(),
                "file_count": len(generated_files),
            }

            return ToolResult(success=True, data=result)

        except Exception as e:
            return ToolResult(
                success=False, error=f"ROI analysis generation failed: {str(e)}"
            )

    def _validate_and_process_data(
        self, analysis_data: Dict[str, Any], stakeholder_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate input data and apply business-specific adjustments."""
        # Extract core metrics with defaults
        validated = {
            "monthly_investment": float(analysis_data.get("monthly_investment", 12000)),
            "monthly_savings": float(analysis_data.get("monthly_savings", 71822)),
            "team_size": int(analysis_data.get("team_size", 5)),
            "institution_name": stakeholder_info.get("institution_name", "Institution"),
            "email_to": stakeholder_info.get("email_to", []),
            "business_type": analysis_data.get("business_type", "financial"),
        }

        # Calculate derived metrics
        validated["net_monthly_benefit"] = (
            validated["monthly_savings"] - validated["monthly_investment"]
        )

        # Calculate payback period (days)
        if validated["monthly_investment"] > 0:
            validated["payback_days"] = (
                validated["monthly_investment"] / validated["monthly_savings"]
            ) * 30
        else:
            validated["payback_days"] = 0

        # Calculate ROI percentage
        if validated["monthly_investment"] > 0:
            validated["roi_percentage"] = (
                validated["net_monthly_benefit"] / validated["monthly_investment"]
            ) * 100
        else:
            validated["roi_percentage"] = 0

        # Savings breakdown (defaults based on business type)
        if validated["business_type"] == "financial":
            validated["savings_breakdown"] = {
                "labor_efficiency": validated["monthly_savings"] * 0.205,  # 20.5%
                "error_reduction": validated["monthly_savings"] * 0.783,  # 78.3%
                "audit_preparation": validated["monthly_savings"] * 0.012,  # 1.2%
            }
        else:
            # Generic breakdown
            validated["savings_breakdown"] = {
                "efficiency_gains": validated["monthly_savings"] * 0.6,
                "error_reduction": validated["monthly_savings"] * 0.3,
                "other_savings": validated["monthly_savings"] * 0.1,
            }

        return validated

    def _calculate_financial_metrics(
        self, validated_data: Dict[str, Any]
    ) -> ROIMetrics:
        """Calculate comprehensive financial metrics."""
        monthly_investment = validated_data["monthly_investment"]
        monthly_savings = validated_data["monthly_savings"]
        net_monthly = validated_data["net_monthly_benefit"]
        payback_days = validated_data["payback_days"]

        return ROIMetrics(
            monthly_investment=monthly_investment,
            monthly_savings=monthly_savings,
            net_monthly_benefit=net_monthly,
            payback_days=payback_days,
            roi_percentage=validated_data["roi_percentage"],
            annual_net_benefit=net_monthly * 12,
            three_year_value=net_monthly * 12 * 3,
            savings_breakdown=validated_data["savings_breakdown"],
        )

    def _generate_stakeholder_config(
        self,
        business_type: str,
        validated_data: Dict[str, Any],
        stakeholder_info: Dict[str, Any],
        customization_level: str,
    ) -> StakeholderConfig:
        """Generate stakeholder-specific configuration."""
        template = self.templates["email_config"]

        # Customize based on business type and level
        if business_type == "financial":
            subject_template = (
                "Echoes AI ROI Analysis - {payback_days}-Day Payback Opportunity"
            )
        else:
            subject_template = "Echoes AI ROI Analysis - Business Process Optimization"

        email_subject = subject_template.format(
            payback_days=int(validated_data["payback_days"])
        )

        return StakeholderConfig(
            institution_name=validated_data["institution_name"],
            email_subject=email_subject,
            email_to=(
                validated_data["email_to"]
                if isinstance(validated_data["email_to"], list)
                else [validated_data["email_to"]]
            ),
            email_from=template["email_from"],
            team_size=validated_data["team_size"],
            decision_deadline=template["decision_deadline"],
            contract_duration=template["contract_duration"],
            rollout_timeline=template["rollout_timeline"],
            stakeholder_priorities=self._generate_stakeholder_priorities(
                validated_data
            ),
        )

    def _generate_stakeholder_priorities(
        self, validated_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Generate stakeholder-specific messaging."""
        priorities = {}
        templates = self.templates["stakeholder_priorities"]

        annual_net = validated_data["net_monthly_benefit"] * 12
        error_reduction = 75  # Default, could be parameterized

        priorities["CFO"] = templates["CFO"].format(
            payback_days=int(validated_data["payback_days"]), annual_net=annual_net
        )
        priorities["CTO"] = templates["CTO"].format(error_reduction=error_reduction)
        priorities["CCO"] = templates["CCO"]

        return priorities

    def _generate_format(
        self,
        format_type: str,
        roi_metrics: ROIMetrics,
        stakeholder_config: StakeholderConfig,
        validated_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate specific output format."""
        if format_type == "yaml":
            return self._generate_yaml_config(
                stakeholder_config, roi_metrics, validated_data
            )
        elif format_type == "csv":
            return self._generate_csv_data(roi_metrics, validated_data)
        elif format_type == "spreadsheet":
            return self._generate_spreadsheet_data(
                roi_metrics, stakeholder_config, validated_data
            )
        elif format_type == "report":
            return self._generate_executive_report(
                roi_metrics, stakeholder_config, validated_data
            )
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _generate_yaml_config(
        self,
        stakeholder_config: StakeholderConfig,
        roi_metrics: ROIMetrics,
        validated_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate YAML configuration for stakeholder emails."""
        config = {
            "email_subject": stakeholder_config.email_subject,
            "email_to": stakeholder_config.email_to,
            "email_from": stakeholder_config.email_from,
            "institution_name": stakeholder_config.institution_name,
            "team_size": stakeholder_config.team_size,
            "monthly_investment": roi_metrics.monthly_investment,
            "monthly_savings": roi_metrics.monthly_savings,
            "net_monthly_benefit": roi_metrics.net_monthly_benefit,
            "roi_percentage": roi_metrics.roi_percentage,
            "payback_days": roi_metrics.payback_days,
            "decision_deadline": stakeholder_config.decision_deadline,
            "contract_duration": stakeholder_config.contract_duration,
            "rollout_timeline": stakeholder_config.rollout_timeline,
            "stakeholder_priorities": stakeholder_config.stakeholder_priorities,
            "savings_breakdown": roi_metrics.savings_breakdown,
            "generated_at": datetime.now().isoformat(),
        }

        yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False)
        return {
            "format": "yaml",
            "filename": f"roi_config_{stakeholder_config.institution_name.lower().replace(' ', '_')}.yaml",
            "content": yaml_content,
            "size": len(yaml_content),
        }

    def _generate_csv_data(
        self, roi_metrics: ROIMetrics, validated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate CSV data for analysis."""
        rows = []

        # Executive Summary
        rows.extend(
            [
                ["Section", "Metric", "Value", "Glimpse", "Notes"],
                [
                    "Executive Summary",
                    "Monthly Investment",
                    roi_metrics.monthly_investment,
                    "USD",
                    "Fixed monthly cost",
                ],
                [
                    "Executive Summary",
                    "Monthly Savings",
                    roi_metrics.monthly_savings,
                    "USD",
                    "Total operational savings",
                ],
                [
                    "Executive Summary",
                    "Net Monthly Benefit",
                    roi_metrics.net_monthly_benefit,
                    "USD",
                    "After investment",
                ],
                [
                    "Executive Summary",
                    "Payback Period",
                    roi_metrics.payback_days,
                    "Days",
                    "Time to break even",
                ],
                [
                    "Executive Summary",
                    "ROI Percentage",
                    roi_metrics.roi_percentage,
                    "%",
                    "Return on investment",
                ],
                [
                    "Executive Summary",
                    "Annual Net Benefit",
                    roi_metrics.annual_net_benefit,
                    "USD",
                    "Year 1 benefit",
                ],
                [
                    "Executive Summary",
                    "3-Year Value",
                    roi_metrics.three_year_value,
                    "USD",
                    "Cumulative benefit",
                ],
            ]
        )

        # Savings Breakdown
        rows.append([])
        rows.append(
            ["Section", "Component", "Monthly Amount", "Annual Amount", "Percentage"]
        )
        total_savings = roi_metrics.monthly_savings
        for component, amount in roi_metrics.savings_breakdown.items():
            annual_amount = amount * 12
            percentage = (amount / total_savings) * 100 if total_savings > 0 else 0
            rows.append(
                [
                    "Savings Breakdown",
                    component.replace("_", " ").title(),
                    amount,
                    annual_amount,
                    ".1f",
                ]
            )

        # Convert to CSV string
        output = []
        for row in rows:
            output.append(",".join(str(cell) for cell in row))

        csv_content = "\n".join(output)
        return {
            "format": "csv",
            "filename": f"roi_analysis_data_{validated_data['institution_name'].lower().replace(' ', '_')}.csv",
            "content": csv_content,
            "size": len(csv_content),
            "rows": len(rows),
        }

    def _generate_spreadsheet_data(
        self,
        roi_metrics: ROIMetrics,
        stakeholder_config: StakeholderConfig,
        validated_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate spreadsheet-style CSV data."""
        sheets = {}

        # Executive Dashboard
        dashboard_data = [
            ["ECHOES AI - EXECUTIVE ROI DASHBOARD"],
            [f"Institution: {stakeholder_config.institution_name}"],
            [f"Date: {datetime.now().strftime('%B %d, %Y')}"],
            [],
            ["KEY PERFORMANCE INDICATORS"],
            ["Metric", "Value", "Notes"],
            ["Monthly Investment", ".0f", "Fixed cost"],
            ["Monthly Savings", ".0f", "Total savings"],
            ["Net Monthly Benefit", ".0f", "After investment"],
            ["Payback Period", ".0f", "Time to break even"],
            ["ROI", ".0f", "Return on investment"],
            ["Annual Net Benefit", ".0f", "Year 1 benefit"],
            ["3-Year Value", ".0f", "Cumulative benefit"],
        ]

        # Cash Flow Projections (12 months)
        cash_flow = [
            ["Month", "Investment", "Savings", "Net Benefit", "Cumulative"],
        ]
        cumulative = 0
        for month in range(1, 13):
            cumulative += roi_metrics.net_monthly_benefit
            cash_flow.append(
                [
                    month,
                    roi_metrics.monthly_investment,
                    roi_metrics.monthly_savings,
                    roi_metrics.net_monthly_benefit,
                    cumulative,
                ]
            )

        sheets["executive_dashboard"] = dashboard_data
        sheets["cash_flow_projections"] = cash_flow

        # Convert sheets to CSV format
        csv_content = ""
        for sheet_name, data in sheets.items():
            csv_content += f"\n=== {sheet_name.upper()} ===\n"
            for row in data:
                csv_content += ",".join(str(cell) for cell in row) + "\n"

        return {
            "format": "spreadsheet",
            "filename": f"roi_master_spreadsheet_{stakeholder_config.institution_name.lower().replace(' ', '_')}.csv",
            "content": csv_content,
            "size": len(csv_content),
            "sheets": list(sheets.keys()),
        }

    def _generate_executive_report(
        self,
        roi_metrics: ROIMetrics,
        stakeholder_config: StakeholderConfig,
        validated_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate executive summary report."""
        # Format savings breakdown
        breakdown_lines = []
        total_savings = roi_metrics.monthly_savings
        for component, amount in roi_metrics.savings_breakdown.items():
            annual = amount * 12
            percentage = (amount / total_savings) * 100 if total_savings > 0 else 0
            breakdown_lines.append(
                f"- {component.replace('_', ' ').title()}: ${amount:,.0f}/month (${annual:,.0f}/year, {percentage:.1f}%)"
            )
        breakdown_text = "\n".join(breakdown_lines)

        # Fill template
        report_content = self.templates["executive_summary"].format(
            institution_name=stakeholder_config.institution_name,
            analysis_date=datetime.now().strftime("%B %d, %Y"),
            monthly_investment=roi_metrics.monthly_investment,
            monthly_savings=roi_metrics.monthly_savings,
            net_monthly_benefit=roi_metrics.net_monthly_benefit,
            payback_days=roi_metrics.payback_days,
            roi_percentage=roi_metrics.roi_percentage,
            annual_net_benefit=roi_metrics.annual_net_benefit,
            three_year_value=roi_metrics.three_year_value,
            breakdown_text=breakdown_text,
            decision_deadline=stakeholder_config.decision_deadline,
            rollout_timeline=stakeholder_config.rollout_timeline,
        )

        return {
            "format": "report",
            "filename": f"roi_executive_summary_{stakeholder_config.institution_name.lower().replace(' ', '_')}.md",
            "content": report_content,
            "size": len(report_content),
        }

    def to_openai_schema(self) -> Dict[str, Any]:
        """Return OpenAI function schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "business_type": {
                            "type": "string",
                            "enum": [
                                "financial",
                                "healthcare",
                                "manufacturing",
                                "retail",
                                "other",
                            ],
                            "description": "Type of business or industry",
                        },
                        "analysis_data": {
                            "type": "object",
                            "description": "Core business metrics and parameters",
                            "properties": {
                                "monthly_investment": {
                                    "type": "number",
                                    "description": "Monthly investment amount",
                                },
                                "monthly_savings": {
                                    "type": "number",
                                    "description": "Expected monthly savings",
                                },
                                "team_size": {
                                    "type": "integer",
                                    "description": "Number of team members affected",
                                },
                            },
                            "required": ["monthly_investment", "monthly_savings"],
                        },
                        "stakeholder_info": {
                            "type": "object",
                            "description": "Information about stakeholders and institution",
                            "properties": {
                                "institution_name": {
                                    "type": "string",
                                    "description": "Name of the institution",
                                },
                                "email_to": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "description": "List of stakeholder email addresses",
                                },
                            },
                            "required": ["institution_name"],
                        },
                        "output_formats": {
                            "type": "array",
                            "items": {
                                "type": "string",
                                "enum": ["yaml", "csv", "spreadsheet", "report"],
                            },
                            "description": "Desired output formats",
                            "default": ["yaml", "csv", "spreadsheet", "report"],
                        },
                        "customization_level": {
                            "type": "string",
                            "enum": ["basic", "standard", "comprehensive"],
                            "description": "Level of customization",
                            "default": "comprehensive",
                        },
                    },
                    "required": ["business_type", "analysis_data", "stakeholder_info"],
                },
            },
        }
