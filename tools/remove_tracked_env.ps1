<#
Removes a tracked .env file from the git index and commits the deletion.
This does NOT rewrite history. Use the purge scripts in tools/ to remove from history.

Usage: .\tools\remove_tracked_env.ps1 [-Execute]
#>

param(
    [switch]$Execute
)

if (-not (Test-Path ".git")) { Write-Error "This script must be run from the repository root"; exit 1 }

$envPath = ".env"
if (-not (Test-Path $envPath)) { Write-Host ".env not present in working tree."; exit 0 }

Write-Host "Found .env in working tree. It will be removed from the index and committed." -ForegroundColor Yellow
Write-Host "Dry-run: git rm --cached .env && git commit -m 'Remove tracked .env (sensitive) from working tree'"

if ($Execute) {
    git rm --cached .env
    git commit -m "Remove tracked .env (sensitive) from working tree"
    Write-Host "Committed deletion of .env. This does not rewrite history. Use tools/purge_repo_mirror.ps1 to remove from history." -ForegroundColor Green
}
