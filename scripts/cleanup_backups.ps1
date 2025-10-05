# Remove backup directories causing linting errors
Remove-Item -Path "src\.code_quality_backup" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\quality_reports" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\security_reports" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\integrity_report.txt" -Force -ErrorAction SilentlyContinue

# Remove other problematic files
Remove-Item -Path "src\AI_INTEGRATION_GUIDE.md" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "src\ms-python.black-formatter" -Force -ErrorAction SilentlyContinue
