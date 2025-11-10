# ChatGPT Integration Guide for Echoes AI Assistant

## Overview
The Echoes AI Assistant now supports ChatGPT integration, providing seamless switching between advanced local intelligence and OpenAI's ChatGPT models.

## Installation Requirements

### Install OpenAI Package
```bash
pip install openai
```

### Set Up API Key
Option 1 - Environment Variable (Recommended):
```bash
export OPENAI_API_KEY="your-api-key-here"
# On Windows:
set OPENAI_API_KEY="your-api-key-here"
```

Option 2 - Runtime Configuration:
```
enable openai your-api-key-here
```

## Usage Instructions

### Basic Usage
```bash
python assistant.py
```

### Enable ChatGPT Integration
```
💬 You: enable openai sk-your-api-key-here
🤖 Assistant: ✅ OpenAI enabled!
```

### Switch Between Models
```
💬 You: set model gpt-4
🤖 Assistant: 🤖 Model set to gpt-4

💬 You: set model gpt-3.5-turbo
🤖 Assistant: 🤖 Model set to gpt-3.5-turbo
```

### Disable ChatGPT
```
💬 You: disable openai
🤖 Assistant: ✅ OpenAI disabled. Using local intelligence.
```

## Available Models

### GPT-3.5-Turbo
- **Speed**: Fast response times
- **Cost**: Economical for frequent use
- **Capabilities**: General conversation, basic reasoning
- **Best for**: Quick responses, casual chat

### GPT-4
- **Speed**: Moderate response times
- **Cost**: Higher per-token cost
- **Capabilities**: Advanced reasoning, complex problem-solving
- **Best for**: Complex questions, detailed analysis

### GPT-4-Turbo-Preview
- **Speed**: Fastest GPT-4 variant
- **Cost**: Competitive pricing
- **Capabilities**: Latest GPT-4 improvements
- **Best for**: Cutting-edge performance

## Features

### Intelligent Fallback
- Automatic fallback to local intelligence if ChatGPT fails
- Seamless user experience with no interruption
- Error recovery and retry mechanisms

### Context Preservation
- Conversation history maintained across model switches
- Context-aware responses regardless of intelligence source
- Session continuity and memory

### Performance Monitoring
- Track which intelligence source is being used
- Monitor response times and success rates
- Compare performance between models

## Configuration Options

### Model Selection
```python
assistant = IntelligentAssistant(openai_api_key="your-key")
assistant.set_model("gpt-4")
```

### Fallback Behavior
```python
assistant.fallback_enabled = True  # Enable local fallback
assistant.fallback_enabled = False  # ChatGPT only
```

### Temperature and Parameters
The system uses optimized parameters:
- Temperature: 0.7 (balanced creativity/accuracy)
- Max Tokens: 1000 (comprehensive responses)
- Top P: 1.0 (full probability distribution)

## Cost Management

### Monitoring Usage
Check stats to track API usage:
```
💬 You: stats
📊 Assistant Stats:
  total_interactions: 15
  current_model: gpt-4
  intelligence_source: ChatGPT
```

### Cost Optimization Tips
1. Use GPT-3.5-turbo for casual conversations
2. Switch to GPT-4 for complex problems only
3. Enable fallback to avoid API failures
4. Monitor usage with stats command

## Troubleshooting

### Common Issues

**"OpenAI not installed"**
```bash
pip install openai
```

**"API key not found"**
- Set environment variable or use enable command
- Verify API key is valid and active

**"Connection failed"**
- Check internet connection
- Verify API key has sufficient credits
- Try disabling and re-enabling OpenAI

**"Model not available"**
- Check your API access level
- Some models require special access
- Use `set model` to see available options

### Error Recovery
The system automatically:
- Falls back to local intelligence on errors
- Maintains conversation context
- Provides clear error messages
- Allows retry without losing state

## Best Practices

### For Development
1. Start with local intelligence for testing
2. Enable ChatGPT for user-facing features
3. Use appropriate models for different tasks
4. Monitor costs and performance

### For Production
1. Set environment variables for API keys
2. Enable fallback for reliability
3. Use GPT-3.5-turbo for cost efficiency
4. Implement usage monitoring

### For Advanced Users
1. Experiment with different models
2. Compare response quality
3. Optimize for your specific use case
4. Leverage conversation context

## Security Considerations

### API Key Protection
- Never commit API keys to version control
- Use environment variables in production
- Rotate keys regularly for security
- Monitor API usage for anomalies

### Data Privacy
- Conversation history stored locally
- API calls to OpenAI include conversation context
- Consider privacy implications for sensitive data
- Use local intelligence for confidential conversations

## Integration Examples

### Python Script Integration
```python
from assistant import IntelligentAssistant

# Initialize with ChatGPT
assistant = IntelligentAssistant(openai_api_key="your-key")

# Chat with automatic model selection
response = assistant.chat("Hello, how can you help me?")

# Switch models dynamically
assistant.set_model("gpt-4")
advanced_response = assistant.chat("Explain quantum computing")

# Check current configuration
stats = assistant.get_stats()
print(f"Using: {stats['intelligence_source']}")
```

### Environment Configuration
```bash
# .env file
OPENAI_API_KEY=your-api-key-here

# Load in Python
from dotenv import load_dotenv
load_dotenv()

assistant = IntelligentAssistant()
```

## Performance Comparison

### Response Times
- Local Intelligence: ~0.1s
- GPT-3.5-turbo: ~0.5-1.0s
- GPT-4: ~1.0-2.0s

### Quality Metrics
- Local Intelligence: Good for basic tasks
- GPT-3.5-turbo: Excellent for general conversation
- GPT-4: Superior for complex reasoning

### Cost Efficiency
- Local Intelligence: Free
- GPT-3.5-turbo: $0.002/1K tokens
- GPT-4: $0.03/1K tokens

## Future Enhancements

### Planned Features
- Streaming responses from ChatGPT
- Custom model fine-tuning
- Batch processing capabilities
- Advanced prompt engineering
- Multi-model comparison

### Integration Roadmap
1. Enhanced streaming support
2. Custom instruction sets
3. Plugin system for extensions
4. Enterprise features
5. Advanced analytics

---

**Quick Start Summary:**
1. Install: `pip install openai`
2. Set key: `export OPENAI_API_KEY="your-key"`
3. Run: `python assistant.py`
4. Enable: `enable openai` (if not auto-enabled)
5. Chat normally - enjoy enhanced intelligence! 🚀
