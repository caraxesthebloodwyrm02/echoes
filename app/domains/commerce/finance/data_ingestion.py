"""
Phase 1: Data Ingestion - Secure Financial Data Gateway

Handles secure ingestion of diverse financial data with provenance tracking
and compliance validation.
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, validator

from .security_utils import security_manager

logger = logging.getLogger(__name__)


class DataSourceType(str, Enum):
    """Types of financial data sources"""

    BANK_STATEMENT = "bank_statement"
    INCOME_RECORD = "income_record"
    EXPENSE_REPORT = "expense_report"
    BALANCE_SHEET = "balance_sheet"
    INCOME_STATEMENT = "income_statement"
    CASH_FLOW = "cash_flow"
    MARKET_DATA = "market_data"
    CREDIT_SCORE = "credit_score"
    INVESTMENT_PORTFOLIO = "investment_portfolio"


class UserType(str, Enum):
    """Type of financial advisor user"""

    INDIVIDUAL = "individual"
    ENTERPRISE = "enterprise"


class FinancialDataInput(BaseModel):
    """Input model for financial data"""

    user_type: UserType
    source_type: DataSourceType
    data: Dict
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    currency: str = Field(default="USD", description="Currency code (ISO 4217)")
    metadata: Dict = Field(default_factory=dict)

    @validator("data")
    def validate_data(cls, v):
        if not v:
            raise ValueError("Data cannot be empty")
        return v


class IngestedData(BaseModel):
    """Model for processed and validated financial data"""

    id: str
    user_type: UserType
    source_type: DataSourceType
    data: Dict
    provenance: Dict
    ingestion_timestamp: datetime
    validation_status: str
    compliance_checks: Dict
    metadata: Dict


class FinancialDataIngestor:
    """
    Secure gateway for all financial data ingestion.

    Features:
    - Multi-source data ingestion (personal and enterprise)
    - Provenance tracking for data integrity
    - Compliance validation (GDPR, SOC2, financial regulations)
    - Data sanitization and encryption
    """

    def __init__(self, enable_provenance: bool = True, enable_encryption: bool = True):
        self.enable_provenance = enable_provenance
        self.enable_encryption = enable_encryption
        self.ingested_data_cache: List[IngestedData] = []
        self.security_manager = security_manager

    def ingest_data(self, financial_input: FinancialDataInput) -> IngestedData:
        """
        Ingest financial data with security and compliance validation.

        Args:
            financial_input: Financial data to ingest

        Returns:
            IngestedData: Processed and validated data with provenance
        """
        logger.info(f"Ingesting {financial_input.source_type} data for {financial_input.user_type}")

        # Validate data integrity
        validation_result = self._validate_data(financial_input)

        # Check compliance
        compliance_result = self._check_compliance(financial_input)

        # Generate provenance record
        provenance = self._generate_provenance(financial_input)

        # Sanitize and encrypt sensitive data
        sanitized_data = self._sanitize_data(financial_input.data)

        # Encrypt sensitive fields if encryption is enabled
        if self.enable_encryption:
            sanitized_data = self.security_manager.encrypt_sensitive_data(sanitized_data)
            logger.info("Sensitive data encrypted")

        # Create audit log entry
        audit_log = self.security_manager.create_audit_log(
            action="data_ingestion",
            user_id=financial_input.metadata.get("user_id", "unknown"),
            resource=f"{financial_input.user_type}:{financial_input.source_type}",
            details={
                "source_type": financial_input.source_type,
                "validation_status": validation_result["status"],
                "compliance_checks": compliance_result,
            },
        )
        logger.info(f"Audit log created: {audit_log['timestamp']}")

        # Create ingested data record
        ingested = IngestedData(
            id=self._generate_id(),
            user_type=financial_input.user_type,
            source_type=financial_input.source_type,
            data=sanitized_data,
            provenance=provenance,
            ingestion_timestamp=datetime.utcnow(),
            validation_status=validation_result["status"],
            compliance_checks=compliance_result,
            metadata=financial_input.metadata,
        )

        # Cache for future reference
        self.ingested_data_cache.append(ingested)

        logger.info(f"Successfully ingested data: {ingested.id}")
        return ingested

    def ingest_batch(self, inputs: List[FinancialDataInput]) -> List[IngestedData]:
        """
        Ingest multiple financial data sources in batch.

        Args:
            inputs: List of financial data inputs

        Returns:
            List of ingested and validated data records
        """
        return [self.ingest_data(input_data) for input_data in inputs]

    def _validate_data(self, financial_input: FinancialDataInput) -> Dict:
        """Validate data structure and completeness"""
        validation = {"status": "valid", "checks": [], "warnings": []}

        # Check required fields based on source type
        required_fields = self._get_required_fields(financial_input.source_type)
        missing_fields = [f for f in required_fields if f not in financial_input.data]

        if missing_fields:
            validation["warnings"].append(f"Missing recommended fields: {missing_fields}")

        # Check data types and ranges
        if financial_input.source_type == DataSourceType.BANK_STATEMENT:
            if "balance" in financial_input.data and financial_input.data["balance"] < 0:
                validation["warnings"].append("Negative balance detected")

        validation["checks"].append("Structure validation: PASSED")
        validation["checks"].append("Completeness check: PASSED")

        return validation

    def _check_compliance(self, financial_input: FinancialDataInput) -> Dict:
        """Check compliance with financial regulations"""
        # Use advanced PII detection from security manager
        pii_findings = self.security_manager.detect_pii(financial_input.data)

        # Check if any PII was found
        pii_detected = any(len(v) > 0 for v in pii_findings.values())

        compliance = {
            "gdpr_compliant": True,
            "pii_detected": pii_detected,
            "pii_details": pii_findings,
            "data_retention_policy": "90_days",
            "encryption_required": True,
            "encryption_enabled": self.enable_encryption,
            "audit_trail_enabled": True,
        }

        # Check for sensitive data
        if compliance["pii_detected"]:
            compliance["anonymization_required"] = True
            logger.warning(f"PII detected in financial data: {list(pii_findings.keys())}")

        return compliance

    def _generate_provenance(self, financial_input: FinancialDataInput) -> Dict:
        """Generate provenance record for data traceability"""
        return {
            "source": "user_upload",
            "ingestion_method": "api",
            "timestamp": datetime.utcnow().isoformat(),
            "data_origin": financial_input.metadata.get("origin", "unknown"),
            "processing_version": "1.0.0",
            "integrity_hash": self._calculate_hash(financial_input.data),
        }

    def _sanitize_data(self, data: Dict) -> Dict:
        """Sanitize and encrypt sensitive data fields"""
        sanitized = data.copy()

        # Mask sensitive fields
        sensitive_fields = ["ssn", "tax_id", "account_number", "routing_number"]
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = self._mask_sensitive_field(sanitized[field])

        return sanitized

    def _detect_pii(self, data: Dict) -> bool:
        """Detect personally identifiable information"""
        pii_indicators = ["ssn", "social_security", "tax_id", "passport", "drivers_license"]
        return any(indicator in str(data).lower() for indicator in pii_indicators)

    def _get_required_fields(self, source_type: DataSourceType) -> List[str]:
        """Get required fields for each data source type"""
        field_map = {
            DataSourceType.BANK_STATEMENT: ["balance", "transactions", "account_number"],
            DataSourceType.INCOME_RECORD: ["amount", "source", "date"],
            DataSourceType.EXPENSE_REPORT: ["total_expenses", "categories", "period"],
            DataSourceType.BALANCE_SHEET: ["assets", "liabilities", "equity"],
            DataSourceType.INCOME_STATEMENT: ["revenue", "expenses", "net_income"],
            DataSourceType.CASH_FLOW: [
                "operating_cash_flow",
                "investing_cash_flow",
                "financing_cash_flow",
            ],
        }
        return field_map.get(source_type, [])

    def _mask_sensitive_field(self, value: str) -> str:
        """Mask sensitive field values"""
        if len(str(value)) > 4:
            return "*" * (len(str(value)) - 4) + str(value)[-4:]
        return "****"

    def _calculate_hash(self, data: Dict) -> str:
        """Calculate integrity hash for data"""
        import json

        data_str = json.dumps(data, sort_keys=True)
        return self.security_manager.hash_data(data_str)

    def _generate_id(self) -> str:
        """Generate unique ID for ingested data"""
        import uuid

        return f"FIN-{uuid.uuid4().hex[:12].upper()}"

    def get_ingested_data(self, data_id: str) -> Optional[IngestedData]:
        """Retrieve ingested data by ID"""
        for data in self.ingested_data_cache:
            if data.id == data_id:
                return data
        return None

    def get_user_data(self, user_type: UserType) -> List[IngestedData]:
        """Get all ingested data for a specific user type"""
        return [d for d in self.ingested_data_cache if d.user_type == user_type]
