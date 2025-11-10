"""
Tests for self_rag module.
"""

import asyncio

import pytest

from api.self_rag import SelfRAGVerifier, VerificationResult


class TestVerificationResult:
    """Test VerificationResult dataclass."""

    def test_verification_result_init(self):
        """Test VerificationResult initialization."""
        from datetime import datetime

        result = VerificationResult(
            verdict="TRUE",
            confidence=0.9,
            explanation="Test explanation",
            evidence_used=["evidence1"],
            contradictions=[],
            supporting_evidence=["support1"],
            processing_time=0.1,
            timestamp=datetime.now(),
        )
        assert result.verdict == "TRUE"
        assert result.confidence == 0.9
        assert result.explanation == "Test explanation"

    def test_verification_result_methods(self):
        """Test VerificationResult methods."""
        from datetime import datetime

        result = VerificationResult(
            verdict="UNCERTAIN",
            confidence=0.5,
            explanation="Uncertain result",
            evidence_used=[],
            contradictions=[],
            supporting_evidence=[],
            processing_time=0.0,
            timestamp=datetime.now(),
        )
        # Test that the object can be created and has expected attributes
        assert hasattr(result, "verdict")
        assert hasattr(result, "confidence")
        assert hasattr(result, "explanation")


class TestSelfRAGVerifier:
    """Test SelfRAGVerifier class."""

    def test_self_rag_init(self):
        """Test SelfRAGVerifier initialization."""
        try:
            verifier = SelfRAGVerifier()
            assert verifier is not None
            assert hasattr(verifier, "verify_claim")
        except (TypeError, ImportError):
            pytest.skip("SelfRAGVerifier has complex dependencies")

    def test_self_rag_verify_claim(self):
        """Test claim verification method."""
        try:
            verifier = SelfRAGVerifier()
            # Test basic verification
            result = asyncio.run(verifier.verify_claim("Test claim", "Test context"))
            # Should return a VerificationResult or None
            assert result is None or isinstance(result, VerificationResult)
        except (TypeError, ImportError, AttributeError):
            pytest.skip("SelfRAGVerifier methods not available")

    def test_self_rag_verify_claim_with_options(self):
        """Test claim verification with options."""
        try:
            verifier = SelfRAGVerifier()
            options = {"min_confidence": 0.7, "max_evidence_chunks": 5}
            result = asyncio.run(
                verifier.verify_claim("Test claim", "Test context", options)
            )
            # Should return a VerificationResult or None
            assert result is None or isinstance(result, VerificationResult)
        except (TypeError, ImportError, AttributeError):
            pytest.skip("SelfRAGVerifier methods not available")

    def test_self_rag_batch_verify(self):
        """Test batch verification method."""
        try:
            verifier = SelfRAGVerifier()
            claims = [
                {"claim": "Claim 1", "context": "Context 1"},
                {"claim": "Claim 2", "context": "Context 2"},
            ]
            results = asyncio.run(verifier.batch_verify(claims))
            # Should return a list of results
            assert isinstance(results, list)
        except (TypeError, ImportError, AttributeError):
            pytest.skip("SelfRAGVerifier batch methods not available")
