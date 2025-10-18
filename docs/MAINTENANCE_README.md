# Echoes Project Maintenance Guide

This guide covers the automated maintenance and cleanup system for the Echoes project, following best practices from the development workflow.

## Overview

The maintenance system provides:
- **Regular cleanup** of context and cache data
- **Garbage collection** for temporary files
- **Security checks** and best practices validation
- **Automated scheduling** via Windows Task Scheduler

## Files

- `scheduled_maintenance.ps1` - Main maintenance script
- `setup_maintenance_task.ps1` - Task scheduler setup script
- `setup_maintenance.bat` - Easy setup batch file
- `logs/maintenance_*.log` - Maintenance execution logs

## Quick Setup

### Option 1: Automated Setup (Recommended)
Run the batch file for an interactive setup:
```cmd
setup_maintenance.bat
```

### Option 2: Manual Setup
Set up daily maintenance:
```powershell
.\setup_maintenance_task.ps1 -Schedule Daily
```

Set up weekly maintenance:
```powershell
.\setup_maintenance_task.ps1 -Schedule Weekly
```

## What Gets Cleaned

### Context and Cache Data
- Removes files older than 30 days from `data/context/`
- Removes files older than 30 days from `data/cache/`
- Optimizes large memory files (>10MB)

### Temporary Files
- Python cache directories (`__pycache__/`, `.pyc` files)
- Test cache (`.pytest_cache/`, `htmlcov/`)
- MyPy and Ruff cache directories
- Temporary debug files

### Empty Directories
- Removes empty directories recursively
- Cleans up abandoned directory structures

### Security Checks
- Scans for exposed secrets in configuration files
- Checks for world-writable files
- Validates file permissions

### Best Practices
- Ensures required project files exist
- Checks for large files (>100MB)
- Validates Python cache directory counts

## Manual Execution

### Run Maintenance Now
```powershell
.\setup_maintenance_task.ps1 -RunNow
```

### Dry Run (Safe Testing)
```powershell
.\scheduled_maintenance.ps1 -DryRun -Verbose
```

### Force Mode (Advanced)
```powershell
.\scheduled_maintenance.ps1 -Force -Verbose
```

## Scheduling Options

### Daily Maintenance (Recommended)
- Runs every day at 2:00 AM
- Cleans up most temporary files
- Performs security checks

### Weekly Maintenance
- Runs every Sunday at 2:00 AM
- More thorough cleanup
- Includes optimization of large files

### Custom Scheduling
```powershell
# Every 6 hours
.\setup_maintenance_task.ps1 -Schedule Hourly -Interval 6

# Every 2 weeks
.\setup_maintenance_task.ps1 -Schedule Weekly -Interval 2
```

## Configuration Options

### Max Age Settings
```powershell
# Clean files older than 7 days
.\scheduled_maintenance.ps1 -MaxAgeDays 7

# Clean files older than 90 days
.\scheduled_maintenance.ps1 -MaxAgeDays 90
```

### Verbose Logging
```powershell
.\scheduled_maintenance.ps1 -Verbose
```

## Task Management

### View Scheduled Tasks
```powershell
Get-ScheduledTask -TaskName "EchoesProjectMaintenance"
```

### Start Task Manually
```powershell
Start-ScheduledTask -TaskName "EchoesProjectMaintenance"
```

### Remove Scheduled Task
```powershell
.\setup_maintenance_task.ps1 -Uninstall
```

Or use Task Scheduler GUI:
```cmd
taskschd.msc
```

## Log Files

Maintenance logs are stored in `logs/maintenance_YYYY-MM-DD.log`:
```
[2024-01-15 02:00:01] [INFO] === Echoes Project Maintenance Script Started ===
[2024-01-15 02:00:01] [INFO] Project Root: C:\Projects\Echoes
[2024-01-15 02:00:02] [INFO] --- Cleaning Context and Cache Data ---
[2024-01-15 02:00:02] [INFO] No old files to remove in C:\Projects\Echoes\data\context
[2024-01-15 02:00:02] [INFO] No old files to remove in C:\Projects\Echoes\data\cache
```

## Best Practices

### When to Run Maintenance
- **Daily**: For active development projects
- **Weekly**: For stable projects with less frequent changes
- **Before releases**: Always run before creating releases
- **After major changes**: Run after significant refactoring

### Monitoring
- Check log files regularly for warnings
- Monitor disk space usage
- Review security check results
- Validate that critical files aren't accidentally removed

### Customization
- Modify `MaxAgeDays` based on project needs
- Add custom cleanup patterns in the script
- Extend security checks for project-specific requirements

## Troubleshooting

### Task Not Running
1. Check Task Scheduler for task status
2. Verify PowerShell execution policy
3. Check user permissions
4. Review log files for errors

### Files Not Being Cleaned
1. Check file permissions
2. Verify paths exist
3. Use `-Verbose` flag for detailed logging
4. Try `-DryRun` first to see what would be cleaned

### Script Errors
1. Ensure PowerShell 5.1+ is installed
2. Check execution policy: `Get-ExecutionPolicy`
3. Run with administrator privileges if needed
4. Check log files for detailed error messages

## Integration with CI/CD

The maintenance script can be integrated into CI/CD pipelines:

```yaml
- name: Run maintenance
  run: |
    ./scheduled_maintenance.ps1 -MaxAgeDays 7
  continue-on-error: true
```

## Security Considerations

- Scripts run with user privileges
- No network access or external downloads
- Safe file operations with error handling
- Comprehensive logging for audit trails
- No sensitive data processing

---

**Following the Echoes project workflow guidelines for automated maintenance and best practices compliance.**
