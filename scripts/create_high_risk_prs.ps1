<#
.SYNOPSIS
    Creates branches and draft PRs for high-risk tasks from the automation framework.
.DESCRIPTION
    This script reads high-risk tasks from the highrisk_review.json file and creates
    corresponding Git branches and GitHub draft PRs for each task. It updates the
    review file with PR and branch information.
.NOTES
    Requires GitHub CLI (gh) to be installed and authenticated.
    Run: gh auth login
#>

# Configuration
$ProjectRoot = "e:/Projects/automation-framework-clean"
$ReviewFile = Join-Path $ProjectRoot "automation/reports/highrisk_review.json"
$UpdatedReviewFile = Join-Path $ProjectRoot "automation/reports/highrisk_review_updated.json"

# Check if GitHub CLI is installed
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "GitHub CLI (gh) is not installed. Please install it from https://cli.github.com/"
    exit 1
}

# Check if authenticated with GitHub
$ghAuthStatus = gh auth status 2>&1
if ($ghAuthStatus -match "not logged into any GitHub hosts") {
    Write-Error "Not authenticated with GitHub. Please run 'gh auth login' first."
    exit 1
}

# Load the review data
if (-not (Test-Path $ReviewFile)) {
    Write-Error "Review file not found: $ReviewFile"
    exit 1
}

$reviewData = Get-Content $ReviewFile -Raw | ConvertFrom-Json -Depth 10
$updatedTasks = @()

# Get current branch name
$currentBranch = git rev-parse --abbrev-ref HEAD

# Process each task
foreach ($task in $reviewData.tasks) {
    $taskId = $task.task_id
    $branchName = $task.branch_name
    $prTitle = $task.pr_title
    $prBody = $task.pr_body
    
    Write-Host "`nProcessing task: $taskId" -ForegroundColor Cyan
    Write-Host "=" * 80
    
    try {
        # Check if branch already exists
        $branchExists = git show-ref --verify --quiet "refs/heads/$branchName" 2>$null
        
        if (-not $branchExists) {
            # Create and switch to new branch
            Write-Host "Creating branch: $branchName"
            git checkout -b $branchName 2>&1 | ForEach-Object { Write-Host $_ }
            
            # Add a placeholder commit
            $commitMessage = "chore: Initial commit for task $taskId"
            $null = git commit --allow-empty -m $commitMessage 2>&1
            
            # Push the branch
            Write-Host "Pushing branch to remote..."
            git push -u origin $branchName 2>&1 | ForEach-Object { Write-Host $_ }
        } else {
            Write-Host "Branch $branchName already exists, checking it out..." -ForegroundColor Yellow
            git checkout $branchName 2>&1 | ForEach-Object { Write-Host $_ }
        }
        
        # Create draft PR if it doesn't exist
        $prExists = gh pr view $branchName --json number 2>$null
        
        if (-not $prExists) {
            Write-Host "Creating draft PR for branch: $branchName"
            $prUrl = gh pr create \
                --title $prTitle \
                --body $prBody \
                --draft \
                --head $branchName \
                --repo (git config --get remote.origin.url) \
                --json url --jq '.url' 2>&1
                
            if ($LASTEXITCODE -ne 0) {
                throw "Failed to create PR: $prUrl"
            }
            
            Write-Host "Created draft PR: $prUrl" -ForegroundColor Green
            
            # Add labels based on task category and severity
            $labels = @("high-risk", $task.category, $task.severity) | Where-Object { $_ }
            if ($labels) {
                gh pr edit $prUrl --add-label $labels 2>&1 | Out-Null
            }
            
            # Add reviewers if specified
            $reviewers = @()
            if ($task.required_approvals -contains 'Security Team') {
                $reviewers += 'security-team'
            }
            if ($task.required_approvals -contains 'Tech Lead') {
                $reviewers += 'tech-lead'
            }
            
            if ($reviewers) {
                gh pr edit $prUrl --add-reviewer ($reviewers -join ',') 2>&1 | Out-Null
            }
            
            # Update task with PR URL
            $task | Add-Member -NotePropertyName 'pr_url' -NotePropertyValue $prUrl -Force
        } else {
            $prUrl = gh pr view $branchName --json url --jq '.url'
            Write-Host "PR already exists: $prUrl" -ForegroundColor Yellow
            $task | Add-Member -NotePropertyName 'pr_url' -NotePropertyValue $prUrl -Force
        }
        
        # Add branch and PR info to the task
        $task | Add-Member -NotePropertyName 'branch_created' -NotePropertyValue $true -Force
        $task | Add-Member -NotePropertyName 'pr_created' -NotePropertyValue $true -Force
        $task | Add-Member -NotePropertyName 'last_updated' -NotePropertyValue (Get-Date -Format 'o') -Force
        
    } catch {
        Write-Host "Error processing task $taskId : $_" -ForegroundColor Red
        $task | Add-Member -NotePropertyName 'error' -NotePropertyValue $_.Exception.Message -Force
    } finally {
        # Switch back to the original branch
        git checkout $currentBranch 2>&1 | Out-Null
    }
    
    $updatedTasks += $task
}

# Update the review data with the processed tasks
$reviewData.tasks = $updatedTasks

# Save the updated review data
$reviewData | ConvertTo-Json -Depth 10 | Set-Content -Path $UpdatedReviewFile -Encoding UTF8

Write-Host "`nProcessing complete!" -ForegroundColor Green
Write-Host "Original review file: $ReviewFile"
Write-Host "Updated review file: $UpdatedReviewFile"
Write-Host "`nNext steps:"
Write-Host "1. Review the updated highrisk_review_updated.json"
Write-Host "2. Check the created branches and PRs on GitHub"
Write-Host "3. Assign additional reviewers as needed"
Write-Host "4. Follow up on the remediation steps in each PR"
