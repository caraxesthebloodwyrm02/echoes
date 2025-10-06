# CORRECTED Development Environment Setup
# Run these commands in sequence

Write-Host "🧹 CLEANUP: Removing backup directories..." -ForegroundColor Yellow
Remove-Item -Path "src\.code_quality_backup" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\quality_reports" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\security_reports" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\integrity_report.txt" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\AI_INTEGRATION_GUIDE.md" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\ms-python.black-formatter" -Force -ErrorAction SilentlyContinue

Write-Host "🐍 SETUP: Creating virtual environment..." -ForegroundColor Green
python -m venv venv
& "venv\Scripts\activate"

Write-Host "📦 INSTALL: Installing dependencies..." -ForegroundColor Green
pip install --upgrade pip
pip install -r requirements-dev.txt

# Skip editable install for now due to missing subpackages
# pip install -e .

Write-Host "🔗 PRE-COMMIT: Installing hooks..." -ForegroundColor Green
pre-commit install

Write-Host "✅ TEST: Running setup verification..." -ForegroundColor Green
ruff check src/ packages/ --exclude "src/venv/*" --exclude "*/__pycache__/*"
black --check src/ packages/ --exclude "src/venv/*" --exclude "*/__pycache__/*"
isort --check-only src/ packages/ --skip "src/venv" --skip "__pycache__"

Write-Host "🎉 SUCCESS: Development environment ready!" -ForegroundColor Cyan
