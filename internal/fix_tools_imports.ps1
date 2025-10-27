# fix_tools_imports.ps1
# A simpler script to fix imports in a specific file

$filePath = "core\tools.py"

if (-not (Test-Path $filePath)) {
    Write-Host "File not found: $filePath" -ForegroundColor Red
    exit 1
}

Write-Host "Processing $filePath..." -ForegroundColor Cyan

# Read the file content
$content = Get-Content -Path $filePath -Raw

# Check if the file contains relative imports
if ($content -match 'from\s+\.(_migration)') {
    Write-Host "Found relative import in $filePath" -ForegroundColor Yellow
    
    # Replace relative import with absolute import
    $newContent = $content -replace 'from\s+\.(_migration)', 'from core.$1'
    
    # Show the change
    Write-Host "Before:" -ForegroundColor Gray
    ($content -split "`n" | Select-String -Pattern 'from\s+\._migration').Line
    
    Write-Host "After:" -ForegroundColor Gray
    ($newContent -split "`n" | Select-String -Pattern 'from\s+core\._migration').Line
    
    # Ask for confirmation before making changes
    $confirmation = Read-Host "Do you want to apply these changes? (y/n)"
    if ($confirmation -eq 'y') {
        $newContent | Set-Content -Path $filePath -NoNewline
        Write-Host "File updated successfully!" -ForegroundColor Green
    } else {
        Write-Host "No changes were made." -ForegroundColor Yellow
    }
} else {
    Write-Host "No relative imports found in $filePath" -ForegroundColor Green
    
    # Check if the file already has the correct import
    if ($content -match 'from\s+core\._migration') {
        Write-Host "File already has the correct absolute import." -ForegroundColor Green
    } else {
        Write-Host "No import statements found that need to be fixed." -ForegroundColor Gray
    }
}
