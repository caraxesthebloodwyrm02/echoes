# Development environment setup commands
# Run these in your terminal/PowerShell

# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Install development dependencies
pip install -e .
pip install -r requirements-dev.txt

# 4. Install pre-commit hooks
pre-commit install

# 5. Test setup with pre-commit
pre-commit run --all-files

# 6. Run tests
pytest --cov=. --cov-report=html

# 7. Check linting
ruff check .
black --check .
isort --check-only .

# 8. Security check
bandit -r .
