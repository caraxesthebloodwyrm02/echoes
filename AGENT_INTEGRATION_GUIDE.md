# OpenAI Agents SDK Integration Guide

## Overview
The Echoes project now includes a powerful AI agent orchestration system built on the OpenAI Agents SDK. This enables collaborative AI workflows for code analysis, architecture design, and testing.

## Key Features
- **Multi-Agent Collaboration**: Specialized agents that can hand off tasks to each other
- **Smart Model Selection**: Automatic gpt-4o for important tasks, gpt-4o-mini for basic tasks
- **Rate Limit Handling**: Built-in exponential backoff with retry logic
- **Sequential Task Execution**: Tasks processed in order with full context
- **Session Management**: Built-in conversation memory support
- **Tool Integration**: Framework ready for custom function tools

## Rate Limit Mitigation

The system includes comprehensive rate limit handling based on OpenAI's recommended practices:

### Automatic Retry Logic
- **Exponential Backoff**: Delays increase exponentially (1s, 2s, 4s, 8s...)
- **Jitter**: Random variation prevents thundering herd problems
- **Configurable Limits**: Default 6 retries, customizable per orchestrator
- **Error Tracking**: Detailed success/failure reporting

### Configuration
```python
# Default settings (conservative)
orchestrator = AIAgentOrchestrator()

# Aggressive settings for testing
orchestrator = AIAgentOrchestrator(max_retries=3, initial_delay=0.5)

# Conservative settings for production
orchestrator = AIAgentOrchestrator(max_retries=10, initial_delay=2.0)
```

### What Gets Retried
- Rate limit errors (429)
- Temporary API failures
- Network timeouts
- Other transient errors

### Monitoring
The system provides detailed retry information:
```python
result = await orchestrator.execute_workflow()
print(f"Tasks completed: {result['tasks_completed']}")
print(f"Tasks failed: {result['tasks_failed']}")
print(f"Retry config: {result['retry_config']}")
```

## Quick Start

```python
from ai_agents.orchestrator import create_code_analysis_workflow

# Create a collaborative workflow
orchestrator = create_code_analysis_workflow()

# Add tasks
orchestrator.add_task("Review authentication security", "code_reviewer")
orchestrator.add_task("Design microservices architecture", "architect")

# Execute workflow
result = await orchestrator.execute_workflow()
```

## Agent Types

### Code Reviewer (gpt-4o)
- Analyzes code quality, security, and best practices
- Provides detailed recommendations
- Can hand off to architects and testers

### System Architect (gpt-4o)
- Designs scalable, maintainable architectures
- Creates implementation plans
- Collaborates with reviewers and testers

### Test Engineer (gpt-4o-mini)
- Creates comprehensive test suites
- Validates functionality
- Focuses on practical testing approaches

## Model Selection Rules
- **Important Tasks**: Use gpt-4o (code review, architecture design)
- **Basic Tasks**: Use gpt-4o-mini (test generation, routine analysis)
- **Override**: Manually specify model if needed

## Usage Examples

### Basic Agent Creation
```python
from ai_agents.orchestrator import AIAgentOrchestrator, AgentTemplates

orchestrator = AIAgentOrchestrator()

# Create agents with automatic model selection
reviewer = orchestrator.create_agent(**AgentTemplates.create_code_reviewer())
architect = orchestrator.create_agent(**AgentTemplates.create_architect())
tester = orchestrator.create_agent(**AgentTemplates.create_test_engineer())
```

### Custom Agent
```python
custom_agent = orchestrator.create_agent(
    name="security_analyst",
    instructions="Analyze security vulnerabilities and provide mitigation strategies",
    task_importance="important"  # Uses gpt-4o
)
```

### Adding Tools
```python
from agents import function_tool

@function_tool
def run_security_scan(code: str) -> str:
    """Run security analysis on code"""
    # Implementation here
    return "Security analysis results"

agent = orchestrator.create_agent(
    name="security_agent",
    instructions="Perform security analysis",
    tools=[run_security_scan]
)
```

## Practical Workflows

### Code Review Pipeline
1. Code reviewer analyzes codebase
2. Identifies architectural issues
3. Handoffs to architect for redesign
4. Architect creates implementation plan
5. Tester creates validation tests

### Development Workflow
1. Architect designs new features
2. Code reviewer validates design
3. Tester creates test plans
4. Agents iterate on feedback

## API Quota Management
- Monitor usage at https://platform.openai.com/usage
- Use gpt-4o-mini for routine tasks to save costs
- Budget resets monthly - plan accordingly

## Future Enhancements
- Redis session storage for persistent memory
- Voice-enabled agents with speech processing
- Custom tool integrations
- Multi-provider support (Anthropic, Google, etc.)

## Troubleshooting
- **Quota Exceeded**: Wait for monthly reset or upgrade plan
- **Import Errors**: Ensure openai-agents is installed: `pip install openai-agents`
- **Model Errors**: Check model names and availability
- **Handoff Issues**: Verify agent names match exactly
