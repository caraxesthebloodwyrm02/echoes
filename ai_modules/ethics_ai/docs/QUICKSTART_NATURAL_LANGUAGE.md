# Natural Language Task Execution - Quick Start

## Install Dependencies

```bash
pip install azure-ai-inference python-dotenv
```

## Set Environment Variable

Create `.env` file:
```env
GITHUB_TOKEN=your_github_pat_token_here
```

Get token at: https://github.com/settings/tokens

## Usage

### Method 1: Command Line (Easiest)

```bash
python use_lumina.py "Use assistant to organize the codebase with goal to improve maintainability"
```

### Method 2: In Your Code

```python
import asyncio
from app.core import execute_task

async def main():
    result = await execute_task(
        "Use assistant to organize the codebase with goal to improve maintainability",
        dry_run=True  # Safe preview mode
    )

    print(f"Success: {result.success}")
    print(f"Output: {result.final_output}")

asyncio.run(main())
```

### Method 3: Interactive Demo

```bash
python examples/natural_language_demo.py
```

## Request Format

```
Use assistant to [ACTION] with goal to [GOAL]
```

**Actions**: organize, refactor, upgrade, analyze, test, document, fix, optimize, secure

**Examples**:
- `"Use assistant to organize the codebase with goal to improve maintainability"`
- `"Use assistant to refactor code with goal to improve readability"`
- `"Use assistant to analyze workflows with goal to find improvements"`
- `"Use assistant to upgrade dependencies with goal to use latest versions"`

## What Happens

1. ✅ Parses your natural language request
2. ✅ Gathers context from codebase
3. ✅ Thinks through approach (AI reasoning)
4. ✅ Creates execution plan with phases
5. ✅ Simulates execution
6. ✅ Executes (or previews in dry-run)
7. ✅ Generates comprehensive report

## Modes

**Dry-run (default)**: Simulates without making changes
```python
result = await execute_task(request, dry_run=True)
```

**Live execution**: Actually makes changes
```python
result = await execute_task(request, dry_run=False)
```

## Next Steps

- Read full guide: `NATURAL_LANGUAGE_GUIDE.md`
- See implementation: `IMPLEMENTATION_COMPLETE.md`
- Try examples: `python examples/natural_language_demo.py`

## Need Help?

Check `NATURAL_LANGUAGE_GUIDE.md` for:
- Complete API reference
- More examples
- Best practices
- Troubleshooting
