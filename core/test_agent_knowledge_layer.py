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

"""
Tests for Agent Knowledge Layer
"""

import pytest


class TestAgentKnowledgeLayer:
    """Test AgentKnowledgeLayer functionality"""

    @pytest.fixture
    def knowledge_layer(self):
        """Create knowledge layer instance"""
        try:
            from ai_agents.agent_knowledge_layer import AgentKnowledgeLayer

            layer = AgentKnowledgeLayer(enable_kg=True)
            yield layer
        except ImportError:
            pytest.skip("Agent knowledge layer dependencies not available")

    def test_initialization(self, knowledge_layer):
        """Test knowledge layer initializes correctly"""
        assert knowledge_layer is not None
        assert hasattr(knowledge_layer, "agent_registry")
        assert hasattr(knowledge_layer, "kg_bridge")

    def test_register_agent(self, knowledge_layer):
        """Test agent registration"""
        success = knowledge_layer.register_agent(
            agent_name="test_architect",
            agent_type="architect",
            capabilities=["design", "planning", "architecture"],
            metadata={"description": "Test architect agent"},
        )

        assert success is True
        assert "test_architect" in knowledge_layer.agent_registry
        assert knowledge_layer.agent_registry["test_architect"]["agent_type"] == "architect"

    def test_duplicate_registration(self, knowledge_layer):
        """Test that duplicate registration succeeds (updates registration)"""
        knowledge_layer.register_agent(agent_name="duplicate_agent", agent_type="tester", capabilities=["testing"])

        # Try to register again - should succeed (overwrites)
        success = knowledge_layer.register_agent(
            agent_name="duplicate_agent", agent_type="tester", capabilities=["testing"]
        )

        assert success is True

    def test_share_discovery(self, knowledge_layer):
        """Test sharing discoveries"""
        from ai_agents.agent_knowledge_layer import AgentDiscovery

        # Register agent first
        knowledge_layer.register_agent(agent_name="discoverer", agent_type="reviewer", capabilities=["code_review"])

        # Create and share discovery
        discovery = AgentDiscovery(
            agent_name="discoverer",
            discovery_type="code_smell",
            content="Found duplicate code in authentication module",
            confidence=0.85,
            metadata={"module": "auth", "lines": "50-75"},
        )

        success = knowledge_layer.share_discovery(discovery)
        assert success is True
        assert len(knowledge_layer.discoveries) >= 1
        assert knowledge_layer.agent_registry["discoverer"]["discoveries_count"] >= 1

    def test_share_unregistered_agent(self, knowledge_layer):
        """Test that unregistered agent can still share (will be tracked)"""
        from ai_agents.agent_knowledge_layer import AgentDiscovery

        discovery = AgentDiscovery(
            agent_name="unregistered",
            discovery_type="issue",
            content="Some discovery",
            confidence=0.5,
        )

        success = knowledge_layer.share_discovery(discovery)
        assert success is True  # Sharing succeeds even if agent not registered

    def test_query_discoveries(self, knowledge_layer):
        """Test querying discoveries"""
        from ai_agents.agent_knowledge_layer import AgentDiscovery

        # Register agents
        knowledge_layer.register_agent(agent_name="agent1", agent_type="architect", capabilities=["design"])

        # Share some discoveries
        knowledge_layer.share_discovery(
            AgentDiscovery(
                agent_name="agent1",
                discovery_type="pattern",
                content="Database connection pooling pattern identified",
                confidence=0.9,
            )
        )

        knowledge_layer.share_discovery(
            AgentDiscovery(
                agent_name="agent1",
                discovery_type="issue",
                content="Database query optimization needed",
                confidence=0.75,
            )
        )

        # Query discoveries
        results = knowledge_layer.query_discoveries(agent_name="agent1", min_confidence=0.5, limit=5)

        # Results depend on KG availability
        assert isinstance(results, list)
        assert len(results) >= 1

    def test_get_recommendations(self, knowledge_layer):
        """Test getting recommendations for an agent"""
        # Register multiple agents
        knowledge_layer.register_agent(
            agent_name="architect1",
            agent_type="architect",
            capabilities=["design", "planning", "microservices"],
        )
        knowledge_layer.register_agent(
            agent_name="reviewer1",
            agent_type="reviewer",
            capabilities=["code_review", "security"],
        )

        # Get recommendations for architect1
        recommendations = knowledge_layer.get_agent_recommendations("architect1")

        assert isinstance(recommendations, list)
        # Should recommend collaboration since no handoffs yet

    def test_handoff_context(self, knowledge_layer):
        """Test creating handoff context"""
        # Register agents
        knowledge_layer.register_agent(agent_name="agent_a", agent_type="architect", capabilities=["design"])
        knowledge_layer.register_agent(agent_name="agent_b", agent_type="implementer", capabilities=["coding"])

        # Create handoff
        context = knowledge_layer.create_handoff_context(
            source_agent="agent_a",
            target_agent="agent_b",
            task_description="Implement authentication system",
            context_data={"design_doc": "auth_design.md"},
            priority="high",
        )

        assert context is not None
        assert context.source_agent == "agent_a"
        assert context.target_agent == "agent_b"
        assert context.task_description == "Implement authentication system"
        assert context.priority == "high"

    def test_statistics(self, knowledge_layer):
        """Test getting statistics"""
        from ai_agents.agent_knowledge_layer import AgentDiscovery

        # Register and use agent
        knowledge_layer.register_agent(agent_name="stats_agent", agent_type="tester", capabilities=["testing"])

        knowledge_layer.share_discovery(
            AgentDiscovery(
                agent_name="stats_agent",
                discovery_type="test_result",
                content="All tests passed",
                confidence=1.0,
            )
        )

        # Get global stats
        stats = knowledge_layer.get_stats()
        assert "discoveries_shared" in stats
        assert "agents_registered" in stats
        assert stats["discoveries_stored"] >= 1
        assert stats["active_agents"] >= 1

    def test_learn_patterns(self, knowledge_layer):
        """Test pattern learning from agent interactions"""
        from ai_agents.agent_knowledge_layer import AgentDiscovery

        # Register multiple agents
        knowledge_layer.register_agent(agent_name="agent_x", agent_type="architect", capabilities=["design"])
        knowledge_layer.register_agent(agent_name="agent_y", agent_type="reviewer", capabilities=["review"])

        # Both discover same pattern type
        knowledge_layer.share_discovery(
            AgentDiscovery(
                agent_name="agent_x",
                discovery_type="performance_issue",
                content="Slow query detected in users table",
                confidence=0.8,
            )
        )

        knowledge_layer.share_discovery(
            AgentDiscovery(
                agent_name="agent_y",
                discovery_type="performance_issue",
                content="Inefficient index usage in products table",
                confidence=0.75,
            )
        )

        # Learn patterns
        patterns = knowledge_layer.learn_patterns()
        assert isinstance(patterns, dict)
        assert "common_discoveries" in patterns


class TestAgentDiscovery:
    """Test AgentDiscovery class"""

    def test_discovery_creation(self):
        """Test creating a discovery object"""
        try:
            from ai_agents.agent_knowledge_layer import AgentDiscovery

            discovery = AgentDiscovery(
                agent_name="test_agent",
                discovery_type="insight",
                content="Test content",
                confidence=0.9,
                metadata={"key": "value"},
            )

            assert discovery.agent_name == "test_agent"
            assert discovery.discovery_type == "insight"
            assert discovery.confidence == 0.9
            assert discovery.discovery_id is not None

        except ImportError:
            pytest.skip("AgentDiscovery not available")

    def test_discovery_to_dict(self):
        """Test converting discovery to dictionary"""
        try:
            from ai_agents.agent_knowledge_layer import AgentDiscovery

            discovery = AgentDiscovery(
                agent_name="test_agent",
                discovery_type="pattern",
                content="Test pattern",
                confidence=0.85,
            )

            data = discovery.to_dict()
            assert isinstance(data, dict)
            assert data["agent_name"] == "test_agent"
            assert data["discovery_type"] == "pattern"
            assert "timestamp" in data
            assert "discovery_id" in data

        except ImportError:
            pytest.skip("AgentDiscovery not available")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
