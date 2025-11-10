"""Unit tests for the AI client and model manager."""

import time
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from core.ai.model_manager import ModelConfig, ModelManager
from core.ai.openai_client import ChatMessage, OpenAIClient

# Test data
SAMPLE_MODEL_RESPONSE = {
    "id": "chatcmpl-123",
    "object": "chat.completion",
    "created": int(time.time()),
    "model": "gpt-3.5-turbo",
    "choices": [
        {
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "Test response",
                "tool_calls": None,
            },
            "finish_reason": "stop",
        }
    ],
    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
}


# Fixtures
@pytest.fixture
def mock_openai():
    with patch("openai.OpenAI") as mock:
        yield mock


@pytest.fixture
def model_manager():
    return ModelManager()


@pytest.fixture
def openai_client(model_manager):
    with patch("openai.OpenAI") as mock_client:
        mock_client.return_value.models.list.return_value = MagicMock(data=[])
        client = OpenAIClient(api_key="test-key", model_manager=model_manager)
        client._client = mock_client.return_value
        yield client


def test_model_manager_initialization(model_manager):
    """Test that ModelManager initializes with default models."""
    models = model_manager.list_models()
    assert len(models) >= 2  # Should have at least the default models
    assert model_manager.get_current_model() is not None


def test_add_and_get_model(model_manager):
    """Test adding and retrieving a model."""
    model_config = ModelConfig(
        id="test-model",
        purpose="testing",
        max_tokens=2048,
        cost_per_token=0.00001,
        priority=1,
    )

    model_manager.add_model(model_config)
    retrieved = model_manager.get_model("test-model")

    assert retrieved is not None
    assert retrieved.id == "test-model"
    assert retrieved.purpose == "testing"


def test_set_current_model(model_manager):
    """Test setting the current model."""
    model_manager.add_model(ModelConfig(id="test-model"))
    assert model_manager.set_current_model("test-model")
    assert model_manager.get_current_model().id == "test-model"

    # Test with invalid model
    assert not model_manager.set_current_model("non-existent-model")


def test_model_usage_tracking(model_manager):
    """Test that model usage is tracked correctly."""
    model_id = "test-model"
    model_manager.add_model(ModelConfig(id=model_id))

    # Record some usage
    model_manager._record_usage(model_id, 100)
    model_manager._record_usage(model_id, 200)
    model_manager._record_usage(model_id, 0, error=True)

    stats = model_manager.get_usage_stats(model_id)[model_id]
    assert stats["calls"] == 3  # All calls should be counted, including errors
    assert stats["tokens"] == 300
    assert stats["errors"] == 1
    assert stats["last_used"] is not None


def test_openai_client_initialization(openai_client):
    """Test that OpenAIClient initializes correctly."""
    assert openai_client is not None
    assert openai_client.api_key == "test-key"
    assert openai_client.model_manager is not None


def test_chat_completion(openai_client):
    """Test generating a chat completion."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.id = SAMPLE_MODEL_RESPONSE["id"]
    mock_response.object = SAMPLE_MODEL_RESPONSE["object"]
    mock_response.created = SAMPLE_MODEL_RESPONSE["created"]
    mock_response.model = SAMPLE_MODEL_RESPONSE["model"]

    mock_choice = MagicMock()
    mock_choice.index = 0
    mock_choice.message.role = "assistant"
    mock_choice.message.content = "Test response"
    mock_choice.message.tool_calls = None
    mock_choice.finish_reason = "stop"

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = 10
    mock_usage.completion_tokens = 5
    mock_usage.total_tokens = 15

    mock_response.choices = [mock_choice]
    mock_response.usage = mock_usage

    # Mock the actual API call to return our mock response
    openai_client._client.chat.completions.create.return_value = mock_response

    # Make the API call
    messages = [{"role": "user", "content": "Hello, world!"}]
    response = openai_client.chat_completion(messages)

    # Verify the response
    assert response["id"] == SAMPLE_MODEL_RESPONSE["id"]
    assert response["choices"][0]["message"]["content"] == "Test response"
    assert response["usage"]["total_tokens"] == 15

    # Verify the model usage was recorded
    stats = openai_client.model_manager.get_usage_stats(response["model"])[
        response["model"]
    ]
    assert stats["tokens"] == 15
    assert stats["calls"] == 1


def test_generate_text(openai_client):
    """Test the generate_text convenience method."""
    # Mock the chat_completion method
    openai_client.chat_completion = MagicMock(
        return_value={
            "choices": [{"message": {"content": "Test response", "role": "assistant"}}]
        }
    )

    # Test without system message
    response = openai_client.generate_text("Hello!")
    assert response == "Test response"

    # Test with system message
    response = openai_client.generate_text(
        "Hello!", system_message="You are a helpful assistant."
    )
    assert response == "Test response"

    # Verify the chat_completion was called with the right arguments
    openai_client.chat_completion.assert_called_with(
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]
    )


def test_rate_limiting(openai_client):
    """Test that rate limiting is enforced."""
    # Mock time.sleep to speed up the test
    with patch("time.sleep") as mock_sleep:
        # First call - no delay
        openai_client._rate_limit_delay()
        mock_sleep.assert_not_called()

        # Second call - should trigger a delay
        openai_client._rate_limit_delay()
        mock_sleep.assert_called_once()

        # Reset the mock
        mock_sleep.reset_mock()

        # Set last request time to be long ago - no delay expected
        openai_client._last_request_time = time.time() - 10
        openai_client._rate_limit_delay()
        mock_sleep.assert_not_called()


def test_chat_message_serialization():
    """Test that ChatMessage can be serialized to and from dict."""
    message = ChatMessage(role="user", content="Hello, world!", name="test_user")

    # Convert to dict and back
    message_dict = message.to_dict()
    new_message = ChatMessage.from_dict(message_dict)

    # Verify the data is preserved
    assert new_message.role == message.role
    assert new_message.content == message.content
    assert new_message.name == message.name


def test_model_config_serialization():
    """Test that ModelConfig can be serialized to and from dict."""
    created = datetime(2023, 1, 1)
    config = ModelConfig(
        id="test-model",
        purpose="testing",
        max_tokens=2048,
        cost_per_token=0.00001,
        priority=1,
        created=created,
        owned_by="user123",
    )

    # Convert to dict and back
    config_dict = config.to_dict()
    new_config = ModelConfig.from_dict(config_dict)

    # Verify the data is preserved
    assert new_config.id == config.id
    assert new_config.purpose == config.purpose
    assert new_config.max_tokens == config.max_tokens
    assert new_config.cost_per_token == config.cost_per_token
    assert new_config.priority == config.priority
    assert new_config.owned_by == config.owned_by
    # Handle both string and datetime objects for created
    assert str(new_config.created) == str(config.created)


def test_openai_api_error(openai_client):
    """Test handling of OpenAI API errors."""
    # Mock an API error
    openai_client._client.chat.completions.create.side_effect = Exception("API error")

    # Get the current model
    current_model = openai_client.model_manager.get_current_model().id

    # Record initial error count
    initial_errors = openai_client.model_manager.get_usage_stats(current_model)[
        current_model
    ]["errors"]

    # Make the API call (should raise an exception)
    with pytest.raises(Exception):
        openai_client.chat_completion([{"role": "user", "content": "Hello!"}])

    # Verify the error was recorded
    stats = openai_client.model_manager.get_usage_stats(current_model)[current_model]
    assert stats["errors"] == initial_errors + 1


def test_model_not_found(openai_client):
    """Test behavior when a non-existent model is requested."""
    with pytest.raises(ValueError):
        openai_client.chat_completion(
            [{"role": "user", "content": "Hello!"}], model="non-existent-model"
        )


def test_empty_model_manager():
    """Test ModelManager with no initial models."""
    manager = ModelManager()

    # Clear default models for this test
    for model in manager.list_models():
        manager.remove_model(model.id)

    assert len(manager.list_models()) == 0
    assert manager.get_current_model() is None

    # Test setting current model when none exist
    assert not manager.set_current_model("any-model")
