# Contributing to School Ecosystem Project

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Security](#security)
 - [Maintainers](#maintainers)

## Code of Conduct

This project follows ethical research standards and evidence-based practices. All contributors are expected to:

- Respect intellectual property and cite sources appropriately
- Maintain confidentiality of sensitive information
- Present balanced perspectives on controversial topics
- Communicate clearly and professionally

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/school.git
   cd school
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/school.git
   ```

## Development Setup

### Prerequisites

- Python 3.10 or 3.11
- pip (Python package manager)
- Git

### Installation

1. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

2. **Activate the virtual environment**:
   - Windows (PowerShell): `.venv\Scripts\Activate.ps1`
   - Windows (CMD): `.venv\Scripts\activate.bat`
   - Linux/Mac: `source .venv/bin/activate`

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Install pre-commit hooks**:
   ```bash
   pre-commit install
   ```

### Environment Configuration

Copy `.env.example` to `.env` and configure as needed:
```bash
cp .env.example .env
```

## Development Workflow

### Creating a Branch

Always create a new branch for your work:
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

### Making Changes

1. **Write code** following our [code standards](#code-standards)
2. **Add tests** for new functionality
3. **Run tests locally** before committing
4. **Commit your changes** with clear messages

### Commit Messages

Follow conventional commit format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Build process or auxiliary tool changes

Example:
```
feat(ecosystem): add stakeholder feedback collection

Implement feedback collection system for stakeholders with
timestamp tracking and categorization.

Closes #123
```

## Code Standards

### Python Style Guide

We follow PEP 8 with some modifications:

- **Line length**: 100 characters (enforced by Black)
- **Docstrings**: Google style
- **Type hints**: Encouraged for public APIs
- **Import order**: Managed by isort

### Code Formatting

Code is automatically formatted using:
- **Black** for code formatting
- **isort** for import sorting

Run formatters manually:
```bash
black .
isort .
```

### Linting

We use multiple linters:
- **flake8** for style guide enforcement
- **mypy** for type checking
- **bandit** for security issues

Run linters:
```bash
flake8 .
mypy .
bandit -r .
```

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit. To run manually:
```bash
pre-commit run --all-files
```

## Testing

### Running Tests

Run all tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_checkin.py
```

Run tests matching a pattern:
```bash
pytest -k "test_stakeholder"
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Include docstrings for complex tests
- Use fixtures for common setup

Example:
```python
def test_stakeholder_registration():
    """Test that a new stakeholder can be registered successfully."""
    stakeholder = register_stakeholder("John Doe", "student")
    assert stakeholder.name == "John Doe"
    assert stakeholder.role == "student"
```

### Test Coverage

- Aim for >80% code coverage
- All new features must include tests
- Bug fixes should include regression tests

## Pull Request Process

### Before Submitting

1. **Update your branch** with latest upstream changes:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks**:
   ```bash
   # Format code
   black .
   isort .

   # Run linters
   flake8 .
   bandit -r .

   # Run tests
   pytest --cov=.
   ```

3. **Update documentation** if needed

### Submitting a Pull Request

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a pull request** on GitHub

3. **Fill out the PR template** completely:
   - Clear description of changes
   - Link to related issues
   - Screenshots (if applicable)
   - Testing performed

4. **Wait for review** and address feedback

### PR Requirements

- All CI checks must pass
- Code coverage should not decrease
- At least one approving review required
- No merge conflicts
- Branch is up-to-date with main

## Security

### Reporting Security Issues

**Do not** open public issues for security vulnerabilities. Instead:

1. Email security concerns to [SECURITY_EMAIL]
2. Include detailed description of the vulnerability
3. Provide steps to reproduce if possible

### Security Best Practices

- Never commit secrets, API keys, or passwords
- Use environment variables for sensitive configuration
- Keep dependencies up-to-date
- Run `bandit` security scans regularly
- Use `safety check` for dependency vulnerabilities

## Maintainers

If you need help, reach out to the maintainers:

- Name: Maintainer Name
  - Email: maintainer@example.com
  - Role: Core Maintainer
  - Areas: Research Lab / steam-engine-dynamics

For security matters, please use the contact in the Security section.

## Additional Resources

- [Project README](README.md)
- [Project Structure](STRUCTURE.md)
- [Reorganization Summary](REORGANIZATION_SUMMARY.md)

## Questions?

If you have questions, please:
1. Check existing documentation
2. Search closed issues
3. Open a new issue with the `question` label

Thank you for contributing! 🎉
