# Natural Language Task Execution - Complete Guide

## Overview

Lumina now supports **natural language task execution** where you simply describe what you want to achieve, and the system autonomously:
1. **Understands** your request
2. **Gathers** relevant context
3. **Thinks** through the approach
4. **Plans** execution phases
5. **Simulates** the execution
6. **Executes** the task
7. **Reports** results

## Quick Start

### 30-Second Usage

```bash
python use_lumina.py "Use assistant to organize the codebase with goal to improve maintainability"
```

### In Your Code

```python
from app.core import execute_task

result = await execute_task(
    "Use assistant to refactor code with goal to improve readability",
    dry_run=True
)

print(result.final_output)
```

## How It Works

### Architecture

```
Your Natural Language Request
         ↓
    Task Interpreter
    (Parse intent, extract goal)
         ↓
    Context Gatherer
    (Scan codebase, load docs)
         ↓
    Reasoning Engine
    (Think, simulate, plan)
         ↓
    Phase Planner
    (Break into steps)
         ↓
    Autonomous Executor
    (Execute each phase)
         ↓
    Results & Report
```

### Components

**1. Task Interpreter** (`app/core/task_interpreter.py`)
- Parses natural language into structured tasks
- Extracts action, target, goal, constraints
- Determines priority

**2. Context Gatherer** (`app/core/context_gatherer.py`)
- Scans project structure
- Finds relevant files
- Loads documentation
- Extracts dependencies

**3. Autonomous Executor** (`app/core/autonomous_executor.py`)
- Orchestrates entire workflow
- Thinks through approach
- Creates execution plan
- Simulates execution
- Executes phases
- Reports results

**4. Natural Language Interface** (`app/core/natural_language_interface.py`)
- Simple entry point
- Handles formatting
- Provides user-friendly output

## Usage Examples

### Example 1: Organize Codebase

```python
from app.core import execute_task

result = await execute_task(
    "Use assistant to organize the codebase with goal to improve maintainability"
)
```

**What happens:**
1. Parses: action=organize, goal=improve maintainability
2. Scans: Finds all Python files, directories
3. Thinks: Plans optimal structure
4. Creates phases: Analyze → Plan → Execute → Validate
5. Executes: Moves files, creates directories
6. Reports: Summary of changes

### Example 2: Refactor Code

```python
result = await execute_task(
    "Use assistant to refactor code with goal to improve readability"
)
```

### Example 3: Analyze Workflows

```python
result = await execute_task(
    "Use assistant to analyze workflows with goal to find automation opportunities"
)
```

### Example 4: With Constraints

```python
result = await execute_task(
    """
    Use assistant to organize the codebase with goal to improve structure.
    Only touch Python files. Don't modify tests. Must preserve existing functionality.
    """
)
```

## Request Format

### Basic Format

```
Use assistant to [ACTION] with goal to [GOAL]
```

### Supported Actions

- **organize** - Organize codebase structure
- **refactor** - Refactor code
- **upgrade** - Upgrade dependencies
- **analyze** - Analyze workflows/code
- **test** - Improve tests
- **document** - Add documentation
- **fix** - Fix issues
- **optimize** - Optimize performance
- **secure** - Enhance security

### Adding Constraints

```
Use assistant to [ACTION] with goal to [GOAL].
Only [CONSTRAINT]. Don't [CONSTRAINT]. Must [REQUIREMENT].
```

Examples:
- "Only touch Python files"
- "Don't modify tests"
- "Must preserve existing functionality"
- "Without changing APIs"

## Execution Modes

### Dry-Run Mode (Default)

```python
result = await execute_task(request, dry_run=True)
```

- Simulates execution
- No actual changes made
- Shows what would happen
- Safe for exploration

### Live Execution

```python
result = await execute_task(request, dry_run=False)
```

- Actually executes changes
- Makes real modifications
- Use with caution
- Recommended: test in dry-run first

## Execution Result

```python
@dataclass
class ExecutionResult:
    success: bool                      # True if successful
    plan: ExecutionPlan                # Execution plan created
    completed_phases: List[ExecutionPhase]  # Phases executed
    final_output: str                  # Final report
    duration: str                      # Time taken
    errors: List[str]                  # Any errors
```

### Accessing Results

```python
result = await execute_task(request)

# Check success
if result.success:
    print("✅ Task completed successfully")

# Get duration
print(f"Took: {result.duration}")

# See phases
for phase in result.completed_phases:
    print(f"{phase.name}: {phase.status}")

# Read output
print(result.final_output)

# Check for errors
if result.errors:
    for error in result.errors:
        print(f"Error: {error}")
```

## Execution Phases

Each task is broken into phases:

1. **Analyze Current State**
   - Scan files
   - Identify issues
   - Understand context

2. **Plan Changes**
   - Create change list
   - Prioritize actions
   - Identify risks

3. **Execute Changes**
   - Apply changes
   - Verify correctness
   - Handle errors

4. **Validate Results**
   - Run tests
   - Check quality
   - Confirm success

## Command Line Usage

### Basic

```bash
python use_lumina.py
```

Uses default request.

### Custom Request

```bash
python use_lumina.py "Use assistant to analyze workflows with goal to find improvements"
```

### Interactive Demo

```bash
python examples/natural_language_demo.py
```

Runs interactive demo with multiple examples.

## API Reference

### execute_task()

```python
async def execute_task(
    request: str,
    project_root: Optional[str] = None,
    dry_run: bool = True,
) -> ExecutionResult
```

**Parameters:**
- `request`: Natural language request
- `project_root`: Project directory (default: current)
- `dry_run`: If True, simulate only

**Returns:**
- `ExecutionResult` with complete information

### NaturalLanguageInterface

```python
from app.core import NaturalLanguageInterface

interface = NaturalLanguageInterface(project_root="/path/to/project")

result = await interface.execute(
    "Your request here",
    dry_run=True,
    verbose=True
)
```

### TaskInterpreter

```python
from app.core import parse_task

parsed = parse_task(
    "Use assistant to organize codebase with goal to improve maintainability"
)

print(parsed.action)  # TaskAction.ORGANIZE_CODEBASE
print(parsed.goal)    # "improve maintainability"
print(parsed.target)  # "/path/to/project"
```

## Integration with Existing Code

### With Lumina

```python
from app.core import get_lumina, execute_task

# Use Lumina directly
lumina = get_lumina()
response = lumina.chat("What should I do?")

# Or use natural language execution
result = await execute_task(
    "Use assistant to organize the codebase"
)
```

### With Automation Framework

```python
from app.core import execute_task
from automation.core.context import Context

context = Context(dry_run=False)

result = await execute_task(
    "Use assistant to organize codebase",
    dry_run=context.dry_run
)
```

## Examples

### Example 1: Full Workflow

```python
import asyncio
from app.core import execute_task

async def organize_project():
    # Execute task
    result = await execute_task(
        "Use assistant to organize the codebase with goal to improve maintainability",
        dry_run=True
    )

    # Check result
    if result.success:
        print("✅ Success!")
        print(f"Completed {len(result.completed_phases)} phases")
        print(f"\nSummary:\n{result.final_output}")
    else:
        print("❌ Failed")
        for error in result.errors:
            print(f"Error: {error}")

asyncio.run(organize_project())
```

### Example 2: Multiple Tasks

```python
tasks = [
    "Use assistant to organize codebase",
    "Use assistant to analyze workflows",
    "Use assistant to upgrade dependencies",
]

for task in tasks:
    result = await execute_task(task, dry_run=True)
    print(f"{task}: {'✅' if result.success else '❌'}")
```

### Example 3: Interactive

```python
while True:
    request = input("What would you like to do? ")
    if request.lower() == 'quit':
        break

    result = await execute_task(request, dry_run=True)
    print(f"\n{result.final_output}\n")
```

## Best Practices

1. **Start with dry-run**: Always test with `dry_run=True` first
2. **Be specific**: Clear goals get better results
3. **Add constraints**: Specify what NOT to do
4. **Check results**: Review execution plan before live run
5. **Iterative**: Run multiple times, refining request

## Troubleshooting

### "GITHUB_TOKEN not set"
**Fix**: Add `GITHUB_TOKEN` to `.env` file

### Task not understood
**Fix**: Use clearer action words (organize, refactor, analyze, etc.)

### No changes made
**Fix**: Check if `dry_run=True` (default)

### Errors during execution
**Fix**: Check `result.errors` for details

## Performance

- **Parsing**: <1 second
- **Context gathering**: 1-3 seconds
- **Planning**: 3-10 seconds (uses AI reasoning)
- **Execution**: Varies by task
- **Total**: Typically 10-30 seconds for dry-run

## Security

- ✅ Dry-run mode by default
- ✅ Sandboxed execution
- ✅ File operations restricted to project
- ✅ No arbitrary code execution
- ✅ All changes logged

## Future Enhancements

See `MASTER_IMPLEMENTATION_ROADMAP.md` for:
- Voice input support
- Multi-step workflows
- Learning from feedback
- Proactive suggestions
- Real-time monitoring

## Summary

Natural language task execution is now fully functional:

✅ **Parse** natural language requests
✅ **Gather** relevant context
✅ **Think** through approach
✅ **Plan** execution phases
✅ **Simulate** execution
✅ **Execute** autonomously
✅ **Report** results

**Get started:**
```bash
python use_lumina.py "Use assistant to organize the codebase"
```

Or in code:
```python
from app.core import execute_task
result = await execute_task("Your request here")
```

Welcome to the future of natural language coding! ✨
