# AI Assistant Examples

This directory contains example scripts demonstrating how to use the AI Assistant module integrated with the automation framework.

## Prerequisites

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up GitHub Token:**
   - Get a token at: https://github.com/settings/tokens
   - Add to `.env` file:
     ```env
     GITHUB_TOKEN=your_github_pat_token_here
     ```

## Examples

### 1. Basic Usage (`assistant_basic_usage.py`)

Demonstrates fundamental assistant features:
- Simple conversations
- System prompts
- Conversation history
- Resetting conversations
- Custom model parameters

**Run:**
```bash
python examples/assistant_basic_usage.py
```

**What you'll learn:**
- How to create an assistant
- How to send messages and get responses
- How to customize behavior with system prompts
- How to manage conversation state

---

### 2. Tool Calling (`assistant_with_tools.py`)

Shows how to register custom tools/functions:
- Time checking tool
- Calculator tool
- File information tool
- Multiple tools working together

**Run:**
```bash
python examples/assistant_with_tools.py
```

**What you'll learn:**
- How to register custom functions
- How to define tool parameters (JSON schema)
- How the assistant automatically calls tools
- How to handle tool errors

---

### 3. Automation Integration (`assistant_automation_integration.py`)

Demonstrates integration with the automation framework:
- Using assistant with Context
- Integration with AutomationLogger
- Task planning helper
- Interactive sessions
- Confirmation logic

**Run:**
```bash
python examples/assistant_automation_integration.py
```

**What you'll learn:**
- How to integrate with automation Context
- How to use with Logger for tracking
- How to build task planning workflows
- How to use assistant for decision support

---

### 4. Interactive Demo (`assistant_interactive_demo.py`)

Interactive command-line chat interface:
- Real-time conversation
- Built-in commands (/reset, /history, /help, /quit)
- User-friendly interface

**Run:**
```bash
python examples/assistant_interactive_demo.py
```

**Commands:**
- `/reset` - Clear conversation history
- `/history` - View all messages
- `/help` - Show help
- `/quit` - Exit

**What you'll learn:**
- How to build an interactive chat interface
- How to handle user commands
- How to display conversation history
- How to handle errors gracefully

---

## Quick Start

1. **First time setup:**
   ```bash
   # Install dependencies
   pip install -r requirements.txt

   # Copy environment template
   cp .env.example .env

   # Edit .env and add your GITHUB_TOKEN
   ```

2. **Run the interactive demo:**
   ```bash
   python examples/assistant_interactive_demo.py
   ```

3. **Try the examples in order:**
   ```bash
   python examples/assistant_basic_usage.py
   python examples/assistant_with_tools.py
   python examples/assistant_automation_integration.py
   ```

## Common Use Cases

### Code Review Assistant
```python
system_prompt = "You are a code review assistant. Analyze code for bugs, style issues, and improvements."
assistant = create_assistant(system_prompt=system_prompt)
response = assistant.chat("Review this function: def add(a, b): return a + b")
```

### Documentation Helper
```python
system_prompt = "You help write clear, concise documentation for code."
assistant = create_assistant(system_prompt=system_prompt)
response = assistant.chat("Write documentation for a function that calculates factorial")
```

### Task Planner
```python
system_prompt = "You help break down complex tasks into actionable steps."
assistant = create_assistant(system_prompt=system_prompt)
response = assistant.chat("I need to deploy a web app to production. What steps should I take?")
```

### Debugging Assistant
```python
system_prompt = "You are a debugging expert. Help identify and fix code issues."
assistant = create_assistant(system_prompt=system_prompt)
response = assistant.chat("I'm getting a KeyError in my Python script. How do I debug it?")
```

## Tips

1. **Start with basic_usage.py** to understand fundamentals
2. **Experiment with system prompts** to customize behavior
3. **Use the interactive demo** for quick testing
4. **Check the full guide** at `docs/AI_ASSISTANT_GUIDE.md`

## Troubleshooting

### "GITHUB_TOKEN environment variable is required"
- Make sure you've set `GITHUB_TOKEN` in your `.env` file
- Verify the token is valid at https://github.com/settings/tokens

### Import errors
- Run `pip install -r requirements.txt`
- Make sure you're in the project root directory

### Rate limiting
- GitHub Models has rate limits
- Wait a few minutes between large batches of requests
- Consider adding delays between API calls

## Next Steps

After trying these examples:
1. Read the full guide: `docs/AI_ASSISTANT_GUIDE.md`
2. Integrate the assistant into your own automation tasks
3. Create custom tools for your specific use cases
4. Experiment with different models and parameters

## Support

- Full documentation: `docs/AI_ASSISTANT_GUIDE.md`
- Azure AI Inference: https://learn.microsoft.com/en-us/azure/ai-services/
- GitHub Models: https://github.com/marketplace/models
