#!/usr/bin/env pwsh

# Automation Framework - Reusable Patterns That Worked
# This script encapsulates all the successful patterns identified from the security automation system

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("security", "cleanup", "maintenance", "monitoring")]
    [string]$TaskType,
    
    [ValidateSet("daily", "weekly", "monthly", "ondemand")]
    [string]$Frequency = "ondemand",
    
    [switch]$DryRun,
    [switch]$SetupSchedule,
    [string]$ConfigFile = "automation_config.json"
)

$ErrorActionPreference = "Stop"
$ScriptName = "Automation-Framework"

# ============================================================================
# PATTERN 1: Centralized Logging with Color-Coded Output
# ============================================================================
function Write-FrameworkLog {
    param(
        [string]$Message,
        [ValidateSet("DEBUG", "INFO", "WARN", "ERROR", "SUCCESS")]
        [string]$Level = "INFO",
        [string]$LogFile = "logs/automation_framework.log"
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] [$ScriptName] $Message"
    
    # Console output with colors
    $color = switch ($Level) {
        "DEBUG"   { "Gray" }
        "INFO"    { "White" }
        "WARN"    { "Yellow" }
        "ERROR"   { "Red" }
        "SUCCESS" { "Green" }
        default   { "White" }
    }
    
    Write-Host $LogMessage -ForegroundColor $color
    
    # File logging with error handling
    try {
        if (-not (Test-Path (Split-Path $LogFile))) {
            New-Item -ItemType Directory -Path (Split-Path $LogFile) -Force | Out-Null
        }
        Add-Content -Path $LogFile -Value $LogMessage -ErrorAction SilentlyContinue
    }
    catch {
        # Silently continue if logging fails to prevent script interruption
    }
}

# ============================================================================
# PATTERN 2: Configuration-Driven Task Management
# ============================================================================
function Get-TaskConfiguration {
    param([string]$ConfigPath)
    
    Write-FrameworkLog "Loading configuration from: $ConfigPath" -Level "DEBUG"
    
    if (-not (Test-Path $ConfigPath)) {
        Write-FrameworkLog "Configuration file not found. Creating default configuration." -Level "WARN"
        return Create-DefaultConfiguration -ConfigPath $ConfigPath
    }
    
    try {
        $config = Get-Content $ConfigPath | ConvertFrom-Json
        Write-FrameworkLog "Configuration loaded successfully" -Level "SUCCESS"
        return $config
    }
    catch {
        Write-FrameworkLog "Failed to load configuration: $($_.Exception.Message)" -Level "ERROR"
        throw
    }
}

function Create-DefaultConfiguration {
    param([string]$ConfigPath)
    
    $defaultConfig = @{
        framework = @{
            version = "1.0.0"
            tasks = @{
                security = @{
                    daily = @("security_checklist_verify", "analyze_logs")
                    weekly = @("test_recovery")
                    monthly = @("ssl_cert_manager")
                }
                cleanup = @{
                    daily = @("temp_file_cleanup")
                    weekly = @("cache_cleanup")
                    monthly = @("full_sanitization")
                }
                maintenance = @{
                    daily = @("health_check")
                    weekly = @("dependency_update_check")
                    monthly = @("system_optimization")
                }
                monitoring = @{
                    daily = @("log_analysis", "performance_check")
                    weekly = @("security_scan")
                    monthly = @("comprehensive_audit")
                }
            }
            scheduling = @{
                daily_time = "06:00"
                weekly_day = "Sunday"
                weekly_time = "02:00"
                monthly_day = 1
                monthly_time = "03:00"
            }
            reporting = @{
                enabled = $true
                format = "html"
                retention_days = 30
                email_notifications = $false
            }
        }
    }
    
    try {
        $defaultConfig | ConvertTo-Json -Depth 10 | Out-File $ConfigPath
        Write-FrameworkLog "Default configuration created: $ConfigPath" -Level "SUCCESS"
        return $defaultConfig
    }
    catch {
        Write-FrameworkLog "Failed to create default configuration: $($_.Exception.Message)" -Level "ERROR"
        throw
    }
}

# ============================================================================
# PATTERN 3: Modular Task Execution with Error Handling
# ============================================================================
function Invoke-TaskModule {
    param(
        [string]$TaskName,
        [string]$ScriptPath,
        [hashtable]$Parameters = @{},
        [bool]$DryRun = $false
    )
    
    Write-FrameworkLog "Executing task: $TaskName" -Level "INFO"
    
    if (-not (Test-Path $ScriptPath)) {
        Write-FrameworkLog "Task script not found: $ScriptPath" -Level "ERROR"
        return @{ Success = $false; Error = "Script not found"; Duration = 0 }
    }
    
    $startTime = Get-Date
    
    try {
        if ($DryRun) {
            Write-FrameworkLog "[DRY RUN] Would execute: $ScriptPath" -Level "DEBUG"
            return @{ Success = $true; Error = $null; Duration = 0; DryRun = $true }
        }
        
        # Execute the script with parameters
        $result = & $ScriptPath @Parameters
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        
        Write-FrameworkLog "Task $TaskName completed successfully in $([math]::Round($duration, 2)) seconds" -Level "SUCCESS"
        return @{ Success = $true; Error = $null; Duration = $duration }
    }
    catch {
        $endTime = Get-Date
        $duration = ($endTime - $startTime).TotalSeconds
        $errorMsg = $_.Exception.Message
        
        Write-FrameworkLog "Task $TaskName failed after $([math]::Round($duration, 2)) seconds: $errorMsg" -Level "ERROR"
        return @{ Success = $false; Error = $errorMsg; Duration = $duration }
    }
}

# ============================================================================
# PATTERN 4: Prerequisites and Safety Checks
# ============================================================================
function Test-SystemPrerequisites {
    Write-FrameworkLog "Checking system prerequisites..." -Level "INFO"
    
    $checks = @()
    
    # PowerShell version check
    $psVersion = $PSVersionTable.PSVersion
    $checks += @{
        Name = "PowerShell Version"
        Status = $psVersion.Major -ge 5
        Details = "Current: $psVersion, Required: 5.0+"
    }
    
    # Administrator privileges (for scheduled tasks)
    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    $checks += @{
        Name = "Administrator Privileges"
        Status = $isAdmin -or -not $SetupSchedule
        Details = if ($SetupSchedule -and -not $isAdmin) { "Required for scheduled task setup" } else { "Available" }
    }
    
    # Required directories
    $requiredDirs = @("scripts", "logs", "security_config")
    foreach ($dir in $requiredDirs) {
        $exists = Test-Path $dir
        if (-not $exists) {
            try {
                New-Item -ItemType Directory -Path $dir -Force | Out-Null
                $exists = $true
            }
            catch {
                $exists = $false
            }
        }
        
        $checks += @{
            Name = "Directory: $dir"
            Status = $exists
            Details = if ($exists) { "Available" } else { "Failed to create" }
        }
    }
    
    # Report results
    $failedChecks = $checks | Where-Object { -not $_.Status }
    
    foreach ($check in $checks) {
        $level = if ($check.Status) { "SUCCESS" } else { "ERROR" }
        Write-FrameworkLog "$($check.Name): $($check.Details)" -Level $level
    }
    
    if ($failedChecks.Count -gt 0) {
        Write-FrameworkLog "Prerequisites check failed. $($failedChecks.Count) issues found." -Level "ERROR"
        return $false
    }
    
    Write-FrameworkLog "All prerequisites satisfied" -Level "SUCCESS"
    return $true
}

# ============================================================================
# PATTERN 5: Comprehensive Reporting
# ============================================================================
function New-ExecutionReport {
    param(
        [hashtable]$Results,
        [string]$TaskType,
        [string]$Frequency,
        [timespan]$TotalDuration
    )
    
    $reportPath = "logs/execution_report_$(Get-Date -Format 'yyyy-MM-dd_HH-mm-ss').html"
    
    $totalTasks = $Results.Count
    $successfulTasks = ($Results.Values | Where-Object { $_.Success }).Count
    $failedTasks = $totalTasks - $successfulTasks
    $successRate = if ($totalTasks -gt 0) { [math]::Round(($successfulTasks / $totalTasks) * 100, 1) } else { 0 }
    
    $htmlReport = @"
<!DOCTYPE html>
<html>
<head>
    <title>Automation Framework Execution Report</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }
        .metric { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; border-left: 4px solid #007bff; }
        .metric h3 { margin: 0; font-size: 2em; color: #007bff; }
        .metric p { margin: 5px 0 0 0; color: #6c757d; }
        .task { margin: 10px 0; padding: 15px; border-radius: 5px; border-left: 4px solid; }
        .task.success { border-color: #28a745; background-color: #d4edda; }
        .task.failed { border-color: #dc3545; background-color: #f8d7da; }
        .task h4 { margin: 0 0 10px 0; }
        .task .duration { font-size: 0.9em; color: #6c757d; }
        .footer { margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #6c757d; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Automation Framework Report</h1>
            <p><strong>Task Type:</strong> $TaskType | <strong>Frequency:</strong> $Frequency | <strong>Generated:</strong> $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")</p>
        </div>

        <div class="summary">
            <div class="metric">
                <h3>$totalTasks</h3>
                <p>Total Tasks</p>
            </div>
            <div class="metric">
                <h3 style="color: #28a745;">$successfulTasks</h3>
                <p>Successful</p>
            </div>
            <div class="metric">
                <h3 style="color: #dc3545;">$failedTasks</h3>
                <p>Failed</p>
            </div>
            <div class="metric">
                <h3 style="color: #17a2b8;">$successRate%</h3>
                <p>Success Rate</p>
            </div>
        </div>

        <h2>Task Details</h2>
"@

    foreach ($taskName in $Results.Keys) {
        $result = $Results[$taskName]
        $status = if ($result.Success) { "success" } else { "failed" }
        $statusText = if ($result.Success) { "✅ SUCCESS" } else { "❌ FAILED" }
        $durationText = if ($result.Duration -gt 0) { "$([math]::Round($result.Duration, 2))s" } else { "N/A" }
        
        $htmlReport += @"
        <div class="task $status">
            <h4>$taskName</h4>
            <p><strong>Status:</strong> $statusText</p>
            <p class="duration"><strong>Duration:</strong> $durationText</p>
"@
        
        if ($result.Error) {
            $htmlReport += "<p><strong>Error:</strong> $($result.Error)</p>"
        }
        
        if ($result.DryRun) {
            $htmlReport += "<p><strong>Note:</strong> Dry run - no actual changes made</p>"
        }
        
        $htmlReport += "</div>"
    }

    $htmlReport += @"
        <div class="footer">
            <p>Total Execution Time: $([math]::Round($TotalDuration.TotalMinutes, 2)) minutes</p>
            <p>Generated by Automation Framework v1.0.0</p>
        </div>
    </div>
</body>
</html>
"@

    try {
        $htmlReport | Out-File $reportPath -Encoding UTF8
        Write-FrameworkLog "Execution report generated: $reportPath" -Level "SUCCESS"
        return $reportPath
    }
    catch {
        Write-FrameworkLog "Failed to generate report: $($_.Exception.Message)" -Level "ERROR"
        return $null
    }
}

# ============================================================================
# PATTERN 6: Automated Scheduling Integration
# ============================================================================
function Set-AutomatedSchedule {
    param(
        [string]$TaskType,
        [string]$Frequency,
        [hashtable]$ScheduleConfig
    )
    
    if (-not $SetupSchedule) {
        Write-FrameworkLog "Schedule setup skipped (use -SetupSchedule to enable)" -Level "INFO"
        return
    }
    
    Write-FrameworkLog "Setting up automated schedule for $TaskType ($Frequency)" -Level "INFO"
    
    $taskName = "AutomationFramework-$TaskType-$Frequency"
    $scriptPath = $MyInvocation.ScriptName
    $arguments = "-TaskType $TaskType -Frequency $Frequency -ConfigFile $ConfigFile"
    
    try {
        # Remove existing task if it exists
        schtasks /Delete /TN $taskName /F 2>$null
        
        # Create new scheduled task based on frequency
        switch ($Frequency) {
            "daily" {
                $time = $ScheduleConfig.daily_time
                schtasks /Create /TN $taskName /TR "powershell.exe -ExecutionPolicy Bypass -File `"$scriptPath`" $arguments" /SC DAILY /ST $time /RU $env:USERNAME
            }
            "weekly" {
                $day = $ScheduleConfig.weekly_day
                $time = $ScheduleConfig.weekly_time
                schtasks /Create /TN $taskName /TR "powershell.exe -ExecutionPolicy Bypass -File `"$scriptPath`" $arguments" /SC WEEKLY /D $day /ST $time /RU $env:USERNAME
            }
            "monthly" {
                $day = $ScheduleConfig.monthly_day
                $time = $ScheduleConfig.monthly_time
                schtasks /Create /TN $taskName /TR "powershell.exe -ExecutionPolicy Bypass -File `"$scriptPath`" $arguments" /SC MONTHLY /D $day /ST $time /RU $env:USERNAME
            }
        }
        
        Write-FrameworkLog "Scheduled task created: $taskName" -Level "SUCCESS"
    }
    catch {
        Write-FrameworkLog "Failed to create scheduled task: $($_.Exception.Message)" -Level "ERROR"
    }
}

# ============================================================================
# MAIN EXECUTION ORCHESTRATOR
# ============================================================================
function Start-AutomationFramework {
    $startTime = Get-Date
    
    Write-FrameworkLog "Starting Automation Framework - Task Type: $TaskType, Frequency: $Frequency" -Level "INFO"
    
    if ($DryRun) {
        Write-FrameworkLog "DRY RUN MODE - No actual changes will be made" -Level "WARN"
    }
    
    # Step 1: Prerequisites check
    if (-not (Test-SystemPrerequisites)) {
        Write-FrameworkLog "Prerequisites check failed. Exiting." -Level "ERROR"
        return 1
    }
    
    # Step 2: Load configuration
    try {
        $config = Get-TaskConfiguration -ConfigPath $ConfigFile
    }
    catch {
        Write-FrameworkLog "Configuration loading failed. Exiting." -Level "ERROR"
        return 1
    }
    
    # Step 3: Get tasks for the specified type and frequency
    $tasks = $config.framework.tasks.$TaskType.$Frequency
    if (-not $tasks -or $tasks.Count -eq 0) {
        Write-FrameworkLog "No tasks configured for $TaskType ($Frequency)" -Level "WARN"
        return 0
    }
    
    Write-FrameworkLog "Found $($tasks.Count) tasks to execute: $($tasks -join ', ')" -Level "INFO"
    
    # Step 4: Execute tasks
    $results = @{}
    foreach ($taskName in $tasks) {
        $scriptPath = "scripts\$taskName.ps1"
        $results[$taskName] = Invoke-TaskModule -TaskName $taskName -ScriptPath $scriptPath -DryRun $DryRun
    }
    
    # Step 5: Generate report
    $totalDuration = (Get-Date) - $startTime
    $reportPath = New-ExecutionReport -Results $results -TaskType $TaskType -Frequency $Frequency -TotalDuration $totalDuration
    
    # Step 6: Set up scheduling if requested
    if ($SetupSchedule) {
        Set-AutomatedSchedule -TaskType $TaskType -Frequency $Frequency -ScheduleConfig $config.framework.scheduling
    }
    
    # Step 7: Final summary
    $successCount = ($results.Values | Where-Object { $_.Success }).Count
    $totalCount = $results.Count
    
    if ($successCount -eq $totalCount) {
        Write-FrameworkLog "All tasks completed successfully ($successCount/$totalCount)" -Level "SUCCESS"
        return 0
    } else {
        Write-FrameworkLog "Some tasks failed ($successCount/$totalCount successful)" -Level "WARN"
        return 1
    }
}

# Execute the framework
exit (Start-AutomationFramework)
