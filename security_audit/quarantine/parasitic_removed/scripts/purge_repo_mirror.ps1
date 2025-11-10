<#
One-shot helper to mirror-clone a remote repo, remove `.env` from history using git-filter-repo,
run housekeeping, and optionally force-push rewritten refs. This script prints exact commands
by default. To actually run them, provide -Execute and confirm the prompts.

Usage (dry-run):
  .\tools\purge_repo_mirror.ps1 -RemoteUrl 'https://github.com/owner/repo.git'

To execute (destructive):
  .\tools\purge_repo_mirror.ps1 -RemoteUrl 'https://github.com/owner/repo.git' -Execute

Notes:
- This script does not run anything unless -Execute is provided.
- Before running -Execute, make a local backup and ensure you have permissions to force-push.
- Recommended tool: git-filter-repo (https://github.com/newren/git-filter-repo). If not installed,
  the script prints installation guidance.
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$RemoteUrl,
    [string]$MirrorDir = 'repo-mirror.git',
    [switch]$Execute
)

function WriteCmd($c) { Write-Host "  $c" }

Write-Host "Preparing commands to purge .env from: $RemoteUrl"
Write-Host "Mirror directory: $MirrorDir"

# Step 0: Check for git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: git is not available on PATH." -ForegroundColor Red
    exit 1
}

# Recommended install instruction for git-filter-repo
$filterRepoInstalled = (Get-Command git-filter-repo -ErrorAction SilentlyContinue)
if (-not $filterRepoInstalled) {
    Write-Host "Note: 'git-filter-repo' not found on PATH. Recommended install commands (pick one):"
    WriteCmd "python -m pip install --upgrade pip"
    WriteCmd "python -m pip install git-filter-repo"
    Write-Host "Or see: https://github.com/newren/git-filter-repo for platform-specific installs"
}

Write-Host "Commands (dry-run). Review them carefully before running."
Write-Host "1) Create a mirrored clone"
WriteCmd "git clone --mirror $RemoteUrl $MirrorDir"

Write-Host "2) Remove .env from history (git-filter-repo recommended)"
WriteCmd "cd $MirrorDir"
WriteCmd "git filter-repo --invert-paths --path .env"

Write-Host "3) Housekeeping"
WriteCmd "git reflog expire --expire=now --all"
WriteCmd "git gc --prune=now --aggressive"

Write-Host "4) Force-push rewritten refs to origin"
WriteCmd "git push origin --force --all"
WriteCmd "git push origin --force --tags"

if ($Execute) {
    Write-Host "Execution requested. This will run the commands above and force-push."
    $confirm = Read-Host "Type 'CONFIRM' to proceed"
    if ($confirm -ne 'CONFIRM') { Write-Host 'Aborted by user.'; exit 2 }

    Write-Host "Running: git clone --mirror $RemoteUrl $MirrorDir"
    git clone --mirror $RemoteUrl $MirrorDir
    Set-Location $MirrorDir

    if (Get-Command git-filter-repo -ErrorAction SilentlyContinue) {
        git filter-repo --invert-paths --path .env
    } else {
        Write-Host "git-filter-repo not found. Attempting fallback with git filter-branch (slower)." -ForegroundColor Yellow
        WriteCmd "git filter-branch --force --index-filter \"git rm --cached --ignore-unmatch .env\" --prune-empty --tag-name-filter cat -- --all"
        git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty --tag-name-filter cat -- --all
    Remove-Item -Force -Recurse ".git\refs\original\" 2>$null
    }

    git reflog expire --expire=now --all
    git gc --prune=now --aggressive

    Write-Host "Ready to push rewritten history. Confirm again to force-push to origin."
    $confirm2 = Read-Host "Type 'PUSH' to force-push the rewritten history to the remote"
    if ($confirm2 -ne 'PUSH') { Write-Host 'Push aborted by user.'; exit 0 }

    git push origin --force --all
    git push origin --force --tags
    Write-Host "Done. Remember to notify collaborators to re-clone the repository."
}
