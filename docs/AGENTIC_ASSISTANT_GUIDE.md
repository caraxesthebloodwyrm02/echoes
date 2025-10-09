

# Agentic AI Assistant - Complete Guide

## Overview

The Agentic AI Assistant is a sophisticated multi-model AI system with intelligent routing, autonomous tool execution, and seamless automation framework integration.

### Key Features

- ✅ **Multi-Model Support**: QwQ, DeepSeek, Mistral, Qwen, Llama, GPT-4
- ✅ **Intelligent Routing**: Automatic model selection based on task type
- ✅ **Autonomous Actions**: Built-in tool library for file operations, calculations, time, etc.
- ✅ **Agentic Behavior**: Proactive, context-aware, and goal-oriented
- ✅ **Framework Integration**: Seamless integration with automation Context and Logger
- ✅ **Configuration System**: Flexible configuration with persistence
- ✅ **Orchestration Layer**: High-level API for complex workflows

## Quick Start

### Installation

```bash
pip install azure-ai-inference
```

### Configuration

Add to `.env`:
```env
GITHUB_TOKEN=your_github_pat_token_here
```

Get token at: https://github.com/settings/tokens

### Simplest Usage

```python
from app.core import chat, code, reason, plan

# Quick chat
response = chat("What is Python?")

# Code generation
response = code("Write a function to sort a list")

# Reasoning
response = reason("Why use microservices?")

# Planning
response = plan("Steps to deploy a web app")
```

## Available Models

### Industry-Leading Models

| Model | ID | Best For | Context | Provider |
|-------|----|---------| |--------|----------|
| **QwQ-32B** | `qwq-32b` | Reasoning, complex problems | 32K | Alibaba |
| **DeepSeek-Coder** | `deepseek-coder` | Code generation, debugging | 16K | DeepSeek |
| **Qwen 2.5 Coder** | `qwen-coder` | Coding, reasoning | 32K | Alibaba |
| **Mistral Large** | `mistral-large` | General purpose, tool calling | 128K | Mistral |
| **Mistral Small** | `mistral-small` | Fast, cost-effective | 32K | Mistral |
| **Llama 3.3** | `llama-3.3` | General purpose, open-source | 128K | Meta |
| **GPT-4.1** | `gpt-4.1` | Advanced reasoning | 8K | OpenAI |

### Model Capabilities

- **Reasoning**: QwQ-32B, Mistral Large, GPT-4.1
- **Coding**: DeepSeek-Coder, Qwen Coder, QwQ-32B
- **Agentic**: QwQ-32B, Mistral Large, Llama 3.3
- **Fast**: Mistral Small, DeepSeek-Coder
- **Long Context**: Mistral Large (128K), Llama 3.3 (128K)

## Usage Patterns

### 1. Convenience Functions (Easiest)

```python
from app.core import chat, code, reason, plan

# General chat
response = chat("Explain Docker")

# Coding tasks
response = code("Write a binary search")

# Reasoning tasks
response = reason("Why is caching important?")

# Planning tasks
response = plan("Plan a microservices architecture")
```

### 2. Agentic Assistant (Full Control)

```python
from app.core import create_agentic_assistant

# Create assistant
assistant = create_agentic_assistant(
    user_name="YourName",
    model_id="qwq-32b",  # Optional, auto-selects if None
    use_case="agentic",   # 'coding', 'reasoning', 'agentic'
)

# Chat (tools auto-registered)
response = assistant.chat("What time is it and what's 2+2?")

# Switch models dynamically
assistant.switch_model("deepseek-coder")
response = assistant.chat("Write a quicksort")

# Get statistics
stats = assistant.get_stats()
print(stats)
```

### 3. Orchestrator (Most Powerful)

```python
from app.core import get_orchestrator, TaskType

# Get orchestrator (singleton)
orchestrator = get_orchestrator()

# Automatic task routing
response = orchestrator.execute_task(
    "Write a REST API",
    task_type=TaskType.CODING,  # Routes to best coding model
)

# Convenience methods
response = orchestrator.code_task("Write bubble sort")
response = orchestrator.reasoning_task("Explain Big O")
response = orchestrator.planning_task("Plan deployment")

# Manual model selection
response = orchestrator.chat("Hello", model_id="mistral-large")

# List available models
models = orchestrator.list_available_models()

# Get stats
stats = orchestrator.get_stats()
```

## Built-in Tools

The agentic assistant includes these tools (auto-registered):

### File Operations

```python
# Read file
assistant.chat("Read the requirements.txt file")

# List files
assistant.chat("List all Python files in the current directory")

# Get file info
assistant.chat("Tell me about the main.py file")
```

### System Information

```python
# Current time
assistant.chat("What time is it?")

# Automation context
assistant.chat("What's my current automation context?")
```

### Calculations

```python
# Safe math
assistant.chat("Calculate 157 * 234")
assistant.chat("What's (100 + 50) / 3?")
```

## Configuration

### Using AssistantConfig

```python
from app.core import AssistantConfig, create_agentic_assistant

# Create custom config
config = AssistantConfig(
    user_name="Developer",
    default_model="qwq-32b",
    temperature=0.7,
    auto_register_tools=True,
    proactive_suggestions=True,
    verbose_logging=True,
    enable_file_tools=True,
    safe_mode=True,
)

# Use config
assistant = create_agentic_assistant(
    user_name=config.user_name,
    model_id=config.default_model,
    temperature=config.temperature,
)
```

### Configuration Options

```python
@dataclass
class AssistantConfig:
    # User settings
    user_name: str = "User"
    user_role: str = "Developer"

    # Model settings
    default_model: str = "qwq-32b"
    fallback_model: str = "mistral-small"
    temperature: float = 0.7
    top_p: float = 0.9

    # Behavior settings
    auto_register_tools: bool = True
    proactive_suggestions: bool = True
    verbose_logging: bool = True
    max_conversation_turns: int = 20

    # Tool settings
    enable_file_tools: bool = True
    enable_code_execution: bool = True
    safe_mode: bool = True

    # Integration settings
    automation_integration: bool = True
    use_automation_logger: bool = True

    # Advanced settings
    model_routing: bool = True
    retry_on_error: bool = True
    max_retries: int = 2
```

### Persistent Configuration

```python
from app.core import ConfigManager

# Load config
manager = ConfigManager()
config = manager.load()

# Update config
manager.update(
    default_model="deepseek-coder",
    temperature=0.3,
)

# Save
manager.save()

# Reset to defaults
manager.reset()
```

## Automation Framework Integration

### With Context and Logger

```python
from app.core import create_agentic_assistant
from automation.core.context import Context
from automation.core.logger import AutomationLogger

# Create automation components
context = Context(
    dry_run=False,
    user_info={"name": "Developer", "role": "Engineer"},
    env={"environment": "production"},
)

logger = AutomationLogger()

# Create integrated assistant
assistant = create_agentic_assistant(
    user_name="Developer",
    model_id="qwq-32b",
    automation_context=context,
    logger=logger,
)

# Assistant now uses logger automatically
logger.info("Querying assistant")
response = assistant.chat("Analyze the codebase")
logger.success("Query completed")

# Assistant can access context via tool
response = assistant.chat("What's my current context?")
```

### With Orchestrator

```python
from app.core import get_orchestrator, AssistantConfig
from automation.core.context import Context

config = AssistantConfig(
    user_name="Engineer",
    automation_integration=True,
    use_automation_logger=True,
)

context = Context(dry_run=False)

orchestrator = get_orchestrator(
    config=config,
    automation_context=context,
)

# Orchestrator integrates with automation framework
response = orchestrator.planning_task("Plan the deployment")
```

## Advanced Features

### Custom Tools

```python
import json

def custom_tool_function(param1: str, param2: int) -> str:
    """Your custom tool logic."""
    result = {"param1": param1, "param2": param2, "result": param1 * param2}
    return json.dumps(result)

# Register custom tool
assistant.assistant.register_tool(
    name="my_custom_tool",
    description="Does something custom",
    parameters={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "First param"},
            "param2": {"type": "integer", "description": "Second param"},
        },
        "required": ["param1", "param2"],
    },
    function=custom_tool_function,
)

# Use it
response = assistant.chat("Use my_custom_tool with 'test' and 42")
```

### Model Comparison

```python
models = ["qwq-32b", "deepseek-coder", "mistral-large"]
question = "What are SOLID principles?"

for model_id in models:
    assistant = create_agentic_assistant(model_id=model_id)
    response = assistant.chat(question)
    print(f"\n{model_id}:\n{response}\n")
```

### Task Routing

```python
from app.core import get_orchestrator, TaskType

orchestrator = get_orchestrator()

# Different task types auto-route to best models
tasks = [
    ("Write a sorting algorithm", TaskType.CODING),
    ("Explain time complexity", TaskType.REASONING),
    ("Plan a CI/CD pipeline", TaskType.PLANNING),
    ("Review this code", TaskType.CODE_REVIEW),
]

for message, task_type in tasks:
    response = orchestrator.execute_task(message, task_type=task_type)
    model = orchestrator.active_assistant.model_info.name
    print(f"{task_type.value} -> {model}")
```

## Best Practices

### 1. Choose the Right Model

```python
# For reasoning and complex problems
assistant = create_agentic_assistant(model_id="qwq-32b")

# For coding tasks
assistant = create_agentic_assistant(model_id="deepseek-coder")

# For general purpose
assistant = create_agentic_assistant(model_id="mistral-large")

# Or let it auto-select
assistant = create_agentic_assistant(use_case="agentic")
```

### 2. Use Tools Proactively

```python
# Don't ask permission
response = assistant.chat("Read the main.py file and summarize it")

# Tools execute automatically
response = assistant.chat("What's the current time and list files here")
```

### 3. Leverage Agentic Behavior

```python
# Give high-level goals
response = assistant.chat(
    "I need to deploy this application to production. "
    "Analyze the codebase and give me a deployment plan."
)

# Assistant will use tools to gather info and provide comprehensive plan
```

### 4. Reset Long Conversations

```python
# Reset when conversation gets long
if len(assistant.assistant.get_history()) > 30:
    assistant.reset(keep_tools=True)
```

### 5. Handle Errors Gracefully

```python
try:
    response = assistant.chat(message)
except Exception as e:
    logger.error(f"Assistant error: {e}")
    # Fallback or retry logic
```

## Examples

### Complete examples in `examples/`:

1. **`quickstart.py`** - Get started in 30 seconds
2. **`agentic_assistant_demo.py`** - Comprehensive agentic assistant demo
3. **`orchestrator_demo.py`** - Orchestrator features and routing
4. **`assistant_basic_usage.py`** - Basic assistant usage
5. **`assistant_with_tools.py`** - Tool calling examples
6. **`assistant_automation_integration.py`** - Automation framework integration

Run any example:
```bash
python examples/quickstart.py
python examples/agentic_assistant_demo.py
python examples/orchestrator_demo.py
```

## API Reference

### Core Functions

```python
# Convenience functions
chat(message: str, model_id: str = None) -> str
code(message: str) -> str
reason(message: str) -> str
plan(message: str) -> str

# Factories
create_agentic_assistant(
    user_name: str = "User",
    model_id: str = None,
    use_case: str = "agentic",
    **kwargs
) -> AgenticAssistant

get_orchestrator(
    config: AssistantConfig = None,
    automation_context: Context = None,
) -> AssistantOrchestrator

# Model registry
ModelRegistry.get_model(model_id: str) -> ModelInfo
ModelRegistry.get_default_model(use_case: str) -> ModelInfo
ModelRegistry.list_models() -> List[ModelInfo]
```

### AgenticAssistant Methods

```python
assistant.chat(message: str) -> str
assistant.switch_model(model_id: str) -> bool
assistant.reset(keep_tools: bool = True) -> None
assistant.get_stats() -> Dict[str, Any]
assistant.register_standard_tools() -> None
```

### AssistantOrchestrator Methods

```python
orchestrator.execute_task(message: str, task_type: TaskType, model_id: str) -> str
orchestrator.chat(message: str, model_id: str) -> str
orchestrator.code_task(message: str) -> str
orchestrator.reasoning_task(message: str) -> str
orchestrator.planning_task(message: str) -> str
orchestrator.switch_model(model_id: str) -> bool
orchestrator.reset_conversation(model_id: str) -> None
orchestrator.get_stats() -> Dict[str, Any]
orchestrator.list_available_models() -> List[Dict]
```

## Troubleshooting

### "GITHUB_TOKEN environment variable is required"
**Fix:** Set `GITHUB_TOKEN` in `.env` file

### Rate Limiting
**Fix:** Wait between requests, use `mistral-small` for faster tasks

### Context Length Errors
**Fix:** Reset conversation with `assistant.reset()`

### Tool Not Found
**Fix:** Ensure tools are registered with `register_standard_tools()`

### Import Errors
**Fix:** Run `pip install -r requirements.txt`

## Performance Tips

1. **Use appropriate models**: DeepSeek for coding, QwQ for reasoning
2. **Enable model routing**: Set `model_routing=True` in config
3. **Lower temperature for speed**: Use `temperature=0.3` for deterministic tasks
4. **Reuse assistants**: Orchestrator caches assistant instances
5. **Reset conversations**: Prevent context buildup

## Security

1. ✅ Token stored in `.env` (gitignored)
2. ✅ Safe mode restricts file access to project directory
3. ✅ Tool execution sandboxed
4. ✅ Input validation on all tools
5. ✅ No arbitrary code execution

## Resources

- **Examples**: `examples/` directory
- **Basic Guide**: `docs/AI_ASSISTANT_GUIDE.md`
- **Integration Summary**: `AI_ASSISTANT_INTEGRATION.md`
- **Quick Start**: `ASSISTANT_QUICK_START.md`
- **GitHub Models**: https://github.com/marketplace/models
- **Azure AI**: https://learn.microsoft.com/azure/ai-services/

## Support

For issues:
1. Check examples in `examples/`
2. Review this guide
3. Check GitHub Models documentation
4. Verify `GITHUB_TOKEN` is set correctly

## License

Part of the automation framework project (MIT License).
