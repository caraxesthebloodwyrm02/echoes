# Helper: create a timestamped branch, commit staged changes, push to origin, print PR URL
Set-Location -Path (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location ..

$ts = Get-Date -Format "yyyyMMddHHmmss"
$branch = "ci/run-integration-test-$ts"
Write-Host "Creating branch: $branch"

$checkout = git checkout -b $branch 2>&1
Write-Host $checkout

Write-Host "Staging changes..."
git add -A

$diff = git diff --cached --quiet; if ($LASTEXITCODE -ne 0) {
    Write-Host "Committing staged changes..."
    git commit -m "ci: add integration test helpers and make integration_test robust"
} else {
    Write-Host "No changes to commit"
}

Write-Host "Pushing branch to origin..."
$push = git push -u origin $branch 2>&1
Write-Host $push

if ($LASTEXITCODE -eq 0) {
    $remoteUrl = git remote get-url origin
    # Normalize remote URL to owner/repo
    if ($remoteUrl -match 'github.com[:/](.+?)/(.+?)(?:\.git)?$') {
        $owner = $Matches[1]
        $repo = $Matches[2]
        $prUrl = "https://github.com/$owner/$repo/pull/new/$branch"
        Write-Host "Branch pushed: $branch"
        Write-Host "Create a PR at: $prUrl"
    } else {
        Write-Host "Branch pushed: $branch"
        Write-Host "Remote URL not recognized: $remoteUrl"
    }
} else {
    Write-Host "Push failed with exit code $LASTEXITCODE"
}
