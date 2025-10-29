# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Privacy Filter Module
Provides comprehensive PII detection and filtering capabilities
"""

import hashlib
import re
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class PIIEntity:
    """Represents a detected PII entity"""

    type: str
    value: str
    start: int
    end: int
    confidence: float = 1.0


class PrivacyFilter:
    """
    Comprehensive PII detection and filtering system

    Supports multiple filtering modes:
    - redact: Complete removal with [REDACTED]
    - anonymize: Consistent token replacement
    - mask: Partial information display
    """

    def __init__(self):
        # PII patterns - ordered by specificity (most specific first)
        self.patterns = {
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
            "phone": re.compile(r"\b(\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b"),
            "ssn": re.compile(r"\b\d{3}[\s.-]\d{2}[\s.-]\d{4}\b"),
            "ip_address": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
            "date_of_birth": re.compile(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{4}\b"),
        }

        # Token cache for consistent anonymization
        self.token_cache: Dict[str, str] = {}

    def detect_pii(self, text: str) -> List[PIIEntity]:
        """Detect all PII entities in text"""
        entities = []

        for pii_type, pattern in self.patterns.items():
            for match in pattern.finditer(text):
                entity = PIIEntity(
                    type=pii_type,
                    value=match.group(),
                    start=match.start(),
                    end=match.end(),
                )
                entities.append(entity)

        return entities

    def redact(self, text: str) -> str:
        """
        Complete PII removal - replaces all PII with [REDACTED]
        Maximum privacy protection
        """
        entities = self.detect_pii(text)
        result = text

        # Sort by end position to avoid offset issues
        entities.sort(key=lambda x: x.end, reverse=True)

        for entity in entities:
            result = result[: entity.start] + "[REDACTED]" + result[entity.end :]

        return result

    def anonymize(self, text: str, deterministic: bool = True) -> str:
        """
        Consistent token replacement
        Same input always produces same token (useful for data analysis)
        """
        entities = self.detect_pii(text)
        result = text

        # Sort by end position to avoid offset issues
        entities.sort(key=lambda x: x.end, reverse=True)

        for entity in entities:
            if deterministic:
                token = self._get_consistent_token(entity.value, entity.type)
            else:
                token = self._get_random_token(entity.type)

            result = result[: entity.start] + token + result[entity.end :]

        return result

    def mask(self, text: str) -> str:
        """
        Partial information display
        Shows limited information while maintaining some context
        """
        entities = self.detect_pii(text)
        result = text

        # Sort by end position to avoid offset issues
        entities.sort(key=lambda x: x.end, reverse=True)

        for entity in entities:
            masked = self._mask_entity(entity)
            result = result[: entity.start] + masked + result[entity.end :]

        return result

    def _get_consistent_token(self, value: str, pii_type: str) -> str:
        """Generate consistent token for anonymization"""
        if value in self.token_cache:
            return self.token_cache[value]

        # Create hash-based token
        hash_obj = hashlib.md5(f"{pii_type}:{value}".encode())
        token = f"[{pii_type.upper()}_{hash_obj.hexdigest()[:8]}]"

        self.token_cache[value] = token
        return token

    def _get_random_token(self, pii_type: str) -> str:
        """Generate random token"""
        import secrets

        token = secrets.token_hex(4)
        return f"[{pii_type.upper()}_{token}]"

    def _mask_entity(self, entity: PIIEntity) -> str:
        """Mask PII entity based on type"""
        if entity.type == "email":
            # john.doe@example.com -> j***@e*******
            parts = entity.value.split("@")
            if len(parts) == 2:
                username = parts[0][:1] + "*" * (len(parts[0]) - 1) if len(parts[0]) > 1 else "*"
                domain_parts = parts[1].split(".")
                domain = domain_parts[0][:1] + "*" * (len(domain_parts[0]) - 1) if len(domain_parts[0]) > 1 else "*"
                return f"{username}@{domain}.{'*' * len('.'.join(domain_parts[1:]))}"

        elif entity.type == "phone":
            # (555) 123-4567 -> (555) ***-****
            return re.sub(r"\d(?=\d{4})", "*", entity.value)

        elif entity.type == "ssn":
            # 123-45-6789 -> ***-**-6789
            return "***-**-****"

        elif entity.type == "credit_card":
            # 1234 5678 9012 3456 -> **** **** **** 3456
            parts = entity.value.replace(" ", "").replace("-", "")
            return f"{'*' * 12} {parts[-4:]}"

        elif entity.type == "ip_address":
            # 192.168.1.1 -> 192.***.***.***
            parts = entity.value.split(".")
            return f"{parts[0]}.***.***.***"

        elif entity.type == "date_of_birth":
            # 01/15/1990 -> **/**/1990
            parts = re.split(r"[/-]", entity.value)
            if len(parts) == 3:
                return f"**/**/{parts[2]}"

        # Default: show first and last character
        if len(entity.value) <= 2:
            return "*" * len(entity.value)
        return entity.value[0] + "*" * (len(entity.value) - 2) + entity.value[-1]
