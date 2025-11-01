param(
  [switch]$DryRun,
  [switch]$Verbose
)

$logFile = Join-Path -Path (Get-Location) -ChildPath "restructure.log"
Function Log($msg){
  $time = (Get-Date).ToString("u")
  $line = "$time`t$msg"
  Add-Content -Path $logFile -Value $line
  if ($Verbose) { Write-Output $line }
}

# Directories to create
$targets = @{
  "assets" = @("audio","images","archives","data")
  "backend" = @()
  "frontend" = @()
  "tools" = @()
  "docs" = @()
}

# Move mapping (source -> dest relative to repo root)
$moves = @(
  @{ src = "pyproject.toml"; dest = "backend/pyproject.toml" },
  @{ src = "pytest.ini"; dest = "backend/pytest.ini" },
  @{ src = "App.tsx"; dest = "frontend/src/App.tsx" },
  @{ src = "index.tsx"; dest = "frontend/src/index.tsx" },
  @{ src = "index.html"; dest = "frontend/index.html" },
  @{ src = "From_Zero_to_Hero__Building_a_Robust_Python_Dev_Environment,_Ma.m4a"; dest = "assets/audio/From_Zero_to_Hero.m4a" },
  @{ src = "ffmpeg-release-full.7z"; dest = "assets/archives/ffmpeg-release-full.7z" },
  @{ src = "NotebookLM Mind Map.png"; dest = "docs/NotebookLM Mind Map.png" },
  @{ src = "setup_maintenance.bat"; dest = "tools/setup_maintenance.bat" }
  # add additional explicit moves as needed
)

# Files to delete from root (after move) - keep minimal list
$keepRoot = @("README.md","LICENSE",".gitignore","Development.code-workspace")

# Start
Log "== Starting restructure run. DryRun=$DryRun =="
if (-not $DryRun) {
  # create a backup folder
  $backup = Join-Path -Path (Get-Location) -ChildPath "backup_pre_restructure"
  if (-not (Test-Path $backup)) {
    New-Item -Path $backup -ItemType Directory | Out-Null
    Log "Created backup folder: $backup"
  }
}

# Create directories
foreach ($k in $targets.Keys) {
  $base = Join-Path -Path (Get-Location) -ChildPath $k
  if ($DryRun) {
    Log "[DRYRUN] Would create directory: $base"
  } else {
    if (-not (Test-Path $base)) {
      New-Item -Path $base -ItemType Directory | Out-Null
      Log "Created directory: $base"
    } else {
      Log "Directory exists: $base"
    }
    foreach ($sub in $targets[$k]) {
      $subdir = Join-Path $base $sub
      if (-not (Test-Path $subdir)) {
        New-Item -Path $subdir -ItemType Directory | Out-Null
        Log "Created subdir: $subdir"
      }
    }
  }
}

# Move files
foreach ($m in $moves) {
  $src = Join-Path -Path (Get-Location) -ChildPath $m.src
  $dest = Join-Path -Path (Get-Location) -ChildPath $m.dest
  $destDir = Split-Path -Parent $dest

  if (-not (Test-Path $src)) {
    Log "WARNING: source missing: $src"
    continue
  }

  if ($DryRun) {
    Log "[DRYRUN] Would move '$src' -> '$dest'"
  } else {
    # ensure dest dir exists
    if (-not (Test-Path $destDir)) { New-Item -Path $destDir -ItemType Directory | Out-Null }
    # backup file
    $backupPath = Join-Path $backup (Split-Path -Leaf $src)
    Copy-Item -Path $src -Destination $backupPath -Force
    Log "Backed up $src -> $backupPath"
    Move-Item -Path $src -Destination $dest -Force
    Log "Moved $src -> $dest"
  }
}

# Create README, Makefile, .gitignore if not exist
$readmePath = Join-Path (Get-Location) "README.md"
$makefilePath = Join-Path (Get-Location) "Makefile"
$gitignorePath = Join-Path (Get-Location) ".gitignore"

if ($DryRun) {
  Log "[DRYRUN] Would create README.md, Makefile, .gitignore if missing"
} else {
  if (-not (Test-Path $readmePath)) {
    @"
# Echoes Platform

Overview. Architecture. Setup. Maintenance.
- Backend: backend/
- Frontend: frontend/
- Assets: assets/
- Tools: tools/
- Docs: docs/

Setup:
1. Backend: `cd backend && poetry install`
2. Frontend: `cd frontend && npm install`
3. Dev: `make dev`

License: MIT
"@ | Out-File -FilePath $readmePath -Encoding UTF8
    Log "Created README.md"
  } else { Log "README.md exists" }

  if (-not (Test-Path $makefilePath)) {
    @"
install:
\tcd backend && poetry install
\tcd frontend && npm install

dev:
\t# run backend and frontend concurrently (example)
\tcd backend && poetry run uvicorn app:app --reload

test:
\tcd backend && poetry run pytest
"@ | Out-File -FilePath $makefilePath -Encoding UTF8
    Log "Created Makefile"
  } else { Log "Makefile exists" }

  if (-not (Test-Path $gitignorePath)) {
    @"
# Python
__pycache__/
*.pyc
.venv/
# Node
node_modules/
dist/
# Assets
assets/archives/
# Editor
.vscode/
.idea/
"@ | Out-File -FilePath $gitignorePath -Encoding UTF8
    Log "Created .gitignore"
  } else { Log ".gitignore exists" }
}

Log "== Restructure completed. DryRun=$DryRun =="
