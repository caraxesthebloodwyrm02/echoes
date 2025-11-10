# Setup Scheduled Maintenance Task
# This script creates a Windows Task Scheduler task to run maintenance regularly

param(
    [string]$TaskName = "EchoesProjectMaintenance",
    [string]$Schedule = "Daily",  # Daily, Weekly, Monthly
    [int]$Interval = 1,  # Every N days/hours
    [switch]$Uninstall,
    [switch]$RunNow
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$MaintenanceScript = Join-Path $ScriptDir "scheduled_maintenance.ps1"

function Write-Log {
    param([string]$Message)
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$Timestamp] $Message"
}

if ($Uninstall) {
    Write-Log "Uninstalling scheduled task: $TaskName"
    try {
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction Stop
        Write-Log "Successfully uninstalled maintenance task"
    } catch {
        Write-Log "Failed to uninstall task or task doesn't exist: $($_.Exception.Message)"
    }
    exit 0
}

if ($RunNow) {
    Write-Log "Running maintenance script now..."
    try {
        & $MaintenanceScript -Verbose
        Write-Log "Maintenance completed successfully"
    } catch {
        Write-Log "Maintenance failed: $($_.Exception.Message)"
        exit 1
    }
    exit 0
}

# Check if maintenance script exists
if (!(Test-Path $MaintenanceScript)) {
    Write-Log "ERROR: Maintenance script not found: $MaintenanceScript"
    exit 1
}

# Create scheduled task
Write-Log "Setting up scheduled maintenance task: $TaskName"
Write-Log "Schedule: $Schedule every $Interval units"
Write-Log "Script: $MaintenanceScript"

try {
    # Remove existing task if it exists
    $ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($ExistingTask) {
        Write-Log "Removing existing task..."
        Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    }

    # Create new task
    $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$MaintenanceScript`""

    $Trigger = switch ($Schedule) {
        "Daily" {
            New-ScheduledTaskTrigger -Daily -DaysInterval $Interval -At "02:00"
        }
        "Weekly" {
            New-ScheduledTaskTrigger -Weekly -WeeksInterval $Interval -At "02:00" -DaysOfWeek Sunday
        }
        "Hourly" {
            New-ScheduledTaskTrigger -Once -At "02:00" -RepetitionInterval (New-TimeSpan -Hours $Interval) -RepetitionDuration (New-TimeSpan -Days 1)
        }
        default {
            Write-Log "ERROR: Invalid schedule type. Use Daily, Weekly, or Hourly"
            exit 1
        }
    }

    # Task settings
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

    # Register the task
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Regular maintenance and cleanup for Echoes project"

    Write-Log "Successfully created scheduled task: $TaskName"
    Write-Log "Task will run $Schedule at 2:00 AM"

    # Show task info
    $Task = Get-ScheduledTask -TaskName $TaskName
    Write-Log "Task Status: $($Task.State)"
    Write-Log "Next Run Time: $($Task.NextRunTime)"

} catch {
    Write-Log "ERROR: Failed to create scheduled task: $($_.Exception.Message)"
    exit 1
}

Write-Log ""
Write-Log "To manage the task:"
Write-Log "  View:    Get-ScheduledTask -TaskName $TaskName"
Write-Log "  Run:     Start-ScheduledTask -TaskName $TaskName"
Write-Log "  Edit:    Start-Process taskschd.msc"
Write-Log "  Remove:  .\$($MyInvocation.MyCommand.Name) -Uninstall"
Write-Log ""
Write-Log "To run maintenance manually:"
Write-Log "  Normal:  .\$($MyInvocation.MyCommand.Name) -RunNow"
Write-Log "  Dry run: & '$MaintenanceScript' -DryRun -Verbose"
