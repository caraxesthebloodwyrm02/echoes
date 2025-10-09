# Echoes
[![build-and-test](https://github.com/caraxesthebloodwyrm02/echoes/actions/workflows/build-and-test.yml/badge.svg?event=pull_request)](https://github.com/caraxesthebloodwyrm02/echoes/actions/workflows/build-and-test.yml)

## Echoes Project

## Python Toolchain

This project uses Python 3.10.x as the baseline for all applications. A single virtual environment is maintained at the repository root.

### Setup

```bash
# Create virtual environment (one time)
python3.10 -m venv .venv

# Activate
# Windows:
.venv\Scripts\activate
# Unix:
source .venv/bin/activate

# Install dependencies
pip install -r requirements/dev.txt  # For development
pip install -r requirements/base.txt # For runtime only
```

### Requirements Structure

- `requirements/base.txt`: Core runtime dependencies
- `requirements/dev.txt`: Development tooling (includes base.txt)
- `requirements/docs.txt`: Documentation generation (includes base.txt)

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov

# Run specific test types
pytest -m unit        # Fast unit tests
pytest -m e2e         # End-to-end tests
pytest -m slow        # Slow tests (may be skipped)
```

### Code Quality

Pre-commit hooks are configured for automatic code formatting and linting:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Formatters & Lint Workflow

Use Black, isort, and autoflake locally to keep formatting and imports clean:

```bash
# Install/upgrade tools
pip install --upgrade black isort autoflake

# Format code (Black)
black .

# Sort imports (isort)
isort .

# Remove unused imports/variables (autoflake)
autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r .
```

Run these before committing if pre-commit highlights issues.

### Demo Loop Guards

Some interactive/demo scripts can loop while waiting for model/tool output. To
avoid accidental infinite loops during development, a bounded iteration guard is
used (e.g., `MAX_ROUNDS`) in `examples/Untitled-1.py`:

```python
MAX_ROUNDS = 20
for round_idx in range(MAX_ROUNDS):
    # call model / process tool calls
    ...
else:
    print("[WARN] Maximum iterations reached without terminating. Check tool behavior.")
```

Adjust the limit to suit your use case when running longer sessions.

### Core Utilities

The project uses centralized utilities from `packages.core`:

- **Logging**: `get_logger(name)` for consistent logging across modules
- **Configuration**: Pydantic-based settings with `.env` support
- **Schemas**: Typed data models for podcasts, prompts, and cache entries

### Development Workflow

1. Create feature branch like `feat/centralize-utilities`
2. Make changes using atomic commits (e.g., `feat: add centralized logging module`)
3. Run tests/CI after each major change; ensure coverage >=80%
4. Commit changes
5. Create pull request

### Documentation

Generate documentation with:

```bash
pip install -r requirements/docs.txt
cd docs && make html
```
