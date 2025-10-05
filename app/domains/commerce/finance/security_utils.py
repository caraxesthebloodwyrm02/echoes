"""
Security utilities for FinanceAdvisor module

Provides encryption, PII detection, and secure data handling.
"""

import base64
import hashlib
import hmac
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logger = logging.getLogger(__name__)


class FinanceSecurity:
    """Security utilities for financial data handling"""

    def __init__(self, key: Optional[bytes] = None):
        """Initialize with encryption key"""
        if key is None:
            # In production, load from secure key management service
            key = self._generate_key()
        self.fernet = Fernet(key)

    def _generate_key(self) -> bytes:
        """Generate encryption key (for development only)"""
        # WARNING: In production, use proper key management
        salt = b"finance_advisor_salt"
        password = b"dev_encryption_key_change_in_production"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))

    def encrypt_sensitive_data(self, data: Dict) -> Dict:
        """Encrypt sensitive fields in financial data"""
        encrypted_data = data.copy()

        # Fields that typically contain sensitive information
        sensitive_fields = {
            "ssn",
            "social_security",
            "tax_id",
            "account_number",
            "routing_number",
            "credit_card",
            "bank_account",
            "salary",
            "income",
            "balance",
            "debt",
        }

        for key, value in data.items():
            if any(field in key.lower() for field in sensitive_fields):
                if isinstance(value, str):
                    encrypted_data[key] = self._encrypt_value(value)
                elif isinstance(value, (int, float)):
                    # Convert numbers to strings for encryption
                    encrypted_data[key] = self._encrypt_value(str(value))

        return encrypted_data

    def decrypt_sensitive_data(self, data: Dict) -> Dict:
        """Decrypt sensitive fields in financial data"""
        decrypted_data = data.copy()

        for key, value in data.items():
            if isinstance(value, str) and value.startswith("ENC:"):
                try:
                    decrypted_data[key] = self._decrypt_value(value)
                except Exception as e:
                    logger.warning(f"Failed to decrypt field {key}: {e}")
                    # Keep encrypted value if decryption fails

        return decrypted_data

    def _encrypt_value(self, value: str) -> str:
        """Encrypt a single value"""
        encrypted = self.fernet.encrypt(value.encode())
        return f"ENC:{encrypted.decode()}"

    def _decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a single value"""
        if not encrypted_value.startswith("ENC:"):
            return encrypted_value

        encrypted_data = encrypted_value[4:]  # Remove 'ENC:' prefix
        decrypted = self.fernet.decrypt(encrypted_data.encode())
        return decrypted.decode()

    def detect_pii(self, data: Dict) -> Dict[str, List[str]]:
        """Detect potential PII in data"""
        pii_findings = {
            "email_addresses": [],
            "phone_numbers": [],
            "social_security_numbers": [],
            "credit_card_numbers": [],
            "bank_account_numbers": [],
        }

        def scan_text(text: str) -> None:
            # Email pattern
            email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
            emails = re.findall(email_pattern, text)
            pii_findings["email_addresses"].extend(emails)

            # Phone pattern (US format)
            phone_pattern = r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b"
            phones = re.findall(phone_pattern, text)
            pii_findings["phone_numbers"].extend(phones)

            # SSN pattern
            ssn_pattern = r"\b\d{3}[-]?\d{2}[-]?\d{4}\b"
            ssn_matches = re.findall(ssn_pattern, text)
            # Filter out obvious non-SSN patterns (like dates)
            for match in ssn_matches:
                if not re.match(r"19\d{2}|20\d{2}", match):  # Not a year
                    pii_findings["social_security_numbers"].append(match)

            # Credit card pattern (basic)
            cc_pattern = r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b"
            ccs = re.findall(cc_pattern, text)
            pii_findings["credit_card_numbers"].extend(ccs)

        def scan_dict(d: Dict) -> None:
            for key, value in d.items():
                if isinstance(value, str):
                    scan_text(value)
                elif isinstance(value, dict):
                    scan_dict(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, str):
                            scan_text(item)
                        elif isinstance(item, dict):
                            scan_dict(item)

        scan_dict(data)

        # Remove duplicates
        for key in pii_findings:
            pii_findings[key] = list(set(pii_findings[key]))

        return pii_findings

    def hash_data(self, data: str, salt: Optional[str] = None) -> str:
        """Create a secure hash of data for integrity checking"""
        if salt is None:
            salt = os.urandom(16).hex()

        salted_data = f"{salt}:{data}"
        hash_obj = hashlib.sha256(salted_data.encode())
        return f"{salt}:{hash_obj.hexdigest()}"

    def verify_hash(self, data: str, hashed_value: str) -> bool:
        """Verify data integrity against hash"""
        try:
            salt, hash_value = hashed_value.split(":", 1)
            expected_hash = self.hash_data(data, salt)
            return hmac.compare_digest(expected_hash, hashed_value)
        except Exception:
            return False

    def create_audit_log(
        self, action: str, user_id: str, resource: str, details: Optional[Dict] = None
    ) -> Dict:
        """Create a standardized audit log entry"""
        return {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "user_id": user_id,
            "resource": resource,
            "details": details or {},
            "ip_address": "system",  # In production, get from request
            "user_agent": "FinanceAdvisor",
        }


# Global security instance (in production, use dependency injection)
security_manager = FinanceSecurity()
