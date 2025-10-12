"""
Context-Aware Filtering: Understand that 'Python' means different things in different contexts
"""

from typing import Dict, List, Tuple

import numpy as np

from .semantic_engine import ContextualEmbedding, SemanticVector


class ContextFilter:
    """
    Apply domain-specific understanding to weight skills differently based on context.
    Core insight: 'Python' in Data Science vs Web Development contexts should be weighted differently.
    """

    CONTEXT_MAPPINGS = {
        "data_science": {
            "python": {"weight": 0.9, "related": ["pandas", "numpy", "scikit-learn"]},
            "javascript": {"weight": 0.3, "related": ["frontend", "web"]},
        },
        "web_development": {
            "python": {"weight": 0.7, "related": ["django", "flask", "backend"]},
            "javascript": {"weight": 0.9, "related": ["react", "node", "frontend"]},
        },
        "machine_learning": {
            "python": {
                "weight": 0.95,
                "related": ["tensorflow", "pytorch", "scikit-learn"],
            },
            "r": {"weight": 0.8, "related": ["statistics", "data_science"]},
            "javascript": {"weight": 0.2, "related": ["frontend"]},
        },
        "devops": {
            "python": {"weight": 0.6, "related": ["automation", "scripting"]},
            "docker": {"weight": 0.95, "related": ["kubernetes", "containers"]},
            "javascript": {"weight": 0.4, "related": ["node", "backend"]},
        },
    }

    def apply_context(self, embedding: SemanticVector, job_context: str) -> ContextualEmbedding:
        """
        Weight embedding based on job context.
        This is where the semantic understanding gets contextualized.
        """
        context_config = self.CONTEXT_MAPPINGS.get(job_context, {})

        # Adjust weights based on context relevance
        adjusted_vector = self._adjust_weights(embedding.vector, embedding.semantic_tags, context_config)

        return ContextualEmbedding(
            vector=adjusted_vector,
            original_embedding=embedding,
            context=job_context,
            relevance_score=self._calculate_context_relevance(embedding.semantic_tags, job_context),
        )

    def _adjust_weights(self, vector: np.ndarray, semantic_tags: set, context_config: Dict) -> np.ndarray:
        """Apply context-specific weight adjustments to the embedding vector"""

        adjusted_vector = vector.copy()

        # Apply tag-specific weights
        for tag in semantic_tags:
            if tag in context_config:
                weight = context_config[tag]["weight"]
                # Boost or reduce the vector components based on context
                adjusted_vector *= weight

        # Apply related skill bonuses
        for tag, config in context_config.items():
            if tag in semantic_tags:
                related_bonus = len(set(config["related"]) & semantic_tags) * 0.1
                adjusted_vector *= 1 + related_bonus

        # Normalize to prevent explosion
        norm = np.linalg.norm(adjusted_vector)
        if norm > 0:
            adjusted_vector = adjusted_vector / norm

        return adjusted_vector

    def _calculate_context_relevance(self, semantic_tags: set, context: str) -> float:
        """Calculate how relevant the skill set is for the given context"""

        if context not in self.CONTEXT_MAPPINGS:
            return 0.5  # Neutral relevance for unknown contexts

        context_config = self.CONTEXT_MAPPINGS[context]
        relevance_score = 0.0
        total_possible = 0

        for tag, config in context_config.items():
            total_possible += 1
            if tag in semantic_tags:
                relevance_score += config["weight"]

        # Bonus for related skills
        for tag, config in context_config.items():
            if tag in semantic_tags:
                related_overlap = len(set(config["related"]) & semantic_tags)
                relevance_score += related_overlap * 0.1

        return min(relevance_score / max(total_possible, 1), 1.0)

    def get_context_suggestions(self, skill_tags: set) -> List[Tuple[str, float]]:
        """
        Suggest most relevant contexts for a given skill set.
        Returns list of (context, relevance_score) tuples.
        """
        suggestions = []

        for context in self.CONTEXT_MAPPINGS.keys():
            relevance = self._calculate_context_relevance(skill_tags, context)
            suggestions.append((context, relevance))

        # Sort by relevance (highest first)
        suggestions.sort(key=lambda x: x[1], reverse=True)

        return suggestions[:3]  # Top 3 suggestions


class ContextValidator:
    """
    Validate that context filtering makes intuitive sense
    """

    def validate_context_separation(self, context_filter: ContextFilter) -> Dict[str, bool]:
        """
        Test that different contexts produce different embeddings for the same skill
        """
        test_skill = "python"
        contexts = ["data_science", "web_development", "machine_learning"]

        results = {}

        # Get embeddings for same skill in different contexts
        embeddings = {}
        for context in contexts:
            # Create a mock semantic vector
            mock_vector = SemanticVector(
                vector=np.random.rand(384),  # Mock embedding
                confidence=0.8,
                semantic_tags={"python", "programming"},
                original_text=test_skill,
                context=context,
            )

            contextual = context_filter.apply_context(mock_vector, context)
            embeddings[context] = contextual.vector

        # Check that embeddings are different (cosine similarity < 0.95)
        for i, ctx1 in enumerate(contexts):
            for ctx2 in contexts[i + 1 :]:
                similarity = np.dot(embeddings[ctx1], embeddings[ctx2]) / (
                    np.linalg.norm(embeddings[ctx1]) * np.linalg.norm(embeddings[ctx2])
                )
                results[f"{ctx1}_vs_{ctx2}"] = similarity < 0.95

        return results
