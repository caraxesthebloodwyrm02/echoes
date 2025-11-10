# Setup development environment
# Install pre-commit
pip install --upgrade pip
pip install pre-commit
pre-commit install

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install --install-hooks

# Create .env file if it doesn't exist
if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "Created .env file from example. Please update with your configuration."
}

Write-Host "✅ Development environment setup complete!"
Write-Host "Run 'pre-commit run --all-files' to check for issues."
