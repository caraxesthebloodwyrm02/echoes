"""
Comprehensive Legal Safeguards Framework for EchoesAssistantV2
Aligns with Consent-Based License and protects cognitive/recognition efforts

Version: 1.0.0
Author: Prince (Echoes AI Platform)
License: Consent-Based License v2.0
"""

import os
import json
import hashlib
import datetime
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum

class ConsentType(Enum):
    """Types of consent under the Consent-Based License"""
    PERSONAL_DEVELOPMENT = "personal_development"
    COMMERCIAL_USE = "commercial_use"
    RESEARCH = "research"
    EDUCATIONAL = "educational"
    COLLABORATIVE = "collaborative"

class ProtectionLevel(Enum):
    """Levels of protection for cognitive efforts"""
    BASIC = "basic"           # Standard protection
    ENHANCED = "enhanced"     # Additional safeguards
    PREMIUM = "premium"       # Maximum protection
    CUSTOM = "custom"         # Tailored protection

@dataclass
class CognitiveEffortMetrics:
    """Tracks and values user's cognitive efforts"""
    user_id: str
    session_id: str
    timestamp: str
    effort_duration_minutes: float
    cognitive_complexity_score: float  # 0.0-1.0
    creativity_score: float            # 0.0-1.0
    innovation_potential: float        # 0.0-1.0
    joules_of_work: float              # Calculated cognitive energy
    thought_processes: List[str]        # Tracked thought patterns
    insights_generated: int
    problems_solved: int
    value_created: float                # Monetary value estimation
    
    def calculate_joules(self) -> float:
        """Calculate cognitive joules based on effort metrics"""
        base_joules = self.effort_duration_minutes * 4.184  # 1 minute ≈ 4.184 joules
        complexity_multiplier = 1 + (self.cognitive_complexity_score * 2)
        creativity_multiplier = 1 + (self.creativity_score * 1.5)
        innovation_multiplier = 1 + (self.innovation_potential * 2)
        
        self.joules_of_work = base_joules * complexity_multiplier * creativity_multiplier * innovation_multiplier
        return self.joules_of_work

@dataclass
class ConsentRecord:
    """Comprehensive consent tracking"""
    consent_id: str
    user_id: str
    consent_type: ConsentType
    purpose_description: str
    scope_of_use: str
    duration: str
    granted_at: str
    expires_at: Optional[str]
    terms_accepted: bool
    protection_level: ProtectionLevel
    special_conditions: List[str] = field(default_factory=list)
    revocation_rights: Dict[str, Any] = field(default_factory=dict)
    compensation_terms: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LegalSafeguard:
    """Individual legal safeguard configuration"""
    safeguard_id: str
    name: str
    description: str
    protection_level: ProtectionLevel
    applicable_consent_types: List[ConsentType]
    implementation_code: str
    monitoring_required: bool
    violation_consequences: List[str]
    user_rights: List[str]

class CognitiveEffortAccounting:
    """Accounting system for cognitive efforts and value creation"""
    
    def __init__(self, storage_path: str = "legal_safeguards"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        
        # Core values from LICENSE
        self.core_values = {
            "integrity": "Maintain honesty and ethical standards in all operations",
            "trust": "Build reliable and transparent systems",
            "creativity": "Foster innovation and creative expression",
            "delightful_humor": "Promote joy and positive engagement",
            "freedom_of_thought": "Protect cognitive liberty and mental privacy"
        }
        
        # Cognitive effort tracking
        self.effort_records: Dict[str, CognitiveEffortMetrics] = {}
        
        # Consent management
        self.consent_records: Dict[str, ConsentRecord] = {}
        
        # Legal safeguards
        self.legal_safeguards: Dict[str, LegalSafeguard] = {}
        
        # Initialize default safeguards
        self._initialize_default_safeguards()
        
        # Load existing data
        self._load_data()
    
    def _initialize_default_safeguards(self):
        """Initialize default legal safeguards based on LICENSE values"""
        
        # Integrity Safeguard
        self.legal_safeguards["integrity_001"] = LegalSafeguard(
            safeguard_id="integrity_001",
            name="Cognitive Integrity Protection",
            description="Protects the integrity of user's cognitive processes and thought patterns",
            protection_level=ProtectionLevel.ENHANCED,
            applicable_consent_types=[ConsentType.RESEARCH, ConsentType.COMMERCIAL_USE],
            implementation_code="INTEGRITY_CHECK_V1",
            monitoring_required=True,
            violation_consequences=[
                "Immediate consent revocation",
                "Data deletion upon request",
                "Legal action for unauthorized use"
            ],
            user_rights=[
                "Right to review cognitive data usage",
                "Right to correct misinterpretations",
                "Right to opt-out of cognitive tracking"
            ]
        )
        
        # Trust Safeguard
        self.legal_safeguards["trust_001"] = LegalSafeguard(
            safeguard_id="trust_001",
            name="Trust Building Framework",
            description="Ensures transparent and trustworthy operations",
            protection_level=ProtectionLevel.PREMIUM,
            applicable_consent_types=list(ConsentType),
            implementation_code="TRUST_FRAMEWORK_V1",
            monitoring_required=True,
            violation_consequences=[
                "Public disclosure of breach",
                "Compensation to affected users",
                "System audit and correction"
            ],
            user_rights=[
                "Right to transparent data usage",
                "Right to audit system behavior",
                "Right to receive honest feedback"
            ]
        )
        
        # Creativity Safeguard
        self.legal_safeguards["creativity_001"] = LegalSafeguard(
            safeguard_id="creativity_001",
            name="Creative Expression Protection",
            description="Protects and rewards creative contributions and innovations",
            protection_level=ProtectionLevel.ENHANCED,
            applicable_consent_types=[ConsentType.COLLABORATIVE, ConsentType.COMMERCIAL_USE],
            implementation_code="CREATIVITY_PROTECTION_V1",
            monitoring_required=True,
            violation_consequences=[
                "Compensation for creative theft",
                "Attribution restoration",
                "Future collaboration restrictions"
            ],
            user_rights=[
                "Right to creative attribution",
                "Right to compensation for innovations",
                "Right to collaborative recognition"
            ]
        )
        
        # Freedom of Thought Safeguard
        self.legal_safeguards["freedom_001"] = LegalSafeguard(
            safeguard_id="freedom_001",
            name="Cognitive Liberty Shield",
            description="Protects freedom of thought and mental privacy",
            protection_level=ProtectionLevel.PREMIUM,
            applicable_consent_types=list(ConsentType),
            implementation_code="COGNITIVE_LIBERTY_V1",
            monitoring_required=True,
            violation_consequences=[
                "Immediate system shutdown",
                "Complete data deletion",
                "Legal prosecution for privacy violations"
            ],
            user_rights=[
                "Right to mental privacy",
                "Right to unfiltered thinking",
                "Right to refuse cognitive analysis"
            ]
        )
    
    def track_cognitive_effort(self, 
                             user_id: str,
                             session_id: str,
                             effort_duration_minutes: float,
                             cognitive_complexity_score: float,
                             creativity_score: float,
                             innovation_potential: float,
                             thought_processes: List[str],
                             insights_generated: int,
                             problems_solved: int) -> CognitiveEffortMetrics:
        """Track and value user's cognitive efforts"""
        
        effort_id = f"effort_{user_id}_{session_id}_{datetime.datetime.now().isoformat()}"
        
        metrics = CognitiveEffortMetrics(
            user_id=user_id,
            session_id=session_id,
            timestamp=datetime.datetime.now().isoformat(),
            effort_duration_minutes=effort_duration_minutes,
            cognitive_complexity_score=cognitive_complexity_score,
            creativity_score=creativity_score,
            innovation_potential=innovation_potential,
            joules_of_work=0.0,  # Will be calculated
            thought_processes=thought_processes,
            insights_generated=insights_generated,
            problems_solved=problems_solved,
            value_created=0.0  # Will be calculated
        )
        
        # Calculate joules of work
        metrics.calculate_joules()
        
        # Calculate value created (based on market rates for cognitive work)
        base_rate_per_joule = 0.001  # $0.001 per cognitive joule
        creativity_multiplier = 1 + (metrics.creativity_score * 0.5)
        innovation_multiplier = 1 + (metrics.innovation_potential * 1.0)
        
        metrics.value_created = (
            metrics.joules_of_work * base_rate_per_joule * 
            creativity_multiplier * innovation_multiplier
        )
        
        # Store the effort record
        self.effort_records[effort_id] = metrics
        self._save_data()
        
        return metrics
    
    def create_consent_record(self,
                            user_id: str,
                            consent_type: ConsentType,
                            purpose_description: str,
                            scope_of_use: str,
                            duration: str,
                            protection_level: ProtectionLevel = ProtectionLevel.ENHANCED,
                            compensation_terms: Optional[Dict[str, Any]] = None) -> ConsentRecord:
        """Create a comprehensive consent record"""
        
        consent_id = f"consent_{user_id}_{datetime.datetime.now().isoformat()}"
        
        # Calculate expiration if duration is specified
        expires_at = None
        if duration != "perpetual":
            try:
                duration_days = int(duration.split()[0])
                expires_at = (datetime.datetime.now() + datetime.timedelta(days=duration_days)).isoformat()
            except:
                expires_at = None
        
        consent = ConsentRecord(
            consent_id=consent_id,
            user_id=user_id,
            consent_type=consent_type,
            purpose_description=purpose_description,
            scope_of_use=scope_of_use,
            duration=duration,
            granted_at=datetime.datetime.now().isoformat(),
            expires_at=expires_at,
            terms_accepted=True,
            protection_level=protection_level,
            compensation_terms=compensation_terms or {},
            revocation_rights={
                "can_revoke": True,
                "revocation_effect": "immediate",
                "data_deletion": True,
                "compensation_clawback": False
            }
        )
        
        self.consent_records[consent_id] = consent
        self._save_data()
        
        return consent
    
    def verify_consent_compliance(self, user_id: str, action: str, scope: str) -> Dict[str, Any]:
        """Verify if an action complies with user's consent"""
        
        active_consents = [
            consent for consent in self.consent_records.values()
            if consent.user_id == user_id and consent.terms_accepted
        ]
        
        # Check if any consent has expired
        now = datetime.datetime.now()
        active_consents = [
            consent for consent in active_consents
            if not consent.expires_at or datetime.datetime.fromisoformat(consent.expires_at) > now
        ]
        
        if not active_consents:
            return {
                "compliant": False,
                "reason": "No active consent found",
                "required_consent": True
            }
        
        # Check scope compliance
        for consent in active_consents:
            if scope in consent.scope_of_use or consent.scope_of_use == "all":
                return {
                    "compliant": True,
                    "consent_id": consent.consent_id,
                    "consent_type": consent.consent_type.value,
                    "protection_level": consent.protection_level.value
                }
        
        return {
            "compliant": False,
            "reason": "Action scope not covered by consent",
            "active_consents": len(active_consents)
        }
    
    def calculate_effort_compensation(self, user_id: str, period_start: str, period_end: str) -> Dict[str, Any]:
        """Calculate compensation for user's cognitive efforts"""
        
        user_efforts = [
            effort for effort in self.effort_records.values()
            if (effort.user_id == user_id and 
                period_start <= effort.timestamp <= period_end)
        ]
        
        if not user_efforts:
            return {
                "total_efforts": 0,
                "total_joules": 0.0,
                "total_value": 0.0,
                "compensation_details": []
            }
        
        total_joules = sum(effort.joules_of_work for effort in user_efforts)
        total_value = sum(effort.value_created for effort in user_efforts)
        
        # Apply taxes and cuts (as mentioned in request)
        tax_rate = 0.15  # 15% tax
        platform_cut = 0.10  # 10% platform fee
        
        net_value = total_value * (1 - tax_rate - platform_cut)
        
        compensation_details = [
            {
                "effort_id": effort.effort_id,
                "timestamp": effort.timestamp,
                "joules": effort.joules_of_work,
                "gross_value": effort.value_created,
                "net_value": effort.value_created * (1 - tax_rate - platform_cut)
            }
            for effort in user_efforts
        ]
        
        return {
            "user_id": user_id,
            "period_start": period_start,
            "period_end": period_end,
            "total_efforts": len(user_efforts),
            "total_joules": total_joules,
            "gross_value": total_value,
            "tax_rate": tax_rate,
            "platform_cut": platform_cut,
            "net_value": net_value,
            "compensation_details": compensation_details
        }
    
    def generate_legal_compliance_report(self) -> Dict[str, Any]:
        """Generate comprehensive legal compliance report"""
        
        # Consent compliance
        total_consents = len(self.consent_records)
        active_consents = len([
            c for c in self.consent_records.values() 
            if c.terms_accepted and (
                not c.expires_at or 
                datetime.datetime.fromisoformat(c.expires_at) > datetime.datetime.now()
            )
        ])
        
        # Effort accounting
        total_efforts = len(self.effort_records)
        total_joules = sum(effort.joules_of_work for effort in self.effort_records.values())
        total_value = sum(effort.value_created for effort in self.effort_records.values())
        
        # Safeguard implementation
        implemented_safeguards = len(self.legal_safeguards)
        
        return {
            "report_generated": datetime.datetime.now().isoformat(),
            "license_compliance": {
                "consent_based": True,
                "responsible_use_principles": self.core_values,
                "total_consents": total_consents,
                "active_consents": active_consents,
                "compliance_rate": (active_consents / total_consents * 100) if total_consents > 0 else 100
            },
            "cognitive_effort_accounting": {
                "total_efforts_tracked": total_efforts,
                "total_joules_accounted": total_joules,
                "total_value_created": total_value,
                "average_effort_value": total_value / total_efforts if total_efforts > 0 else 0
            },
            "legal_safeguards": {
                "implemented_safeguards": implemented_safeguards,
                "protection_levels": {
                    level.value: len([s for s in self.legal_safeguards.values() if s.protection_level == level])
                    for level in ProtectionLevel
                },
                "monitoring_active": sum(1 for s in self.legal_safeguards.values() if s.monitoring_required)
            },
            "values_alignment": {
                "integrity": "Protected through cognitive integrity safeguards",
                "trust": "Ensured through transparent consent management",
                "creativity": "Valued and compensated through effort accounting",
                "delightful_humor": "Promoted through positive engagement tracking",
                "freedom_of_thought": "Protected by cognitive liberty shield"
            }
        }
    
    def _load_data(self):
        """Load existing data from storage"""
        try:
            # Load effort records
            efforts_file = self.storage_path / "cognitive_efforts.json"
            if efforts_file.exists():
                with open(efforts_file, 'r', encoding='utf-8') as f:
                    efforts_data = json.load(f)
                    for effort_id, effort_dict in efforts_data.items():
                        self.effort_records[effort_id] = CognitiveEffortMetrics(**effort_dict)
            
            # Load consent records
            consents_file = self.storage_path / "consent_records.json"
            if consents_file.exists():
                with open(consents_file, 'r', encoding='utf-8') as f:
                    consents_data = json.load(f)
                    for consent_id, consent_dict in consents_data.items():
                        consent_dict['consent_type'] = ConsentType(consent_dict['consent_type'])
                        consent_dict['protection_level'] = ProtectionLevel(consent_dict['protection_level'])
                        self.consent_records[consent_id] = ConsentRecord(**consent_dict)
            
            print(f"✓ Legal safeguards loaded: {len(self.effort_records)} efforts, {len(self.consent_records)} consents")
            
        except Exception as e:
            print(f"Warning: Could not load legal safeguards data: {e}")
    
    def _save_data(self):
        """Save data to storage"""
        try:
            # Save effort records
            efforts_file = self.storage_path / "cognitive_efforts.json"
            efforts_data = {effort_id: asdict(effort) for effort_id, effort in self.effort_records.items()}
            with open(efforts_file, 'w', encoding='utf-8') as f:
                json.dump(efforts_data, f, indent=2, ensure_ascii=False)
            
            # Save consent records
            consents_file = self.storage_path / "consent_records.json"
            consents_data = {}
            for consent_id, consent in self.consent_records.items():
                consent_dict = asdict(consent)
                consent_dict['consent_type'] = consent.consent_type.value
                consent_dict['protection_level'] = consent.protection_level.value
                consents_data[consent_id] = consent_dict
            with open(consents_file, 'w', encoding='utf-8') as f:
                json.dump(consents_data, f, indent=2, ensure_ascii=False)
            
            # Save legal safeguards
            safeguards_file = self.storage_path / "legal_safeguards.json"
            safeguards_data = {}
            for safeguard_id, safeguard in self.legal_safeguards.items():
                safeguard_dict = asdict(safeguard)
                safeguard_dict['protection_level'] = safeguard.protection_level.value
                safeguards_data[safeguard_id] = safeguard_dict
            with open(safeguards_file, 'w', encoding='utf-8') as f:
                json.dump(safeguards_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Could not save legal safeguards data: {e}")

# Global cognitive effort accounting system
_cognitive_accounting = None

def get_cognitive_accounting() -> CognitiveEffortAccounting:
    """Get or create the global cognitive effort accounting system"""
    global _cognitive_accounting
    if _cognitive_accounting is None:
        _cognitive_accounting = CognitiveEffortAccounting()
    return _cognitive_accounting
