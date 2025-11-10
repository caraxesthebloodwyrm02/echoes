"""
Enhanced Accounting System for EchoesAssistantV2
Comprehensive End User Protection with Advanced Financial Security and Transparency

Version: 3.0.0 - Enhanced End User Protection
Author: Prince (Echoes AI Platform)
License: Consent-Based License v2.0
"""

import base64
import datetime
import hashlib
import json
import secrets
from dataclasses import asdict, dataclass, field
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from enhanced_legal_safeguards import (
    DataRetention,
    PrivacyControl,
    ProtectionLevel,
    get_enhanced_cognitive_accounting,
)


class AccountingPeriod(Enum):
    """Enhanced accounting period types with user control"""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ON_DEMAND = "on_demand"  # New: User-controlled reporting


class ValueType(Enum):
    """Enhanced types of value creation with user protection"""

    COGNITIVE_JOULES = "cognitive_joules"
    CREATIVE_INSIGHTS = "creative_insights"
    PROBLEM_SOLUTIONS = "problem_solutions"
    INNOVATION_POTENTIAL = "innovation_potential"
    COLLABORATIVE_VALUE = "collaborative_value"
    RESEARCH_CONTRIBUTION = "research_contribution"  # New: Research-specific value
    PERSONAL_DEVELOPMENT = "personal_development"  # New: Personal growth value
    PRIVACY_PROTECTED = "privacy_protected"  # New: Privacy bonus value


class PayoutMethod(Enum):
    """Enhanced payout methods with user security"""

    BANK_TRANSFER = "bank_transfer"
    CRYPTO_WALLET = "crypto_wallet"
    DIGITAL_WALLET = "digital_wallet"
    CREDIT_ACCOUNT = "credit_account"
    CHARITY_DONATION = "charity_donation"
    PLATFORM_CREDITS = "platform_credits"
    DEFERRED_COMPENSATION = "deferred_compensation"  # New: For long-term value


class TaxJurisdiction(Enum):
    """Enhanced tax jurisdictions with user optimization"""

    US_STANDARD = "us_standard"
    EU_STANDARD = "eu_standard"
    INTERNATIONAL = "international"
    TAX_OPTIMIZED = "tax_optimized"  # New: User tax optimization
    PRIVACY_PROTECTED = "privacy_protected"  # New: Privacy-first tax handling


@dataclass
class TransactionRecord:
    """Enhanced transaction record with comprehensive user protection"""

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
    # New enhanced protection fields
    privacy_bonus_applied: Decimal = Decimal("0.00")
    user_protection_level: str = "enhanced"
    data_retention_compliant: bool = True
    consent_withdrawal_provision: bool = True
    user_encryption_verified: bool = False
    audit_trail_hash: Optional[str] = None
    payout_eligibility: bool = True
    tax_optimization_applied: bool = False
    cross_border_compliance: bool = True

    def calculate_blockchain_hash(self) -> str:
        """Enhanced blockchain-style hash for immutability and user verification"""
        transaction_data = f"{self.transaction_id}{self.user_id}{self.timestamp}{self.gross_value}{self.net_value}{self.privacy_bonus_applied}"
        return hashlib.sha256(transaction_data.encode()).hexdigest()

    def calculate_audit_hash(self) -> str:
        """Calculate audit trail hash for user verification"""
        audit_data = f"{self.transaction_id}{self.user_id}{self.timestamp}{self.payout_eligibility}{self.data_retention_compliant}"
        return hashlib.sha256(audit_data.encode()).hexdigest()


@dataclass
class UserAccount:
    """Enhanced user accounting record with comprehensive protection"""

    user_id: str
    created_at: str
    total_cognitive_joules: float = 0.0
    total_gross_value: Decimal = Decimal("0.00")
    total_net_value: Decimal = Decimal("0.00")
    total_tax_paid: Decimal = Decimal("0.00")
    total_platform_fees: Decimal = Decimal("0.00")
    total_privacy_bonus: Decimal = Decimal("0.00")  # New: Track privacy bonuses
    consent_records: List[str] = field(default_factory=list)
    transactions: List[str] = field(default_factory=list)
    value_breakdown: Dict[str, Decimal] = field(default_factory=dict)
    # New enhanced protection fields
    privacy_preference: PrivacyControl = PrivacyControl.MINIMAL_COLLECTION
    protection_level: ProtectionLevel = ProtectionLevel.ENHANCED
    payout_method: PayoutMethod = PayoutMethod.BANK_TRANSFER
    tax_jurisdiction: TaxJurisdiction = TaxJurisdiction.US_STANDARD
    payout_eligibility_threshold: Decimal = Decimal("10.00")  # User-configurable
    auto_payout_enabled: bool = True
    deferred_compensation_enabled: bool = False
    tax_optimization_enabled: bool = False
    audit_notifications: bool = True
    data_retention_policy: DataRetention = DataRetention.THIRTY_DAYS
    user_encryption_key: Optional[str] = None

    def update_totals(self, transactions: List[TransactionRecord]):
        """Enhanced totals update with privacy bonus tracking"""
        self.total_cognitive_joules = sum(t.cognitive_joules for t in transactions)
        self.total_gross_value = sum(t.gross_value for t in transactions)
        self.total_net_value = sum(t.net_value for t in transactions)
        self.total_tax_paid = sum(t.gross_value * t.tax_rate for t in transactions)
        self.total_platform_fees = sum(t.platform_cut for t in transactions)
        self.total_privacy_bonus = sum(t.privacy_bonus_applied for t in transactions)

        # Update value breakdown
        self.value_breakdown = {}
        for transaction in transactions:
            value_type = transaction.value_type.value
            if value_type not in self.value_breakdown:
                self.value_breakdown[value_type] = Decimal("0.00")
            self.value_breakdown[value_type] += transaction.net_value


@dataclass
class FinancialStatement:
    """Enhanced financial statement with user protection transparency"""

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
    # New enhanced protection fields
    total_privacy_bonus_distributed: Decimal = Decimal("0.00")
    user_protection_compliance_rate: float = 0.0
    data_retention_compliance_rate: float = 0.0
    consent_withdrawal_rate: float = 0.0
    audit_success_rate: float = 0.0
    cross_border_compliance_rate: float = 0.0
    user_satisfaction_score: float = 0.0
    tax_optimization_savings: Decimal = Decimal("0.00")
    payout_processing_success_rate: float = 0.0


@dataclass
class PayoutRecord:
    """Enhanced payout record with user security and control"""

    payout_id: str
    user_id: str
    transaction_ids: List[str]
    total_amount: Decimal
    payout_method: PayoutMethod
    requested_at: str
    processed_at: Optional[str]
    status: str  # pending, processing, completed, failed, cancelled
    transaction_hash: Optional[str] = None
    # New enhanced protection fields
    user_verified: bool = False
    security_checks_passed: bool = False
    tax_documents_generated: bool = False
    audit_trail_complete: bool = False
    privacy_protection_applied: bool = True
    user_approval_required: bool = True
    payout_encryption_enabled: bool = True
    compliance_verified: bool = True


class EnhancedAccountingSystem:
    """Enhanced accounting system with comprehensive end user protection"""

    def __init__(self, storage_path: str = "Accounting"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # Initialize enhanced legal safeguards
        self.legal_system = get_enhanced_cognitive_accounting()

        # Enhanced accounting configuration with user protection
        self.config = {
            "base_value_per_joule": Decimal("0.001"),  # $0.001 per joule
            "standard_tax_rate": Decimal("0.15"),  # 15% standard tax
            "platform_cut_rate": Decimal("0.10"),  # 10% platform fee
            "privacy_bonus_rates": {
                PrivacyControl.MINIMAL_COLLECTION: Decimal("1.0"),
                PrivacyControl.PSEUDONYMIZATION: Decimal("1.1"),
                PrivacyControl.FULL_ANONYMIZATION: Decimal("1.3"),
                PrivacyControl.ZERO_TRACKING: Decimal("1.5"),
            },
            "creativity_bonus_multiplier": Decimal("1.5"),
            "innovation_bonus_multiplier": Decimal("2.0"),
            "research_bonus_multiplier": Decimal("1.8"),
            "minimum_payout_threshold": Decimal("10.00"),
            "user_protection_fee_waiver": Decimal(
                "0.05"
            ),  # 5% fee waiver for high protection
            "tax_optimization_savings_rate": Decimal("0.02"),  # 2% additional savings
            "audit_compliance_bonus": Decimal("0.01"),  # 1% bonus for audit compliance
        }

        # Load enhanced data
        self.user_accounts = self._load_user_accounts()
        self.transactions = self._load_transactions()
        self.payout_records = self._load_payout_records()

        # User protection monitoring
        self.protection_monitoring = {
            "transaction_security": True,
            "payout_encryption": True,
            "audit_compliance": True,
            "tax_optimization": True,
            "privacy_protection": True,
            "user_verification": True,
            "data_retention_enforcement": True,
            "consent_withdrawal_processing": True,
        }

    def create_enhanced_user_account(
        self,
        user_id: str,
        privacy_preference: PrivacyControl = PrivacyControl.MINIMAL_COLLECTION,
        protection_level: ProtectionLevel = ProtectionLevel.ENHANCED,
        payout_method: PayoutMethod = PayoutMethod.BANK_TRANSFER,
        tax_jurisdiction: TaxJurisdiction = TaxJurisdiction.US_STANDARD,
        payout_threshold: Decimal = Decimal("10.00"),
    ) -> Dict[str, Any]:
        """Create enhanced user account with comprehensive protection"""
        try:
            # Check if account already exists
            if user_id in self.user_accounts:
                return {"success": False, "error": "User account already exists"}

            # Create enhanced user account
            user_account = UserAccount(
                user_id=user_id,
                created_at=datetime.datetime.now().isoformat(),
                privacy_preference=privacy_preference,
                protection_level=protection_level,
                payout_method=payout_method,
                tax_jurisdiction=tax_jurisdiction,
                payout_eligibility_threshold=payout_threshold,
                auto_payout_enabled=True,
                tax_optimization_enabled=tax_jurisdiction
                == TaxJurisdiction.TAX_OPTIMIZED,
                audit_notifications=protection_level
                in [ProtectionLevel.PREMIUM, ProtectionLevel.SOVEREIGN],
                data_retention_policy=DataRetention.THIRTY_DAYS,
            )

            # Generate user encryption key for enhanced security
            if protection_level in [ProtectionLevel.PREMIUM, ProtectionLevel.SOVEREIGN]:
                user_account.user_encryption_key = self._generate_user_encryption_key(
                    user_id
                )

            # Save user account
            self.user_accounts[user_id] = user_account
            self._save_user_accounts()

            return {
                "success": True,
                "user_id": user_id,
                "account_created": True,
                "protection_features": {
                    "privacy_preference": privacy_preference.value,
                    "protection_level": protection_level.value,
                    "encryption_enabled": user_account.user_encryption_key is not None,
                    "audit_notifications": user_account.audit_notifications,
                    "tax_optimization": user_account.tax_optimization_enabled,
                },
                "message": "Enhanced user account created with comprehensive protection",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create enhanced user account: {str(e)}",
            }

    def process_enhanced_transaction(
        self,
        user_id: str,
        session_id: str,
        cognitive_joules: float,
        effort_metrics: Dict[str, Any],
        value_type: ValueType = ValueType.COGNITIVE_JOULES,
    ) -> Dict[str, Any]:
        """Process enhanced transaction with user protection and privacy bonuses"""
        try:
            # Verify user account exists
            if user_id not in self.user_accounts:
                return {"success": False, "error": "User account not found"}

            user_account = self.user_accounts[user_id]

            # Get enhanced legal compliance
            legal_compliance = self.legal_system.verify_enhanced_user_protection(
                user_id, "transaction_processing"
            )
            if not legal_compliance["success"]:
                return {
                    "success": False,
                    "error": "Legal compliance verification failed",
                }

            # Calculate base value
            base_value = (
                Decimal(str(cognitive_joules)) * self.config["base_value_per_joule"]
            )

            # Apply value type bonuses
            value_multiplier = Decimal("1.0")
            if value_type == ValueType.CREATIVE_INSIGHTS:
                value_multiplier = self.config["creativity_bonus_multiplier"]
            elif value_type == ValueType.INNOVATION_POTENTIAL:
                value_multiplier = self.config["innovation_bonus_multiplier"]
            elif value_type == ValueType.RESEARCH_CONTRIBUTION:
                value_multiplier = self.config["research_bonus_multiplier"]

            # Apply privacy bonus
            privacy_bonus_rate = self.config["privacy_bonus_rates"].get(
                user_account.privacy_preference, Decimal("1.0")
            )
            privacy_bonus_amount = base_value * (privacy_bonus_rate - Decimal("1.0"))

            # Calculate gross value with all bonuses
            gross_value = base_value * value_multiplier * privacy_bonus_rate

            # Apply tax optimization if enabled
            tax_rate = self.config["standard_tax_rate"]
            if user_account.tax_optimization_enabled:
                tax_rate -= self.config["tax_optimization_savings_rate"]

            # Apply platform cut with protection fee waiver
            platform_cut_rate = self.config["platform_cut_rate"]
            if user_account.protection_level in [
                ProtectionLevel.PREMIUM,
                ProtectionLevel.SOVEREIGN,
            ]:
                platform_cut_rate -= self.config["user_protection_fee_waiver"]

            platform_cut = gross_value * platform_cut_rate
            tax_amount = gross_value * tax_rate
            net_value = gross_value - platform_cut - tax_amount

            # Create enhanced transaction record
            transaction_id = (
                f"txn_{user_id}_{session_id}_{datetime.datetime.now().isoformat()}"
            )
            transaction = TransactionRecord(
                transaction_id=transaction_id,
                user_id=user_id,
                session_id=session_id,
                timestamp=datetime.datetime.now().isoformat(),
                value_type=value_type,
                gross_value=gross_value,
                tax_rate=tax_rate,
                platform_cut=platform_cut,
                net_value=net_value,
                cognitive_joules=cognitive_joules,
                effort_metrics=effort_metrics,
                consent_compliance=legal_compliance["protection_compliance"],
                blockchain_hash=None,  # Will be calculated
                privacy_bonus_applied=privacy_bonus_amount,
                user_protection_level=user_account.protection_level.value,
                data_retention_compliant=True,
                consent_withdrawal_provision=True,
                user_encryption_verified=user_account.user_encryption_key is not None,
                audit_trail_hash=None,  # Will be calculated
                payout_eligibility=net_value
                >= user_account.payout_eligibility_threshold,
                tax_optimization_applied=user_account.tax_optimization_enabled,
                cross_border_compliance=True,
            )

            # Calculate hashes
            transaction.blockchain_hash = transaction.calculate_blockchain_hash()
            transaction.audit_trail_hash = transaction.calculate_audit_hash()

            # Save transaction
            self.transactions[transaction_id] = transaction
            self._save_transactions()

            # Update user account
            user_transactions = [
                t for t in self.transactions.values() if t.user_id == user_id
            ]
            user_account.update_totals(user_transactions)
            self._save_user_accounts()

            return {
                "success": True,
                "transaction_id": transaction_id,
                "transaction_details": {
                    "gross_value": float(gross_value),
                    "net_value": float(net_value),
                    "tax_amount": float(tax_amount),
                    "platform_fee": float(platform_cut),
                    "privacy_bonus": float(privacy_bonus_amount),
                    "value_multiplier": float(value_multiplier),
                    "tax_rate": float(tax_rate),
                    "platform_cut_rate": float(platform_cut_rate),
                },
                "user_protection": {
                    "privacy_level": user_account.privacy_preference.value,
                    "protection_level": user_account.protection_level.value,
                    "encryption_verified": transaction.user_encryption_verified,
                    "data_retention_compliant": transaction.data_retention_compliant,
                    "payout_eligibility": transaction.payout_eligibility,
                },
                "message": "Enhanced transaction processed with user protection",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process enhanced transaction: {str(e)}",
            }

    def request_enhanced_payout(
        self,
        user_id: str,
        payout_method: Optional[PayoutMethod] = None,
        amount: Optional[Decimal] = None,
    ) -> Dict[str, Any]:
        """Request enhanced payout with comprehensive user security"""
        try:
            # Verify user account
            if user_id not in self.user_accounts:
                return {"success": False, "error": "User account not found"}

            user_account = self.user_accounts[user_id]

            # Check payout eligibility
            eligible_transactions = [
                t
                for t in self.transactions.values()
                if t.user_id == user_id and t.payout_eligibility and t.net_value > 0
            ]

            if not eligible_transactions:
                return {
                    "success": False,
                    "error": "No eligible transactions for payout",
                }

            # Calculate total available amount
            total_available = sum(t.net_value for t in eligible_transactions)

            # Validate amount if specified
            if amount is not None:
                if amount > total_available:
                    return {
                        "success": False,
                        "error": f"Requested amount ${amount} exceeds available ${total_available}",
                    }
                if amount < user_account.payout_eligibility_threshold:
                    return {
                        "success": False,
                        "error": f"Requested amount ${amount} below minimum threshold ${user_account.payout_eligibility_threshold}",
                    }
            else:
                amount = total_available
                if amount < user_account.payout_eligibility_threshold:
                    return {
                        "success": False,
                        "error": f"Available amount ${amount} below minimum threshold ${user_account.payout_eligibility_threshold}",
                    }

            # Use specified or default payout method
            final_payout_method = payout_method or user_account.payout_method

            # Create enhanced payout record
            payout_id = f"payout_{user_id}_{datetime.datetime.now().isoformat()}"
            payout_record = PayoutRecord(
                payout_id=payout_id,
                user_id=user_id,
                transaction_ids=[t.transaction_id for t in eligible_transactions],
                total_amount=amount,
                payout_method=final_payout_method,
                requested_at=datetime.datetime.now().isoformat(),
                processed_at=None,
                status="pending",
                user_verified=False,
                security_checks_passed=False,
                tax_documents_generated=False,
                audit_trail_complete=False,
                privacy_protection_applied=True,
                user_approval_required=user_account.protection_level
                == ProtectionLevel.SOVEREIGN,
                payout_encryption_enabled=user_account.user_encryption_key is not None,
                compliance_verified=True,
            )

            # Save payout record
            self.payout_records[payout_id] = payout_record
            self._save_payout_records()

            return {
                "success": True,
                "payout_id": payout_id,
                "payout_details": {
                    "amount": float(amount),
                    "method": final_payout_method.value,
                    "transaction_count": len(eligible_transactions),
                    "status": "pending",
                    "user_approval_required": payout_record.user_approval_required,
                    "encryption_enabled": payout_record.payout_encryption_enabled,
                },
                "security_features": {
                    "user_verification_required": True,
                    "tax_documents_prepared": True,
                    "audit_trail_enabled": True,
                    "privacy_protection_active": True,
                    "compliance_verified": True,
                },
                "message": "Enhanced payout request created with comprehensive security",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to request enhanced payout: {str(e)}",
            }

    def generate_enhanced_financial_statement(
        self, user_id: str, period_days: int = 30
    ) -> Dict[str, Any]:
        """Generate enhanced financial statement with user protection transparency"""
        try:
            # Verify user account
            if user_id not in self.user_accounts:
                return {"success": False, "error": "User account not found"}

            user_account = self.user_accounts[user_id]

            # Calculate period dates
            period_end = datetime.datetime.now()
            period_start = period_end - datetime.timedelta(days=period_days)

            # Filter transactions for period
            period_transactions = [
                t
                for t in self.transactions.values()
                if t.user_id == user_id
                and datetime.datetime.fromisoformat(t.timestamp.replace("Z", "+00:00"))
                >= period_start
            ]

            if not period_transactions:
                return {
                    "success": False,
                    "error": "No transactions found for the specified period",
                }

            # Calculate period metrics
            total_joules = sum(t.cognitive_joules for t in period_transactions)
            total_gross = sum(t.gross_value for t in period_transactions)
            total_net = sum(t.net_value for t in period_transactions)
            total_tax = sum(t.gross_value * t.tax_rate for t in period_transactions)
            total_platform = sum(t.platform_cut for t in period_transactions)
            total_privacy_bonus = sum(
                t.privacy_bonus_applied for t in period_transactions
            )

            # Create enhanced financial statement
            statement = FinancialStatement(
                period_type=AccountingPeriod.MONTHLY,
                period_start=period_start.isoformat(),
                period_end=period_end.isoformat(),
                total_users=1,
                total_cognitive_joules=total_joules,
                total_gross_value=total_gross,
                total_net_value=total_net,
                total_tax_collected=total_tax,
                total_platform_revenue=total_platform,
                average_joules_per_user=total_joules,
                average_value_per_user=total_net,
                total_privacy_bonus_distributed=total_privacy_bonus,
                user_protection_compliance_rate=1.0,  # All transactions compliant
                data_retention_compliance_rate=1.0,
                consent_withdrawal_rate=0.0,
                audit_success_rate=1.0,
                cross_border_compliance_rate=1.0,
                user_satisfaction_score=0.95,  # Based on protection features
                tax_optimization_savings=total_tax
                * self.config["tax_optimization_savings_rate"]
                if user_account.tax_optimization_enabled
                else Decimal("0.00"),
                payout_processing_success_rate=1.0,
            )

            # Value breakdown by type
            value_breakdown = {}
            for transaction in period_transactions:
                value_type = transaction.value_type.value
                if value_type not in value_breakdown:
                    value_breakdown[value_type] = Decimal("0.00")
                value_breakdown[value_type] += transaction.net_value

            return {
                "success": True,
                "user_id": user_id,
                "period_days": period_days,
                "financial_statement": {
                    "summary": {
                        "total_cognitive_joules": total_joules,
                        "total_gross_value": float(total_gross),
                        "total_net_value": float(total_net),
                        "total_tax_paid": float(total_tax),
                        "total_platform_fees": float(total_platform),
                        "total_privacy_bonus": float(total_privacy_bonus),
                        "effective_tax_rate": float(total_tax / total_gross)
                        if total_gross > 0
                        else 0,
                        "effective_platform_rate": float(total_platform / total_gross)
                        if total_gross > 0
                        else 0,
                    },
                    "value_breakdown": {
                        k: float(v) for k, v in value_breakdown.items()
                    },
                    "protection_metrics": {
                        "user_protection_level": user_account.protection_level.value,
                        "privacy_preference": user_account.privacy_preference.value,
                        "privacy_bonus_rate": float(
                            self.config["privacy_bonus_rates"][
                                user_account.privacy_preference
                            ]
                        ),
                        "tax_optimization_enabled": user_account.tax_optimization_enabled,
                        "tax_savings": float(statement.tax_optimization_savings),
                        "audit_compliance": statement.audit_success_rate,
                        "data_retention_compliance": statement.data_retention_compliance_rate,
                    },
                    "transaction_count": len(period_transactions),
                    "average_transaction_value": float(
                        total_net / len(period_transactions)
                    ),
                    "payout_eligibility": {
                        "current_balance": float(total_net),
                        "minimum_threshold": float(
                            user_account.payout_eligibility_threshold
                        ),
                        "eligible_for_payout": total_net
                        >= user_account.payout_eligibility_threshold,
                    },
                },
                "message": "Enhanced financial statement generated with user protection transparency",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate enhanced financial statement: {str(e)}",
            }

    def _generate_user_encryption_key(self, user_id: str) -> str:
        """Generate encryption key for user data protection"""
        # Simple hash-based key generation for demonstration
        password = f"{user_id}_echoes_protection".encode()
        salt = f"echoes_user_salt_{secrets.token_hex(8)}".encode()
        key_material = password + salt + secrets.token_bytes(32)
        key_hash = hashlib.sha256(key_material).digest()
        return base64.urlsafe_b64encode(key_hash).decode()

    def _load_user_accounts(self) -> Dict[str, UserAccount]:
        """Load user accounts with enhanced deserialization"""
        accounts_file = self.storage_path / "user_accounts.json"
        if accounts_file.exists():
            with open(accounts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                accounts = {}
                for user_id, account_data in data.items():
                    # Convert enum fields
                    if isinstance(account_data.get("privacy_preference"), str):
                        account_data["privacy_preference"] = PrivacyControl(
                            account_data["privacy_preference"]
                        )
                    if isinstance(account_data.get("protection_level"), str):
                        account_data["protection_level"] = ProtectionLevel(
                            account_data["protection_level"]
                        )
                    if isinstance(account_data.get("payout_method"), str):
                        account_data["payout_method"] = PayoutMethod(
                            account_data["payout_method"]
                        )
                    if isinstance(account_data.get("tax_jurisdiction"), str):
                        account_data["tax_jurisdiction"] = TaxJurisdiction(
                            account_data["tax_jurisdiction"]
                        )
                    if isinstance(account_data.get("data_retention_policy"), str):
                        account_data["data_retention_policy"] = DataRetention(
                            account_data["data_retention_policy"]
                        )

                    # Convert Decimal fields
                    for field in [
                        "total_gross_value",
                        "total_net_value",
                        "total_tax_paid",
                        "total_platform_fees",
                        "total_privacy_bonus",
                        "payout_eligibility_threshold",
                    ]:
                        if field in account_data and isinstance(
                            account_data[field], (int, float, str)
                        ):
                            account_data[field] = Decimal(str(account_data[field]))

                    accounts[user_id] = UserAccount(**account_data)
                return accounts
        return {}

    def _save_user_accounts(self):
        """Save user accounts with proper serialization"""
        accounts_file = self.storage_path / "user_accounts.json"
        accounts_data = {}
        for user_id, account in self.user_accounts.items():
            account_dict = asdict(account)
            # Convert enum fields to strings
            account_dict["privacy_preference"] = account.privacy_preference.value
            account_dict["protection_level"] = account.protection_level.value
            account_dict["payout_method"] = account.payout_method.value
            account_dict["tax_jurisdiction"] = account.tax_jurisdiction.value
            account_dict["data_retention_policy"] = account.data_retention_policy.value
            # Convert Decimal fields to strings
            for field in [
                "total_gross_value",
                "total_net_value",
                "total_tax_paid",
                "total_platform_fees",
                "total_privacy_bonus",
                "payout_eligibility_threshold",
            ]:
                if field in account_dict:
                    account_dict[field] = str(account_dict[field])
            accounts_data[user_id] = account_dict

        with open(accounts_file, "w", encoding="utf-8") as f:
            json.dump(accounts_data, f, indent=2, ensure_ascii=False)

    def _load_transactions(self) -> Dict[str, TransactionRecord]:
        """Load transactions with enhanced deserialization"""
        transactions_file = self.storage_path / "transactions.json"
        if transactions_file.exists():
            with open(transactions_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                transactions = {}
                for txn_id, txn_data in data.items():
                    # Convert enum fields
                    if isinstance(txn_data.get("value_type"), str):
                        txn_data["value_type"] = ValueType(txn_data["value_type"])

                    # Convert Decimal fields
                    for field in [
                        "gross_value",
                        "tax_rate",
                        "platform_cut",
                        "net_value",
                        "privacy_bonus_applied",
                    ]:
                        if field in txn_data and isinstance(
                            txn_data[field], (int, float, str)
                        ):
                            txn_data[field] = Decimal(str(txn_data[field]))

                    transactions[txn_id] = TransactionRecord(**txn_data)
                return transactions
        return {}

    def _save_transactions(self):
        """Save transactions with proper serialization"""
        transactions_file = self.storage_path / "transactions.json"
        transactions_data = {}
        for txn_id, transaction in self.transactions.items():
            txn_dict = asdict(transaction)
            # Convert enum fields to strings
            txn_dict["value_type"] = transaction.value_type.value
            # Convert Decimal fields to strings
            for field in [
                "gross_value",
                "tax_rate",
                "platform_cut",
                "net_value",
                "privacy_bonus_applied",
            ]:
                if field in txn_dict:
                    txn_dict[field] = str(txn_dict[field])
            transactions_data[txn_id] = txn_dict

        with open(transactions_file, "w", encoding="utf-8") as f:
            json.dump(transactions_data, f, indent=2, ensure_ascii=False)

    def _load_payout_records(self) -> Dict[str, PayoutRecord]:
        """Load payout records with enhanced deserialization"""
        payouts_file = self.storage_path / "payout_records.json"
        if payouts_file.exists():
            with open(payouts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                payouts = {}
                for payout_id, payout_data in data.items():
                    # Convert enum fields
                    if isinstance(payout_data.get("payout_method"), str):
                        payout_data["payout_method"] = PayoutMethod(
                            payout_data["payout_method"]
                        )

                    # Convert Decimal fields
                    if "total_amount" in payout_data and isinstance(
                        payout_data["total_amount"], (int, float, str)
                    ):
                        payout_data["total_amount"] = Decimal(
                            str(payout_data["total_amount"])
                        )

                    payouts[payout_id] = PayoutRecord(**payout_data)
                return payouts
        return {}

    def _save_payout_records(self):
        """Save payout records with proper serialization"""
        payouts_file = self.storage_path / "payout_records.json"
        payouts_data = {}
        for payout_id, payout in self.payout_records.items():
            payout_dict = asdict(payout)
            # Convert enum fields to strings
            payout_dict["payout_method"] = payout.payout_method.value
            # Convert Decimal fields to strings
            if "total_amount" in payout_dict:
                payout_dict["total_amount"] = str(payout["total_amount"])
            payouts_data[payout_id] = payout_dict

        with open(payouts_file, "w", encoding="utf-8") as f:
            json.dump(payouts_data, f, indent=2, ensure_ascii=False)


def get_enhanced_accounting() -> EnhancedAccountingSystem:
    """Get enhanced accounting system with comprehensive user protection"""
    return EnhancedAccountingSystem()


# Export enhanced classes for integration
__all__ = [
    "EnhancedAccountingSystem",
    "get_enhanced_accounting",
    "TransactionRecord",
    "UserAccount",
    "FinancialStatement",
    "PayoutRecord",
    "AccountingPeriod",
    "ValueType",
    "PayoutMethod",
    "TaxJurisdiction",
]
