# Twitter Bearer Token Setup Script
# This script helps you set your Twitter Bearer Token as an environment variable

param(
    [Parameter(Mandatory=$true)]
    [string]$BearerToken
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Twitter Bearer Token Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set the environment variable
try {
    [Environment]::SetEnvironmentVariable("TWITTER_BEARER_TOKEN", $BearerToken, "Machine")
    Write-Host "✅ Twitter Bearer Token set successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "The token has been saved as a system environment variable." -ForegroundColor Yellow
    Write-Host "You may need to restart your PowerShell session or IDE for changes to take effect." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To verify, run: python check_twitter_credentials.py" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to set the environment variable." -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please run this script as Administrator." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Press Enter to exit"
