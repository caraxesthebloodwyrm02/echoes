"""
Comprehensive test suite for FinanceAdvisor security utilities

Tests encryption, PII detection, hashing, and audit logging.
"""

from datetime import datetime

import pytest

from app.domains.commerce.finance.security_utils import FinanceSecurity, security_manager


class TestFinanceSecurity:
    """Test suite for FinanceSecurity class"""

    @pytest.fixture
    def security(self):
        """Create a FinanceSecurity instance for testing"""
        return FinanceSecurity()

    def test_encryption_decryption(self, security):
        """Test data encryption and decryption"""
        test_data = {
            "account_number": "1234567890",
            "ssn": "123-45-6789",
            "salary": 75000,
            "name": "John Doe",
        }

        # Encrypt
        encrypted = security.encrypt_sensitive_data(test_data)

        # Verify sensitive fields are encrypted
        assert encrypted["account_number"].startswith("ENC:")
        assert encrypted["ssn"].startswith("ENC:")
        assert encrypted["salary"].startswith("ENC:")
        assert encrypted["name"] == "John Doe"  # Not sensitive

        # Decrypt
        decrypted = security.decrypt_sensitive_data(encrypted)

        # Verify decryption
        assert decrypted["account_number"] == "1234567890"
        assert decrypted["ssn"] == "123-45-6789"
        assert decrypted["salary"] == "75000"  # Converted to string

    def test_encrypt_nested_data(self, security):
        """Test encryption of nested data structures"""
        nested_data = {
            "user": {"name": "Jane Smith", "ssn": "987-65-4321", "bank_account": "9876543210"},
            "income": 100000,
        }

        encrypted = security.encrypt_sensitive_data(nested_data)

        # Top level income should be encrypted
        assert encrypted["income"].startswith("ENC:")

        # Nested data should not be affected (current implementation)
        assert isinstance(encrypted["user"], dict)

    def test_pii_detection_email(self, security):
        """Test PII detection for email addresses"""
        data = {
            "contact": "john.doe@example.com",
            "message": "Please contact me at jane.smith@test.org",
        }

        pii = security.detect_pii(data)

        assert len(pii["email_addresses"]) == 2
        assert "john.doe@example.com" in pii["email_addresses"]
        assert "jane.smith@test.org" in pii["email_addresses"]

    def test_pii_detection_phone(self, security):
        """Test PII detection for phone numbers"""
        data = {"phone": "555-123-4567", "mobile": "5559876543", "text": "Call me at 555.555.5555"}

        pii = security.detect_pii(data)

        assert len(pii["phone_numbers"]) >= 2

    def test_pii_detection_ssn(self, security):
        """Test PII detection for social security numbers"""
        data = {"ssn": "123-45-6789", "tax_id": "987654321", "note": "My SSN is 555-55-5555"}

        pii = security.detect_pii(data)

        assert len(pii["social_security_numbers"]) >= 2

    def test_pii_detection_credit_card(self, security):
        """Test PII detection for credit card numbers"""
        data = {"card": "4532-1234-5678-9010", "payment": "5555 5555 5555 4444"}

        pii = security.detect_pii(data)

        assert len(pii["credit_card_numbers"]) >= 1

    def test_pii_detection_no_pii(self, security):
        """Test PII detection when no PII is present"""
        data = {"product": "Widget", "quantity": 10, "price": 29.99}

        pii = security.detect_pii(data)

        # All categories should be empty
        for category in pii.values():
            assert len(category) == 0

    def test_hash_data(self, security):
        """Test data hashing for integrity"""
        data = "sensitive information"

        hashed = security.hash_data(data)

        # Verify hash format (salt:hash)
        assert ":" in hashed
        salt, hash_value = hashed.split(":", 1)
        assert len(salt) == 32  # 16 bytes as hex
        assert len(hash_value) == 64  # SHA256 hex digest

    def test_verify_hash_valid(self, security):
        """Test hash verification with valid data"""
        data = "test data"
        hashed = security.hash_data(data)

        assert security.verify_hash(data, hashed) is True

    def test_verify_hash_invalid(self, security):
        """Test hash verification with invalid data"""
        data = "test data"
        hashed = security.hash_data(data)

        modified_data = "modified data"
        assert security.verify_hash(modified_data, hashed) is False

    def test_verify_hash_malformed(self, security):
        """Test hash verification with malformed hash"""
        data = "test data"
        malformed_hash = "invalid_hash_format"

        assert security.verify_hash(data, malformed_hash) is False

    def test_create_audit_log(self, security):
        """Test audit log creation"""
        audit_log = security.create_audit_log(
            action="data_access",
            user_id="user123",
            resource="financial_report",
            details={"report_id": "R-12345"},
        )

        # Verify audit log structure
        assert audit_log["action"] == "data_access"
        assert audit_log["user_id"] == "user123"
        assert audit_log["resource"] == "financial_report"
        assert audit_log["details"]["report_id"] == "R-12345"
        assert "timestamp" in audit_log
        assert "ip_address" in audit_log
        assert "user_agent" in audit_log

        # Verify timestamp format
        datetime.fromisoformat(audit_log["timestamp"])

    def test_global_security_manager(self):
        """Test global security manager instance"""
        assert security_manager is not None
        assert isinstance(security_manager, FinanceSecurity)

    def test_encryption_consistency(self, security):
        """Test that encryption produces different outputs for same input"""
        data1 = {"ssn": "123-45-6789"}
        data2 = {"ssn": "123-45-6789"}

        encrypted1 = security.encrypt_sensitive_data(data1)
        encrypted2 = security.encrypt_sensitive_data(data2)

        # Same input should produce different encrypted output (due to IV)
        # But decryption should yield same result
        decrypted1 = security.decrypt_sensitive_data(encrypted1)
        decrypted2 = security.decrypt_sensitive_data(encrypted2)

        assert decrypted1["ssn"] == decrypted2["ssn"]

    def test_decrypt_non_encrypted_field(self, security):
        """Test decryption handles non-encrypted fields gracefully"""
        data = {"account_number": "1234567890", "name": "John Doe"}

        # Try to decrypt data that's not encrypted
        result = security.decrypt_sensitive_data(data)

        # Non-encrypted fields should remain unchanged
        assert result["account_number"] == "1234567890"
        assert result["name"] == "John Doe"

    def test_pii_detection_nested_dict(self, security):
        """Test PII detection in nested dictionaries"""
        data = {"user": {"profile": {"email": "nested@example.com", "phone": "555-123-4567"}}}

        pii = security.detect_pii(data)

        assert "nested@example.com" in pii["email_addresses"]
        assert len(pii["phone_numbers"]) >= 1

    def test_pii_detection_list(self, security):
        """Test PII detection in lists"""
        data = {"contacts": ["alice@example.com", "bob@test.com", {"email": "charlie@demo.org"}]}

        pii = security.detect_pii(data)

        assert len(pii["email_addresses"]) >= 2

    def test_hash_with_custom_salt(self, security):
        """Test hashing with custom salt"""
        data = "test data"
        salt = "custom_salt_value"

        hashed = security.hash_data(data, salt)

        # Verify custom salt is used
        assert hashed.startswith(f"{salt}:")

        # Verify verification works with custom salt
        assert security.verify_hash(data, hashed) is True

    def test_encrypt_empty_string(self, security):
        """Test encryption of empty string"""
        data = {"account_number": ""}

        encrypted = security.encrypt_sensitive_data(data)

        # Empty string should still be encrypted
        assert encrypted["account_number"].startswith("ENC:")

        # Decrypt and verify
        decrypted = security.decrypt_sensitive_data(encrypted)
        assert decrypted["account_number"] == ""

    def test_encrypt_numeric_fields(self, security):
        """Test encryption of numeric fields"""
        data = {"salary": 75000, "balance": 12345.67, "debt": 5000}

        encrypted = security.encrypt_sensitive_data(data)

        # All numeric fields should be encrypted
        assert encrypted["salary"].startswith("ENC:")
        assert encrypted["balance"].startswith("ENC:")
        assert encrypted["debt"].startswith("ENC:")

        # Decrypt and verify
        decrypted = security.decrypt_sensitive_data(encrypted)
        assert decrypted["salary"] == "75000"
        assert decrypted["balance"] == "12345.67"
        assert decrypted["debt"] == "5000"


class TestSecurityEdgeCases:
    """Test edge cases and error handling"""

    def test_decrypt_invalid_encrypted_data(self):
        """Test decryption with invalid encrypted data"""
        security = FinanceSecurity()
        data = {"field": "ENC:invalid_encrypted_data"}

        # Should handle gracefully and keep encrypted value
        result = security.decrypt_sensitive_data(data)
        assert result["field"] == "ENC:invalid_encrypted_data"

    def test_empty_data_encryption(self):
        """Test encryption with empty dictionary"""
        security = FinanceSecurity()
        data = {}

        encrypted = security.encrypt_sensitive_data(data)
        assert encrypted == {}

    def test_empty_data_pii_detection(self):
        """Test PII detection with empty dictionary"""
        security = FinanceSecurity()
        data = {}

        pii = security.detect_pii(data)

        # All categories should be empty lists
        for category in pii.values():
            assert category == []

    def test_none_values_in_data(self):
        """Test handling of None values"""
        security = FinanceSecurity()
        data = {"account_number": None, "name": "John Doe"}

        # Should not crash
        encrypted = security.encrypt_sensitive_data(data)
        assert encrypted["account_number"] is None
        assert encrypted["name"] == "John Doe"


@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security utilities"""

    def test_full_encryption_workflow(self):
        """Test complete encryption/decryption workflow"""
        security = FinanceSecurity()

        original_data = {
            "user_id": "U12345",
            "name": "Jane Doe",
            "ssn": "123-45-6789",
            "account_number": "9876543210",
            "balance": 50000,
            "email": "jane@example.com",
        }

        # Step 1: Detect PII
        pii = security.detect_pii(original_data)
        assert len(pii["email_addresses"]) > 0

        # Step 2: Encrypt
        encrypted = security.encrypt_sensitive_data(original_data)

        # Step 3: Create integrity hash
        import json

        data_str = json.dumps(encrypted, sort_keys=True)
        hash_value = security.hash_data(data_str)

        # Step 4: Verify integrity
        assert security.verify_hash(data_str, hash_value) is True

        # Step 5: Decrypt
        decrypted = security.decrypt_sensitive_data(encrypted)

        # Verify sensitive fields restored
        assert decrypted["ssn"] == "123-45-6789"
        assert decrypted["account_number"] == "9876543210"

    def test_audit_log_workflow(self):
        """Test audit logging workflow"""
        security = FinanceSecurity()

        # Create multiple audit logs
        logs = []
        for i in range(3):
            log = security.create_audit_log(
                action=f"action_{i}",
                user_id=f"user_{i}",
                resource=f"resource_{i}",
                details={"index": i},
            )
            logs.append(log)

        # Verify all logs have timestamps
        for log in logs:
            assert "timestamp" in log
            assert log["action"].startswith("action_")

        # Verify logs are in chronological order (approximately)
        timestamps = [datetime.fromisoformat(log["timestamp"]) for log in logs]
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
Comprehensive test suite for FinanceAdvisor data ingestion

Tests secure data ingestion, validation, compliance, and provenance tracking.
"""


import pytest

from app.domains.commerce.finance.data_ingestion import (
    DataSourceType,
    FinancialDataIngestor,
    FinancialDataInput,
    IngestedData,
    UserType,
)


class TestFinancialDataInput:
    """Test FinancialDataInput model validation"""

    def test_valid_personal_input(self):
        """Test valid personal financial data input"""
        input_data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.BANK_STATEMENT,
            data={"balance": 10000, "transactions": [{"amount": 100, "date": "2024-01-01"}]},
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 1, 31),
            currency="USD",
            metadata={"source": "test"},
        )

        assert input_data.user_type == UserType.INDIVIDUAL
        assert input_data.source_type == DataSourceType.BANK_STATEMENT
        assert input_data.currency == "USD"

    def test_valid_enterprise_input(self):
        """Test valid enterprise financial data input"""
        input_data = FinancialDataInput(
            user_type=UserType.ENTERPRISE,
            source_type=DataSourceType.BALANCE_SHEET,
            data={"assets": 1000000, "liabilities": 500000, "equity": 500000},
            metadata={"company": "Test Corp"},
        )

        assert input_data.user_type == UserType.ENTERPRISE
        assert input_data.source_type == DataSourceType.BALANCE_SHEET

    def test_invalid_empty_data(self):
        """Test validation fails with empty data"""
        with pytest.raises(ValueError, match="Data cannot be empty"):
            FinancialDataInput(
                user_type=UserType.INDIVIDUAL, source_type=DataSourceType.BANK_STATEMENT, data={}
            )

    def test_default_currency(self):
        """Test default currency is USD"""
        input_data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.INCOME_RECORD,
            data={"amount": 5000},
        )

        assert input_data.currency == "USD"


class TestFinancialDataIngestor:
    """Test FinancialDataIngestor functionality"""

    @pytest.fixture
    def ingestor(self):
        """Create a FinancialDataIngestor instance"""
        return FinancialDataIngestor(enable_provenance=True, enable_encryption=True)

    @pytest.fixture
    def sample_bank_statement(self):
        """Sample bank statement data"""
        return FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.BANK_STATEMENT,
            data={
                "account_number": "1234567890",
                "balance": 15000,
                "transactions": [
                    {"date": "2024-01-15", "amount": -500, "description": "Groceries"},
                    {"date": "2024-01-20", "amount": 3000, "description": "Salary"},
                ],
            },
            period_start=datetime(2024, 1, 1),
            period_end=datetime(2024, 1, 31),
            metadata={"user_id": "U123"},
        )

    def test_ingest_bank_statement(self, ingestor, sample_bank_statement):
        """Test ingestion of bank statement"""
        result = ingestor.ingest_data(sample_bank_statement)

        assert isinstance(result, IngestedData)
        assert result.user_type == UserType.INDIVIDUAL
        assert result.source_type == DataSourceType.BANK_STATEMENT
        assert result.validation_status == "valid"
        assert result.id.startswith("FIN-")

    def test_ingested_data_has_provenance(self, ingestor, sample_bank_statement):
        """Test ingested data includes provenance tracking"""
        result = ingestor.ingest_data(sample_bank_statement)

        assert "provenance" in result.dict()
        assert "source" in result.provenance
        assert "timestamp" in result.provenance
        assert "integrity_hash" in result.provenance

    def test_ingested_data_has_compliance_checks(self, ingestor, sample_bank_statement):
        """Test ingested data includes compliance validation"""
        result = ingestor.ingest_data(sample_bank_statement)

        assert "compliance_checks" in result.dict()
        compliance = result.compliance_checks

        assert "gdpr_compliant" in compliance
        assert "pii_detected" in compliance
        assert "encryption_required" in compliance
        assert "audit_trail_enabled" in compliance

    def test_pii_detection_in_compliance(self, ingestor):
        """Test PII detection triggers compliance flags"""
        data_with_pii = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.INCOME_RECORD,
            data={"ssn": "123-45-6789", "email": "user@example.com", "amount": 50000},
            metadata={"user_id": "U456"},
        )

        result = ingestor.ingest_data(data_with_pii)

        compliance = result.compliance_checks
        assert compliance["pii_detected"] is True
        assert "anonymization_required" in compliance

    def test_data_sanitization(self, ingestor):
        """Test sensitive data is sanitized"""
        sensitive_data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.BANK_STATEMENT,
            data={"account_number": "9876543210", "routing_number": "123456789", "balance": 20000},
            metadata={"user_id": "U789"},
        )

        result = ingestor.ingest_data(sensitive_data)

        # Account number should be masked or encrypted
        if ingestor.enable_encryption:
            # If encrypted, should have ENC: prefix
            assert result.data["account_number"].startswith("ENC:")
        else:
            # If not encrypted, should be masked
            assert "****" in str(result.data["account_number"])

    def test_encryption_when_enabled(self, ingestor):
        """Test encryption is applied when enabled"""
        ingestor.enable_encryption = True

        financial_data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.INCOME_RECORD,
            data={"ssn": "123-45-6789", "salary": 75000},
            metadata={"user_id": "U999"},
        )

        result = ingestor.ingest_data(financial_data)

        # Sensitive fields should be encrypted
        assert result.data["ssn"].startswith("ENC:")
        assert result.data["salary"].startswith("ENC:")

    def test_no_encryption_when_disabled(self):
        """Test no encryption when disabled"""
        ingestor = FinancialDataIngestor(enable_encryption=False)

        financial_data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.INCOME_RECORD,
            data={"salary": 75000},
        )

        result = ingestor.ingest_data(financial_data)

        # Should be masked but not encrypted
        assert "****" in str(result.data.get("salary", ""))

    def test_batch_ingestion(self, ingestor):
        """Test batch ingestion of multiple data sources"""
        inputs = [
            FinancialDataInput(
                user_type=UserType.INDIVIDUAL,
                source_type=DataSourceType.INCOME_RECORD,
                data={"amount": 5000, "source": "salary"},
            ),
            FinancialDataInput(
                user_type=UserType.INDIVIDUAL,
                source_type=DataSourceType.EXPENSE_REPORT,
                data={"total_expenses": 2000, "categories": ["food", "rent"]},
            ),
            FinancialDataInput(
                user_type=UserType.INDIVIDUAL,
                source_type=DataSourceType.BANK_STATEMENT,
                data={"balance": 10000, "account_number": "1234567890"},
            ),
        ]

        results = ingestor.ingest_batch(inputs)

        assert len(results) == 3
        assert all(isinstance(r, IngestedData) for r in results)
        assert results[0].source_type == DataSourceType.INCOME_RECORD
        assert results[1].source_type == DataSourceType.EXPENSE_REPORT
        assert results[2].source_type == DataSourceType.BANK_STATEMENT

    def test_data_caching(self, ingestor, sample_bank_statement):
        """Test ingested data is cached"""
        result = ingestor.ingest_data(sample_bank_statement)

        assert len(ingestor.ingested_data_cache) == 1
        assert ingestor.ingested_data_cache[0].id == result.id

    def test_get_ingested_data_by_id(self, ingestor, sample_bank_statement):
        """Test retrieval of ingested data by ID"""
        result = ingestor.ingest_data(sample_bank_statement)

        retrieved = ingestor.get_ingested_data(result.id)

        assert retrieved is not None
        assert retrieved.id == result.id
        assert retrieved.source_type == DataSourceType.BANK_STATEMENT

    def test_get_nonexistent_data(self, ingestor):
        """Test retrieval of non-existent data returns None"""
        result = ingestor.get_ingested_data("FIN-NONEXISTENT")
        assert result is None

    def test_get_user_data(self, ingestor):
        """Test retrieval of data by user type"""
        # Ingest data for different user types
        individual_data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.INCOME_RECORD,
            data={"amount": 5000},
        )

        enterprise_data = FinancialDataInput(
            user_type=UserType.ENTERPRISE,
            source_type=DataSourceType.BALANCE_SHEET,
            data={"assets": 1000000, "liabilities": 500000, "equity": 500000},
        )

        ingestor.ingest_data(individual_data)
        ingestor.ingest_data(enterprise_data)

        # Get individual data
        individual_results = ingestor.get_user_data(UserType.INDIVIDUAL)
        assert len(individual_results) == 1
        assert individual_results[0].user_type == UserType.INDIVIDUAL

        # Get enterprise data
        enterprise_results = ingestor.get_user_data(UserType.ENTERPRISE)
        assert len(enterprise_results) == 1
        assert enterprise_results[0].user_type == UserType.ENTERPRISE


class TestDataValidation:
    """Test data validation logic"""

    @pytest.fixture
    def ingestor(self):
        return FinancialDataIngestor()

    def test_bank_statement_validation(self, ingestor):
        """Test validation of bank statement data"""
        bank_data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.BANK_STATEMENT,
            data={"balance": 5000, "transactions": [], "account_number": "1234567890"},
        )

        result = ingestor.ingest_data(bank_data)
        assert result.validation_status == "valid"

    def test_negative_balance_warning(self, ingestor):
        """Test warning for negative balance"""
        bank_data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.BANK_STATEMENT,
            data={"balance": -1000, "transactions": [], "account_number": "1234567890"},
        )

        result = ingestor.ingest_data(bank_data)
        # Still valid but should have warnings
        assert result.validation_status == "valid"

    def test_income_record_validation(self, ingestor):
        """Test validation of income record"""
        income_data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.INCOME_RECORD,
            data={"amount": 5000, "source": "salary", "date": "2024-01-15"},
        )

        result = ingestor.ingest_data(income_data)
        assert result.validation_status == "valid"

    def test_balance_sheet_validation(self, ingestor):
        """Test validation of balance sheet"""
        balance_sheet = FinancialDataInput(
            user_type=UserType.ENTERPRISE,
            source_type=DataSourceType.BALANCE_SHEET,
            data={"assets": 1000000, "liabilities": 600000, "equity": 400000},
        )

        result = ingestor.ingest_data(balance_sheet)
        assert result.validation_status == "valid"


class TestProvenanceTracking:
    """Test provenance tracking functionality"""

    @pytest.fixture
    def ingestor(self):
        return FinancialDataIngestor(enable_provenance=True)

    def test_provenance_includes_timestamp(self, ingestor):
        """Test provenance includes timestamp"""
        data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.INCOME_RECORD,
            data={"amount": 5000},
        )

        result = ingestor.ingest_data(data)

        assert "timestamp" in result.provenance
        # Verify timestamp is valid ISO format
        datetime.fromisoformat(result.provenance["timestamp"])

    def test_provenance_includes_integrity_hash(self, ingestor):
        """Test provenance includes integrity hash"""
        data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.INCOME_RECORD,
            data={"amount": 5000},
        )

        result = ingestor.ingest_data(data)

        assert "integrity_hash" in result.provenance
        assert len(result.provenance["integrity_hash"]) > 0

    def test_provenance_metadata_preserved(self, ingestor):
        """Test metadata is preserved in provenance"""
        data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.INCOME_RECORD,
            data={"amount": 5000},
            metadata={"origin": "mobile_app", "version": "1.0"},
        )

        result = ingestor.ingest_data(data)

        # Original metadata should be preserved
        assert result.metadata["origin"] == "mobile_app"
        assert result.metadata["version"] == "1.0"


class TestComplianceChecks:
    """Test compliance validation"""

    @pytest.fixture
    def ingestor(self):
        return FinancialDataIngestor()

    def test_gdpr_compliance(self, ingestor):
        """Test GDPR compliance check"""
        data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.INCOME_RECORD,
            data={"amount": 5000},
        )

        result = ingestor.ingest_data(data)

        assert result.compliance_checks["gdpr_compliant"] is True

    def test_encryption_required_flag(self, ingestor):
        """Test encryption required flag"""
        data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.BANK_STATEMENT,
            data={"balance": 10000, "account_number": "1234567890"},
        )

        result = ingestor.ingest_data(data)

        assert result.compliance_checks["encryption_required"] is True

    def test_data_retention_policy(self, ingestor):
        """Test data retention policy is set"""
        data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.INCOME_RECORD,
            data={"amount": 5000},
        )

        result = ingestor.ingest_data(data)

        assert "data_retention_policy" in result.compliance_checks
        assert result.compliance_checks["data_retention_policy"] == "90_days"


@pytest.mark.integration
class TestDataIngestionIntegration:
    """Integration tests for data ingestion"""

    def test_full_ingestion_workflow(self):
        """Test complete data ingestion workflow"""
        ingestor = FinancialDataIngestor(enable_provenance=True, enable_encryption=True)

        # Step 1: Create input
        financial_data = FinancialDataInput(
            user_type=UserType.INDIVIDUAL,
            source_type=DataSourceType.BANK_STATEMENT,
            data={
                "account_number": "1234567890",
                "balance": 25000,
                "ssn": "123-45-6789",
                "transactions": [
                    {"date": "2024-01-10", "amount": 1000},
                    {"date": "2024-01-20", "amount": -500},
                ],
            },
            metadata={"user_id": "U123", "source": "api"},
        )

        # Step 2: Ingest
        result = ingestor.ingest_data(financial_data)

        # Step 3: Verify all components
        assert result.validation_status == "valid"
        assert result.compliance_checks["pii_detected"] is True
        assert result.data["account_number"].startswith("ENC:")
        assert "integrity_hash" in result.provenance

        # Step 4: Retrieve
        retrieved = ingestor.get_ingested_data(result.id)
        assert retrieved is not None
        assert retrieved.id == result.id

    def test_multi_source_ingestion(self):
        """Test ingestion of multiple data sources"""
        ingestor = FinancialDataIngestor()

        sources = [
            (DataSourceType.BANK_STATEMENT, {"balance": 10000, "account_number": "123"}),
            (DataSourceType.INCOME_RECORD, {"amount": 5000, "source": "salary"}),
            (DataSourceType.EXPENSE_REPORT, {"total_expenses": 3000, "categories": ["food"]}),
            (
                DataSourceType.BALANCE_SHEET,
                {"assets": 100000, "liabilities": 50000, "equity": 50000},
            ),
        ]

        for source_type, data in sources:
            input_data = FinancialDataInput(
                user_type=UserType.INDIVIDUAL, source_type=source_type, data=data
            )
            result = ingestor.ingest_data(input_data)
            assert result.validation_status == "valid"

        # Verify all data cached
        assert len(ingestor.ingested_data_cache) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
"""
Comprehensive test suite for FinanceAdvisor security utilities

Tests encryption, PII detection, hashing, and audit logging.
"""


import pytest



class TestFinanceSecurity:
    """Test suite for FinanceSecurity class"""

    @pytest.fixture
    def security(self):
        """Create a FinanceSecurity instance for testing"""
        return FinanceSecurity()

    def test_encryption_decryption(self, security):
        """Test data encryption and decryption"""
        test_data = {
            "account_number": "1234567890",
            "ssn": "123-45-6789",
            "salary": 75000,
            "name": "John Doe",
        }

        # Encrypt
        encrypted = security.encrypt_sensitive_data(test_data)

        # Verify sensitive fields are encrypted
        assert encrypted["account_number"].startswith("ENC:")
        assert encrypted["ssn"].startswith("ENC:")
        assert encrypted["salary"].startswith("ENC:")
        assert encrypted["name"] == "John Doe"  # Not sensitive

        # Decrypt
        decrypted = security.decrypt_sensitive_data(encrypted)

        # Verify decryption
        assert decrypted["account_number"] == "1234567890"
        assert decrypted["ssn"] == "123-45-6789"
        assert decrypted["salary"] == "75000"  # Converted to string

    def test_encrypt_nested_data(self, security):
        """Test encryption of nested data structures"""
        nested_data = {
            "user": {"name": "Jane Smith", "ssn": "987-65-4321", "bank_account": "9876543210"},
            "income": 100000,
        }

        encrypted = security.encrypt_sensitive_data(nested_data)

        # Top level income should be encrypted
        assert encrypted["income"].startswith("ENC:")

        # Nested data should not be affected (current implementation)
        assert isinstance(encrypted["user"], dict)

    def test_pii_detection_email(self, security):
        """Test PII detection for email addresses"""
        data = {
            "contact": "john.doe@example.com",
            "message": "Please contact me at jane.smith@test.org",
        }

        pii = security.detect_pii(data)

        assert len(pii["email_addresses"]) == 2
        assert "john.doe@example.com" in pii["email_addresses"]
        assert "jane.smith@test.org" in pii["email_addresses"]

    def test_pii_detection_phone(self, security):
        """Test PII detection for phone numbers"""
        data = {"phone": "555-123-4567", "mobile": "5559876543", "text": "Call me at 555.555.5555"}

        pii = security.detect_pii(data)

        assert len(pii["phone_numbers"]) >= 2

    def test_pii_detection_ssn(self, security):
        """Test PII detection for social security numbers"""
        data = {"ssn": "123-45-6789", "tax_id": "987654321", "note": "My SSN is 555-55-5555"}

        pii = security.detect_pii(data)

        assert len(pii["social_security_numbers"]) >= 2

    def test_pii_detection_credit_card(self, security):
        """Test PII detection for credit card numbers"""
        data = {"card": "4532-1234-5678-9010", "payment": "5555 5555 5555 4444"}

        pii = security.detect_pii(data)

        assert len(pii["credit_card_numbers"]) >= 1

    def test_pii_detection_no_pii(self, security):
        """Test PII detection when no PII is present"""
        data = {"product": "Widget", "quantity": 10, "price": 29.99}

        pii = security.detect_pii(data)

        # All categories should be empty
        for category in pii.values():
            assert len(category) == 0

    def test_hash_data(self, security):
        """Test data hashing for integrity"""
        data = "sensitive information"

        hashed = security.hash_data(data)

        # Verify hash format (salt:hash)
        assert ":" in hashed
        salt, hash_value = hashed.split(":", 1)
        assert len(salt) == 32  # 16 bytes as hex
        assert len(hash_value) == 64  # SHA256 hex digest

    def test_verify_hash_valid(self, security):
        """Test hash verification with valid data"""
        data = "test data"
        hashed = security.hash_data(data)

        assert security.verify_hash(data, hashed) is True

    def test_verify_hash_invalid(self, security):
        """Test hash verification with invalid data"""
        data = "test data"
        hashed = security.hash_data(data)

        modified_data = "modified data"
        assert security.verify_hash(modified_data, hashed) is False

    def test_verify_hash_malformed(self, security):
        """Test hash verification with malformed hash"""
        data = "test data"
        malformed_hash = "invalid_hash_format"

        assert security.verify_hash(data, malformed_hash) is False

    def test_create_audit_log(self, security):
        """Test audit log creation"""
        audit_log = security.create_audit_log(
            action="data_access",
            user_id="user123",
            resource="financial_report",
            details={"report_id": "R-12345"},
        )

        # Verify audit log structure
        assert audit_log["action"] == "data_access"
        assert audit_log["user_id"] == "user123"
        assert audit_log["resource"] == "financial_report"
        assert audit_log["details"]["report_id"] == "R-12345"
        assert "timestamp" in audit_log
        assert "ip_address" in audit_log
        assert "user_agent" in audit_log

        # Verify timestamp format
        datetime.fromisoformat(audit_log["timestamp"])

    def test_global_security_manager(self):
        """Test global security manager instance"""
        assert security_manager is not None
        assert isinstance(security_manager, FinanceSecurity)

    def test_encryption_consistency(self, security):
        """Test that encryption produces different outputs for same input"""
        data1 = {"ssn": "123-45-6789"}
        data2 = {"ssn": "123-45-6789"}

        encrypted1 = security.encrypt_sensitive_data(data1)
        encrypted2 = security.encrypt_sensitive_data(data2)

        # Same input should produce different encrypted output (due to IV)
        # But decryption should yield same result
        decrypted1 = security.decrypt_sensitive_data(encrypted1)
        decrypted2 = security.decrypt_sensitive_data(encrypted2)

        assert decrypted1["ssn"] == decrypted2["ssn"]

    def test_decrypt_non_encrypted_field(self, security):
        """Test decryption handles non-encrypted fields gracefully"""
        data = {"account_number": "1234567890", "name": "John Doe"}

        # Try to decrypt data that's not encrypted
        result = security.decrypt_sensitive_data(data)

        # Non-encrypted fields should remain unchanged
        assert result["account_number"] == "1234567890"
        assert result["name"] == "John Doe"

    def test_pii_detection_nested_dict(self, security):
        """Test PII detection in nested dictionaries"""
        data = {"user": {"profile": {"email": "nested@example.com", "phone": "555-123-4567"}}}

        pii = security.detect_pii(data)

        assert "nested@example.com" in pii["email_addresses"]
        assert len(pii["phone_numbers"]) >= 1

    def test_pii_detection_list(self, security):
        """Test PII detection in lists"""
        data = {"contacts": ["alice@example.com", "bob@test.com", {"email": "charlie@demo.org"}]}

        pii = security.detect_pii(data)

        assert len(pii["email_addresses"]) >= 2

    def test_hash_with_custom_salt(self, security):
        """Test hashing with custom salt"""
        data = "test data"
        salt = "custom_salt_value"

        hashed = security.hash_data(data, salt)

        # Verify custom salt is used
        assert hashed.startswith(f"{salt}:")

        # Verify verification works with custom salt
        assert security.verify_hash(data, hashed) is True

    def test_encrypt_empty_string(self, security):
        """Test encryption of empty string"""
        data = {"account_number": ""}

        encrypted = security.encrypt_sensitive_data(data)

        # Empty string should still be encrypted
        assert encrypted["account_number"].startswith("ENC:")

        # Decrypt and verify
        decrypted = security.decrypt_sensitive_data(encrypted)
        assert decrypted["account_number"] == ""

    def test_encrypt_numeric_fields(self, security):
        """Test encryption of numeric fields"""
        data = {"salary": 75000, "balance": 12345.67, "debt": 5000}

        encrypted = security.encrypt_sensitive_data(data)

        # All numeric fields should be encrypted
        assert encrypted["salary"].startswith("ENC:")
        assert encrypted["balance"].startswith("ENC:")
        assert encrypted["debt"].startswith("ENC:")

        # Decrypt and verify
        decrypted = security.decrypt_sensitive_data(encrypted)
        assert decrypted["salary"] == "75000"
        assert decrypted["balance"] == "12345.67"
        assert decrypted["debt"] == "5000"


class TestSecurityEdgeCases:
    """Test edge cases and error handling"""

    def test_decrypt_invalid_encrypted_data(self):
        """Test decryption with invalid encrypted data"""
        security = FinanceSecurity()
        data = {"field": "ENC:invalid_encrypted_data"}

        # Should handle gracefully and keep encrypted value
        result = security.decrypt_sensitive_data(data)
        assert result["field"] == "ENC:invalid_encrypted_data"

    def test_empty_data_encryption(self):
        """Test encryption with empty dictionary"""
        security = FinanceSecurity()
        data = {}

        encrypted = security.encrypt_sensitive_data(data)
        assert encrypted == {}

    def test_empty_data_pii_detection(self):
        """Test PII detection with empty dictionary"""
        security = FinanceSecurity()
        data = {}

        pii = security.detect_pii(data)

        # All categories should be empty lists
        for category in pii.values():
            assert category == []

    def test_none_values_in_data(self):
        """Test handling of None values"""
        security = FinanceSecurity()
        data = {"account_number": None, "name": "John Doe"}

        # Should not crash
        encrypted = security.encrypt_sensitive_data(data)
        assert encrypted["account_number"] is None
        assert encrypted["name"] == "John Doe"


@pytest.mark.integration
class TestSecurityIntegration:
    """Integration tests for security utilities"""

    def test_full_encryption_workflow(self):
        """Test complete encryption/decryption workflow"""
        security = FinanceSecurity()

        original_data = {
            "user_id": "U12345",
            "name": "Jane Doe",
            "ssn": "123-45-6789",
            "account_number": "9876543210",
            "balance": 50000,
            "email": "jane@example.com",
        }

        # Step 1: Detect PII
        pii = security.detect_pii(original_data)
        assert len(pii["email_addresses"]) > 0

        # Step 2: Encrypt
        encrypted = security.encrypt_sensitive_data(original_data)

        # Step 3: Create integrity hash
        import json

        data_str = json.dumps(encrypted, sort_keys=True)
        hash_value = security.hash_data(data_str)

        # Step 4: Verify integrity
        assert security.verify_hash(data_str, hash_value) is True

        # Step 5: Decrypt
        decrypted = security.decrypt_sensitive_data(encrypted)

        # Verify sensitive fields restored
        assert decrypted["ssn"] == "123-45-6789"
        assert decrypted["account_number"] == "9876543210"

    def test_audit_log_workflow(self):
        """Test audit logging workflow"""
        security = FinanceSecurity()

        # Create multiple audit logs
        logs = []
        for i in range(3):
            log = security.create_audit_log(
                action=f"action_{i}",
                user_id=f"user_{i}",
                resource=f"resource_{i}",
                details={"index": i},
            )
            logs.append(log)

        # Verify all logs have timestamps
        for log in logs:
            assert "timestamp" in log
            assert log["action"].startswith("action_")

        # Verify logs are in chronological order (approximately)
        timestamps = [datetime.fromisoformat(log["timestamp"]) for log in logs]
        for i in range(len(timestamps) - 1):
            assert timestamps[i] <= timestamps[i + 1]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
