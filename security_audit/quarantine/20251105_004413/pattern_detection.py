"""
Pattern Detection Glimpse for Echoes Research Platform with Selective Attention

Enhanced pattern detection with selective attention mechanisms for authentic AI responses.
Provides focused pattern recognition using attention-based filtering and ML explainability.
"""

import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

# REMOVED: numpy import - not needed for simplified pattern detection
# REMOVED: RAG middleware imports - pattern detection now works without retrieval
# from src.rag_orbit.embeddings import EmbeddingEngine
# from src.rag_orbit.retrieval import FAISSRetriever
# from src.rag_orbit.chunking import ChunkingEngine

logger = logging.getLogger(__name__)


@dataclass
class DetectedPattern:
    """A detected pattern with metadata"""

    pattern_type: str
    description: str
    confidence: float
    span: tuple[int, int]  # (start, end) character positions
    evidence: list[str]
    related_patterns: list[str] = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.related_patterns is None:
            self.related_patterns = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict[str, Any]:
        return {
            "pattern_type": self.pattern_type,
            "description": self.description,
            "confidence": self.confidence,
            "span": self.span,
            "evidence": self.evidence,
            "related_patterns": self.related_patterns,
            "metadata": self.metadata,
        }


@dataclass
class PatternDetectionResult:
    """Result of pattern detection analysis"""

    patterns: list[DetectedPattern]
    confidence: float
    processing_time: float
    text_length: int
    timestamp: datetime
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class PatternDetector:
    """
    Enhanced pattern detection Glimpse with selective attention mechanisms.

    Provides focused pattern recognition using attention-based filtering
    and ML explainability for authentic AI responses.
    """

    def __init__(self):
        # REMOVED: RAG middleware dependencies - simplified for direct responses
        # self.embedding_engine = embedding_engine or EmbeddingEngine()
        # self.retriever = retriever
        # self.chunking_engine = chunking_engine or ChunkingEngine()

        # Pattern recognition templates with attention weights
        self.pattern_templates = {
            "temporal": [
                (r"\b(before|after|during|when|then|now|future|past|present)\b", 0.8),
                (r"\b(\d{1,2}[:/]\d{2}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b", 0.9),
                (r"\b(week|month|year|day|hour|minute)s?\b", 0.7),
            ],
            "causal": [
                (r"\b(because|therefore|thus|hence|consequently|resulting)\b", 0.9),
                (r"\b(causes?|effects?|leads? to|results? in)\b", 0.8),
                (r"\b(if|then|when|whenever)\b.*?\b(then|follows?|occurs?)\b", 0.7),
            ],
            "comparative": [
                (r"\b(more|less|better|worse|greater|smaller|faster|slower)\b", 0.8),
                (r"\b(compared? to|versus|vs\.?|than)\b", 0.9),
                (r"\b(similar|different|alike|distinct)\b", 0.7),
            ],
            "quantitative": [
                (r"\b(\d+(?:\.\d+)?%|\d+(?:\.\d+)?(?:k|m|b|trillion))\b", 0.9),
                (
                    r"\b(increase|decrease|grow|decline|rise|fall)\b.*?\b(\d+(?:\.\d+)?%?)\b",
                    0.8,
                ),
                (r"\b(approximately|about|around|roughly)\b.*?\b\d+\b", 0.6),
            ],
            "relational": [
                (r"\b(associated|correlated|linked|connected|related)\b", 0.8),
                (r"\b(depends? on|relies? on|influenced? by)\b", 0.7),
                (r"\b(interacts?|interactions?|relationships?)\b", 0.6),
            ],
        }

        # Attention threshold for pattern filtering
        self.attention_threshold = 0.6
        self.attention_weights = {
            "temporal": 0.8,
            "causal": 0.9,
            "comparative": 0.7,
            "quantitative": 0.9,
            "relational": 0.6,
        }

    async def detect_patterns(
        self,
        text: str,
        context: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
    ) -> PatternDetectionResult:
        """
        Detect patterns in text using multiple analysis techniques.

        Args:
            text: Text to analyze
            context: Additional context information
            options: Detection options and parameters

        Returns:
            PatternDetectionResult with detected patterns
        """
        start_time = datetime.utcnow()

        options = options or {}
        min_confidence = options.get("min_confidence", 0.6)
        max_patterns = options.get("max_patterns", 10)

        # Multi-stage pattern detection - simplified without RAG
        patterns = []

        # Stage 1: Rule-based pattern detection
        rule_patterns = await self._detect_rule_based_patterns(text)
        patterns.extend(rule_patterns)

        # REMOVED: Stage 2: Semantic pattern detection (requires RAG middleware)
        # if self.retriever:
        #     semantic_patterns = await self._detect_semantic_patterns(text, context)
        #     patterns.extend(semantic_patterns)

        # Stage 3: Statistical pattern analysis
        statistical_patterns = await self._detect_statistical_patterns(text)
        patterns.extend(statistical_patterns)

        # Filter and rank patterns
        filtered_patterns = [p for p in patterns if p.confidence >= min_confidence]

        # Sort by confidence and limit results
        filtered_patterns.sort(key=lambda x: x.confidence, reverse=True)
        filtered_patterns = filtered_patterns[:max_patterns]

        # Calculate overall confidence - simplified without numpy
        overall_confidence = (
            sum([p.confidence for p in filtered_patterns]) / len(filtered_patterns)
            if filtered_patterns
            else 0.0
        )

        processing_time = (datetime.utcnow() - start_time).total_seconds()

        return PatternDetectionResult(
            patterns=filtered_patterns,
            confidence=overall_confidence,
            processing_time=processing_time,
            text_length=len(text),
            timestamp=datetime.utcnow(),
            metadata={
                "detection_method": "simplified_rule_based",
                "stages_used": ["rule_based", "statistical"],
                "rag_middleware": False,  # No RAG middleware for authentic responses
            },
        )

    async def _detect_rule_based_patterns(self, text: str) -> list[DetectedPattern]:
        """Rule-based pattern detection using regex patterns with selective attention"""
        patterns = []
        text_lower = text.lower()

        # Apply selective attention to focus on important text sections
        sentences = re.split(r"[.!?]+", text)
        important_sentences = self._apply_selective_attention(sentences)
        ". ".join(important_sentences)

        for pattern_type, regex_patterns in self.pattern_templates.items():
            attention_weight = self.attention_weights.get(pattern_type, 0.5)

            for regex, _base_confidence in regex_patterns:
                matches = list(re.finditer(regex, text_lower, re.IGNORECASE))
                for match in matches:
                    # Calculate confidence with attention weighting
                    match_confidence = min(
                        0.9, len(match.group()) / 20
                    )  # Longer matches = higher confidence
                    weighted_confidence = match_confidence * attention_weight

                    # Apply selective attention filter
                    if weighted_confidence >= self.attention_threshold:
                        pattern = DetectedPattern(
                            pattern_type=pattern_type,
                            description=f"{pattern_type.title()} pattern detected: '{match.group()}'",
                            confidence=weighted_confidence,
                            span=(match.start(), match.end()),
                            evidence=[
                                f"Regex match: {regex}",
                                f"Attention weight: {attention_weight}",
                            ],
                            metadata={
                                "regex": regex,
                                "match_text": match.group(),
                                "method": "rule_based_attention",
                                "attention_weight": attention_weight,
                                "base_confidence": match_confidence,
                            },
                        )
                        patterns.append(pattern)

        return patterns

    def _apply_selective_attention(self, sentences: list[str]) -> list[str]:
        """Apply selective attention to filter important sentences"""
        important_sentences = []

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            # Calculate importance score based on various factors
            score = 0

            # Length factor (medium length sentences are often more informative)
            word_count = len(sentence.split())
            if 5 <= word_count <= 20:
                score += 0.3
            elif word_count > 20:
                score += 0.2

            # Keyword presence
            important_keywords = [
                "because",
                "therefore",
                "significant",
                "important",
                "key",
                "critical",
                "major",
            ]
            keyword_count = sum(
                1 for keyword in important_keywords if keyword in sentence.lower()
            )
            score += keyword_count * 0.2

            # Numerical data presence
            if re.search(r"\d+", sentence):
                score += 0.2

            # Apply attention threshold
            if score >= 0.3:  # Minimum importance threshold
                important_sentences.append(sentence)

        return important_sentences

    async def _detect_statistical_patterns(self, text: str) -> list[DetectedPattern]:
        """Statistical pattern analysis"""
        patterns = []

        # Word frequency analysis
        words = re.findall(r"\b\w+\b", text.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Detect repetitive patterns
        total_words = len(words)
        for word, freq in word_freq.items():
            if freq > total_words * 0.05:  # Word appears in >5% of text
                confidence = min(0.8, freq / total_words * 10)
                pattern = DetectedPattern(
                    pattern_type="repetitive",
                    description=f"Repetitive word pattern: '{word}' ({freq} occurrences)",
                    confidence=confidence,
                    span=(0, len(text)),  # Whole text
                    evidence=[f"Frequency: {freq}/{total_words}"],
                    metadata={
                        "method": "statistical",
                        "word": word,
                        "frequency": freq,
                        "total_words": total_words,
                    },
                )
                patterns.append(pattern)

        # Sentence length analysis - simplified without numpy
        sentences = re.split(r"[.!?]+", text)
        sentence_lengths = [len(s.strip().split()) for s in sentences if s.strip()]

        if sentence_lengths:
            avg_length = sum(sentence_lengths) / len(sentence_lengths)

            # Simple variance calculation
            variance = sum((x - avg_length) ** 2 for x in sentence_lengths) / len(
                sentence_lengths
            )
            std_length = variance**0.5

            if std_length > avg_length * 0.5:  # High variation in sentence length
                confidence = min(0.75, std_length / avg_length)
                pattern = DetectedPattern(
                    pattern_type="structural_variation",
                    description="High variation in sentence structure detected",
                    confidence=confidence,
                    span=(0, len(text)),
                    evidence=[f"Avg length: {avg_length:.1f}, Std: {std_length:.1f}"],
                    metadata={
                        "method": "statistical",
                        "avg_sentence_length": avg_length,
                        "std_sentence_length": std_length,
                    },
                )
                patterns.append(pattern)

        return patterns

    async def analyze_relationships(
        self, patterns: list[DetectedPattern]
    ) -> list[DetectedPattern]:
        """Analyze relationships between detected patterns"""
        # Group patterns by type and proximity
        for i, pattern in enumerate(patterns):
            related = []

            for j, other in enumerate(patterns):
                if i == j:
                    continue

                # Check if patterns are related by proximity
                if abs(pattern.span[0] - other.span[0]) < 500:  # Within 500 chars
                    if pattern.pattern_type != other.pattern_type:
                        related.append(f"{other.pattern_type}_{j}")

                # Check semantic relationships
                if pattern.pattern_type == "causal" and other.pattern_type in [
                    "temporal",
                    "comparative",
                ]:
                    related.append(f"causal_link_{j}")

            pattern.related_patterns = related

        return patterns


# Global pattern detector instance
pattern_detector = None


async def detect_patterns(
    text: str,
    context: dict[str, Any] | None = None,
    options: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Main entry point for pattern detection.

    Simplified version without RAG middleware for authentic AI responses.
    """
    global pattern_detector

    # Initialize pattern detector if needed
    if pattern_detector is None:
        pattern_detector = PatternDetector()

    # Perform detection
    result = await pattern_detector.detect_patterns(text, context, options)

    # Analyze relationships (simplified without RAG)
    result.patterns = await pattern_detector.analyze_relationships(result.patterns)

    # Convert to dict format for API
    return [pattern.to_dict() for pattern in result.patterns]
