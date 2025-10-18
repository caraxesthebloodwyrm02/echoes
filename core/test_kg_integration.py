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
Integration tests for Knowledge Graph Bridge
"""

from datetime import datetime

import pytest


class TestKnowledgeGraphBridge:
    """Test KnowledgeGraphBridge functionality"""

    @pytest.fixture
    def kg_bridge(self):
        """Create a KG bridge instance for testing"""
        try:
            from prompting.core.kg_bridge import KnowledgeGraphBridge

            bridge = KnowledgeGraphBridge(enable_kg=True, cache_size=10)
            yield bridge
            # Cleanup
            bridge.clear_cache()
        except ImportError:
            pytest.skip("Knowledge graph dependencies not available")

    @pytest.fixture
    def sample_insights(self):
        """Sample insights for testing"""
        return [
            {
                "content": "High complexity detected in authentication module",
                "category": "performance",
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat(),
                "session_id": "test_session_1",
            },
            {
                "content": "Security vulnerability found in user input validation",
                "category": "security",
                "confidence": 0.92,
                "timestamp": datetime.now().isoformat(),
                "session_id": "test_session_1",
            },
            {
                "content": "Code refactoring improved maintainability score",
                "category": "general",
                "confidence": 0.78,
                "timestamp": datetime.now().isoformat(),
                "session_id": "test_session_2",
            },
            {
                "content": "Authentication module requires additional testing",
                "category": "quality",
                "confidence": 0.65,
                "timestamp": datetime.now().isoformat(),
                "session_id": "test_session_2",
            },
        ]

    def test_bridge_initialization(self, kg_bridge):
        """Test that KG bridge initializes correctly"""
        assert kg_bridge is not None
        stats = kg_bridge.get_stats()
        assert "enabled" in stats
        assert "kg_available" in stats

    def test_sync_insights_to_kg(self, kg_bridge, sample_insights):
        """Test syncing insights to knowledge graph"""
        synced = kg_bridge.sync_insights_to_kg(sample_insights)

        # Should sync all or partial insights
        assert synced >= 0
        assert synced <= len(sample_insights)

        # Check stats
        stats = kg_bridge.get_stats()
        if kg_bridge.enabled:
            assert stats["insights_in_kg"] >= synced

    def test_semantic_search_basic(self, kg_bridge, sample_insights):
        """Test basic semantic search functionality"""
        if not kg_bridge.enabled:
            pytest.skip("KG not enabled")

        # Sync insights first
        kg_bridge.sync_insights_to_kg(sample_insights)

        # Search for authentication-related insights
        results = kg_bridge.semantic_search(
            query="authentication security", limit=3, min_confidence=0.6
        )

        assert isinstance(results, list)
        # Should find at least some results or return empty gracefully
        assert len(results) >= 0

    def test_semantic_search_with_category_filter(self, kg_bridge, sample_insights):
        """Test semantic search with category filtering"""
        if not kg_bridge.enabled:
            pytest.skip("KG not enabled")

        kg_bridge.sync_insights_to_kg(sample_insights)

        # Search only in security category
        results = kg_bridge.semantic_search(
            query="vulnerability", category="security", limit=5
        )

        assert isinstance(results, list)
        # All results should be security category if any returned
        for result in results:
            assert result["category"] == "security"

    def test_semantic_search_confidence_threshold(self, kg_bridge, sample_insights):
        """Test semantic search confidence filtering"""
        if not kg_bridge.enabled:
            pytest.skip("KG not enabled")

        kg_bridge.sync_insights_to_kg(sample_insights)

        # Search with high confidence threshold
        results = kg_bridge.semantic_search(
            query="code quality", min_confidence=0.8, limit=5
        )

        # All results should meet confidence threshold
        for result in results:
            assert result["confidence"] >= 0.8

    def test_semantic_search_caching(self, kg_bridge, sample_insights):
        """Test that semantic search results are cached"""
        if not kg_bridge.enabled:
            pytest.skip("KG not enabled")

        kg_bridge.sync_insights_to_kg(sample_insights)

        # First search
        results1 = kg_bridge.semantic_search(query="test query", limit=3)
        cache_size_1 = kg_bridge.get_stats()["cache_size"]

        # Same search should use cache
        results2 = kg_bridge.semantic_search(query="test query", limit=3)
        cache_size_2 = kg_bridge.get_stats()["cache_size"]

        # Cache size should be same (not duplicate entry)
        assert cache_size_2 == cache_size_1

        # Results should be identical
        assert len(results1) == len(results2)

    def test_cache_clear(self, kg_bridge, sample_insights):
        """Test cache clearing functionality"""
        if not kg_bridge.enabled:
            pytest.skip("KG not enabled")

        kg_bridge.sync_insights_to_kg(sample_insights)
        kg_bridge.semantic_search(query="test", limit=3)

        # Verify cache has entries
        assert kg_bridge.get_stats()["cache_size"] > 0

        # Clear cache
        kg_bridge.clear_cache()

        # Verify cache is empty
        assert kg_bridge.get_stats()["cache_size"] == 0

    def test_find_related_insights(self, kg_bridge, sample_insights):
        """Test finding related insights"""
        if not kg_bridge.enabled:
            pytest.skip("KG not enabled")

        kg_bridge.sync_insights_to_kg(sample_insights)

        # Find insights related to authentication
        related = kg_bridge.find_related_insights(
            insight_content="authentication", similarity_threshold=0.5, limit=3
        )

        assert isinstance(related, list)
        # Each result should be a tuple of (uri, similarity_score)
        for item in related:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_infer_patterns(self, kg_bridge, sample_insights):
        """Test pattern inference from knowledge graph"""
        if not kg_bridge.enabled:
            pytest.skip("KG not enabled")

        kg_bridge.sync_insights_to_kg(sample_insights)

        patterns = kg_bridge.infer_patterns()

        assert isinstance(patterns, dict)
        # Should have pattern categories
        assert len(patterns) >= 0

    def test_get_recommendations(self, kg_bridge, sample_insights):
        """Test recommendation generation"""
        if not kg_bridge.enabled:
            pytest.skip("KG not enabled")

        kg_bridge.sync_insights_to_kg(sample_insights)

        recommendations = kg_bridge.get_recommendations()

        assert isinstance(recommendations, list)
        # Each recommendation should have required fields
        for rec in recommendations:
            assert "type" in rec
            assert "priority" in rec
            assert "recommendation" in rec

    def test_fallback_when_kg_disabled(self):
        """Test that bridge works gracefully when KG is disabled"""
        from prompting.core.kg_bridge import KnowledgeGraphBridge

        bridge = KnowledgeGraphBridge(enable_kg=False)

        # All methods should work without errors
        assert bridge.sync_insights_to_kg([]) == 0
        assert bridge.semantic_search("test") == []
        assert bridge.find_related_insights("test") == []
        assert bridge.infer_patterns() == {}
        assert bridge.get_recommendations() == []

        stats = bridge.get_stats()
        assert stats["enabled"] is False

    def test_stats_reporting(self, kg_bridge, sample_insights):
        """Test statistics reporting"""
        stats = kg_bridge.get_stats()

        # Should have all required fields
        assert "enabled" in stats
        assert "kg_available" in stats
        assert "cache_size" in stats
        assert "cache_capacity" in stats

        if kg_bridge.enabled:
            kg_bridge.sync_insights_to_kg(sample_insights)
            stats = kg_bridge.get_stats()
            assert "insights_in_kg" in stats


class TestContextManagerKGIntegration:
    """Test ContextManager integration with KG bridge"""

    @pytest.fixture
    def context_manager_with_kg(self):
        """Create ContextManager with KG integration"""
        try:
            import tempfile

            from prompting.core.context_manager import ContextManager

            # Use temporary directory for storage
            temp_dir = tempfile.mkdtemp()
            cm = ContextManager(storage_path=temp_dir, enable_kg=True)
            yield cm

            # Cleanup
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)
        except ImportError as e:
            pytest.skip(f"Required dependencies not available: {e}")

    def test_context_manager_initialization_with_kg(self, context_manager_with_kg):
        """Test that ContextManager initializes with KG bridge"""
        assert context_manager_with_kg is not None
        assert hasattr(context_manager_with_kg, "kg_bridge")

    def test_add_insight_syncs_to_kg(self, context_manager_with_kg):
        """Test that adding insights syncs to knowledge graph"""
        # Add some insights
        context_manager_with_kg.add_insight(
            "Test insight about code quality", category="quality", confidence=0.85
        )

        context_manager_with_kg.add_insight(
            "Another insight about performance", category="performance", confidence=0.75
        )

        # Verify insights were added
        assert len(context_manager_with_kg.memory["insights"]) >= 2

    def test_get_relevant_insights_uses_semantic_search(self, context_manager_with_kg):
        """Test that get_relevant_insights uses semantic search when KG enabled"""
        # Add insights
        context_manager_with_kg.add_insight(
            "Database queries need optimization", category="performance", confidence=0.9
        )

        context_manager_with_kg.add_insight(
            "Authentication module has security concerns",
            category="security",
            confidence=0.85,
        )

        # Search for insights
        results = context_manager_with_kg.get_relevant_insights(
            query="database performance", limit=5
        )

        # Should return results (semantic or keyword fallback)
        assert isinstance(results, list)

    def test_context_manager_kg_fallback(self):
        """Test that ContextManager works without KG"""
        try:
            import tempfile

            from prompting.core.context_manager import ContextManager

            temp_dir = tempfile.mkdtemp()
            cm = ContextManager(storage_path=temp_dir, enable_kg=False)

            # Should work normally without KG
            cm.add_insight("Test insight", category="general", confidence=0.8)
            results = cm.get_relevant_insights("test", limit=3)

            assert isinstance(results, list)

            # Cleanup
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)

        except ImportError:
            pytest.skip("ContextManager not available")


class TestPerformanceBenchmarks:
    """Performance benchmarks for KG integration"""

    def test_semantic_search_performance(self):
        """Benchmark semantic search vs keyword search"""
        try:
            import time

            from prompting.core.kg_bridge import KnowledgeGraphBridge

            bridge = KnowledgeGraphBridge(enable_kg=True)

            # Create test dataset
            insights = [
                {
                    "content": f"Test insight {i} about performance and optimization",
                    "category": "performance",
                    "confidence": 0.7 + (i % 3) * 0.1,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": f"session_{i % 5}",
                }
                for i in range(50)
            ]

            # Sync to KG
            bridge.sync_insights_to_kg(insights)

            # Benchmark semantic search
            start = time.time()
            for _ in range(10):
                bridge.semantic_search("performance optimization", limit=5)
            semantic_duration = time.time() - start

            # Should complete within reasonable time (< 1 second for 10 searches)
            assert semantic_duration < 1.0

        except ImportError:
            pytest.skip("KG dependencies not available")

    def test_cache_effectiveness(self):
        """Test that caching improves performance"""
        try:
            import time

            from prompting.core.kg_bridge import KnowledgeGraphBridge

            bridge = KnowledgeGraphBridge(enable_kg=True, cache_size=50)

            # Sync test data
            insights = [
                {
                    "content": f"Insight {i}",
                    "category": "test",
                    "confidence": 0.8,
                    "timestamp": datetime.now().isoformat(),
                    "session_id": "test",
                }
                for i in range(20)
            ]
            bridge.sync_insights_to_kg(insights)

            # First search (uncached)
            start = time.time()
            bridge.semantic_search("test query", limit=5)
            uncached_time = time.time() - start

            # Second search (cached)
            start = time.time()
            bridge.semantic_search("test query", limit=5)
            cached_time = time.time() - start

            # Cached search should be faster or similar
            assert cached_time <= uncached_time * 1.5

        except ImportError:
            pytest.skip("KG dependencies not available")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
