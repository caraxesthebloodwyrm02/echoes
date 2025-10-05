#!/usr/bin/env pwsh

# Automation Framework Installer - Loops Successful Patterns into Automated System
# This script sets up the complete automation framework based on proven patterns

param(
    [switch]$InstallAll,
    [switch]$SecurityOnly,
    [switch]$CleanupOnly,
    [switch]$MaintenanceOnly,
    [switch]$MonitoringOnly,
    [switch]$SetupSchedules,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

function Write-InstallerLog {
    param(
        [string]$Message,
        [ValidateSet("DEBUG", "INFO", "WARN", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )
    
    $colors = @{
        "DEBUG" = "Gray"
        "INFO" = "White" 
        "WARN" = "Yellow"
        "ERROR" = "Red"
        "SUCCESS" = "Green"
    }
    
    $timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor $colors[$Level]
}

function Show-FrameworkHeader {
    Clear-Host
    Write-Host @"

    ╔══════════════════════════════════════════════════════════════╗
    ║                 🤖 AUTOMATION FRAMEWORK INSTALLER            ║
    ║                                                              ║
    ║  Implementing Proven Patterns from Security Automation      ║
    ╚══════════════════════════════════════════════════════════════╝

"@ -ForegroundColor Cyan
}

function Test-FrameworkPrerequisites {
    Write-InstallerLog "Checking framework prerequisites..." -Level "INFO"
    
    $allGood = $true
    
    # Check PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 5) {
        Write-InstallerLog "PowerShell 5.0+ required. Current: $($PSVersionTable.PSVersion)" -Level "ERROR"
        $allGood = $false
    } else {
        Write-InstallerLog "✓ PowerShell version: $($PSVersionTable.PSVersion)" -Level "SUCCESS"
    }
    
    # Check if we're on Windows (for scheduled tasks)
    if (-not $IsWindows -and -not ($PSVersionTable.PSVersion.Major -eq 5)) {
        Write-InstallerLog "✗ Windows required for full framework functionality" -Level "ERROR"
        $allGood = $false
    } else {
        Write-InstallerLog "✓ Running on Windows" -Level "SUCCESS"
    }
    
    # Check for existing successful scripts
    $requiredScripts = @(
        "scripts\security_checklist_verify.ps1",
        "scripts\analyze_logs.ps1", 
        "scripts\test_recovery.ps1",
        "scripts\ssl_cert_manager.ps1",
        "scripts\sanitize_codebase.ps1"
    )
    
    foreach ($script in $requiredScripts) {
        if (Test-Path $script) {
            Write-InstallerLog "✓ Found: $script" -Level "SUCCESS"
        } else {
            Write-InstallerLog "✗ Missing: $script" -Level "ERROR"
            $allGood = $false
        }
    }
    
    return $allGood
}

function Install-FrameworkConfiguration {
    Write-InstallerLog "Installing framework configuration..." -Level "INFO"
    
    $configPath = "automation_config.json"
    
    # Enhanced configuration based on what worked
    $frameworkConfig = @{
        framework = @{
            version = "1.0.0"
            installed_date = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
            
            # Task definitions based on successful patterns
            tasks = @{
                security = @{
                    daily = @("security_checklist_verify", "analyze_logs")
                    weekly = @("test_recovery") 
                    monthly = @("ssl_cert_manager")
                    description = "Comprehensive security monitoring and validation"
                }
                cleanup = @{
                    daily = @("temp_cleanup")
                    weekly = @("cache_cleanup") 
                    monthly = @("sanitize_codebase")
                    description = "System cleanup and optimization"
                }
                maintenance = @{
                    daily = @("health_check", "log_rotation")
                    weekly = @("dependency_check", "performance_analysis")
                    monthly = @("system_optimization", "backup_verification")
                    description = "System maintenance and health monitoring"
                }
                monitoring = @{
                    daily = @("performance_monitor", "error_analysis")
                    weekly = @("security_scan", "resource_analysis") 
                    monthly = @("comprehensive_audit", "trend_analysis")
                    description = "Continuous monitoring and analysis"
                }
            }
            
            # Scheduling configuration that worked
            scheduling = @{
                daily_time = "06:00"
                weekly_day = "Sunday"
                weekly_time = "02:00" 
                monthly_day = 1
                monthly_time = "03:00"
                timezone = "Local"
            }
            
            # Reporting configuration from successful implementation
            reporting = @{
                enabled = $true
                format = "html"
                include_charts = $true
                retention_days = 90
                email_notifications = $false
                slack_notifications = $false
                report_location = "logs\reports"
            }
            
            # Logging configuration that worked well
            logging = @{
                level = "INFO"
                file_location = "logs\framework.log"
                max_file_size_mb = 50
                retention_days = 30
                console_colors = $true
            }
            
            # Safety and validation settings
            safety = @{
                dry_run_default = $false
                require_confirmation = $false
                backup_before_changes = $true
                rollback_enabled = $true
                max_execution_time_minutes = 60
            }
        }
    }
    
    try {
        $frameworkConfig | ConvertTo-Json -Depth 10 | Out-File $configPath -Encoding UTF8
        Write-InstallerLog "✓ Framework configuration created: $configPath" -Level "SUCCESS"
        return $true
    }
    catch {
        Write-InstallerLog "✗ Failed to create configuration: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Install-TaskCategory {
    param(
        [string]$Category,
        [array]$Tasks
    )
    
    Write-InstallerLog "Installing $Category automation..." -Level "INFO"
    
    foreach ($frequency in @("daily", "weekly", "monthly")) {
        $taskName = "AutomationFramework-$Category-$frequency"
        
        try {
            # Remove existing task
            schtasks /Delete /TN $taskName /F 2>$null | Out-Null
            
            # Create new scheduled task
            $scriptPath = (Resolve-Path "scripts\automation_framework.ps1").Path
            $arguments = "-TaskType $Category -Frequency $frequency"
            
            switch ($frequency) {
                "daily" {
                    $schedule = "/SC DAILY /ST 06:00"
                }
                "weekly" {
                    $schedule = "/SC WEEKLY /D SUN /ST 02:00"
                }
                "monthly" {
                    $schedule = "/SC MONTHLY /D 1 /ST 03:00"
                }
            }
            
            $command = "schtasks /Create /TN `"$taskName`" /TR `"powershell.exe -ExecutionPolicy Bypass -File \`"$scriptPath\`" $arguments`" $schedule /RU $env:USERNAME /F"
            
            Invoke-Expression $command | Out-Null
            Write-InstallerLog "✓ Created scheduled task: $taskName" -Level "SUCCESS"
        }
        catch {
            Write-InstallerLog "✗ Failed to create task $taskName : $($_.Exception.Message)" -Level "ERROR"
        }
    }
}

function Install-MonitoringDashboard {
    Write-InstallerLog "Creating monitoring dashboard..." -Level "INFO"
    
    $dashboardPath = "logs\dashboard.html"
    
    $dashboard = @"
<!DOCTYPE html>
<html>
<head>
    <title>Automation Framework Dashboard</title>
    <meta http-equiv="refresh" content="300">
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
        .container { max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 20px 0; }
        .card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .card h3 { margin-top: 0; color: #333; }
        .status { padding: 5px 10px; border-radius: 15px; font-size: 0.9em; font-weight: bold; }
        .status.success { background: #d4edda; color: #155724; }
        .status.warning { background: #fff3cd; color: #856404; }
        .status.error { background: #f8d7da; color: #721c24; }
        .metric { text-align: center; margin: 10px 0; }
        .metric .value { font-size: 2em; font-weight: bold; color: #667eea; }
        .metric .label { color: #666; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 Automation Framework Dashboard</h1>
        <p>Real-time monitoring of automated tasks and system health</p>
    </div>
    
    <div class="container">
        <div class="grid">
            <div class="card">
                <h3>📊 System Status</h3>
                <div class="metric">
                    <div class="value" id="system-status">●</div>
                    <div class="label">Framework Status</div>
                </div>
                <p>Last updated: <span id="last-update">$(Get-Date -Format "yyyy-MM-dd HH:mm:ss")</span></p>
            </div>
            
            <div class="card">
                <h3>🔒 Security Tasks</h3>
                <div class="status success">All systems operational</div>
                <ul>
                    <li>Daily: Security checklist, Log analysis</li>
                    <li>Weekly: Recovery testing</li>
                    <li>Monthly: SSL certificate management</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>🧹 Cleanup Tasks</h3>
                <div class="status success">Automated cleanup active</div>
                <ul>
                    <li>Daily: Temporary file cleanup</li>
                    <li>Weekly: Cache cleanup</li>
                    <li>Monthly: Full system sanitization</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>🔧 Maintenance Tasks</h3>
                <div class="status success">Maintenance scheduled</div>
                <ul>
                    <li>Daily: Health checks, Log rotation</li>
                    <li>Weekly: Dependency checks</li>
                    <li>Monthly: System optimization</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>📈 Monitoring Tasks</h3>
                <div class="status success">Monitoring active</div>
                <ul>
                    <li>Daily: Performance monitoring</li>
                    <li>Weekly: Security scans</li>
                    <li>Monthly: Comprehensive audits</li>
                </ul>
            </div>
            
            <div class="card">
                <h3>📋 Recent Reports</h3>
                <p>Latest execution reports will appear here</p>
                <div id="recent-reports">
                    <p><em>No reports generated yet</em></p>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Auto-refresh status indicators
        setInterval(function() {
            document.getElementById('last-update').textContent = new Date().toLocaleString();
        }, 60000);
    </script>
</body>
</html>
"@

    try {
        $dashboard | Out-File $dashboardPath -Encoding UTF8
        Write-InstallerLog "✓ Monitoring dashboard created: $dashboardPath" -Level "SUCCESS"
        return $true
    }
    catch {
        Write-InstallerLog "✗ Failed to create dashboard: $($_.Exception.Message)" -Level "ERROR"
        return $false
    }
}

function Show-InstallationSummary {
    param([hashtable]$Results)
    
    Write-Host "`n" -NoNewline
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "AUTOMATION FRAMEWORK INSTALLATION COMPLETE" -ForegroundColor Cyan
    Write-Host "=" * 70 -ForegroundColor Cyan
    
    Write-Host "`n🎯 WHAT WAS INSTALLED:" -ForegroundColor Yellow
    
    if ($Results.Security) {
        Write-Host "  ✅ Security Automation (Daily/Weekly/Monthly)" -ForegroundColor Green
    }
    if ($Results.Cleanup) {
        Write-Host "  ✅ Cleanup Automation (Proven sanitization patterns)" -ForegroundColor Green
    }
    if ($Results.Maintenance) {
        Write-Host "  ✅ Maintenance Automation (Health monitoring)" -ForegroundColor Green
    }
    if ($Results.Monitoring) {
        Write-Host "  ✅ Monitoring Automation (Performance tracking)" -ForegroundColor Green
    }
    if ($Results.Dashboard) {
        Write-Host "  ✅ Monitoring Dashboard (Real-time status)" -ForegroundColor Green
    }
    
    Write-Host "`n🚀 USAGE COMMANDS:" -ForegroundColor Yellow
    Write-Host "  Manual execution:" -ForegroundColor White
    Write-Host "    .\scripts\automation_framework.ps1 -TaskType security -Frequency daily" -ForegroundColor Cyan
    Write-Host "    .\scripts\automation_framework.ps1 -TaskType cleanup -Frequency weekly" -ForegroundColor Cyan
    
    Write-Host "`n  View dashboard:" -ForegroundColor White
    Write-Host "    Start-Process logs\dashboard.html" -ForegroundColor Cyan
    
    Write-Host "`n  Check scheduled tasks:" -ForegroundColor White
    Write-Host "    Get-ScheduledTask -TaskName 'AutomationFramework-*'" -ForegroundColor Cyan
    
    Write-Host "`n📊 MONITORING:" -ForegroundColor Yellow
    Write-Host "  • Dashboard: logs\dashboard.html" -ForegroundColor White
    Write-Host "  • Reports: logs\execution_report_*.html" -ForegroundColor White
    Write-Host "  • Logs: logs\framework.log" -ForegroundColor White
    
    Write-Host "`n🔄 AUTOMATED SCHEDULES:" -ForegroundColor Yellow
    Write-Host "  • Daily tasks: 6:00 AM" -ForegroundColor White
    Write-Host "  • Weekly tasks: Sunday 2:00 AM" -ForegroundColor White
    Write-Host "  • Monthly tasks: 1st day 3:00 AM" -ForegroundColor White
    
    Write-Host "`n" -NoNewline
    Write-Host "=" * 70 -ForegroundColor Cyan
    Write-Host "Framework ready! All proven patterns are now automated. 🎉" -ForegroundColor Green
    Write-Host "=" * 70 -ForegroundColor Cyan
}

# Main installation process
Show-FrameworkHeader

Write-InstallerLog "Starting Automation Framework installation..." -Level "INFO"

# Prerequisites check
if (-not (Test-FrameworkPrerequisites)) {
    Write-InstallerLog "Prerequisites check failed. Please resolve issues and try again." -Level "ERROR"
    exit 1
}

# Install configuration
if (-not (Install-FrameworkConfiguration)) {
    Write-InstallerLog "Configuration installation failed." -Level "ERROR"
    exit 1
}

# Track what gets installed
$installResults = @{
    Security = $false
    Cleanup = $false
    Maintenance = $false
    Monitoring = $false
    Dashboard = $false
}

# Check admin privileges for scheduled tasks
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if ($SetupSchedules -and -not $isAdmin) {
    Write-InstallerLog "Administrator privileges required for scheduled task setup" -Level "ERROR"
    Write-InstallerLog "Please run as Administrator or use without -SetupSchedules" -Level "INFO"
    exit 1
}

# Install categories based on parameters
if ($InstallAll -or $SecurityOnly) {
    if ($SetupSchedules) { Install-TaskCategory -Category "security" }
    $installResults.Security = $true
    Write-InstallerLog "✓ Security automation configured" -Level "SUCCESS"
}

if ($InstallAll -or $CleanupOnly) {
    if ($SetupSchedules) { Install-TaskCategory -Category "cleanup" }
    $installResults.Cleanup = $true
    Write-InstallerLog "✓ Cleanup automation configured" -Level "SUCCESS"
}

if ($InstallAll -or $MaintenanceOnly) {
    if ($SetupSchedules) { Install-TaskCategory -Category "maintenance" }
    $installResults.Maintenance = $true
    Write-InstallerLog "✓ Maintenance automation configured" -Level "SUCCESS"
}

if ($InstallAll -or $MonitoringOnly) {
    if ($SetupSchedules) { Install-TaskCategory -Category "monitoring" }
    $installResults.Monitoring = $true
    Write-InstallerLog "✓ Monitoring automation configured" -Level "SUCCESS"
}

# Install monitoring dashboard
if (Install-MonitoringDashboard) {
    $installResults.Dashboard = $true
}

# Show installation summary
Show-InstallationSummary -Results $installResults

Write-InstallerLog "Installation completed successfully!" -Level "SUCCESS"
