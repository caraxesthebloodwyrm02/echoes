# Development Guide

Quick reference for developers working on this project.

## Quick Start

```bash
# Clone and setup
git clone <repo-url>
cd school
python -m venv .venv
.venv\Scripts\Activate.ps1  # Windows PowerShell
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

## Common Commands

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .

# Type check
mypy .

# Security scan
bandit -r . -ll

# Run all pre-commit hooks
pre-commit run --all-files
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_checkin.py

# Run tests matching pattern
pytest -k "stakeholder"

# Run tests in parallel
pytest -n auto
```

### Development Workflow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/my-feature
```

## Project Structure

```
school/
├── .github/              # GitHub workflows and templates
│   ├── workflows/        # CI/CD workflows
│   └── ISSUE_TEMPLATE/   # Issue templates
├── config/               # Configuration files
├── data/                 # Data storage
│   └── ecosystem/        # Ecosystem data
├── docs/                 # Documentation
├── ecosystem_framework/  # Core framework code
├── scripts/              # Utility scripts
├── services/             # Service layer
├── src/                  # Source code
├── tests/                # Test files
├── .flake8               # Flake8 configuration
├── .bandit               # Bandit configuration
├── pyproject.toml        # Python project configuration
├── requirements.txt      # Production dependencies
└── requirements-dev.txt  # Development dependencies
```

## Code Standards

### Python Style

- **Line length**: 100 characters
- **Docstrings**: Google style
- **Type hints**: Use for public APIs
- **Imports**: Sorted with isort

### Example

```python
"""Module for stakeholder management."""

from typing import Dict, Optional

def register_stakeholder(
    name: str,
    role: str,
    contact: Optional[str] = None
) -> Dict[str, str]:
    """Register a new stakeholder in the system.

    Args:
        name: Full name of the stakeholder.
        role: Role type (student, teacher, parent).
        contact: Optional contact information.

    Returns:
        Dictionary containing stakeholder information.

    Raises:
        ValueError: If role is not valid.
    """
    if role not in ["student", "teacher", "parent"]:
        raise ValueError(f"Invalid role: {role}")

    return {
        "name": name,
        "role": role,
        "contact": contact or "",
    }
```

## Testing Guidelines

### Test Structure

```python
def test_feature_description():
    """Test that feature works as expected."""
    # Arrange
    input_data = setup_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected_output
```

### Test Markers

```python
import pytest

@pytest.mark.unit
def test_unit_function():
    """Unit test example."""
    pass

@pytest.mark.integration
def test_integration_flow():
    """Integration test example."""
    pass

@pytest.mark.slow
def test_slow_operation():
    """Slow test example."""
    pass
```

## CI/CD Pipeline

The CI pipeline runs on every push and PR:

1. **Lint Job**: Code formatting and style checks
   - Black formatting
   - isort import sorting
   - flake8 linting
   - mypy type checking

2. **Security Job**: Security scanning
   - Bandit security scan
   - Safety dependency check

3. **Test Job**: Test execution
   - pytest with coverage
   - Multiple Python versions (3.10, 3.11)

4. **Build Job**: Final verification
   - Project structure check
   - Build summary

## Troubleshooting

### Pre-commit Hook Failures

```bash
# Skip hooks temporarily (not recommended)
git commit --no-verify

# Update hooks
pre-commit autoupdate

# Clear hook cache
pre-commit clean
```

### Test Failures

```bash
# Run with verbose output
pytest -vv

# Run with print statements
pytest -s

# Run with debugger
pytest --pdb
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

## Resources

- [Contributing Guide](../CONTRIBUTING.md)
- [Project README](../README.md)
- [Changelog](../CHANGELOG.md)
- [Project Structure](../STRUCTURE.md)

## Getting Help

- Check documentation first
- Search existing issues
- Ask in discussions
- Create a new issue with `question` label
