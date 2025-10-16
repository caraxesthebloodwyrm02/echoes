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

# MIT License
#
# Copyright (c) 2025 Echoes Project
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
KnowledgeGraphBridge - Integrates semantic knowledge graph with context management
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

try:
    from knowledge_graph.system import KnowledgeGraph, SemanticReasoner

    KG_AVAILABLE = True
except ImportError:
    KG_AVAILABLE = False
    logging.warning(
        "Knowledge graph dependencies not available. Install networkx and rdflib."
    )


class KnowledgeGraphBridge:
    """Bridge between ContextManager/InsightSynthesizer and KnowledgeGraph system"""

    def __init__(self, enable_kg: bool = True, cache_size: int = 100):
        """
        Initialize knowledge graph bridge

        Args:
            enable_kg: Enable knowledge graph integration (falls back to keyword search if False)
            cache_size: Number of semantic search results to cache
        """
        self.enabled = enable_kg and KG_AVAILABLE
        self.cache_size = cache_size
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

        if self.enabled:
            try:
                self.kg = KnowledgeGraph()
                self.reasoner = SemanticReasoner(self.kg)
                logging.info("Knowledge graph bridge initialized successfully")
            except Exception as e:
                logging.error(f"Failed to initialize knowledge graph: {e}")
                self.enabled = False
                self.kg = None
                self.reasoner = None
        else:
            self.kg = None
            self.reasoner = None
            if enable_kg:
                logging.warning(
                    "Knowledge graph requested but dependencies not available"
                )

    def sync_insights_to_kg(self, insights: List[Dict[str, Any]]) -> int:
        """
        Synchronize insights from memory to knowledge graph

        Args:
            insights: List of insight dictionaries from ContextManager

        Returns:
            Number of insights successfully synced
        """
        if not self.enabled:
            return 0

        synced_count = 0

        for insight in insights:
            try:
                # Create insight entity in knowledge graph
                insight_uri = self.kg.add_code_entity(
                    "Insight",
                    f"insight_{insight.get('session_id', 'unknown')}_{synced_count}",
                    {
                        "content": insight.get("content", ""),
                        "category": insight.get("category", "general"),
                        "confidence": insight.get("confidence", 0.5),
                        "timestamp": insight.get(
                            "timestamp", datetime.now().isoformat()
                        ),
                        "session_id": insight.get("session_id", ""),
                    },
                )

                # Add relationships if available
                if "related_insights" in insight:
                    for related in insight["related_insights"]:
                        self.kg.add_relationship(
                            insight_uri, "related_to", related, {"similarity": 0.8}
                        )

                synced_count += 1

            except Exception as e:
                logging.error(f"Failed to sync insight to KG: {e}")
                continue

        logging.info(
            f"Synced {synced_count}/{len(insights)} insights to knowledge graph"
        )
        return synced_count

    def semantic_search(
        self,
        query: str,
        category: Optional[str] = None,
        limit: int = 5,
        min_confidence: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search for insights using knowledge graph

        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum number of results
            min_confidence: Minimum confidence threshold

        Returns:
            List of relevant insights with confidence scores
        """
        if not self.enabled:
            return []

        # Check cache first
        cache_key = f"{query}:{category}:{limit}:{min_confidence}"
        if cache_key in self._cache:
            logging.debug(f"Cache hit for query: {query}")
            return self._cache[cache_key]

        try:
            # Build SPARQL query for semantic search
            sparql_query = f"""
            SELECT ?insight ?content ?category ?confidence ?timestamp
            WHERE {{
                ?insight rdf:type code:Insight .
                ?insight code:content ?content .
                ?insight code:category ?category .
                ?insight code:confidence ?confidence .
                ?insight code:timestamp ?timestamp .
                FILTER (?confidence >= {min_confidence})
                {f'FILTER (?category = "{category}")' if category else ""}
            }}
            ORDER BY DESC(?confidence)
            LIMIT {limit * 2}
            """

            raw_results = self.kg.query_knowledge(sparql_query)

            # Calculate semantic similarity (simplified - using content overlap)
            scored_results = []
            query_lower = query.lower()
            query_terms = set(query_lower.split())

            for result in raw_results:
                content = result.get("content", "").lower()
                content_terms = set(content.split())

                # Jaccard similarity for term overlap
                intersection = len(query_terms & content_terms)
                union = len(query_terms | content_terms)
                similarity = intersection / union if union > 0 else 0.0

                # Combine with stored confidence
                confidence = float(result.get("confidence", 0.5))
                combined_score = (similarity * 0.6) + (confidence * 0.4)

                scored_results.append(
                    {
                        "insight": result.get("insight", ""),
                        "content": result.get("content", ""),
                        "category": result.get("category", "general"),
                        "confidence": confidence,
                        "similarity": similarity,
                        "combined_score": combined_score,
                        "timestamp": result.get("timestamp", ""),
                    }
                )

            # Sort by combined score and limit
            scored_results.sort(key=lambda x: x["combined_score"], reverse=True)
            final_results = scored_results[:limit]

            # Cache results
            if len(self._cache) >= self.cache_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(self._cache))
                del self._cache[oldest_key]
            self._cache[cache_key] = final_results

            logging.debug(
                f"Semantic search returned {len(final_results)} results for: {query}"
            )
            return final_results

        except Exception as e:
            logging.error(f"Semantic search failed: {e}")
            return []

    def find_related_insights(
        self, insight_content: str, similarity_threshold: float = 0.7, limit: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find insights related to the given insight using graph similarity

        Args:
            insight_content: Content of the insight to find relations for
            similarity_threshold: Minimum similarity score
            limit: Maximum number of related insights

        Returns:
            List of (insight_uri, similarity_score) tuples
        """
        if not self.enabled:
            return []

        try:
            # Find the insight entity in the graph
            query = f"""
            SELECT ?insight
            WHERE {{
                ?insight rdf:type code:Insight .
                ?insight code:content ?content .
                FILTER (CONTAINS(LCASE(?content), LCASE("{insight_content[:50]}")))
            }}
            LIMIT 1
            """

            results = self.kg.query_knowledge(query)
            if not results:
                return []

            insight_uri = results[0].get("insight")

            # Use knowledge graph's similarity function
            from rdflib import URIRef

            similar = self.kg.find_similar_entities(
                URIRef(insight_uri), similarity_threshold
            )

            return similar[:limit]

        except Exception as e:
            logging.error(f"Failed to find related insights: {e}")
            return []

    def infer_patterns(self) -> Dict[str, List[str]]:
        """
        Use semantic reasoner to infer patterns from knowledge graph

        Returns:
            Dictionary of pattern categories and their instances
        """
        if not self.enabled or not self.reasoner:
            return {}

        try:
            # Run inference on the knowledge graph
            self.kg.infer_relationships()

            # Find patterns using semantic reasoner
            patterns = self.reasoner.find_code_patterns()

            # Add insight-specific patterns
            insight_patterns = self._find_insight_patterns()
            patterns.update(insight_patterns)

            logging.info(
                f"Inferred {sum(len(v) for v in patterns.values())} patterns across {len(patterns)} categories"
            )
            return patterns

        except Exception as e:
            logging.error(f"Pattern inference failed: {e}")
            return {}

    def _find_insight_patterns(self) -> Dict[str, List[str]]:
        """Find patterns specific to insights"""
        patterns = {
            "high_confidence_clusters": [],
            "cross_session_patterns": [],
            "category_trends": [],
        }

        try:
            # Find high-confidence insight clusters
            high_conf_query = """
            SELECT ?category (COUNT(?insight) as ?count) (AVG(?confidence) as ?avg_conf)
            WHERE {
                ?insight rdf:type code:Insight .
                ?insight code:category ?category .
                ?insight code:confidence ?confidence .
                FILTER (?confidence > 0.8)
            }
            GROUP BY ?category
            HAVING (?count > 3)
            ORDER BY DESC(?avg_conf)
            """

            results = self.kg.query_knowledge(high_conf_query)
            for result in results:
                patterns["high_confidence_clusters"].append(
                    f"{result['category']}: {result['count']} insights (avg confidence: {float(result['avg_conf']):.2f})"
                )

        except Exception as e:
            logging.debug(f"Insight pattern detection partial failure: {e}")

        return patterns

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on knowledge graph analysis

        Returns:
            List of recommendation dictionaries
        """
        if not self.enabled or not self.reasoner:
            return []

        try:
            # Get recommendations from semantic reasoner
            recommendations = self.reasoner.recommend_improvements()

            # Add insight-specific recommendations
            insight_recs = self._generate_insight_recommendations()
            recommendations.extend(insight_recs)

            return recommendations

        except Exception as e:
            logging.error(f"Failed to generate recommendations: {e}")
            return []

    def _generate_insight_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations specific to insight management"""
        recommendations = []

        try:
            # Find low-confidence insights
            low_conf_query = """
            SELECT (COUNT(?insight) as ?count)
            WHERE {
                ?insight rdf:type code:Insight .
                ?insight code:confidence ?confidence .
                FILTER (?confidence < 0.5)
            }
            """

            results = self.kg.query_knowledge(low_conf_query)
            if results and int(results[0].get("count", 0)) > 10:
                recommendations.append(
                    {
                        "type": "insight_quality",
                        "priority": "medium",
                        "target": "insight_system",
                        "issue": f"{results[0]['count']} low-confidence insights detected",
                        "recommendation": "Review and validate or remove low-confidence insights",
                    }
                )

        except Exception as e:
            logging.debug(f"Insight recommendation generation partial failure: {e}")

        return recommendations

    def clear_cache(self):
        """Clear the semantic search cache"""
        self._cache.clear()
        logging.debug("Semantic search cache cleared")

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about knowledge graph integration

        Returns:
            Dictionary of statistics
        """
        stats = {
            "enabled": self.enabled,
            "kg_available": KG_AVAILABLE,
            "cache_size": len(self._cache),
            "cache_capacity": self.cache_size,
        }

        if self.enabled and self.kg:
            try:
                # Count insights in knowledge graph
                count_query = """
                SELECT (COUNT(?insight) as ?count)
                WHERE {
                    ?insight rdf:type code:Insight .
                }
                """
                results = self.kg.query_knowledge(count_query)
                if results:
                    stats["insights_in_kg"] = int(results[0].get("count", 0))
            except Exception as e:
                logging.debug(f"Failed to get KG stats: {e}")
                stats["insights_in_kg"] = 0

        return stats


# Convenience function for easy integration
def create_kg_bridge(
    enable_kg: bool = True, cache_size: int = 100
) -> KnowledgeGraphBridge:
    """
    Factory function to create a KnowledgeGraphBridge instance

    Args:
        enable_kg: Enable knowledge graph integration
        cache_size: Cache size for semantic search

    Returns:
        Initialized KnowledgeGraphBridge instance
    """
    return KnowledgeGraphBridge(enable_kg=enable_kg, cache_size=cache_size)
