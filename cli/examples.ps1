# cli/examples.ps1
# Purpose: demo running of harmony vs melody quickstart examples (Windows PowerShell)

Write-Host "Demo: finance profile"
python -m app.harmony.cli --harmony tests/fixtures/harmony_finance.json --melody tests/fixtures/melody_finance.json --format json --epsilon 0.01

Write-Host "\nDemo: arts profile"
python -m app.harmony.cli --harmony tests/fixtures/harmony_arts.json --melody tests/fixtures/melody_arts.json --format json

Write-Host "\nDemo: audit profile (yaml)"
python -m app.harmony.cli --harmony tests/fixtures/harmony_finance.json --melody tests/fixtures/melody_finance.json --format yaml
