#!/usr/bin/env pwsh

# Full Sanitization Task - Wrapper for the proven sanitize_codebase.ps1
# This script is called by the automation framework for monthly cleanup

param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Write-TaskLog {
    param([string]$Message, [string]$Level = "INFO")
    
    $colors = @{ "INFO" = "White"; "SUCCESS" = "Green"; "WARN" = "Yellow"; "ERROR" = "Red" }
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [FULL-SANITIZATION] $Message" -ForegroundColor $colors[$Level]
}

# Main execution
Write-TaskLog "Starting full sanitization task..." -Level "INFO"

try {
    # Check if the main sanitization script exists
    $sanitizeScript = "scripts\sanitize_codebase.ps1"
    
    if (-not (Test-Path $sanitizeScript)) {
        Write-TaskLog "Sanitization script not found: $sanitizeScript" -Level "ERROR"
        exit 1
    }
    
    # Execute the proven sanitization script
    $params = @{}
    if ($DryRun) {
        $params.DryRun = $true
        Write-TaskLog "Running in DRY RUN mode" -Level "WARN"
    }
    
    Write-TaskLog "Executing sanitization script..." -Level "INFO"
    & $sanitizeScript @params
    
    Write-TaskLog "Full sanitization completed successfully" -Level "SUCCESS"
    exit 0
}
catch {
    Write-TaskLog "Full sanitization failed: $($_.Exception.Message)" -Level "ERROR"
    exit 1
}
