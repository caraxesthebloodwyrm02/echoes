# Developer quickstart

## Python Setup

This project uses Python 3.10.x. A single virtual environment is maintained at the repository root.

1) Set up the Python environment

```powershell
# Create virtual environment (one time)
python3.10 -m venv .venv

# Activate
.\.venv\Scripts\Activate.ps1

# Install development dependencies
pip install -r requirements/dev.txt
```

## Running Tests

```powershell
# Run all tests from repo root
pytest

# Run specific test types
pytest -m unit        # Fast unit tests
pytest -m integration # Integration tests
pytest -m e2e         # End-to-end tests
```

## Code Quality

Install pre-commit hooks for automatic formatting and linting:

```powershell
pre-commit install
pre-commit run --all-files
```

## Application Development

2) Start the Python service locally (if applicable)

```powershell
# From repo root (PYTHONPATH is set automatically)
.\.venv\Scripts\python.exe python/service.py
```

3) Run the deterministic integration test (from repo root)

```powershell
.\integration_test.ps1 -Port 8000
```

4) Run CI on PRs: the workflow `.github/workflows/integration-windows.yml` runs the same integration test on Windows runners.

5) If a `.env` was accidentally committed, use `tools/purge_repo_mirror.ps1` (dry-run) to review commands and `tools/purge_env_history.ps1` for alternative guidance.
