"""
Enhanced Truth Verification Glimpse with Selective Attention

Advanced claim verification using selective attention mechanisms and ML explainability
for authentic AI responses with focused evidence analysis.
"""

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from echoes.utils.selective_attention import selective_attention_evidence

# REMOVED: RAG middleware imports - using direct AI responses
# from src.rag_orbit.embeddings import EmbeddingEngine
# from src.rag_orbit.retrieval import FAISSRetriever
# from src.rag_orbit.chunking import ChunkingEngine

logger = logging.getLogger(__name__)


@dataclass
class VerificationResult:
    """Result of truth verification"""

    verdict: str  # TRUE, FALSE, UNCERTAIN
    confidence: float  # 0-1
    explanation: str
    evidence_used: list[str]
    contradictions: list[str]
    supporting_evidence: list[str]
    processing_time: float
    timestamp: datetime


@dataclass
class EvidenceChunk:
    """A piece of evidence with relevance score"""

    text: str
    relevance_score: float
    source: str
    metadata: dict[str, Any]


class SelfRAGVerifier:
    """
    Enhanced truth verification with selective attention mechanisms.

    Advanced claim verification using attention-based evidence filtering
    and ML explainability for authentic AI responses.
    """

    def __init__(self):
        # REMOVED: RAG middleware dependencies
        # self.embedding_engine = embedding_engine or EmbeddingEngine()
        # self.retriever = retriever
        # self.chunking_engine = chunking_engine or ChunkingEngine()

        # Verification thresholds with selective attention
        self.min_evidence_threshold = 0.5
        self.contradiction_threshold = 0.6
        self.uncertainty_threshold = 0.4

        # Selective attention configuration
        self.attention_threshold = 0.7
        self.attention_weights = {
            "direct_support": 0.9,
            "contextual": 0.6,
            "provided": 0.8,
            "semantic_similarity": 0.7,
        }

        # Evidence importance factors
        self.importance_factors = {
            "source_credibility": 0.3,
            "recency": 0.2,
            "specificity": 0.3,
            "corroboration": 0.2,
        }

    async def verify_claim(
        self,
        claim: str,
        evidence: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> VerificationResult:
        """
        Verify the truth of a claim using SELF-RAG methodology.

        Args:
            claim: The claim to verify
            evidence: Optional additional evidence to consider
            context: Additional context information

        Returns:
            VerificationResult with verdict and explanation
        """
        start_time = datetime.now(UTC)

        try:
            # Step 1: Gather relevant evidence
            relevant_evidence = await self._gather_evidence(claim, evidence, context)

            # Step 2: Analyze claim against evidence
            analysis = await self._analyze_claim_against_evidence(
                claim, relevant_evidence
            )

            # Step 3: Generate verdict with confidence
            verdict, confidence, explanation = await self._generate_verdict(
                claim, analysis, relevant_evidence
            )

            processing_time = (datetime.now(UTC) - start_time).total_seconds()

            return VerificationResult(
                verdict=verdict,
                confidence=confidence,
                explanation=explanation,
                evidence_used=[e.text for e in relevant_evidence],
                contradictions=analysis.get("contradictions", []),
                supporting_evidence=analysis.get("supporting", []),
                processing_time=processing_time,
                timestamp=datetime.now(UTC),
            )

        except Exception as e:
            logger.error(f"Truth verification failed: {e}")
            processing_time = (datetime.now(UTC) - start_time).total_seconds()

            return VerificationResult(
                verdict="UNCERTAIN",
                confidence=0.0,
                explanation=f"Verification failed due to error: {str(e)}",
                evidence_used=[],
                contradictions=[],
                supporting_evidence=[],
                processing_time=processing_time,
                timestamp=datetime.now(UTC),
            )

    async def _gather_evidence(
        self,
        claim: str,
        provided_evidence: list[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> list[EvidenceChunk]:
        """
        Gather relevant evidence for claim verification using selective attention.

        Enhanced version with attention-based evidence filtering and importance scoring.
        """
        evidence_chunks = []

        # Add provided evidence with attention weighting
        if provided_evidence:
            for i, text in enumerate(provided_evidence):
                # Calculate attention-weighted relevance score
                base_relevance = 0.8
                attention_weight = self.attention_weights.get("provided", 0.8)
                weighted_relevance = base_relevance * attention_weight

                # Apply selective attention filter
                if weighted_relevance >= self.attention_threshold:
                    chunk = EvidenceChunk(
                        text=text,
                        relevance_score=weighted_relevance,
                        source="provided",
                        metadata={
                            "index": i,
                            "attention_weight": attention_weight,
                            "importance_score": self._calculate_importance_score(
                                text, "provided"
                            ),
                        },
                    )
                    evidence_chunks.append(chunk)

        # REMOVED: Knowledge base retrieval - no RAG middleware
        # if self.retriever:
        #     try:
        #         # Get embedding for claim
        #         claim_embedding = await self.embedding_engine.get_embedding(claim)
        #
        #         # Search for relevant documents
        #         results, _ = self.retriever.search(claim_embedding, top_k=5)
        #
        #         for result in results:
        #             if result.similarity_score > self.min_evidence_threshold:
        #                 chunk = EvidenceChunk(
        #                     text=result.text,
        #                     relevance_score=result.similarity_score,
        #                     source="knowledge_base",
        #                     metadata={
        #                         "chunk_id": result.chunk_id,
        #                         "similarity": result.similarity_score
        #                     }
        #                 )
        #                 evidence_chunks.append(chunk)
        #
        #     except Exception as e:
        #         logger.warning(f"Knowledge base retrieval failed: {e}")

        # Add context as evidence if available with attention weighting
        if context:
            context_text = str(context)
            if context_text:
                base_relevance = 0.5
                attention_weight = self.attention_weights.get("contextual", 0.6)
                weighted_relevance = base_relevance * attention_weight

                # Apply selective attention filter
                if (
                    weighted_relevance >= self.attention_threshold * 0.8
                ):  # Lower threshold for context
                    chunk = EvidenceChunk(
                        text=context_text,
                        relevance_score=weighted_relevance,
                        source="context",
                        metadata={
                            "type": "context",
                            "attention_weight": attention_weight,
                            "importance_score": self._calculate_importance_score(
                                context_text, "context"
                            ),
                        },
                    )
                    evidence_chunks.append(chunk)

        # Apply selective attention to filter most important evidence
        filtered_evidence = selective_attention_evidence(
            [self._evidence_chunk_to_dict(chunk) for chunk in evidence_chunks],
            self.attention_threshold,
        )

        # Convert back to EvidenceChunk objects
        final_evidence = [self._dict_to_evidence_chunk(e) for e in filtered_evidence]

        return final_evidence

    def _calculate_importance_score(self, text: str, source_type: str) -> float:
        """Calculate importance score for evidence based on various factors"""
        score = 0.0

        # Source credibility factor
        credibility_map = {"provided": 0.8, "context": 0.5, "knowledge_base": 0.9}
        score += self.importance_factors["source_credibility"] * credibility_map.get(
            source_type, 0.5
        )

        # Specificity factor (longer, more detailed text gets higher score)
        word_count = len(text.split())
        if word_count > 20:
            score += self.importance_factors["specificity"] * 0.8
        elif word_count > 10:
            score += self.importance_factors["specificity"] * 0.6
        else:
            score += self.importance_factors["specificity"] * 0.3

        # Numerical data presence (indicates factual content)
        import re

        if re.search(r"\d+", text):
            score += self.importance_factors["specificity"] * 0.2

        # Corroboration factor (simplified - would need multiple sources for real implementation)
        score += self.importance_factors["corroboration"] * 0.5

        return min(1.0, score)

    def _evidence_chunk_to_dict(self, chunk: EvidenceChunk) -> dict[str, Any]:
        """Convert EvidenceChunk to dictionary for filtering"""
        return {
            "text": chunk.text,
            "relevance_score": chunk.relevance_score,
            "source": chunk.source,
            "metadata": chunk.metadata,
        }

    def _dict_to_evidence_chunk(self, data: dict[str, Any]) -> EvidenceChunk:
        """Convert dictionary back to EvidenceChunk"""
        return EvidenceChunk(
            text=data["text"],
            relevance_score=data["relevance_score"],
            source=data["source"],
            metadata=data["metadata"],
        )

    async def _analyze_claim_against_evidence(
        self, claim: str, evidence: list[EvidenceChunk]
    ) -> dict[str, Any]:
        """
        Analyze claim against gathered evidence to identify support and contradictions.
        """
        supporting_evidence = []
        contradictions = []
        neutral_evidence = []

        # Simple semantic analysis (can be enhanced with LLM)
        claim_lower = claim.lower()

        for chunk in evidence:
            text_lower = chunk.text.lower()

            # Check for direct support
            support_keywords = ["true", "correct", "verified", "confirmed", "supports"]
            contradiction_keywords = [
                "false",
                "incorrect",
                "contradicts",
                "denies",
                "refutes",
            ]

            support_score = sum(1 for word in support_keywords if word in text_lower)
            contradiction_score = sum(
                1 for word in contradiction_keywords if word in text_lower
            )

            # Calculate semantic similarity (simple approach)
            claim_words = set(claim_lower.split())
            text_words = set(text_lower.split())
            overlap = len(claim_words.intersection(text_words))
            similarity = (
                overlap / max(len(claim_words), len(text_words))
                if max(len(claim_words), len(text_words)) > 0
                else 0
            )

            if contradiction_score > support_score and similarity > 0.3:
                contradictions.append(chunk.text)
            elif support_score > contradiction_score and similarity > 0.2:
                supporting_evidence.append(chunk.text)
            else:
                neutral_evidence.append(chunk.text)

        return {
            "supporting": supporting_evidence,
            "contradictions": contradictions,
            "neutral": neutral_evidence,
            "evidence_count": len(evidence),
        }

    async def _generate_verdict(
        self, claim: str, analysis: dict[str, Any], evidence: list[EvidenceChunk]
    ) -> tuple[str, float, str]:
        """
        Generate final verdict based on evidence analysis.
        """
        supporting_count = len(analysis["supporting"])
        contradiction_count = len(analysis["contradictions"])
        total_evidence = len(evidence)

        if total_evidence == 0:
            return "UNCERTAIN", 0.0, "No evidence available for verification"

        # Calculate confidence based on evidence balance
        support_ratio = supporting_count / total_evidence
        contradiction_ratio = contradiction_count / total_evidence

        if contradiction_ratio > support_ratio and contradiction_count > 0:
            # Contradictions outweigh support
            confidence = min(0.9, contradiction_ratio)
            verdict = "FALSE"
            explanation = (
                f"Claim contradicted by {contradiction_count} evidence sources"
            )
        elif support_ratio > contradiction_ratio and supporting_count > 0:
            # Support outweighs contradictions
            confidence = min(0.9, support_ratio)
            verdict = "TRUE"
            explanation = f"Claim supported by {supporting_count} evidence sources"
        else:
            # Balanced or insufficient evidence
            confidence = max(0.1, 1.0 - (support_ratio + contradiction_ratio))
            verdict = "UNCERTAIN"
            explanation = f"Insufficient evidence: {supporting_count} supporting, {contradiction_count} contradicting"

        # Adjust confidence based on evidence quality - simplified without numpy
        avg_relevance = (
            sum([e.relevance_score for e in evidence]) / len(evidence)
            if evidence
            else 0
        )
        confidence *= avg_relevance

        return verdict, confidence, explanation


# Global verifier instance
verifier = None


async def verify_truth(
    claim: str, evidence: list[str] | None = None, context: dict[str, Any] | None = None
) -> dict[str, Any]:
    """
    Main entry point for truth verification.

    Simplified version without RAG middleware for authentic AI responses.
    """
    global verifier

    # Initialize verifier if needed - simplified without RAG engines
    if verifier is None:
        verifier = SelfRAGVerifier()

    # Perform verification
    result = await verifier.verify_claim(claim, evidence, context)

    # Return in expected format
    return {
        "verdict": result.verdict,
        "confidence": result.confidence,
        "explanation": result.explanation,
        "evidence_used": result.evidence_used,
        "contradictions": result.contradictions,
        "supporting_evidence": result.supporting_evidence,
        "processing_time": result.processing_time,
        "timestamp": result.timestamp.isoformat(),
    }
