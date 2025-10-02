# Contributing to Python Automation Framework

First off, thanks for taking the time to contribute! :tada:

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

- Ensure the bug was not already reported by searching on GitHub under [Issues](https://github.com/caraxesthebloodwyrm02/echoes/issues).
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/caraxesthebloodwyrm02/echoes/issues/new). Be sure to include:
  - A clear title and description
  - Steps to reproduce the issue
  - Expected vs. actual behavior
  - Screenshots if applicable
  - Your environment details

### Suggesting Enhancements

- Open an issue with a clear title and description
- Explain why this enhancement would be useful
- Include any relevant documentation or examples

### Your First Code Contribution

1. Fork the repository
2. Create a new branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Commit your changes: `git commit -m 'Add some amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Unix/MacOS: `source .venv/bin/activate`
4. Install development dependencies: `pip install -r requirements-dev.txt`
5. Install pre-commit hooks: `pre-commit install`

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use type hints for all new code
- Write docstrings following [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
- Keep lines under 88 characters (Black's default)

## Testing

- Write tests for all new functionality
- Run tests: `pytest`
- Check test coverage: `pytest --cov=automation`
- Ensure all tests pass before submitting a PR

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Ensure your code passes all tests and lints
3. Request review from maintainers
4. Address any feedback
5. Once approved, your PR will be merged

## License

By contributing, you agree that your contributions will be licensed under the [MIT License](LICENSE).
