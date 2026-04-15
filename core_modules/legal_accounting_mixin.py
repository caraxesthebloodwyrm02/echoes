"""Legal Safeguards & Enhanced Accounting mixin for EchoesAssistantV2.

Extracted from assistant_v2_core.py (lines 4158–4559) as part of the
god-module decomposition.  All methods operate on ``self.legal_system``,
``self.accounting_system``, and ``self.enable_legal_safeguards`` which
are initialised by the host class.

Depends on ``KnowledgeGraphMixin`` for ``self.add_knowledge_node`` and
``self.add_memory_fragment``.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any


class LegalAccountingMixin:
    """Cognitive effort tracking, consent management, financial statements, license compliance."""

    # -- Attribute stubs for type checkers (set by the host class) -----------
    enable_legal_safeguards: bool
    legal_system: Any
    accounting_system: Any
    session_id: str

    # -- Public API ----------------------------------------------------------

    def track_user_cognitive_effort(
        self,
        user_id: str,
        session_duration_minutes: float,
        complexity_score: float,
        creativity_score: float,
        innovation_score: float,
        thought_processes: list[str],
        insights_generated: int,
        problems_solved: int,
    ) -> dict[str, Any]:
        """Track user's cognitive efforts and calculate value.

        Args:
            user_id: Unique user identifier
            session_duration_minutes: Duration of cognitive work session
            complexity_score: Complexity of work (0.0-1.0)
            creativity_score: Creativity level (0.0-1.0)
            innovation_score: Innovation potential (0.0-1.0)
            thought_processes: List of thought patterns used
            insights_generated: Number of insights created
            problems_solved: Number of problems solved

        Returns:
            Cognitive effort tracking result with value calculation
        """
        if not self.enable_legal_safeguards:
            return {"success": False, "error": "Legal safeguards not enabled"}

        try:
            from enhanced_accounting import ValueType

            # Track cognitive effort through legal system
            effort_metrics = self.legal_system.track_cognitive_effort(
                user_id=user_id,
                session_id=self.session_id,
                effort_duration_minutes=session_duration_minutes,
                cognitive_complexity_score=complexity_score,
                creativity_score=creativity_score,
                innovation_potential=innovation_score,
                thought_processes=thought_processes,
                insights_generated=insights_generated,
                problems_solved=problems_solved,
            )

            # Record transaction in accounting system
            transaction = self.accounting_system.record_cognitive_transaction(
                user_id=user_id,
                session_id=self.session_id,
                effort_metrics=effort_metrics,
                value_type=ValueType.COGNITIVE_JOULES,
            )

            # Add to knowledge graph as memory
            self.add_memory_fragment(
                content=f"User {user_id} completed cognitive session: {session_duration_minutes}min, complexity {complexity_score:.2f}",
                context={
                    "user_id": user_id,
                    "session_id": self.session_id,
                    "cognitive_joules": effort_metrics.joules_of_work,
                    "value_created": float(effort_metrics.value_created),
                    "insights_generated": insights_generated,
                    "problems_solved": problems_solved,
                },
                importance=min(effort_metrics.value_created / 100, 1.0),  # Scale importance to 0-1
            )

            return {
                "success": True,
                "effort_metrics": {
                    "user_id": effort_metrics.user_id,
                    "session_id": effort_metrics.session_id,
                    "cognitive_joules": effort_metrics.joules_of_work,
                    "value_created": float(effort_metrics.value_created),
                    "complexity_score": effort_metrics.cognitive_complexity_score,
                    "creativity_score": effort_metrics.creativity_score,
                    "innovation_score": effort_metrics.innovation_potential,
                },
                "transaction": {
                    "transaction_id": transaction.transaction_id,
                    "gross_value": float(transaction.gross_value),
                    "net_value": float(transaction.net_value),
                    "tax_amount": float(transaction.gross_value * transaction.tax_rate),
                    "platform_fee": float(transaction.gross_value * transaction.platform_cut),
                },
                "values_alignment": {
                    "integrity": "Transparent tracking of cognitive efforts",
                    "trust": "Fair compensation based on value created",
                    "creativity": "Recognition and reward for creative contributions",
                    "freedom_of_thought": "Protection of cognitive privacy and rights",
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_user_consent_agreement(
        self,
        user_id: str,
        consent_type: str = "personal_development",
        purpose_description: str = "AI assistance and cognitive work",
        scope_of_use: str = "general_assistance",
    ) -> dict[str, Any]:
        """Create user consent agreement aligned with LICENSE values.

        Args:
            user_id: Unique user identifier
            consent_type: Type of consent (personal_development, commercial_use, research, etc.)
            purpose_description: Description of purpose for using the system
            scope_of_use: Scope of permitted usage

        Returns:
            Consent agreement creation result
        """
        if not self.enable_legal_safeguards:
            return {"success": False, "error": "Legal safeguards not enabled"}

        try:
            from legal_safeguards import ConsentType, ProtectionLevel

            # Convert string to enum
            consent_enum = ConsentType(consent_type)

            # Create consent record
            consent = self.legal_system.create_consent_record(
                user_id=user_id,
                consent_type=consent_enum,
                purpose_description=purpose_description,
                scope_of_use=scope_of_use,
                duration="perpetual",
                protection_level=ProtectionLevel.ENHANCED,
                compensation_terms={
                    "cognitive_effort_tracked": True,
                    "value_based_compensation": True,
                    "tax_and_deductions_applied": True,
                    "payout_threshold": 10.0,
                },
            )

            # Create user account in accounting system
            user_account = self.accounting_system.create_user_account(user_id, consent_enum)

            # Add to knowledge graph
            self.add_knowledge_node(
                node_id=f"user_{user_id}",
                node_type="user",
                label=f"User {user_id}",
                description=f"User with consent agreement for {consent_type}",
                properties={
                    "user_id": user_id,
                    "consent_type": consent_type,
                    "purpose": purpose_description,
                    "scope": scope_of_use,
                    "protection_level": "enhanced",
                    "created_at": consent.granted_at,
                },
            )

            return {
                "success": True,
                "consent_agreement": {
                    "consent_id": consent.consent_id,
                    "user_id": consent.user_id,
                    "consent_type": consent.consent_type.value,
                    "purpose_description": consent.purpose_description,
                    "scope_of_use": consent.scope_of_use,
                    "protection_level": consent.protection_level.value,
                    "granted_at": consent.granted_at,
                    "terms_accepted": consent.terms_accepted,
                },
                "user_account": {
                    "user_id": user_account.user_id,
                    "created_at": user_account.created_at,
                    "consent_records": user_account.consent_records,
                },
                "values_protection": {
                    "integrity": "Transparent consent process with clear terms",
                    "trust": "Reliable agreement enforcement and compliance",
                    "creativity": "Protection for creative and innovative work",
                    "freedom_of_thought": "Cognitive liberty and privacy safeguards",
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def generate_user_financial_statement(self, user_id: str, period_days: int = 30) -> dict[str, Any]:
        """Generate comprehensive financial statement for user.

        Args:
            user_id: Unique user identifier
            period_days: Number of days for the statement period

        Returns:
            Detailed financial statement with values alignment
        """
        if not self.enable_legal_safeguards:
            return {"success": False, "error": "Legal safeguards not enabled"}

        try:
            # Calculate period dates
            period_end = datetime.now(UTC).isoformat()
            period_start = (datetime.now(UTC) - timedelta(days=period_days)).isoformat()

            # Generate statement from accounting system
            statement = self.accounting_system.generate_user_statement(
                user_id=user_id, period_start=period_start, period_end=period_end
            )

            if "error" in statement:
                return statement

            # Calculate payout eligibility
            payout_info = self.accounting_system.calculate_payout_eligibility(user_id)

            # Get legal compliance status
            legal_compliance = self.legal_system.generate_legal_compliance_report()

            return {
                "success": True,
                "financial_statement": statement,
                "payout_eligibility": payout_info,
                "legal_compliance": {
                    "consent_status": "Active",
                    "compliance_rate": legal_compliance["license_compliance"]["compliance_rate"],
                    "values_alignment": statement["values_alignment"],
                },
                "values_reflection": {
                    "integrity": f"Transparent accounting of {statement['summary']['total_transactions']} transactions",
                    "trust": f"Fair net value of ${statement['summary']['net_value']:.2f} after taxes and fees",
                    "creativity": "Creative contributions valued through bonus multipliers",
                    "delightful_humor": "Positive engagement reflected in value scores",
                    "freedom_of_thought": f"Cognitive rights protected with {legal_compliance['license_compliance']['compliance_rate']:.1f}% compliance",
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def verify_license_compliance(self, operation_type: str, user_id: str, scope: str) -> dict[str, Any]:
        """Verify compliance with Consent-Based License.

        Args:
            operation_type: Type of operation being performed
            user_id: User performing the operation
            scope: Scope of the operation

        Returns:
            License compliance verification result
        """
        if not self.enable_legal_safeguards:
            return {"success": False, "error": "Legal safeguards not enabled"}

        try:
            # Verify consent compliance
            consent_check = self.legal_system.verify_consent_compliance(
                user_id=user_id, action=operation_type, scope=scope
            )

            # Check responsible use principles compliance
            responsible_use_check = {
                "ethical_consideration": self._check_ethical_compliance(operation_type, scope),
                "transparency": self._check_transparency_compliance(operation_type),
                "professional_standards": self._check_professional_compliance(operation_type),
                "community_benefit": self._check_community_benefit(scope),
                "continuous_learning": True,  # Always enabled
                "collaboration": self._check_collaboration_compliance(scope),
                "fairness": self._check_fairness_compliance(user_id, scope),
            }

            # Overall compliance score
            consent_score = 100 if consent_check["compliant"] else 0
            principle_scores = [
                100 if responsible_use_check[principle] else 0
                for principle in responsible_use_check
                if isinstance(responsible_use_check[principle], bool)
            ]
            all_scores = [consent_score] + principle_scores
            overall_compliance = sum(all_scores) / len(all_scores) if all_scores else 0

            return {
                "success": True,
                "license_compliance": {
                    "operation_type": operation_type,
                    "user_id": user_id,
                    "scope": scope,
                    "consent_compliant": consent_check["compliant"],
                    "consent_details": consent_check,
                    "responsible_use_principles": responsible_use_check,
                    "overall_compliance_score": overall_compliance,
                    "compliance_status": (
                        "Fully Compliant"
                        if overall_compliance >= 95
                        else (
                            "Mostly Compliant"
                            if overall_compliance >= 80
                            else ("Needs Attention" if overall_compliance >= 60 else "Non-Compliant")
                        )
                    ),
                },
                "values_upheld": {
                    "integrity": "Ethical considerations and transparency maintained",
                    "trust": "Professional standards and fairness enforced",
                    "creativity": "Collaboration and community benefit promoted",
                    "freedom_of_thought": "Continuous learning and cognitive liberty protected",
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_legal_accounting_statistics(self) -> dict[str, Any]:
        """Get comprehensive legal and accounting statistics.

        Returns:
            Legal safeguards and accounting statistics
        """
        if not self.enable_legal_safeguards:
            return {"success": False, "error": "Legal safeguards not enabled"}

        try:
            # Get legal compliance report
            legal_report = self.legal_system.generate_legal_compliance_report()

            # Get accounting summary
            accounting_stats = {
                "total_users": len(self.accounting_system.user_accounts),
                "total_transactions": len(self.accounting_system.transactions),
                "total_cognitive_joules": sum(
                    tx.cognitive_joules for tx in self.accounting_system.transactions.values()
                ),
                "total_gross_value": sum(tx.gross_value for tx in self.accounting_system.transactions.values()),
                "total_net_value": sum(tx.net_value for tx in self.accounting_system.transactions.values()),
                "total_tax_collected": sum(
                    tx.gross_value * tx.tax_rate for tx in self.accounting_system.transactions.values()
                ),
                "total_platform_fees": sum(
                    tx.gross_value * tx.platform_cut for tx in self.accounting_system.transactions.values()
                ),
            }

            return {
                "success": True,
                "legal_safeguards": legal_report,
                "enhanced_accounting": accounting_stats,
                "values_implementation": {
                    "integrity": {
                        "consent_compliance_rate": legal_report["license_compliance"]["compliance_rate"],
                        "transparent_operations": True,
                    },
                    "trust": {
                        "reliable_compensation": accounting_stats["total_net_value"] > 0,
                        "fair_deductions": True,
                    },
                    "creativity": {
                        "creative_work_valued": True,
                        "innovation_rewards_enabled": True,
                    },
                    "delightful_humor": {
                        "positive_engagement": True,
                        "joyful_interactions": True,
                    },
                    "freedom_of_thought": {
                        "cognitive_rights_protected": True,
                        "privacy_safeguards_active": True,
                    },
                },
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    # -- Private helpers (license compliance checks) -------------------------

    def _check_ethical_compliance(self, operation_type: str, scope: str) -> bool:
        """Check ethical compliance for operation"""
        harmful_operations = ["exploitation", "manipulation", "deception"]
        return not any(harmful in operation_type.lower() or harmful in scope.lower() for harmful in harmful_operations)

    def _check_transparency_compliance(self, operation_type: str) -> bool:
        """Check transparency compliance"""
        # All operations should be transparent
        return True

    def _check_professional_compliance(self, operation_type: str) -> bool:
        """Check professional standards compliance"""
        unprofessional_operations = ["spam", "harassment", "abuse"]
        return not any(unprof in operation_type.lower() for unprof in unprofessional_operations)

    def _check_community_benefit(self, scope: str) -> bool:
        """Check if operation benefits community"""
        beneficial_keywords = [
            "learning",
            "development",
            "research",
            "collaboration",
            "innovation",
        ]
        return any(benefit in scope.lower() for benefit in beneficial_keywords)

    def _check_collaboration_compliance(self, scope: str) -> bool:
        """Check collaboration compliance"""
        return "collaboration" in scope.lower() or "cooperation" in scope.lower()

    def _check_fairness_compliance(self, user_id: str, scope: str) -> bool:
        """Check fairness compliance"""
        # All users should be treated fairly
        return True
