# Scheduled Cleanup and Maintenance Script for Echoes Project
# This script performs regular cleanup and garbage collection following best practices

param(
    [switch]$DryRun,
    [int]$MaxAgeDays = 30,
    [switch]$Verbose,
    [switch]$Force
)

# Configuration
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$DataDir = Join-Path $ProjectRoot "data"
$ContextDir = Join-Path $DataDir "context"
$CacheDir = Join-Path $DataDir "cache"
$TempDirs = @(
    (Join-Path $ProjectRoot ".pytest_cache"),
    (Join-Path $ProjectRoot "__pycache__"),
    (Join-Path $ProjectRoot ".mypy_cache"),
    (Join-Path $ProjectRoot ".ruff_cache"),
    (Join-Path $ProjectRoot ".cache"),
    (Join-Path $ProjectRoot "htmlcov"),
    (Join-Path $ProjectRoot "tmp_debug_venv.py"),
    (Join-Path $ProjectRoot "yt_temp")
)

# Log function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"

    if ($Verbose -or $Level -eq "ERROR" -or $Level -eq "WARNING") {
        Write-Host $LogMessage
    }

    # Also log to file
    $LogDir = Join-Path $ProjectRoot "logs"
    if (!(Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir -Force | Out-Null }
    $LogFile = Join-Path $LogDir "maintenance_$(Get-Date -Format 'yyyy-MM-dd').log"
    Add-Content -Path $LogFile -Value $LogMessage
}

# Clean old files function
function Remove-OldFiles {
    param([string]$Path, [int]$MaxAge = $MaxAgeDays)

    if (!(Test-Path $Path)) {
        Write-Log "Path does not exist: $Path" "WARNING"
        return 0
    }

    $CutoffDate = (Get-Date).AddDays(-$MaxAge)
    $FilesToRemove = Get-ChildItem -Path $Path -File -Recurse |
        Where-Object { $_.LastWriteTime -lt $CutoffDate }

    $Count = $FilesToRemove.Count
    if ($Count -eq 0) {
        Write-Log "No old files to remove in $Path"
        return 0
    }

    Write-Log "Found $Count files older than $MaxAge days in $Path"

    if (!$DryRun) {
        $FilesToRemove | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Log "Removed $Count old files from $Path"
    } else {
        Write-Log "[DRY RUN] Would remove $Count files from $Path"
    }

    return $Count
}

# Clean empty directories
function Remove-EmptyDirectories {
    param([string]$Path)

    if (!(Test-Path $Path)) { return 0 }

    $EmptyDirs = Get-ChildItem -Path $Path -Directory -Recurse |
        Where-Object { (Get-ChildItem -Path $_.FullName -Recurse -File).Count -eq 0 } |
        Sort-Object -Property FullName -Descending

    $Count = 0
    foreach ($Dir in $EmptyDirs) {
        if (!$DryRun) {
            Remove-Item -Path $Dir.FullName -Force -ErrorAction SilentlyContinue
            $Count++
        }
    }

    if ($Count -gt 0) {
        Write-Log "Removed $Count empty directories"
    } elseif ($EmptyDirs.Count -gt 0) {
        Write-Log "[DRY RUN] Would remove $($EmptyDirs.Count) empty directories"
    }

    return $Count
}

# Clean memory and context files
function Optimize-MemoryFiles {
    param([string]$DataPath = $DataDir)

    $MemoryFiles = @(
        (Join-Path $DataPath "memory.json"),
        (Join-Path $DataPath "organizing_memory.json")
    )

    foreach ($File in $MemoryFiles) {
        if (Test-Path $File) {
            $FileSize = (Get-Item $File).Length
            $FileSizeMB = [math]::Round($FileSize / 1MB, 2)

            # Check if memory file is too large (>10MB)
            if ($FileSize -gt 10MB) {
                Write-Log "Large memory file detected: $File ($FileSizeMB MB)" "WARNING"

                if (!$DryRun -and $Force) {
                    # Create backup before optimizing
                    $BackupFile = "$File.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
                    Copy-Item $File $BackupFile
                    Write-Log "Created backup: $BackupFile"

                    # For now, just log - actual optimization would require specific logic
                    # based on the memory file format
                    Write-Log "Memory file optimization needed but not implemented yet" "WARNING"
                }
            } else {
                Write-Log "Memory file size OK: $File ($FileSizeMB MB)"
            }
        }
    }
}

# Run security checks
function Test-SecurityChecks {
    Write-Log "Running security checks..."

    # Check for exposed secrets in common files
    $FilesToCheck = @(
        ".env",
        ".env.local",
        ".env.example",
        "requirements.txt",
        "pyproject.toml"
    )

    $SecretPatterns = @(
        "password\s*=",
        "secret\s*=",
        "key\s*=",
        "token\s*=",
        "api_key\s*="
    )

    foreach ($File in $FilesToCheck) {
        $FilePath = Join-Path $ProjectRoot $File
        if (Test-Path $FilePath) {
            $Content = Get-Content $FilePath -Raw -ErrorAction SilentlyContinue
            if ($Content) {
                foreach ($Pattern in $SecretPatterns) {
                    if ($Content -match $Pattern) {
                        Write-Log "Potential secret exposure in $File" "WARNING"
                        break
                    }
                }
            }
        }
    }

    # Check for world-writable files
    $WorldWritable = Get-ChildItem -Path $ProjectRoot -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Attributes -band [System.IO.FileAttributes]::Archive }

    if ($WorldWritable.Count -gt 0) {
        Write-Log "Found $($WorldWritable.Count) potentially world-writable files" "WARNING"
    }
}

# Run best practices checks
function Test-BestPractices {
    Write-Log "Running best practices checks..."

    # Check for required files
    $RequiredFiles = @(
        ".gitignore",
        "README.md",
        "LICENSE",
        "pyproject.toml"
    )

    foreach ($File in $RequiredFiles) {
        $FilePath = Join-Path $ProjectRoot $File
        if (!(Test-Path $FilePath)) {
            Write-Log "Missing recommended file: $File" "WARNING"
        }
    }

    # Check Python cache directories
    $CacheDirs = Get-ChildItem -Path $ProjectRoot -Directory -Filter "__pycache__" -Recurse
    if ($CacheDirs.Count -gt 10) {
        Write-Log "High number of __pycache__ directories ($($CacheDirs.Count))" "WARNING"
    }

    # Check for large files
    $LargeFiles = Get-ChildItem -Path $ProjectRoot -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object { $_.Length -gt 100MB }

    if ($LargeFiles.Count -gt 0) {
        Write-Log "Found $($LargeFiles.Count) files larger than 100MB:" "WARNING"
        foreach ($File in $LargeFiles) {
            $SizeMB = [math]::Round($File.Length / 1MB, 2)
            Write-Log "  - $($File.FullName) ($SizeMB MB)" "WARNING"
        }
    }
}

# Clean temporary files and logs
function Clear-TempFiles {
    Write-Log "Cleaning temporary files..."

    $TempFiles = Get-ChildItem -Path $ProjectRoot -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object {
            $_.Name -match "\.(tmp|temp|bak|log)$" -or
            $_.Name -match "^~\$.*" -or
            $_.LastWriteTime -lt (Get-Date).AddDays(-7)
        } |
        Where-Object { $_.FullName -notmatch "logs\\" }

    if ($TempFiles.Count -gt 0) {
        Write-Log "Found $($TempFiles.Count) temporary files"
        if (!$DryRun) {
            $TempFiles | Remove-Item -Force -ErrorAction SilentlyContinue
            Write-Log "Removed $($TempFiles.Count) temporary files"
        } else {
            Write-Log "[DRY RUN] Would remove $($TempFiles.Count) temporary files"
        }
    }
}

# Main execution
Write-Log "=== Echoes Project Maintenance Script Started ==="
Write-Log "Project Root: $ProjectRoot"
Write-Log "Dry Run: $DryRun"
Write-Log "Max Age: $MaxAgeDays days"
Write-Log "Force: $Force"

try {
    # 1. Clean context and cache data
    Write-Log "--- Cleaning Context and Cache Data ---"
    $ContextCleaned = Remove-OldFiles -Path $ContextDir
    $CacheCleaned = Remove-OldFiles -Path $CacheDir

    # 2. Clean temporary directories
    Write-Log "--- Cleaning Temporary Directories ---"
    $TempCleaned = 0
    foreach ($Dir in $TempDirs) {
        $TempCleaned += Remove-OldFiles -Path $Dir -MaxAge 7  # 7 days for temp files
    }

    # 3. Remove empty directories
    Write-Log "--- Removing Empty Directories ---"
    $EmptyRemoved = Remove-EmptyDirectories -Path $DataDir

    # 4. Optimize memory files
    Write-Log "--- Optimizing Memory Files ---"
    Optimize-MemoryFiles

    # 5. Clean temporary files
    Write-Log "--- Cleaning Temporary Files ---"
    Clear-TempFiles

    # 6. Run security checks
    Write-Log "--- Running Security Checks ---"
    Test-SecurityChecks

    # 7. Run best practices checks
    Write-Log "--- Running Best Practices Checks ---"
    Test-BestPractices

    # Summary
    Write-Log "--- Maintenance Summary ---"
    Write-Log "Context files cleaned: $ContextCleaned"
    Write-Log "Cache files cleaned: $CacheCleaned"
    Write-Log "Temp files cleaned: $TempCleaned"
    Write-Log "Empty directories removed: $EmptyRemoved"

    Write-Log "=== Echoes Project Maintenance Script Completed ==="

} catch {
    Write-Log "Error during maintenance: $($_.Exception.Message)" "ERROR"
    exit 1
}
