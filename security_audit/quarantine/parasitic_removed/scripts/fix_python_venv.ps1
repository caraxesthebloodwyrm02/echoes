<#
Safe helper to create a python venv and install requirements without dot-sourcing Activate.psn.
Run from repository root in PowerShell (may require Administrator privileges).
#>

param(
    [string]$VenvPath = "python/.venv",
    [string]$Requirements = "python/requirements.txt"
)

Write-Host "Checking python on PATH..."
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) { Write-Error "Python not found on PATH."; exit 1 }

Write-Host "Creating venv at $VenvPath..."
python -m venv $VenvPath
if ($LASTEXITCODE -ne 0) { Write-Error "venv creation failed. Try running PowerShell as Administrator or repair Python installation."; exit 2 }

$venvPython = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) { Write-Error "Expected venv python not found at $venvPython"; exit 3 }

Write-Host "Upgrading pip inside venv..."
$proc = Start-Process -FilePath $venvPython -ArgumentList '-m','pip','install','--upgrade','pip' -NoNewWindow -Wait -PassThru
if ($proc.ExitCode -ne 0) {
    Write-Warning "pip upgrade failed; trying user install fallback"
    Start-Process -FilePath $venvPython -ArgumentList '-m','pip','install','--user','--upgrade','pip' -NoNewWindow -Wait -PassThru | Out-Null
}

if (Test-Path $Requirements) {
    Write-Host "Installing requirements from $Requirements..."
    $proc3 = Start-Process -FilePath $venvPython -ArgumentList '-m','pip','install','-r',$Requirements -NoNewWindow -Wait -PassThru
    if ($proc3.ExitCode -ne 0) { Write-Warning "Install failed; try running PowerShell as Administrator or use --user flag" }
} else {
    Write-Warning "Requirements file $Requirements not found. Skipping install."
}

Write-Host "Done. To run the server use the venv python explicitly:" -ForegroundColor Green
Write-Host "$venvPython -m uvicorn service:app --host 127.0.0.1 --port 8000"
