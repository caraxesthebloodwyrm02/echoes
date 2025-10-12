"""
Semantic Skill Matching: Conceptual Spine & Architecture
Core Insight: Moving beyond keyword matching to understanding intent, context, and relationships.

The "semantic" difference:
- Traditional: "Python" → keyword search → exact matches only
- Semantic: "Python" → understands it relates to "Python programming", "Data Science", "Pandas", etc.
"""

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
from sentence_transformers import SentenceTransformer


@dataclass
class SemanticVector:
    """Represents a skill with semantic understanding"""

    vector: np.ndarray
    confidence: float
    semantic_tags: set
    original_text: str
    context: str = "general"


@dataclass
class ContextualEmbedding:
    """Skill embedding adjusted for specific context"""

    vector: np.ndarray
    original_embedding: SemanticVector
    context: str
    relevance_score: float


@dataclass
class MatchScore:
    """Semantic match score with explainable components"""

    score: float
    components: Dict[str, float]
    explanation: str


class SemanticEmbeddingEngine:
    """
    Convert skills to vectors that capture actual meaning.
    Core of the semantic understanding.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.base_model = SentenceTransformer(model_name)
        self.skill_ontology = SkillOntology()
        self.domain_contexts = DomainContextRegistry()
        self.embedding_cache = {}  # Performance optimization

    def embed_skill(self, skill_text: str, context: str = "general") -> SemanticVector:
        """Embed skill with contextual understanding"""

        # Check cache first
        cache_key = f"{skill_text}_{context}"
        if cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]

        # Step 1: Base semantic embedding
        base_embedding = self.base_model.encode(skill_text)

        # Step 2: Contextual weighting
        context_weights = self.domain_contexts.get_weights(context)
        weighted_embedding = self._apply_context_weights(base_embedding, context_weights)

        # Step 3: Ontology enhancement
        ontology_enhanced = self._enhance_with_ontology(weighted_embedding, skill_text)

        # Create semantic vector
        semantic_vector = SemanticVector(
            vector=ontology_enhanced,
            confidence=self._calculate_confidence(skill_text, context),
            semantic_tags=self._extract_semantic_tags(skill_text),
            original_text=skill_text,
            context=context,
        )

        # Cache result
        self.embedding_cache[cache_key] = semantic_vector
        return semantic_vector

    def _enhance_with_ontology(self, embedding: np.array, skill_text: str) -> np.array:
        """Use skill relationships to improve embedding"""
        related_skills = self.skill_ontology.get_related_skills(skill_text)

        if related_skills:
            # Average embeddings of related skills to capture semantic neighborhood
            related_embeddings = [self.base_model.encode(skill) for skill in related_skills]
            neighborhood_vector = np.mean(related_embeddings, axis=0)

            # Blend with original embedding (60% original, 40% neighborhood)
            enhanced = 0.6 * embedding + 0.4 * neighborhood_vector
            return enhanced

        return embedding

    def _apply_context_weights(self, embedding: np.array, context_weights: Dict) -> np.array:
        """Apply contextual weighting to embedding"""
        # Simplified context weighting - in practice, this would be more sophisticated
        if not context_weights:
            return embedding

        # Apply domain-specific adjustments
        weighted = embedding.copy()
        for tag, weight in context_weights.items():
            if tag in self._extract_semantic_tags_from_embedding(embedding):
                weighted *= weight

        return weighted

    def _calculate_confidence(self, skill_text: str, context: str) -> float:
        """Calculate confidence in the semantic embedding"""
        # Simple confidence based on skill specificity and context match
        base_confidence = min(len(skill_text.split()) / 3, 1.0)  # Longer skills are more specific

        # Boost confidence if skill exists in ontology
        if self.skill_ontology.skill_exists(skill_text):
            base_confidence *= 1.2

        # Context alignment boost
        if self.domain_contexts.is_relevant(skill_text, context):
            base_confidence *= 1.1

        return min(base_confidence, 1.0)

    def _extract_semantic_tags(self, skill_text: str) -> set:
        """Extract semantic tags from skill text"""
        # This would use NLP techniques in practice
        tags = set()

        # Simple tag extraction based on keywords
        skill_lower = skill_text.lower()

        if any(word in skill_lower for word in ["python", "programming", "code"]):
            tags.add("programming")
        if any(word in skill_lower for word in ["data", "analysis", "analytics"]):
            tags.add("data_science")
        if any(word in skill_lower for word in ["machine learning", "ml", "ai"]):
            tags.add("machine_learning")
        if any(word in skill_lower for word in ["web", "javascript", "react"]):
            tags.add("web_development")

        return tags

    def _extract_semantic_tags_from_embedding(self, embedding: np.array) -> set:
        """Extract tags from embedding (simplified)"""
        # In practice, this would use clustering or classification
        return set()


class SkillOntology:
    """Manages skill relationships and hierarchies"""

    def __init__(self):
        # Simplified ontology - in practice, this would be more comprehensive
        self.skill_relations = {
            "python": ["programming", "data_science", "software_engineering"],
            "javascript": ["programming", "web_development", "frontend"],
            "machine learning": ["data_science", "ai", "statistics"],
            "sql": ["data_science", "databases", "analytics"],
            "react": ["javascript", "frontend", "web_development"],
        }

    def get_related_skills(self, skill: str) -> List[str]:
        """Get skills related to the given skill"""
        return self.skill_relations.get(skill.lower(), [])

    def skill_exists(self, skill: str) -> bool:
        """Check if skill exists in ontology"""
        return skill.lower() in self.skill_relations


class DomainContextRegistry:
    """Manages domain-specific contexts for skills"""

    def __init__(self):
        self.contexts = {
            "data_science": {
                "python": {
                    "weight": 0.9,
                    "related": ["pandas", "numpy", "scikit-learn"],
                },
                "sql": {"weight": 0.8, "related": ["databases", "analytics"]},
                "machine learning": {"weight": 0.95, "related": ["statistics", "ai"]},
                "javascript": {"weight": 0.3, "related": ["frontend", "web"]},
            },
            "web_development": {
                "javascript": {"weight": 0.9, "related": ["react", "node", "frontend"]},
                "python": {"weight": 0.7, "related": ["django", "flask", "backend"]},
                "html": {"weight": 0.8, "related": ["css", "frontend"]},
                "machine learning": {"weight": 0.2, "related": ["ai", "backend"]},
            },
        }

    def get_weights(self, context: str) -> Dict[str, float]:
        """Get context-specific weights"""
        return self.contexts.get(context, {})

    def is_relevant(self, skill: str, context: str) -> bool:
        """Check if skill is relevant in context"""
        context_data = self.contexts.get(context, {})
        return skill.lower() in context_data
