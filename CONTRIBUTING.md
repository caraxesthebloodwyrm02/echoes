# Contributing to Echoes

## Development Setup

### Prerequisites
- Python 3.12+
- Git
- Windows Subsystem for Linux (WSL) or native Linux/Mac

### Quick Start
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/echoes.git
   cd echoes
   ```

2. Set up virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # Linux/Mac
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

5. Run tests:
   ```bash
   pytest tests/
   ```

## Project Structure

```
echoes/
├── docs/           # Documentation
├── demos/          # Demo scripts and examples
├── tests/          # Test files
├── docker/         # Docker configuration
├── src/            # Source code
├── requirements.txt
├── README.md
└── CONTRIBUTING.md
```

## Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Use black for code formatting

### Testing
- Write tests for new features
- Maintain test coverage above 80%
- Run tests before committing: `pytest tests/`

### Git Workflow
- Create feature branches from `main`
- Use descriptive commit messages
- Squash commits when merging
- Keep PRs small and focused

### Documentation
- Update documentation for new features
- Keep README.md current
- Use Markdown for all documentation

## Getting Help
- Check existing issues and documentation first
- Create detailed bug reports with reproduction steps
- Ask questions in discussions

## License
By contributing, you agree that your contributions will be licensed under the same license as the project.
