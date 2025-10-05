# Copilot Instructions for AI Advisor

## Overview

-   This repository contains the **AI Advisor** automation framework, designed to provide intelligent automation and advisory capabilities.
-   Core components: `automation/` (framework), `src/` (main application), `packages/` (shared libraries).
-   Automation is driven by YAML configuration (`automation/config/automation_config.yaml`) and orchestrated by `automation/core/orchestrator.py`.

## Project Structure

-   `automation/`: Contains the core automation framework, including task definitions, context management, and orchestration logic.
-   `src/`: Houses the main application code for the AI Advisor.
-   `packages/`: Stores shared libraries and utilities used across different components of the project.
-   `tests/`: Dedicated to integration and end-to-end tests for the entire system.
-   `legacy/`: Contains older code from previous versions, which may require careful handling or migration.

## Key Patterns

-   **Context object** (`automation/core/context.py`): Carries essential data like dry-run flag, user information, environment details, and extra data. All automation tasks receive an instance of this `Context` object.
-   **Dry-run mode**: Activated by setting `--dry-run` or `Context(dry_run=True)`. This mode simulates actions without performing any actual side effects, useful for testing and validation.
-   **Task modules** (`automation/tasks/`): Each task is implemented as a Python function within these modules, accepting a `Context` instance and performing a specific action (e.g., `sanitize_codebase`).
-   **Logging** (`automation/core/logger.py`): Utilizes `AutomationLogger` for structured logging. All automation-related logs should be prefixed with `[automation]`.

## Build & Test

To set up the development environment and run tests:

```bash
# Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files  # Run on all files
```

### Code Quality

-   **Black** - Code formatting
-   **Flake8** - Linting
-   **MyPy** - Type checking
-   **Bandit** - Security scanning

## Running Automation

-   To execute the automation framework:

    ```powershell
    # From project root
    python -m automation.scripts.run_automation --config automation/config/automation_config.yaml
    ```

-   This script parses the YAML configuration, constructs a `Context` object, and executes tasks sequentially.
-   Use `--dry-run` to preview actions without making changes.

## High-Risk PR Creation

-   For generating Pull Requests for tasks identified as high risk:

    ```powershell
    # PowerShell script
    .\automation\scripts\create_highrisk_prs.ps1 -InputJson ".\\automation\\reports\\highrisk_review.json" -DryRun
    ```

-   This script automates the creation of PRs based on a JSON input, as detailed in `automation/scripts/create_highrisk_prs.ps1`.

## Dependencies

-   **Python**: Requires Python 3.10 or newer.
-   **External Packages**: Listed in `requirements.txt`, `requirements-dev.txt`, and `requirements-ci.txt`.
-   **Docker**: Docker images referenced in `docker-compose.yml` are used for CI/CD processes.

## Common Commands

-   `make test`: Executes `pytest` for running unit and integration tests (if `Makefile` is present).
-   `make lint`: Runs configured linters (e.g., flake8/black) for code quality checks.
-   `make build`: Builds Docker images as defined in the project's Docker setup.

## File Conventions

-   **YAML Configuration**: Configuration files are located under `automation/config/` and end with `.yaml`.
-   **Task Modules**: Imported via `automation.tasks.<module>`.
-   **Tests**: Reside in `automation/tests/` and follow the `test_*.py` naming convention.

## Quick Tips

-   **Confirmation**: Use `Context.require_confirmation()` to prompt for user confirmation before executing destructive actions.
-   **Logs**: Inspect `automation/logs/automation_framework.log` for detailed execution logs.
-   **Debugging**: For debugging automation scripts, run `python -m pdb -m automation.scripts.run_automation`

## API Endpoints

### Automation Framework

-   **GET Tasks**: Retrieve tasks for an agent.

    ```http
    GET https://api.ai-advisor.com/v1/tasks?agent_id=agent-007&capabilities=code_analysis,security_scan&status=idle
    ```

### Core Features

-   `POST /api/assertions/validate` - Validate claims with provenance
-   `POST /api/hil/feedback` - Human-in-the-loop feedback
-   `POST /api/agent/execute` - Execute agent actions safely
-   `GET /api/health` - System health check
-   `GET /api/metrics` - Performance metrics

### Interactive Documentation

**[Swagger UI → http://localhost:8000/docs](http://localhost:8000/docs)**

## Example Task JSON

-   An example of a task definition in JSON format:

    ```json
    {
      "tasks": [
        {
          "task_id": "task-123",
          "name": "Sanitize Codebase",
          "module": "automation.tasks.sanitize_codebase",
          "params": {
            "target_directory": "/src",
            "rules": ["remove_temp_files", "format_code"]
          },
          "priority": "high"
        }
      ]
    }
    ```
