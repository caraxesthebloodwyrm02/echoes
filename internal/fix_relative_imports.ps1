# fix_relative_imports.ps1
# Converts relative imports to absolute imports in Python files
# Usage: .\fix_relative_imports.ps1 [-dryRun $true|$false] [-verbose $true|$false]

param(
    [bool]$dryRun = $true,  # Set to $false to actually make changes
    [bool]$verbose = $true  # Set to $false to reduce output
)

# Configuration
$rootDir = "."
$targetDirs = @("core", "tests")  # Add other directories as needed

# Track changes
$script:modifiedFiles = 0
$script:totalChanges = 0
$script:filesWithErrors = 0

function Update-FileImports {
    param (
        [System.IO.FileInfo]$file
    )
    
    $relativePath = $file.FullName.Replace((Resolve-Path $rootDir -ErrorAction SilentlyContinue).Path, "").TrimStart("\")
    if ($verbose) {
        Write-Host "Checking $relativePath..." -ForegroundColor Cyan
    }
    
    try {
        # Read file with explicit UTF-8 encoding
        $content = [System.IO.File]::ReadAllText($file.FullName, [System.Text.Encoding]::UTF8)
        $originalContent = $content
        $changes = 0
        
        # Pattern 1: 'from .module import ...' -> 'from core.module import ...'
        $newContent = [regex]::Replace($content, 
            '(?m)^(\s*from\s+)\.(\w+)', 
            { 
                param($match)
                $prefix = $match.Groups[1].Value
                $module = $match.Groups[2].Value
                $newImport = "${prefix}core.${module}"
                if ($verbose) {
                    Write-Host "  [FIX] $($file.Name): $($match.Value) -> $newImport" -ForegroundColor Yellow
                }
                $script:totalChanges++
                $script:changes++
                $newImport
            })
        
        # Only process other patterns if first one found matches
        if ($newContent -ne $content) {
            $content = $newContent
            $script:modifiedFiles++
        }
        
        # Pattern 2: 'from ..module import ...' -> 'from core.module import ...'
        $newContent = [regex]::Replace($content, 
            '(?m)^(\s*from\s+)\.\.(\w+)', 
            { 
                param($match)
                $prefix = $match.Groups[1].Value
                $module = $match.Groups[2].Value
                $newImport = "${prefix}core.${module}"
                if ($verbose) {
                    Write-Host "  [FIX] $($file.Name): $($match.Value) -> $newImport" -ForegroundColor Yellow
                }
                $script:totalChanges++
                $script:changes++
                $newImport
            })
        
        if ($newContent -ne $content) {
            $content = $newContent
            $script:modifiedFiles++
        }
        
        # Pattern 3: 'import .module' -> 'import core.module'
        $newContent = [regex]::Replace($content, 
            '(?m)^(\s*import\s+)\.(\w+)', 
            { 
                param($match)
                $prefix = $match.Groups[1].Value
                $module = $match.Groups[2].Value
                $newImport = "${prefix}core.${module}"
                if ($verbose) {
                    Write-Host "  [FIX] $($file.Name): $($match.Value) -> $newImport" -ForegroundColor Yellow
                }
                $script:totalChanges++
                $script:changes++
                $newImport
            })
        
        if ($newContent -ne $content) {
            $content = $newContent
            $script:modifiedFiles++
        }
        
        # Save changes if content was modified
        if ($content -ne $originalContent) {
            if (-not $dryRun) {
                try {
                    # Ensure directory exists and is writable
                    $directory = [System.IO.Path]::GetDirectoryName($file.FullName)
                    if (-not (Test-Path -Path $directory)) {
                        New-Item -ItemType Directory -Path $directory -Force | Out-Null
                    }
                    
                    # Write with UTF-8 encoding and preserve BOM if it existed
                    $encoding = New-Object System.Text.UTF8Encoding($true)
                    [System.IO.File]::WriteAllText($file.FullName, $content, $encoding)
                    
                    if ($verbose) {
                        Write-Host "  ✓ Updated $($file.Name) ($changes changes)" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "  ✗ Error writing to $($file.Name): $_" -ForegroundColor Red
                    $script:filesWithErrors++
                }
            } else {
                if ($verbose) {
                    Write-Host "  ✓ Would update $($file.Name) ($changes changes) (dry run)" -ForegroundColor Green
                }
            }
        }
    } catch {
        Write-Host "  ✗ Error processing $($file.Name): $_" -ForegroundColor Red
        $script:filesWithErrors++
    }
}

# Find all Python files in target directories
$pythonFiles = Get-ChildItem -Path $targetDirs -Include "*.py" -Recurse -File -ErrorAction SilentlyContinue

if (-not $pythonFiles) {
    Write-Host "No Python files found in target directories: $($targetDirs -join ', ')" -ForegroundColor Yellow
    exit 1
}

Write-Host "Found $($pythonFiles.Count) Python files to process..." -ForegroundColor Cyan

# Process each file
$pythonFiles | ForEach-Object {
    Update-FileImports -file $_
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
if ($dryRun) {
    Write-Host "DRY RUN: No files were modified" -ForegroundColor Yellow
}
Write-Host "Scanned $($pythonFiles.Count) Python files" -ForegroundColor White
Write-Host "Modified $script:modifiedFiles files" -ForegroundColor Green
Write-Host "Made $script:totalChanges import updates" -ForegroundColor Green

if ($script:filesWithErrors -gt 0) {
    Write-Host "Encountered errors in $script:filesWithErrors files" -ForegroundColor Red
}

if ($dryRun) {
    Write-Host "`nTo apply these changes, run:" -ForegroundColor Cyan
    Write-Host "  .\fix_relative_imports.ps1 -dryRun `$false" -ForegroundColor Yellow
    Write-Host "`nFor less verbose output, add: -verbose `$false" -ForegroundColor Gray
}
