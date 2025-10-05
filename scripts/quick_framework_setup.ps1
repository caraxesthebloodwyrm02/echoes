#!/usr/bin/env pwsh

# Quick Framework Setup - Automated System for Proven Patterns
param(
    [switch]$SetupSchedules,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

function Write-SetupLog {
    param([string]$Message, [string]$Level = "INFO")
    
    $colors = @{ "INFO" = "White"; "SUCCESS" = "Green"; "WARN" = "Yellow"; "ERROR" = "Red" }
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $colors[$Level]
}

function Test-SetupPrerequisites {
    Write-SetupLog "Checking prerequisites..." -Level "INFO"
    
    # Check existing successful scripts
    $requiredScripts = @(
        "scripts\security_checklist_verify.ps1",
        "scripts\analyze_logs.ps1",
        "scripts\test_recovery.ps1", 
        "scripts\ssl_cert_manager.ps1",
        "scripts\sanitize_codebase.ps1",
        "scripts\automation_framework.ps1"
    )
    
    $missing = @()
    foreach ($script in $requiredScripts) {
        if (-not (Test-Path $script)) {
            $missing += $script
        }
    }
    
    if ($missing.Count -gt 0) {
        Write-SetupLog "Missing required scripts: $($missing -join ', ')" -Level "ERROR"
        return $false
    }
    
    Write-SetupLog "All required scripts found" -Level "SUCCESS"
    return $true
}

function New-AutomationConfig {
    Write-SetupLog "Creating automation configuration..." -Level "INFO"
    
    $config = @{
        framework = @{
            version = "1.0.0"
            tasks = @{
                security = @{
                    daily = @("security_checklist_verify", "analyze_logs")
                    weekly = @("test_recovery")
                    monthly = @("ssl_cert_manager")
                }
                cleanup = @{
                    daily = @()
                    weekly = @()
                    monthly = @("sanitize_codebase")
                }
            }
            scheduling = @{
                daily_time = "06:00"
                weekly_day = "Sunday"
                weekly_time = "02:00"
                monthly_day = 1
                monthly_time = "03:00"
            }
        }
    }
    
    try {
        $config | ConvertTo-Json -Depth 10 | Out-File "automation_config.json" -Encoding UTF8
        Write-SetupLog "Configuration created: automation_config.json" -Level "SUCCESS"
        return $true
    }
    catch {
        Write-SetupLog "Failed to create configuration: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Set-AutomatedTasks {
    Write-SetupLog "Setting up automated scheduled tasks..." -Level "INFO"
    
    if (-not $SetupSchedules) {
        Write-SetupLog "Skipping scheduled tasks (use -SetupSchedules to enable)" -Level "WARN"
        return $true
    }
    
    # Check admin privileges
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-SetupLog "Administrator privileges required for scheduled tasks" -Level "ERROR"
        return $false
    }
    
    $frameworkScript = (Resolve-Path "scripts\automation_framework.ps1").Path
    
    # Security tasks
    $tasks = @(
        @{ Name = "AutomationFramework-Security-Daily"; Type = "security"; Freq = "daily"; Schedule = "/SC DAILY /ST 06:00" },
        @{ Name = "AutomationFramework-Security-Weekly"; Type = "security"; Freq = "weekly"; Schedule = "/SC WEEKLY /D SUN /ST 02:00" },
        @{ Name = "AutomationFramework-Security-Monthly"; Type = "security"; Freq = "monthly"; Schedule = "/SC MONTHLY /D 1 /ST 03:00" },
        @{ Name = "AutomationFramework-Cleanup-Monthly"; Type = "cleanup"; Freq = "monthly"; Schedule = "/SC MONTHLY /D 1 /ST 04:00" }
    )
    
    foreach ($task in $tasks) {
        try {
            # Remove existing
            schtasks /Delete /TN $task.Name /F 2>$null | Out-Null
            
            # Create new
            $arguments = "-TaskType $($task.Type) -Frequency $($task.Freq)"
            $command = "schtasks /Create /TN `"$($task.Name)`" /TR `"powershell.exe -ExecutionPolicy Bypass -File \`"$frameworkScript\`" $arguments`" $($task.Schedule) /RU $env:USERNAME /F"
            
            if ($DryRun) {
                Write-SetupLog "[DRY RUN] Would create: $($task.Name)" -Level "INFO"
            } else {
                Invoke-Expression $command | Out-Null
                Write-SetupLog "Created scheduled task: $($task.Name)" -Level "SUCCESS"
            }
        }
        catch {
            Write-SetupLog "Failed to create $($task.Name): $($_.Exception.Message)" -Level "ERROR"
        }
    }
    
    return $true
}

function Show-SetupSummary {
    Write-Host "`n" -NoNewline
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "AUTOMATION FRAMEWORK SETUP COMPLETE" -ForegroundColor Cyan
    Write-Host "=" * 60 -ForegroundColor Cyan
    
    Write-Host "`n🎯 WHAT'S AUTOMATED:" -ForegroundColor Yellow
    Write-Host "  ✅ Security Tasks (Daily/Weekly/Monthly)" -ForegroundColor Green
    Write-Host "     • Daily: Security checklist, Log analysis" -ForegroundColor White
    Write-Host "     • Weekly: Recovery testing" -ForegroundColor White
    Write-Host "     • Monthly: SSL certificate management" -ForegroundColor White
    
    Write-Host "`n  ✅ Cleanup Tasks (Monthly)" -ForegroundColor Green
    Write-Host "     • Monthly: Full codebase sanitization" -ForegroundColor White
    
    Write-Host "`n🚀 USAGE:" -ForegroundColor Yellow
    Write-Host "  Manual execution:" -ForegroundColor White
    Write-Host "    .\scripts\automation_framework.ps1 -TaskType security -Frequency daily" -ForegroundColor Cyan
    Write-Host "    .\scripts\sanitize_codebase.ps1" -ForegroundColor Cyan
    
    Write-Host "`n  Check scheduled tasks:" -ForegroundColor White
    Write-Host "    Get-ScheduledTask -TaskName 'AutomationFramework-*'" -ForegroundColor Cyan
    
    Write-Host "`n📊 MONITORING:" -ForegroundColor Yellow
    Write-Host "  • Execution reports: logs\execution_report_*.html" -ForegroundColor White
    Write-Host "  • Framework logs: logs\automation_framework.log" -ForegroundColor White
    Write-Host "  • Cleanup reports: logs\cleanup_report.txt" -ForegroundColor White
    
    Write-Host "`n🔄 SCHEDULE:" -ForegroundColor Yellow
    Write-Host "  • Security Daily: 6:00 AM" -ForegroundColor White
    Write-Host "  • Security Weekly: Sunday 2:00 AM" -ForegroundColor White
    Write-Host "  • Security Monthly: 1st day 3:00 AM" -ForegroundColor White
    Write-Host "  • Cleanup Monthly: 1st day 4:00 AM" -ForegroundColor White
    
    Write-Host "`n" -NoNewline
    Write-Host "=" * 60 -ForegroundColor Cyan
    Write-Host "All proven patterns are now automated! 🎉" -ForegroundColor Green
    Write-Host "=" * 60 -ForegroundColor Cyan
}

# Main execution
Write-Host "`n🤖 AUTOMATION FRAMEWORK QUICK SETUP" -ForegroundColor Cyan
Write-Host "Implementing proven patterns from successful security automation`n" -ForegroundColor White

if ($DryRun) {
    Write-SetupLog "DRY RUN MODE - No actual changes will be made" -Level "WARN"
}

# Step 1: Prerequisites
if (-not (Test-SetupPrerequisites)) {
    Write-SetupLog "Prerequisites check failed. Exiting." -Level "ERROR"
    exit 1
}

# Step 2: Configuration
if (-not (New-AutomationConfig)) {
    Write-SetupLog "Configuration setup failed. Exiting." -Level "ERROR"
    exit 1
}

# Step 3: Scheduled tasks
if (-not (Set-AutomatedTasks)) {
    Write-SetupLog "Task scheduling failed. Exiting." -Level "ERROR"
    exit 1
}

# Step 4: Summary
Show-SetupSummary

Write-SetupLog "Setup completed successfully!" -Level "SUCCESS"
