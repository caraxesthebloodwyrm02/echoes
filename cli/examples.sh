#!/usr/bin/env bash
# cli/examples.sh
# Purpose: demo running of harmony vs melody quickstart examples

set -euo pipefail

echo "Demo: finance profile"
python -m app.harmony.cli --harmony tests/fixtures/harmony_finance.json --melody tests/fixtures/melody_finance.json --format json --epsilon 0.01

echo
echo "Demo: arts profile"
python -m app.harmony.cli --harmony tests/fixtures/harmony_arts.json --melody tests/fixtures/melody_arts.json --format json

echo
echo "Demo: audit profile (yaml)"
python -m app.harmony.cli --harmony tests/fixtures/harmony_finance.json --melody tests/fixtures/melody_finance.json --format yaml
