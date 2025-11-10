"""
Smoke Tests for Intelligent OpenAI Client
Quick validation tests to ensure integration works properly.
"""

import os
import pytest
from unittest.mock import Mock, patch

# Import the client
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.ai.intelligent_openai_client import (
    IntelligentOpenAIClient,
    ChatMessage
)


class TestIntelligentClientSmoke:
    """Smoke tests for the intelligent OpenAI client."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test basic client initialization."""
        with patch.dict(os.environ, {}, clear=True):
            client = IntelligentOpenAIClient(enable_routing=False)
            
            assert not client.enable_routing
            assert not client._initialized
            assert len(client.providers) == 0
            assert len(client.active_clients) == 0
    
    @pytest.mark.asyncio
    async def test_provider_registration(self):
        """Test provider registration with mock API keys."""
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'test-key',
            'AZURE_OPENAI_API_KEY': 'azure-test-key'
        }):
            client = IntelligentOpenAIClient(enable_routing=False)
            
            # Should register providers based on env vars
            assert len(client.providers) >= 2
            assert 'openai' in client.providers
            assert 'azure' in client.providers
    
    @pytest.mark.asyncio
    async def test_client_without_api_keys(self):
        """Test client behavior when no API keys are present."""
        with patch.dict(os.environ, {}, clear=True):
            client = IntelligentOpenAIClient(enable_routing=False)
            await client.initialize()
            
            # Should handle missing keys gracefully
            assert len(client.active_clients) == 0
            assert client._initialized
    
    @pytest.mark.asyncio
    async def test_friendly_status_messages(self):
        """Test friendly status message generation."""
        with patch.dict(os.environ, {}, clear=True):
            client = IntelligentOpenAIClient(enable_routing=False)
            
            # Not initialized
            status = client.get_friendly_status()
            assert "Initializing" in status or "🔄" in status
            
            # Initialized with no providers
            await client.initialize()
            status = client.get_friendly_status()
            # Should have a friendly message about providers
            assert any(keyword in status for keyword in ["providers", "No providers", "✨", "❌"])
    
    @pytest.mark.asyncio
    async def test_chat_message_conversion(self):
        """Test ChatMessage to dict conversion."""
        msg = ChatMessage(
            role="user",
            content="Hello world",
            name="test_user"
        )
        
        msg_dict = msg.to_dict()
        assert msg_dict["role"] == "user"
        assert msg_dict["content"] == "Hello world"
        assert msg_dict["name"] == "test_user"
    
    @pytest.mark.asyncio
    async def test_cache_key_generation(self):
        """Test cache key generation consistency."""
        client = IntelligentOpenAIClient(enable_routing=False)
        
        messages = [ChatMessage(role="user", content="test")]
        
        key1 = client._generate_cache_key(messages, "gpt-3.5-turbo", 0.7, 100)
        key2 = client._generate_cache_key(messages, "gpt-3.5-turbo", 0.7, 100)
        
        assert key1 == key2
        assert len(key1) == 64  # SHA256 hex length
    
    @pytest.mark.asyncio
    async def test_cache_operations(self):
        """Test cache set and get operations."""
        client = IntelligentOpenAIClient(enable_routing=False)
        
        # Test cache miss
        result = client._get_cached_response("nonexistent")
        assert result is None
        
        # Test cache set and get
        test_response = {"choices": [{"message": {"content": "test"}}]}
        client._cache_response("test_key", test_response)
        
        result = client._get_cached_response("test_key")
        assert result == test_response
    
    @pytest.mark.asyncio
    @patch('core.ai.intelligent_openai_client.OPENAI_AVAILABLE', True)
    @patch('core.ai.intelligent_openai_client.OpenAI')
    async def test_mock_api_call(self, mock_openai):
        """Test API call with mocked OpenAI client."""
        # Setup mock
        mock_client = Mock()
        mock_response = Mock()
        mock_response.model_dump.return_value = {
            "choices": [{"message": {"content": "Mock response"}}]
        }
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            client = IntelligentOpenAIClient(enable_routing=False)
            await client.initialize()
            
            # Make a request
            messages = [ChatMessage(role="user", content="test")]
            response = await client.chat_completion(messages=messages)
            
            assert response["choices"][0]["message"]["content"] == "Mock response"
    
    @pytest.mark.asyncio
    async def test_routing_disabled_fallback(self):
        """Test that routing disabled works correctly."""
        client = IntelligentOpenAIClient(enable_routing=False)
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            await client.initialize()
            
            # Should not have router
            assert client.router is None
            
            # Status should reflect routing disabled
            status = client.get_status()
            assert not status["routing_enabled"]


class TestIntegrationSmoke:
    """Integration smoke tests."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_mock_flow(self):
        """Test complete flow with mocked dependencies."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('core.ai.intelligent_openai_client.OPENAI_AVAILABLE', True):
                with patch('core.ai.intelligent_openai_client.OpenAI') as mock_openai:
                    # Setup mock response
                    mock_client = Mock()
                    mock_response = Mock()
                    mock_response.model_dump.return_value = {
                        "choices": [{"message": {"content": "Test response"}}],
                        "usage": {"total_tokens": 10}
                    }
                    mock_client.chat.completions.create.return_value = mock_response
                    mock_openai.return_value = mock_client
                    
                    # Create and use client
                    client = IntelligentOpenAIClient(enable_routing=False)
                    await client.initialize()
                    
                    # Make request
                    messages = [
                        ChatMessage(role="system", content="You are helpful"),
                        ChatMessage(role="user", content="Say hello")
                    ]
                    
                    response = await client.chat_completion(
                        messages=messages,
                        model="gpt-3.5-turbo",
                        temperature=0.7
                    )
                    
                    # Verify response
                    assert response["choices"][0]["message"]["content"] == "Test response"
                    
                    # Check metrics
                    metrics = client.metrics.get_stats()
                    assert client.metrics.total_requests == 1
                    assert metrics["hit_rate"] == 0.0  # First request is a miss
                    
                    await client.close()
    
    @pytest.mark.asyncio
    async def test_cache_hit_flow(self):
        """Test cache hit on second identical request."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('core.ai.intelligent_openai_client.OPENAI_AVAILABLE', True):
                with patch('core.ai.intelligent_openai_client.OpenAI') as mock_openai:
                    # Setup mock
                    mock_client = Mock()
                    mock_response = Mock()
                    mock_response.model_dump.return_value = {
                        "choices": [{"message": {"content": "Cached response"}}]
                    }
                    mock_client.chat.completions.create.return_value = mock_response
                    mock_openai.return_value = mock_client
                    
                    client = IntelligentOpenAIClient(enable_routing=False)
                    await client.initialize()
                    
                    messages = [ChatMessage(role="user", content="cache test")]
                    
                    # First request
                    response1 = await client.chat_completion(messages=messages)
                    
                    # Second request should hit cache
                    response2 = await client.chat_completion(messages=messages)
                    
                    # Both should be identical
                    assert response1 == response2
                    
                    # Cache metrics should show hit
                    metrics = client.metrics.get_stats()
                    assert client.metrics.total_requests == 2
                    assert metrics["hit_rate"] == 0.5  # 1 hit out of 2 requests
                    
                    await client.close()


if __name__ == "__main__":
    # Run smoke tests
    pytest.main([__file__, "-v", "--tb=short", "-k", "smoke"])
