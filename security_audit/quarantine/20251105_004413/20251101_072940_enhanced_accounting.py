"""
Enhanced Accounting System for EchoesAssistantV2
Integrates with Consent-Based License and tracks every joule of cognitive work

Version: 2.0.0
Author: Prince (Echoes AI Platform)
License: Consent-Based License v2.0
"""

import datetime
import hashlib
import json
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from legal_safeguards import (CognitiveEffortMetrics, ConsentType,
                              ProtectionLevel, get_cognitive_accounting)


class AccountingPeriod(Enum):
    """Accounting period types"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"


class ValueType(Enum):
    """Types of value creation"""

    COGNITIVE_JOULES = "cognitive_joules"
    CREATIVE_INSIGHTS = "creative_insights"
    PROBLEM_SOLUTIONS = "problem_solutions"
    INNOVATION_POTENTIAL = "innovation_potential"
    COLLABORATIVE_VALUE = "collaborative_value"


@dataclass
class TransactionRecord:
    """Individual transaction record for cognitive work"""

    transaction_id: str
    user_id: str
    session_id: str
    timestamp: str
    value_type: ValueType
    gross_value: Decimal
    tax_rate: Decimal
    platform_cut: Decimal
    net_value: Decimal
    cognitive_joules: float
    effort_metrics: Dict[str, Any]
    consent_compliance: Dict[str, Any]
    blockchain_hash: Optional[str] = None

    def calculate_blockchain_hash(self) -> str:
        """Calculate blockchain-style hash for immutability"""
        transaction_data = f"{self.transaction_id}{self.user_id}{self.timestamp}{self.gross_value}{self.net_value}"
        return hashlib.sha256(transaction_data.encode()).hexdigest()


@dataclass
class UserAccount:
    """Complete user accounting record"""

    user_id: str
    created_at: str
    total_cognitive_joules: float = 0.0
    total_gross_value: Decimal = Decimal("0.00")
    total_net_value: Decimal = Decimal("0.00")
    total_tax_paid: Decimal = Decimal("0.00")
    total_platform_fees: Decimal = Decimal("0.00")
    consent_records: List[str] = field(default_factory=list)
    transactions: List[str] = field(default_factory=list)
    value_breakdown: Dict[str, Decimal] = field(default_factory=dict)

    def update_totals(self):
        """Update total values from transactions"""
        # This would be implemented with actual transaction lookup
        pass


@dataclass
class FinancialStatement:
    """Financial statement for accounting periods"""

    period_type: AccountingPeriod
    period_start: str
    period_end: str
    total_users: int
    total_cognitive_joules: float
    total_gross_value: Decimal
    total_net_value: Decimal
    total_tax_collected: Decimal
    total_platform_revenue: Decimal
    average_joules_per_user: float
    average_value_per_user: Decimal
    value_distribution: Dict[str, Decimal]


class CognitiveAccountingSystem:
    """Enhanced accounting system for cognitive efforts with legal compliance"""

    def __init__(self, storage_path: str = "enhanced_accounting"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # Integration with legal safeguards
        self.legal_system = get_cognitive_accounting()

        # Accounting rates and policies
        self.accounting_policies = {
            "base_rate_per_joule": Decimal("0.001"),  # $0.001 per cognitive joule
            "tax_rate": Decimal("0.15"),  # 15% tax
            "platform_cut": Decimal("0.10"),  # 10% platform fee
            "creativity_bonus_multiplier": Decimal("1.5"),
            "innovation_bonus_multiplier": Decimal("2.0"),
            "collaboration_bonus_multiplier": Decimal("1.3"),
            "minimum_payout_threshold": Decimal("10.00"),  # $10 minimum payout
            "payout_frequency_days": 7,  # Weekly payouts
        }

        # User accounts
        self.user_accounts: Dict[str, UserAccount] = {}

        # Transaction records
        self.transactions: Dict[str, TransactionRecord] = {}

        # Financial statements
        self.financial_statements: Dict[str, FinancialStatement] = {}

        # Core values alignment
        self.values_accounting = {
            "integrity": {
                "description": "Transparent and honest accounting practices",
                "metrics": ["accuracy_rate", "audit_compliance", "transparency_score"],
                "weight": 0.25,
            },
            "trust": {
                "description": "Building trust through reliable compensation",
                "metrics": [
                    "payout_timeliness",
                    "value_accuracy",
                    "dispute_resolution",
                ],
                "weight": 0.20,
            },
            "creativity": {
                "description": "Valuing and rewarding creative contributions",
                "metrics": [
                    "creativity_bonus_paid",
                    "innovation_rewards",
                    "creative_attribution",
                ],
                "weight": 0.25,
            },
            "delightful_humor": {
                "description": "Promoting positive and joyful interactions",
                "metrics": [
                    "engagement_bonus",
                    "positive_interaction_rate",
                    "humor_rewards",
                ],
                "weight": 0.15,
            },
            "freedom_of_thought": {
                "description": "Protecting cognitive liberty and privacy",
                "metrics": [
                    "privacy_compliance",
                    "thought_protection",
                    "cognitive_rights",
                ],
                "weight": 0.15,
            },
        }

        # Load existing data
        self._load_data()

    def create_user_account(
        self, user_id: str, consent_type: ConsentType = ConsentType.PERSONAL_DEVELOPMENT
    ) -> UserAccount:
        """Create a new user account with consent integration"""

        if user_id in self.user_accounts:
            return self.user_accounts[user_id]

        # Create consent record through legal system
        consent = self.legal_system.create_consent_record(
            user_id=user_id,
            consent_type=consent_type,
            purpose_description="Cognitive effort accounting and value compensation",
            scope_of_use="accounting, compensation, analytics",
            duration="perpetual",
            protection_level=ProtectionLevel.ENHANCED,
        )

        # Create user account
        account = UserAccount(
            user_id=user_id,
            created_at=datetime.datetime.now().isoformat(),
            consent_records=[consent.consent_id],
        )

        self.user_accounts[user_id] = account
        self._save_data()

        return account

    def record_cognitive_transaction(
        self,
        user_id: str,
        session_id: str,
        effort_metrics: CognitiveEffortMetrics,
        value_type: ValueType = ValueType.COGNITIVE_JOULES,
    ) -> TransactionRecord:
        """Record a cognitive work transaction with full accounting"""

        # Ensure user account exists
        if user_id not in self.user_accounts:
            self.create_user_account(user_id)

        # Verify consent compliance
        consent_check = self.legal_system.verify_consent_compliance(
            user_id=user_id, action="cognitive_accounting", scope="accounting"
        )

        if not consent_check["compliant"]:
            raise ValueError(f"Consent compliance failed: {consent_check['reason']}")

        # Calculate gross value based on effort metrics
        base_value = (
            Decimal(str(effort_metrics.joules_of_work))
            * self.accounting_policies["base_rate_per_joule"]
        )

        # Apply bonuses based on value type and metrics
        bonus_multiplier = Decimal("1.0")

        if value_type == ValueType.CREATIVE_INSIGHTS:
            bonus_multiplier *= self.accounting_policies["creativity_bonus_multiplier"]
            bonus_multiplier *= Decimal(str(1 + effort_metrics.creativity_score))

        elif value_type == ValueType.INNOVATION_POTENTIAL:
            bonus_multiplier *= self.accounting_policies["innovation_bonus_multiplier"]
            bonus_multiplier *= Decimal(str(1 + effort_metrics.innovation_potential))

        elif value_type == ValueType.COLLABORATIVE_VALUE:
            bonus_multiplier *= self.accounting_policies[
                "collaboration_bonus_multiplier"
            ]

        gross_value = base_value * bonus_multiplier

        # Calculate deductions
        tax_amount = gross_value * self.accounting_policies["tax_rate"]
        platform_fee = gross_value * self.accounting_policies["platform_cut"]
        net_value = gross_value - tax_amount - platform_fee

        # Create transaction record
        transaction_id = f"tx_{user_id}_{datetime.datetime.now().isoformat()}"
        transaction = TransactionRecord(
            transaction_id=transaction_id,
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.datetime.now().isoformat(),
            value_type=value_type,
            gross_value=gross_value,
            tax_rate=self.accounting_policies["tax_rate"],
            platform_cut=self.accounting_policies["platform_cut"],
            net_value=net_value,
            cognitive_joules=effort_metrics.joules_of_work,
            effort_metrics=asdict(effort_metrics),
            consent_compliance=consent_check,
        )

        # Calculate blockchain hash for immutability
        transaction.blockchain_hash = transaction.calculate_blockchain_hash()

        # Store transaction
        self.transactions[transaction_id] = transaction

        # Update user account
        user_account = self.user_accounts[user_id]
        user_account.transactions.append(transaction_id)
        user_account.total_cognitive_joules += effort_metrics.joules_of_work
        user_account.total_gross_value += gross_value
        user_account.total_net_value += net_value
        user_account.total_tax_paid += tax_amount
        user_account.total_platform_fees += platform_fee

        # Update value breakdown
        value_type_str = value_type.value
        if value_type_str not in user_account.value_breakdown:
            user_account.value_breakdown[value_type_str] = Decimal("0.00")
        user_account.value_breakdown[value_type_str] += net_value

        self._save_data()

        return transaction

    def generate_user_statement(
        self, user_id: str, period_start: str, period_end: str
    ) -> Dict[str, Any]:
        """Generate detailed user financial statement"""

        if user_id not in self.user_accounts:
            return {"error": "User account not found"}

        user_account = self.user_accounts[user_id]

        # Filter transactions for period
        period_transactions = [
            tx
            for tx in self.transactions.values()
            if (tx.user_id == user_id and period_start <= tx.timestamp <= period_end)
        ]

        if not period_transactions:
            return {
                "user_id": user_id,
                "period_start": period_start,
                "period_end": period_end,
                "message": "No transactions found for period",
                "total_value": Decimal("0.00"),
            }

        # Calculate period totals
        period_gross = sum(tx.gross_value for tx in period_transactions)
        period_net = sum(tx.net_value for tx in period_transactions)
        period_tax = sum(tx.gross_value * tx.tax_rate for tx in period_transactions)
        period_fees = sum(
            tx.gross_value * tx.platform_cut for tx in period_transactions
        )
        period_joules = sum(tx.cognitive_joules for tx in period_transactions)

        # Value breakdown
        value_breakdown = {}
        for tx in period_transactions:
            value_type = tx.value_type.value
            if value_type not in value_breakdown:
                value_breakdown[value_type] = Decimal("0.00")
            value_breakdown[value_type] += tx.net_value

        # Values alignment score
        values_score = self._calculate_values_alignment_score(period_transactions)

        return {
            "user_id": user_id,
            "period_start": period_start,
            "period_end": period_end,
            "summary": {
                "total_transactions": len(period_transactions),
                "total_cognitive_joules": period_joules,
                "gross_value": float(period_gross),
                "tax_amount": float(period_tax),
                "platform_fees": float(period_fees),
                "net_value": float(period_net),
                "average_value_per_transaction": float(
                    period_net / len(period_transactions)
                ),
            },
            "value_breakdown": {k: float(v) for k, v in value_breakdown.items()},
            "values_alignment": values_score,
            "consent_compliance": "All transactions compliant",
            "transaction_ids": [tx.transaction_id for tx in period_transactions],
        }

    def generate_financial_statement(
        self, period_type: AccountingPeriod, period_start: str, period_end: str
    ) -> FinancialStatement:
        """Generate comprehensive financial statement for period"""

        # Filter transactions for period
        period_transactions = [
            tx
            for tx in self.transactions.values()
            if period_start <= tx.timestamp <= period_end
        ]

        if not period_transactions:
            return FinancialStatement(
                period_type=period_type,
                period_start=period_start,
                period_end=period_end,
                total_users=0,
                total_cognitive_joules=0.0,
                total_gross_value=Decimal("0.00"),
                total_net_value=Decimal("0.00"),
                total_tax_collected=Decimal("0.00"),
                total_platform_revenue=Decimal("0.00"),
                average_joules_per_user=0.0,
                average_value_per_user=Decimal("0.00"),
                value_distribution={},
            )

        # Calculate totals
        unique_users = len(set(tx.user_id for tx in period_transactions))
        total_joules = sum(tx.cognitive_joules for tx in period_transactions)
        total_gross = sum(tx.gross_value for tx in period_transactions)
        total_net = sum(tx.net_value for tx in period_transactions)
        total_tax = sum(tx.gross_value * tx.tax_rate for tx in period_transactions)
        total_fees = sum(tx.gross_value * tx.platform_cut for tx in period_transactions)

        # Value distribution
        value_distribution = {}
        for tx in period_transactions:
            value_type = tx.value_type.value
            if value_type not in value_distribution:
                value_distribution[value_type] = Decimal("0.00")
            value_distribution[value_type] += tx.net_value

        statement = FinancialStatement(
            period_type=period_type,
            period_start=period_start,
            period_end=period_end,
            total_users=unique_users,
            total_cognitive_joules=total_joules,
            total_gross_value=total_gross,
            total_net_value=total_net,
            total_tax_collected=total_tax,
            total_platform_revenue=total_fees,
            average_joules_per_user=total_joules / unique_users
            if unique_users > 0
            else 0.0,
            average_value_per_user=total_net / unique_users
            if unique_users > 0
            else Decimal("0.00"),
            value_distribution=value_distribution,
        )

        # Store statement
        statement_id = f"stmt_{period_type.value}_{period_start}_{period_end}"
        self.financial_statements[statement_id] = statement
        self._save_data()

        return statement

    def calculate_payout_eligibility(self, user_id: str) -> Dict[str, Any]:
        """Calculate if user is eligible for payout"""

        if user_id not in self.user_accounts:
            return {"eligible": False, "reason": "User account not found"}

        user_account = self.user_accounts[user_id]

        # Check minimum threshold
        if (
            user_account.total_net_value
            < self.accounting_policies["minimum_payout_threshold"]
        ):
            return {
                "eligible": False,
                "reason": f"Below minimum payout threshold of ${self.accounting_policies['minimum_payout_threshold']}",
                "current_balance": float(user_account.total_net_value),
                "threshold_needed": float(
                    self.accounting_policies["minimum_payout_threshold"]
                    - user_account.total_net_value
                ),
            }

        # Check consent compliance
        consent_check = self.legal_system.verify_consent_compliance(
            user_id=user_id, action="payout", scope="compensation"
        )

        if not consent_check["compliant"]:
            return {
                "eligible": False,
                "reason": f"Consent compliance issue: {consent_check['reason']}",
            }

        return {
            "eligible": True,
            "payout_amount": float(user_account.total_net_value),
            "cognitive_joules_earned": user_account.total_cognitive_joules,
            "last_transaction": max(user_account.transactions)
            if user_account.transactions
            else None,
        }

    def _calculate_values_alignment_score(
        self, transactions: List[TransactionRecord]
    ) -> Dict[str, Any]:
        """Calculate alignment with core values"""

        total_score = 0.0
        value_scores = {}

        for value_name, value_config in self.values_accounting.items():
            # Simplified scoring based on transaction types and metrics
            score = 0.0

            if value_name == "integrity":
                # Score based on consent compliance and transparency
                compliant_tx = len(
                    [
                        tx
                        for tx in transactions
                        if tx.consent_compliance.get("compliant", False)
                    ]
                )
                score = (compliant_tx / len(transactions)) * 100 if transactions else 0

            elif value_name == "creativity":
                # Score based on creative insights and innovation
                creative_tx = len(
                    [
                        tx
                        for tx in transactions
                        if tx.value_type
                        in [ValueType.CREATIVE_INSIGHTS, ValueType.INNOVATION_POTENTIAL]
                    ]
                )
                score = (creative_tx / len(transactions)) * 100 if transactions else 0

            elif value_name == "trust":
                # Score based on timely and accurate compensation
                score = 95.0  # Assume high trust if system is working

            elif value_name == "delightful_humor":
                # Score based on engagement and positive interactions
                score = 85.0  # Assume good user experience

            elif value_name == "freedom_of_thought":
                # Score based on cognitive rights protection
                score = 100.0  # Perfect score for cognitive liberty

            value_scores[value_name] = score
            total_score += score * value_config["weight"]

        return {
            "overall_score": total_score,
            "value_scores": value_scores,
            "compliance_status": "Excellent"
            if total_score >= 90
            else "Good"
            if total_score >= 75
            else "Needs Improvement",
        }

    def export_accounting_data(self, format_type: str = "csv") -> str:
        """Export accounting data for compliance and analysis"""

        # Create comprehensive dataframe
        transaction_data = []
        for tx in self.transactions.values():
            transaction_data.append(
                {
                    "transaction_id": tx.transaction_id,
                    "user_id": tx.user_id,
                    "timestamp": tx.timestamp,
                    "value_type": tx.value_type.value,
                    "cognitive_joules": tx.cognitive_joules,
                    "gross_value": float(tx.gross_value),
                    "tax_rate": float(tx.tax_rate),
                    "platform_cut": float(tx.platform_cut),
                    "net_value": float(tx.net_value),
                    "blockchain_hash": tx.blockchain_hash,
                    "consent_compliant": tx.consent_compliance.get("compliant", False),
                }
            )

        df = pd.DataFrame(transaction_data)

        # Export based on format
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        if format_type.lower() == "csv":
            filename = f"accounting_export_{timestamp}.csv"
            filepath = self.storage_path / filename
            df.to_csv(filepath, index=False)

        elif format_type.lower() == "json":
            filename = f"accounting_export_{timestamp}.json"
            filepath = self.storage_path / filename
            df.to_json(filepath, orient="records", indent=2)

        elif format_type.lower() == "excel":
            filename = f"accounting_export_{timestamp}.xlsx"
            filepath = self.storage_path / filename
            df.to_excel(filepath, index=False)

        return str(filepath)

    def _load_data(self):
        """Load existing accounting data"""
        try:
            # Load user accounts
            accounts_file = self.storage_path / "user_accounts.json"
            if accounts_file.exists():
                with open(accounts_file, "r", encoding="utf-8") as f:
                    accounts_data = json.load(f)
                    for user_id, account_dict in accounts_data.items():
                        # Convert Decimal fields back
                        for field in [
                            "total_gross_value",
                            "total_net_value",
                            "total_tax_paid",
                            "total_platform_fees",
                        ]:
                            if field in account_dict:
                                account_dict[field] = Decimal(str(account_dict[field]))
                        for key, value in account_dict.get(
                            "value_breakdown", {}
                        ).items():
                            account_dict["value_breakdown"][key] = Decimal(str(value))

                        self.user_accounts[user_id] = UserAccount(**account_dict)

            # Load transactions
            transactions_file = self.storage_path / "transactions.json"
            if transactions_file.exists():
                with open(transactions_file, "r", encoding="utf-8") as f:
                    transactions_data = json.load(f)
                    for tx_id, tx_dict in transactions_data.items():
                        # Convert Decimal fields and enums
                        for field in ["gross_value", "net_value"]:
                            if field in tx_dict:
                                tx_dict[field] = Decimal(str(tx_dict[field]))
                        tx_dict["tax_rate"] = Decimal(str(tx_dict["tax_rate"]))
                        tx_dict["platform_cut"] = Decimal(str(tx_dict["platform_cut"]))
                        tx_dict["value_type"] = ValueType(tx_dict["value_type"])

                        self.transactions[tx_id] = TransactionRecord(**tx_dict)

            # Load financial statements
            statements_file = self.storage_path / "financial_statements.json"
            if statements_file.exists():
                with open(statements_file, "r", encoding="utf-8") as f:
                    statements_data = json.load(f)
                    for stmt_id, stmt_dict in statements_data.items():
                        # Convert Decimal fields and enums
                        for field in [
                            "total_gross_value",
                            "total_net_value",
                            "total_tax_collected",
                            "total_platform_revenue",
                            "average_value_per_user",
                        ]:
                            if field in stmt_dict:
                                stmt_dict[field] = Decimal(str(stmt_dict[field]))
                        for key, value in stmt_dict.get(
                            "value_distribution", {}
                        ).items():
                            stmt_dict["value_distribution"][key] = Decimal(str(value))
                        stmt_dict["period_type"] = AccountingPeriod(
                            stmt_dict["period_type"]
                        )

                        self.financial_statements[stmt_id] = FinancialStatement(
                            **stmt_dict
                        )

            print(
                f"✓ Enhanced accounting loaded: {len(self.user_accounts)} users, {len(self.transactions)} transactions"
            )

        except Exception as e:
            print(f"Warning: Could not load enhanced accounting data: {e}")

    def _save_data(self):
        """Save accounting data"""
        try:
            # Save user accounts
            accounts_file = self.storage_path / "user_accounts.json"
            accounts_data = {
                user_id: asdict(account)
                for user_id, account in self.user_accounts.items()
            }
            with open(accounts_file, "w", encoding="utf-8") as f:
                json.dump(accounts_data, f, indent=2, ensure_ascii=False, default=str)

            # Save transactions
            transactions_file = self.storage_path / "transactions.json"
            transactions_data = {
                tx_id: asdict(tx) for tx_id, tx in self.transactions.items()
            }
            with open(transactions_file, "w", encoding="utf-8") as f:
                json.dump(
                    transactions_data, f, indent=2, ensure_ascii=False, default=str
                )

            # Save financial statements
            statements_file = self.storage_path / "financial_statements.json"
            statements_data = {
                stmt_id: asdict(stmt)
                for stmt_id, stmt in self.financial_statements.items()
            }
            with open(statements_file, "w", encoding="utf-8") as f:
                json.dump(statements_data, f, indent=2, ensure_ascii=False, default=str)

        except Exception as e:
            print(f"Warning: Could not save enhanced accounting data: {e}")


# Global enhanced accounting system
_enhanced_accounting = None


def get_enhanced_accounting() -> CognitiveAccountingSystem:
    """Get or create the global enhanced accounting system"""
    global _enhanced_accounting
    if _enhanced_accounting is None:
        _enhanced_accounting = CognitiveAccountingSystem()
    return _enhanced_accounting
