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
Relationship-Aware Matching: Understand that some skills naturally complement each other
"""

from typing import Dict, List

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from .semantic_engine import ContextualEmbedding


class RelationshipAwareMatcher:
    """
    Calculate similarity that understands skill relationships.
    Core insight: Some skills naturally complement each other (Python + SQL, JavaScript + React).
    """

    def __init__(self):
        self.skill_synergies = self._load_skill_synergies()

    def _load_skill_synergies(self) -> Dict[frozenset, float]:
        """Define skill synergies that create bonuses"""
        return {
            frozenset(["python", "sql"]): 0.2,
            frozenset(["javascript", "react"]): 0.15,
            frozenset(["machine learning", "statistics"]): 0.25,
            frozenset(["python", "machine learning"]): 0.18,
            frozenset(["data science", "python"]): 0.22,
            frozenset(["web development", "javascript"]): 0.20,
            frozenset(["backend", "python"]): 0.16,
            frozenset(["frontend", "javascript"]): 0.19,
            frozenset(["databases", "sql"]): 0.17,
            frozenset(["docker", "kubernetes"]): 0.21,
            frozenset(["aws", "docker"]): 0.14,
            frozenset(["tensorflow", "python"]): 0.23,
            frozenset(["pandas", "python"]): 0.20,
        }

    def calculate_semantic_similarity(
        self,
        candidate_embedding: ContextualEmbedding,
        job_embedding: ContextualEmbedding,
    ) -> "MatchScore":
        """
        Calculate similarity that understands skill relationships.
        Returns MatchScore with explainable components.
        """

        # Base cosine similarity
        base_similarity = cosine_similarity(
            candidate_embedding.vector.reshape(1, -1),
            job_embedding.vector.reshape(1, -1),
        )[0][0]

        # Relationship bonus - skills that complement each other
        relationship_bonus = self._calculate_relationship_bonus(
            candidate_embedding.original_embedding.semantic_tags,
            job_embedding.original_embedding.semantic_tags,
        )

        # Context alignment multiplier
        context_alignment = self._calculate_context_alignment(
            candidate_embedding.context, job_embedding.context
        )

        # Final score combines all components
        final_score = (
            base_similarity * 0.6 + relationship_bonus * 0.3 + context_alignment * 0.1
        )

        # Ensure score is between 0 and 1
        final_score = max(0, min(1, final_score))

        components = {
            "base_similarity": base_similarity,
            "relationship_bonus": relationship_bonus,
            "context_alignment": context_alignment,
        }

        explanation = self._generate_explanation(
            base_similarity, relationship_bonus, context_alignment
        )

        return MatchScore(
            score=final_score, components=components, explanation=explanation
        )

    def _calculate_relationship_bonus(
        self, candidate_tags: set, job_tags: set
    ) -> float:
        """
        Reward complementary skill combinations.
        Returns a bonus between 0 and 0.3
        """
        bonus = 0.0

        # Check for skill synergies
        all_tags = candidate_tags | job_tags

        for synergy_pair, bonus_value in self.skill_synergies.items():
            if synergy_pair.issubset(all_tags):
                bonus += bonus_value

        # Additional bonus for skill diversity/complementarity
        shared_tags = candidate_tags & job_tags
        unique_candidate = candidate_tags - job_tags
        unique_job = job_tags - candidate_tags

        # Bonus for having complementary unique skills
        if shared_tags and (unique_candidate or unique_job):
            diversity_bonus = min(len(shared_tags) * 0.05, 0.1)
            bonus += diversity_bonus

        return min(bonus, 0.3)  # Cap the bonus

    def _calculate_context_alignment(
        self, candidate_context: str, job_context: str
    ) -> float:
        """
        Calculate alignment between candidate and job contexts.
        Returns multiplier between 0.8 and 1.2
        """
        if candidate_context == job_context:
            return 1.2  # Perfect alignment
        elif candidate_context == "general" or job_context == "general":
            return 1.0  # Neutral
        else:
            # Check if contexts are related
            related_contexts = {
                "data_science": ["machine_learning", "analytics"],
                "web_development": ["frontend", "backend", "fullstack"],
                "machine_learning": ["data_science", "ai"],
                "devops": ["infrastructure", "cloud"],
            }

            candidate_related = related_contexts.get(candidate_context, [])
            if job_context in candidate_related:
                return 1.1  # Good alignment

        return 0.8  # Poor alignment

    def _generate_explanation(
        self,
        base_similarity: float,
        relationship_bonus: float,
        context_alignment: float,
    ) -> str:
        """Generate human-readable explanation of the match"""

        explanation_parts = []

        # Base similarity explanation
        if base_similarity > 0.8:
            explanation_parts.append("Strong semantic similarity in core skills")
        elif base_similarity > 0.6:
            explanation_parts.append("Moderate semantic similarity")
        else:
            explanation_parts.append("Limited semantic similarity")

        # Relationship bonus explanation
        if relationship_bonus > 0.2:
            explanation_parts.append("Excellent skill complementarity")
        elif relationship_bonus > 0.1:
            explanation_parts.append("Good skill synergy")
        elif relationship_bonus > 0:
            explanation_parts.append("Some complementary skills")

        # Context alignment explanation
        if context_alignment > 1.1:
            explanation_parts.append("Perfect context alignment")
        elif context_alignment > 1.0:
            explanation_parts.append("Good context alignment")
        elif context_alignment < 0.9:
            explanation_parts.append("Context mismatch")

        return "; ".join(explanation_parts)

    def batch_calculate_similarities(
        self,
        candidate_embeddings: List[ContextualEmbedding],
        job_embeddings: List[ContextualEmbedding],
    ) -> List[List[float]]:
        """
        Calculate similarities for multiple candidates and jobs efficiently
        Returns matrix of shape (n_candidates, n_jobs)
        """
        n_candidates = len(candidate_embeddings)
        n_jobs = len(job_embeddings)

        similarity_matrix = np.zeros((n_candidates, n_jobs))

        for i, candidate_emb in enumerate(candidate_embeddings):
            for j, job_emb in enumerate(job_embeddings):
                match_score = self.calculate_semantic_similarity(candidate_emb, job_emb)
                similarity_matrix[i, j] = match_score.score

        return similarity_matrix.tolist()


class MatchScore:
    """Semantic match score with explainable components"""

    def __init__(self, score: float, components: Dict[str, float], explanation: str):
        self.score = score
        self.components = components
        self.explanation = explanation

    def __repr__(self):
        return f"MatchScore(score={self.score:.3f}, explanation='{self.explanation}')"

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "score": self.score,
            "components": self.components,
            "explanation": self.explanation,
        }
