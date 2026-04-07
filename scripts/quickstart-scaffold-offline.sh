#!/usr/bin/env bash
# =============================================================================
# quickstart-scaffold-offline.sh
# Quickstart execution batch for canopy/echoes — atlas/scaffold-offline branch
# Generated: 2026-04-05 | Branch: atlas/scaffold-offline
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "=== canopy/echoes — atlas/scaffold-offline quickstart ==="
echo "Root: $REPO_ROOT"
echo ""

# -----------------------------------------------------------------------------
# 1. Branch verification
# -----------------------------------------------------------------------------
echo "[1/6] Branch check..."
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [[ "$CURRENT_BRANCH" != "atlas/scaffold-offline" ]]; then
    echo "  WARNING: Current branch is '$CURRENT_BRANCH', expected 'atlas/scaffold-offline'"
    echo "  Switch with: git checkout atlas/scaffold-offline"
    exit 1
fi
echo "  OK: on atlas/scaffold-offline"
echo ""

# -----------------------------------------------------------------------------
# 2. Environment sync
# -----------------------------------------------------------------------------
echo "[2/6] Syncing Python environment (uv)..."
if ! command -v uv &>/dev/null; then
    echo "  ERROR: uv not found. Install via: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
uv sync 2>&1 | tail -5
echo "  OK: dependencies synced"
echo ""

# -----------------------------------------------------------------------------
# 3. Environment verification
# -----------------------------------------------------------------------------
echo "[3/6] Verifying environment..."
uv run python verify_environment.py 2>&1 || echo "  WARN: verify_environment.py reported issues (non-fatal)"
echo ""

# -----------------------------------------------------------------------------
# 4. Lint check
# -----------------------------------------------------------------------------
echo "[4/6] Lint (ruff)..."
uv run ruff check . --output-format=concise 2>&1 | tail -10
echo ""

# -----------------------------------------------------------------------------
# 5. Atlas integration tests
# -----------------------------------------------------------------------------
echo "[5/6] Atlas integration tests..."
uv run pytest tests/test_atlas_integration.py -q --tb=short 2>&1
echo ""

# -----------------------------------------------------------------------------
# 6. Atlas drift check
# -----------------------------------------------------------------------------
echo "[6/6] Atlas drift check (embeddedness regression)..."
uv run python scripts/atlas_drift_check.py 2>&1
echo ""

echo "=== Quickstart complete ==="
echo ""
echo "Next steps:"
echo "  Launch REPL:      uv run python scripts/atlas_repl.py"
echo "  Launch API:       uv run python start_api.py"
echo "  Run all tests:    uv run pytest tests/ -q"
echo "  Full coverage:    make coverage"
