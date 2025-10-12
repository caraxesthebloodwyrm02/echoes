# Contributing to TrajectoX

Thank you for your interest in contributing to TrajectoX! This document provides guidelines and processes for contributing to the project.

## Contribution Checklist (IDE Hint)

Before submitting a pull request, ensure your contribution meets these requirements:

### For All Contributors
- [ ] **Code Quality**: Run pre-commit hooks and ensure no linting errors
- [ ] **Documentation**: Update relevant documentation for any API or configuration changes
- [ ] **Testing**: Add unit/integration tests and verify coverage doesn't decrease
- [ ] **Commits**: Use clear, atomic commit messages following conventional format

### Developers
- [ ] Write unit/integration tests for new features and bug fixes
- [ ] Update docstrings for any modified functions/classes
- [ ] Ensure backward compatibility or document breaking changes
- [ ] Test edge cases and error conditions

### Product Owners
- [ ] Tag high-impact bugs/features with the `evolution-item` label
- [ ] Provide clear acceptance criteria for new features
- [ ] Review impact on existing functionality and users

### Data Scientists
- [ ] Push performance benchmarks to the `metrics/` directory
- [ ] Document model assumptions and limitations
- [ ] Include data preprocessing and validation steps

### DevOps Engineers
- [ ] Optimize pipeline steps and verify auto-scale configurations
- [ ] Update deployment documentation for infrastructure changes
- [ ] Test rollback procedures for critical changes

### Technical Writers
- [ ] Sync documentation updates after each PR merge
- [ ] Validate that code examples work with current versions
- [ ] Update API documentation for interface changes

## Development Workflow

### 1. Choose an Issue
- Check the [GitHub Issues](https://github.com/caraxesthebloodwyrm02/echoes/issues) for open tasks
- Look for issues labeled `good-first-issue` if you're new to the project
- Comment on the issue to indicate you're working on it

### 2. Set Up Development Environment
```bash
# Clone the repository
git clone https://github.com/caraxesthebloodwyrm02/echoes.git
cd echoes

# Set up Python environment
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements/dev.txt

# Install pre-commit hooks
pre-commit install
```

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 4. Make Changes
- Follow the existing code style and patterns
- Write tests for new functionality
- Update documentation as needed
- Run pre-commit hooks regularly: `pre-commit run --all-files`

### 5. Test Your Changes
```bash
# Run the full test suite
pytest --cov=. --cov-report=html

# Run specific tests
pytest tests/test_specific_module.py

# Check code quality
pre-commit run --all-files
```

### 6. Commit and Push
```bash
# Stage your changes
git add .

# Commit with a clear message
git commit -m "feat: add new feature description

- What was changed
- Why it was changed
- Any breaking changes"

# Push to your branch
git push origin feature/your-feature-name
```

### 7. Create a Pull Request
- Go to the [Pull Requests](https://github.com/caraxesthebloodwyrm02/echoes/pulls) page
- Click "New Pull Request"
- Select your feature branch as the compare branch
- Fill out the pull request template
- Request review from appropriate team members

## Code Style Guidelines

### Python
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Write docstrings for all public functions, classes, and modules
- Use descriptive variable and function names
- Keep functions focused on a single responsibility

### Commit Messages
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
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Testing
- Write unit tests for all new functions and classes
- Include integration tests for API endpoints and workflows
- Aim for at least 90% code coverage
- Test both happy path and error conditions

## Review Process

### Automated Checks
Pull requests will automatically run:
- Code linting and formatting checks
- Unit and integration tests
- Coverage analysis (must be ≥90%)
- Build verification

### Manual Review
Your PR will be reviewed by:
- At least one maintainer
- Relevant domain experts
- QA team for critical changes

### Approval and Merge
Once approved:
- The PR will be merged using squash merge
- The branch will be automatically deleted
- CI/CD will deploy changes to staging

## Getting Help

### Documentation
- [README](README.md) - Project overview and setup
- [Evolution Guide](docs/EVOLUTION_GUIDE.md) - Migration and upgrade instructions
- [API Documentation](docs/) - Detailed API references

### Communication
- **GitHub Issues**: For bugs, features, and general questions
- **Pull Request Comments**: For code review discussions
- **Team Chat**: For real-time collaboration

### Support
If you need help:
1. Check existing issues and documentation
2. Ask in GitHub issue comments
3. Tag relevant maintainers in your PR

## Recognition

Contributors will be:
- Listed in release notes for significant contributions
- Acknowledged in the project's contributor file
- Invited to join the maintainer team for sustained contributions

Thank you for contributing to TrajectoX! 🎉
