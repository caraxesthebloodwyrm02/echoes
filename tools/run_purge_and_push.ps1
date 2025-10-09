<#
One-shot script to mirror-clone a remote repo, remove `.env` using git-filter-repo,
and force-push rewritten history. This script is interactive and destructive when
run with -Execute. By default it prints the exact commands for review.

Usage (dry-run):
  .\tools\run_purge_and_push.ps1 -RemoteUrl 'https://github.com/owner/repo.git'

To execute (destructive):
  .\tools\run_purge_and_push.ps1 -RemoteUrl 'https://github.com/owner/repo.git' -Execute

IMPORTANT: This will rewrite remote history and force-push; collaborators must re-clone.
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$RemoteUrl,
    [string]$MirrorDir = 'repo-mirror.git',
    [switch]$Execute
)

Write-Host "Preparing purge for: $RemoteUrl"

function Invoke-RunCommand([string]$cmd) {
    Write-Host "> $cmd"
    if ($Execute) {
        Invoke-Expression $cmd
    }
}

# Mirror clone
Invoke-RunCommand "git clone --mirror $RemoteUrl $MirrorDir"
Invoke-RunCommand "cd $MirrorDir"

# Detect git-filter-repo
if (Get-Command git-filter-repo -ErrorAction SilentlyContinue) {
    Run-Cmd "git filter-repo --invert-paths --path .env"
} else {
    Write-Host "git-filter-repo not found; falling back to git filter-branch (slower)" -ForegroundColor Yellow
    Invoke-RunCommand "git filter-branch --force --index-filter \"git rm --cached --ignore-unmatch .env\" --prune-empty --tag-name-filter cat -- --all"
    Invoke-RunCommand "Remove-Item -Force -Recurse .git\refs\original\ 2>$null"
}

Invoke-RunCommand "git reflog expire --expire=now --all"
Invoke-RunCommand "git gc --prune=now --aggressive"

Invoke-RunCommand "git push origin --force --all"
Invoke-RunCommand "git push origin --force --tags"

if ($Execute) { Write-Host 'Purge executed.' } else { Write-Host 'Dry-run complete. Re-run with -Execute to run.' }
