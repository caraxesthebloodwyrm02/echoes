#!/bin/bash
# Local CI Simulation Script
# Run this script to simulate the GitHub Actions CI pipeline locally before committing.

set -e  # Exit on any error

echo "🚀 Starting Local CI Simulation..."

# 1. Check if we're in a git repo
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Run 'git init' first."
    exit 1
fi

# 2. Check for required files
required_files=("requirements.txt" "mcp_requirements.txt" "pyproject.toml" ".pre-commit-config.yaml")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file '$file' not found."
        exit 1
    fi
done

echo "✅ Repository and required files check passed."

# 3. Set up Python environment (assume virtual env is activated)
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected. Activate one first."
    echo "   Run: python -m venv .venv && ./.venv/Scripts/activate (Windows)"
    echo "   Or: python -m venv venv && source venv/bin/activate (Linux/Mac)"
fi

# 4. Install dependencies
echo "📦 Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -r mcp_requirements.txt
pip install pytest pytest-asyncio pytest-cov httpx fastapi[all]
pip install ruff black mypy bandit safety
npm install -g markdownlint-cli2
pip install pre-commit

echo "✅ Dependencies installed."

# 5. Run Ruff linting (simulates CI lint job)
echo "🔍 Running Ruff linting..."
ruff check app packages automation --select=E9,F63,F7,F82 --show-source --statistics
ruff check app packages automation --exit-zero --statistics
echo "✅ Ruff linting passed."

# 6. Run Black formatting check
echo "🎨 Checking Black formatting..."
black --check app packages automation tests
echo "✅ Black formatting check passed."

# 7. Run mypy type checking
echo "🔍 Running mypy type checking..."
mypy app packages automation --ignore-missing-imports
echo "✅ mypy type checking passed."

# 8. Run Bandit security scan
echo "🔒 Running Bandit security scan..."
bandit -r app packages automation -ll -i
echo "✅ Bandit security scan passed."

# 9. Run safety dependency check
echo "🛡️  Running safety dependency check..."
safety check --json || true  # Continue on error as in CI
echo "✅ Safety check completed."

# 10. Run Markdown linting
echo "📝 Running Markdown linting..."
markdownlint-cli2 "**/*.md" --config .markdownlint.json
echo "✅ Markdown linting passed."

# 11. Run unit tests with coverage
echo "🧪 Running unit tests with coverage..."
pytest tests/ -v --cov=app --cov=packages --cov-report=xml --cov-report=term --cov-fail-under=80
echo "✅ Unit tests passed."

# 12. Run async tests
echo "🧪 Running async tests..."
pytest tests/test_async.py -v
echo "✅ Async tests passed."

# 13. Test MCP server locally
echo "🤖 Testing MCP server..."
python mcp_server.py &
SERVER_PID=$!
sleep 5

# Test health endpoint
curl -f http://127.0.0.1:8081/health
echo "✅ MCP health check passed."

# Test echo tool
response=$(curl -s -X POST http://127.0.0.1:8081/tools/echo -H "Content-Type: application/json" -d '{"text":"test","repeat":2}')
echo "$response"
echo "$response" | grep -q '"echoed":"test test"' && echo "✅ MCP echo tool test passed." || (echo "❌ MCP echo tool test failed."; kill $SERVER_PID; exit 1)

# Stop server
kill $SERVER_PID
echo "✅ MCP server tests passed."

# 14. Run pre-commit hooks
echo "🔗 Running pre-commit hooks..."
pre-commit run --all-files
echo "✅ Pre-commit hooks passed."

# 15. Check compliance (imports)
echo "📋 Running compliance checks..."
python -c "
from app.core.validation.provenance_enforcer import ProvenanceEnforcerMiddleware
print('✅ Provenance enforcer imports successfully')
"

python -c "
from app.api.schemas import Provenance, Assertion, HILFeedback, AgentExecutionRequest
print('✅ All safety schemas validated')
"
echo "✅ Compliance checks passed."

# 16. Verify documentation exists
echo "📚 Verifying documentation..."
test -f docs/DOMAIN_EXPANSION_PLAN.md || (echo "❌ docs/DOMAIN_EXPANSION_PLAN.md not found."; exit 1)
test -f README.md || (echo "❌ README.md not found."; exit 1)
echo "✅ Documentation files present."

echo ""
echo "🎉 All local CI simulations passed!"
echo ""
echo "Next steps:"
echo "1. Review any warnings above."
echo "2. If everything looks good, commit your changes:"
echo "   git add ."
echo "   git commit -m 'Your commit message'"
echo "3. Push to trigger remote CI:"
echo "   git push origin main"
echo ""
echo "Remember: This script simulates CI but doesn't guarantee remote CI success."
echo "Always check GitHub Actions after pushing."
