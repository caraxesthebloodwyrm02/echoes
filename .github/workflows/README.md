# CI/CD Pipeline Documentation

## Overview

This project uses GitHub Actions for CI/CD with the following workflows:

1. **Main CI Pipeline** (`.github/workflows/ci-optimized.yml`):
   - Linting and formatting
   - Unit tests with multiple Python versions
   - Security scanning
   - Package building
   - Docker image building
   - Deployment to PyPI and Docker Hub

## Local Development Setup

### Prerequisites

- Python 3.10+
- [Poetry](https://python-poetry.org/) (recommended) or pip
- [pre-commit](https://pre-commit.com/)

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# 2. Set up the development environment
./scripts/setup_dev_environment.ps1

# 3. Run the fix script to address common issues
./scripts/fix_issues.ps1 -FixAll
```

## Common Issues and Solutions

### Linting Issues

```bash
# Auto-fix linting issues
ruff check . --fix --unsafe-fixes
black .

# Check for remaining issues
ruff check .
```

### Test Failures

```bash
# Run specific test file
pytest tests/unit/test_module.py -v

# Run with detailed output
pytest -v --tb=long

# Debug with pdb
pytest --pdb
```

### Dependency Issues

```bash
# Update dependencies
poetry update

# Check for security vulnerabilities
safety check
pip-audit
```

## CI/CD Pipeline Details

### Workflow Triggers

- **Push to main/master**: Full CI/CD pipeline
- **Pull Requests**: Linting, testing, and security checks
- **Scheduled**: Daily security scans

### Manual Triggers

You can manually trigger workflows from the GitHub Actions tab:
1. Go to Actions
2. Select the workflow
3. Click "Run workflow"

## Troubleshooting

### Common Failures

1. **Linting Fails**:
   - Run `./scripts/fix_issues.ps1 -LintOnly`
   - Check the linting output and fix any remaining issues

2. **Tests Fail**:
   - Run `./scripts/fix_issues.ps1 -TestOnly`
   - Check the test output for specific failures

3. **Dependency Issues**:
   - Delete `.venv` and reinstall dependencies
   - Update `pyproject.toml` with correct version constraints

### Viewing Logs

1. Go to the Actions tab in GitHub
2. Click on the failed workflow run
3. Click on the failed job
4. Review the logs for error messages

## Best Practices

1. **Before Pushing**:
   - Run `./scripts/fix_issues.ps1 -FixAll`
   - Ensure all tests pass locally
   - Update the changelog if needed

2. **Commit Messages**:
   - Follow Conventional Commits: https://www.conventionalcommits.org/
   - Use `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`

3. **Dependencies**:
   - Pin all dependencies with exact versions
   - Use `poetry add package@version` to add new dependencies
   - Regularly update dependencies with `poetry update`
