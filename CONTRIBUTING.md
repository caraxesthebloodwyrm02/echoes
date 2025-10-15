# Contributing to Echoes

Thank you for your interest in contributing to Echoes! This document provides guidelines and processes for contributing to the project.

## Quick Start for Contributors

### Development Setup

```bash
# Clone the repository
git clone https://github.com/caraxesthebloodwyrm02/echoes.git
cd echoes

# Set up Python environment
pyenv-create  # Create virtual environment
pyenv         # Activate environment

# Install dependencies
pip install -r requirements.txt
pip install -e .[dev]  # Install development dependencies

# Run setup validation
python test_venv_functionality.py
```

### VS Code Setup (Recommended)

For the best development experience:

1. Install recommended extensions (see `.vscode/extensions.json`)
2. Configure Python interpreter:
   - Open Command Palette (`Ctrl+Shift+P`)
   - Select "Python: Select Interpreter"
   - Choose the project virtual environment
3. The workspace includes debug configurations and tasks for common operations

## Contribution Guidelines

### Code Quality Standards

- **Linting & Formatting**: Use Black, Ruff, and Flake8
- **Type Hints**: Required for all function parameters and return values
- **Docstrings**: Required for all public functions, classes, and modules
- **Testing**: Minimum 80% coverage, comprehensive test suites
- **Documentation**: Update docs for API/configuration changes

### Commit Message Format

Follow conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New features
- `fix`: Bug fixes
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

### Pull Request Process

1. **Fork and Branch**: Create a feature branch from `main`
2. **Development**: Implement changes with tests
3. **Validation**: Run full test suite and quality checks
4. **Documentation**: Update relevant docs
5. **PR Creation**: Use descriptive title and detailed description
6. **Review**: Address feedback and iterate
7. **Merge**: Squash merge after approval

## Development Workflow

### Testing

```bash
# Run full test suite
pytest --cov=. --cov-report=html

# Run specific tests
pytest tests/test_specific_module.py -v

# Run code quality checks
python audit_codebase.py

# Check environment
python test_venv_functionality.py
```

### Code Quality Tools

- **Black**: Code formatting (line length: 88)
- **Ruff**: Fast Python linter
- **Flake8**: Additional style checks
- **MyPy**: Type checking
- **Pre-commit**: Automated quality checks

### Key Scripts

- `pyenv` - Activate virtual environment
- `pyenv-create` - Create/recreate environment
- `python test_venv_functionality.py` - Validate setup
- `python audit_codebase.py` - Code quality analysis

## Module-Specific Guidelines

### AI Agents (`ai_agents/`)
- Document agent capabilities and limitations
- Include performance benchmarks
- Test agent collaboration scenarios

### Multimodal Processing (`multimodal/`)
- Validate model accuracy on diverse datasets
- Document preprocessing requirements
- Include cross-modal evaluation metrics

### Security (`security/`)
- Follow secure coding practices
- Document security assumptions
- Include penetration testing results

### MLOps (`mlops/`)
- Version control for models and data
- Document deployment procedures
- Include monitoring and rollback plans

## Review Process

### Automated Checks
- Code linting and formatting
- Unit and integration tests
- Coverage analysis (≥80%)
- Build verification
- Security scanning

### Manual Review
- Code quality and architecture
- Test coverage and scenarios
- Documentation completeness
- Performance implications

## Getting Help

### Resources
- [README](README.md) - Project overview
- [GitHub Issues](https://github.com/caraxesthebloodwyrm02/echoes/issues) - Bug reports and features
- [Discussions](https://github.com/caraxesthebloodwyrm02/echoes/discussions) - Community support

### Communication
- Use clear, descriptive issue/PR titles
- Provide context and examples
- Tag relevant maintainers when needed
- Be respectful and collaborative

## Recognition

Contributors are recognized through:
- Release notes for significant contributions
- Project contributor acknowledgments
- Potential maintainer team invitations

Thank you for contributing to Echoes! 🤖✨
