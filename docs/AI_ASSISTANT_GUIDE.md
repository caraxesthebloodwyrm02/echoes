# AI Assistant Integration Guide

## Overview

The AI Assistant module provides a powerful, conversational AI interface integrated with your automation framework. It uses Azure AI Inference with GitHub Models to provide GPT-4 capabilities with tool calling support.

## Features

- **Conversational Interface**: Natural language interaction with message history
- **Tool/Function Calling**: Register custom Python functions that the AI can call
- **Context Integration**: Works seamlessly with the automation framework's Context and Logger
- **Configurable**: Adjust model parameters (temperature, top_p) for different use cases
- **System Prompts**: Customize assistant behavior for specific tasks

## Quick Start

### 1. Installation

Install the required dependency:

```bash
pip install azure-ai-inference
```

Or install all project dependencies:

```bash
pip install -r requirements.txt
```

### 2. Configuration

Get a GitHub Personal Access Token (PAT):
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (for private repos) or just `public_repo`
4. Copy the token

Add to your `.env` file:

```env
GITHUB_TOKEN=your_github_pat_token_here
```

### 3. Basic Usage

```python
from app.core.assistant import create_assistant

# Create an assistant
assistant = create_assistant()

# Have a conversation
response = assistant.chat("What is Python?")
print(response)

# Continue the conversation
response = assistant.chat("What are its main features?")
print(response)
```

## Advanced Usage

### System Prompts

Customize the assistant's behavior:

```python
system_prompt = """
You are a helpful coding assistant specialized in Python automation.
Provide concise, practical answers with code examples.
"""

assistant = create_assistant(system_prompt=system_prompt)
response = assistant.chat("How do I read a JSON file?")
```

### Tool/Function Calling

Register custom functions that the assistant can call:

```python
from datetime import datetime

def get_current_time() -> str:
    """Get the current time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Register the tool
assistant.register_tool(
    name="get_current_time",
    description="Get the current date and time",
    parameters={
        "type": "object",
        "properties": {},
        "required": [],
    },
    function=get_current_time,
)

# The assistant can now call this function
response = assistant.chat("What time is it?")
```

### Integration with Automation Framework

```python
from app.core.assistant import create_assistant
from automation.core.context import Context
from automation.core.logger import AutomationLogger

# Create automation context
context = Context(dry_run=False)
logger = AutomationLogger()

# Create assistant with context awareness
system_prompt = f"""
You are an automation assistant.
Current environment: {context.env.get('environment', 'development')}
Dry run mode: {context.dry_run}
"""

assistant = create_assistant(system_prompt=system_prompt)

# Use with logging
logger.info("Querying AI assistant")
response = assistant.chat("What tasks should I run?")
logger.success("Query completed")
```

## API Reference

### Assistant Class

#### `__init__(model, endpoint, api_version, temperature, top_p, system_prompt)`

Create a new Assistant instance.

**Parameters:**
- `model` (str): Model identifier (default: "openai/gpt-4.1")
- `endpoint` (str): API endpoint URL
- `api_version` (str): API version
- `temperature` (float): Sampling temperature 0.0-2.0 (default: 1.0)
- `top_p` (float): Nucleus sampling parameter (default: 1.0)
- `system_prompt` (str, optional): System message to set behavior

#### `chat(user_message, max_turns, response_format)`

Send a message and get a response.

**Parameters:**
- `user_message` (str, optional): User message to send
- `max_turns` (int): Maximum conversation turns (default: 10)
- `response_format` (str): "text" or "json_object" (default: "text")

**Returns:** str - Assistant's response

#### `register_tool(name, description, parameters, function)`

Register a tool/function for the assistant to call.

**Parameters:**
- `name` (str): Tool name
- `description` (str): Tool description
- `parameters` (dict): JSON schema for parameters
- `function` (callable): Python function to execute

#### `reset(keep_system_prompt)`

Reset conversation history.

**Parameters:**
- `keep_system_prompt` (bool): Keep system prompt (default: True)

#### `get_history()`

Get conversation history.

**Returns:** List[Dict[str, str]] - Message history

### Helper Functions

#### `create_assistant(system_prompt, **kwargs)`

Factory function to create an Assistant instance.

**Parameters:**
- `system_prompt` (str, optional): System prompt
- `**kwargs`: Additional arguments for Assistant constructor

**Returns:** Assistant instance

## Examples

See the `examples/` directory for complete working examples:

1. **`assistant_basic_usage.py`** - Basic conversation, system prompts, history
2. **`assistant_with_tools.py`** - Tool calling with calculator, file info, time
3. **`assistant_automation_integration.py`** - Integration with automation framework

Run examples:

```bash
python examples/assistant_basic_usage.py
python examples/assistant_with_tools.py
python examples/assistant_automation_integration.py
```

## Model Parameters

### Temperature (0.0 - 2.0)

Controls randomness in responses:
- **0.0-0.3**: Focused, deterministic (good for factual tasks)
- **0.7-1.0**: Balanced creativity and coherence (default)
- **1.5-2.0**: More creative, less predictable

```python
# Deterministic responses
assistant = Assistant(temperature=0.2)

# Creative responses
assistant = Assistant(temperature=1.5)
```

### Top P (0.0 - 1.0)

Nucleus sampling parameter:
- **0.1-0.5**: More focused on likely tokens
- **0.9-1.0**: More diverse responses (default)

## Best Practices

### 1. Use System Prompts

Always set a clear system prompt to guide the assistant's behavior:

```python
system_prompt = """
You are a specialized assistant for [specific domain].
Always [specific instruction].
Never [specific restriction].
"""
```

### 2. Handle Errors Gracefully

```python
try:
    response = assistant.chat(user_message)
except Exception as e:
    logger.error(f"Assistant error: {e}")
    # Fallback behavior
```

### 3. Reset Long Conversations

Reset the conversation periodically to avoid context length limits:

```python
if len(assistant.get_history()) > 20:
    assistant.reset(keep_system_prompt=True)
```

### 4. Use Tools for External Data

Don't expect the assistant to know real-time information. Register tools:

```python
# Good: Register a tool
assistant.register_tool(
    name="get_weather",
    description="Get current weather",
    parameters={...},
    function=get_weather_from_api,
)

# Bad: Expect assistant to know
response = assistant.chat("What's the weather right now?")
```

### 5. Validate Tool Outputs

Always validate and sanitize tool outputs before passing to the assistant:

```python
def safe_file_reader(path: str) -> str:
    # Validate path
    if not Path(path).is_relative_to(project_root):
        return "Error: Path outside project"

    # Read safely
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error: {e}"
```

## Troubleshooting

### "GITHUB_TOKEN environment variable is required"

**Solution:** Set your GitHub PAT in the `.env` file:
```env
GITHUB_TOKEN=ghp_your_token_here
```

### Rate Limiting

GitHub Models has rate limits. If you hit them:
- Wait a few minutes before retrying
- Reduce the frequency of requests
- Consider caching responses

### Context Length Errors

If conversations get too long:
```python
# Reset conversation
assistant.reset(keep_system_prompt=True)

# Or create a new assistant
assistant = create_assistant(system_prompt=system_prompt)
```

### Tool Calling Not Working

Ensure your tool definition matches the JSON schema format:
```python
parameters = {
    "type": "object",
    "properties": {
        "param_name": {
            "type": "string",  # or "number", "boolean", "array", "object"
            "description": "Clear description",
        },
    },
    "required": ["param_name"],  # List required parameters
}
```

## Security Considerations

1. **Never commit tokens**: Keep `GITHUB_TOKEN` in `.env` (gitignored)
2. **Validate tool inputs**: Always validate parameters in tool functions
3. **Limit tool capabilities**: Don't give tools destructive permissions
4. **Sanitize outputs**: Clean tool outputs before displaying to users
5. **Use environment variables**: Never hardcode sensitive data

## Performance Tips

1. **Lower temperature for speed**: Use `temperature=0.3` for faster, more focused responses
2. **Limit max_turns**: Set `max_turns=5` to prevent long tool-calling chains
3. **Cache common queries**: Store frequently asked questions and responses
4. **Batch operations**: Group related questions in one conversation

## Support

For issues or questions:
1. Check the examples in `examples/`
2. Review this guide
3. Check Azure AI Inference documentation: https://learn.microsoft.com/en-us/azure/ai-services/
4. Check GitHub Models documentation: https://github.com/marketplace/models

## License

This module is part of the automation framework project.
