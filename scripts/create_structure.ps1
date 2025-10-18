# File: reorganize_project.ps1

# Project root directory
$root = "e:\Projects\Development"

# Define the file movements as source -> destination mappings
$fileMoves = @{
    # Core modules
    "ai_modules/minicon" = "ai_agents/minicon"
    "ai_modules/bias_detection" = "ai_agents/bias_detection"
    "ai_agents/*.py" = "ai_agents/"

    # API and routes
    "api/clients" = "api/clients"
    "api/middleware" = "api/middleware"
    "api/unified_gateway.py" = "api/"

    # Config
    "config/*" = "config/"
    "configs/*" = "config/"

    # Core functionality
    "core/*" = "core/"
    "echoes/core_inference" = "core/inference"

    # Data
    "data/*" = "data/"
    "synthetic_data" = "data/synthetic"

    # Documentation
    "docs/*" = "docs/"
    "text_reports" = "docs/reports"

    # Integrations
    "integrations/*" = "integrations/"
    "realtime" = "integrations/realtime"

    # Knowledge Graph
    "knowledge_graph" = "knowledge_graph"

    # Monitoring
    "monitoring/*" = "monitoring/"
    "metrics" = "monitoring/metrics"

    # Scripts
    "scripts/*" = "scripts/"
    "tools" = "scripts/tools"

    # Tests
    "tests/*" = "tests/"
    "testing" = "tests/integration"

    # Root level files
    "*.py" = "core/"
    "*.md" = "docs/"
    "*.txt" = "docs/"
    "*.json" = "config/"
    "*.yaml" = "config/"
    "*.yml" = "config/"
}

# Create all target directories first
$fileMoves.Values | ForEach-Object {
    $targetDir = Join-Path $root $_
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        Write-Host "Created directory: $targetDir"
    }
}

# Process each file move
foreach ($move in $fileMoves.GetEnumerator()) {
    $sourcePattern = $move.Key
    $targetDir = $move.Value

    # Handle wildcards in source
    $sourcePath = Join-Path $root $sourcePattern
    $files = Get-ChildItem -Path $sourcePath -Recurse -File -ErrorAction SilentlyContinue

    if ($null -eq $files) {
        Write-Host "No files found matching: $sourcePath"
        continue
    }

    foreach ($file in $files) {
        $relativePath = $file.FullName.Substring($root.Length).TrimStart('\')
        $targetPath = Join-Path $root $targetDir

        # If the source is a directory, preserve the subdirectory structure
        if (Test-Path $file.FullName -PathType Container) {
            $subPath = $file.FullName.Substring((Join-Path $root (Split-Path $sourcePattern -Parent)).Length).TrimStart('\')
            $targetPath = Join-Path $targetPath $subPath
        } else {
            # For individual files, just use the target directory
            $targetPath = Join-Path $targetPath $file.Name
        }

        # Create target directory if it doesn't exist
        $targetDirPath = Split-Path $targetPath -Parent
        if (-not (Test-Path $targetDirPath)) {
            New-Item -ItemType Directory -Path $targetDirPath -Force | Out-Null
        }

        # Move the file if it's not already in the target location
        if ($file.FullName -ne $targetPath) {
            try {
                Move-Item -Path $file.FullName -Destination $targetPath -Force
                Write-Host "Moved: $($file.FullName) -> $targetPath"
            } catch {
                Write-Warning "Failed to move $($file.FullName): $_"
            }
        } else {
            Write-Host "Skipped (already in place): $($file.FullName)"
        }
    }
}

# Special handling for specific files
$specialFiles = @{
    "requirements.txt" = "requirements/"
    "requirements-*.txt" = "requirements/"
    "*.ipynb" = "notebooks/"
    "Dockerfile*" = "deploy/"
    "docker-compose*.yml" = "deploy/"
    "*.sh" = "scripts/"
    "*.ps1" = "scripts/"
}

foreach ($pattern in $specialFiles.Keys) {
    $targetDir = $specialFiles[$pattern]
    $targetPath = Join-Path $root $targetDir

    if (-not (Test-Path $targetPath)) {
        New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
    }

    Get-ChildItem -Path $root -Filter $pattern -File | ForEach-Object {
        if ($_.FullName -notlike "*\scripts\*") {  # Don't move files that are already in scripts
            $targetFile = Join-Path $targetPath $_.Name
            if ($_.FullName -ne $targetFile) {
                try {
                    Move-Item -Path $_.FullName -Destination $targetFile -Force
                    Write-Host "Moved: $($_.FullName) -> $targetFile"
                } catch {
                    Write-Warning "Failed to move $($_.FullName): $_"
                }
            }
        }
    }
}

Write-Host "`nReorganization complete!"
Write-Host "Review the changes and commit them to version control."
Write-Host "Note: Some files may need manual review if they weren't matched by the patterns."
