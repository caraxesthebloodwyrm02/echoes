# Grok Integration in EchoesAI

This document describes the integration of xAI's Grok models into the EchoesAI platform.

## Overview

EchoesAI now supports xAI's Grok models alongside OpenAI models. The integration provides:

- **Grok-beta**: General-purpose text model
- **Grok-vision-beta**: Multimodal model with vision capabilities
- Intelligent routing between multiple AI providers
- Seamless API compatibility with existing EchoesAI code

## Setup

### Environment Variables

Set the following environment variables:

```bash
# xAI API Key (required for Grok models)
export XAI_API_KEY="your-xai-api-key-here"

# Optional: Other AI providers
export OPENAI_API_KEY="your-openai-key"
export AZURE_OPENAI_API_KEY="your-azure-key"
```

### Installation

The Grok client is included in the EchoesAI core AI modules. No additional installation is required.

## Usage

### Basic Usage

```python
from core.ai.intelligent_openai_client import IntelligentOpenAIClient

# Create client (automatically detects available providers)
client = IntelligentOpenAIClient()
await client.initialize()

# Use Grok-beta
response = await client.chat_completion(
    messages=[
        {"role": "user", "content": "Hello, what can you tell me about xAI?"}
    ],
    model="grok-beta"
)

# Use Grok-vision-beta
response = await client.chat_completion(
    messages=[
        {"role": "user", "content": "Describe this image: [image data]"}
    ],
    model="grok-vision-beta"
)
```

### Model Selection

Grok models are automatically selected when:
- `model="grok-beta"` or `model="grok-vision-beta"` is specified
- The xAI provider is available and has API key configured
- Intelligent routing chooses xAI as the best provider for the request

### Configuration

Grok models are configured in the ModelManager with:
- **grok-beta**: 128k token context, free during beta
- **grok-vision-beta**: 128k token context, vision capabilities, free during beta

## API Compatibility

The Grok integration maintains full compatibility with existing EchoesAI code:

- Same message format (OpenAI-style)
- Same response structure
- Same error handling
- Same caching and routing features

## Testing

Run the integration test:

```bash
python test_grok_integration.py
```

This will test both Grok-beta and Grok-vision-beta models with basic queries.

## Architecture

### Components

1. **GrokClient**: Dedicated client for xAI API interactions
2. **IntelligentOpenAIClient**: Enhanced to route requests to Grok when appropriate
3. **ModelManager**: Includes Grok model configurations
4. **Routing System**: Automatically selects between OpenAI, xAI, and other providers

### Provider Priority

Default priority order (higher = preferred):
1. Local models (priority 1)
2. Azure OpenAI (priority 2)
3. OpenAI (priority 3)
4. xAI/Grok (priority 4)

## Error Handling

- Graceful fallback if xAI API key is not configured
- Automatic provider switching on failures
- Detailed logging for debugging

## Performance

- Synchronous Grok API calls (wrapped in async context)
- Intelligent caching shared across all providers
- Load balancing and health monitoring

## Future Enhancements

- Streaming responses for Grok models
- Function calling support
- Advanced routing based on model capabilities
- Custom fine-tuning integration
