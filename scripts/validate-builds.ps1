$ErrorActionPreference = "Stop"
$VerbosePreference = "Continue"

Write-Host "Starting build validation..." -ForegroundColor Blue
Write-Verbose "$(Get-Date) - Build validation started"

$configs = @('Debug', 'Development', 'Staging', 'Release')
$results = @{}
$anyFailures = $false

$configs | ForEach-Object {
    $config = $_
    Write-Host "`n=== Building $config Configuration ===" -ForegroundColor Cyan

    try {
        $output = dotnet build -c $config 2>&1
        $success = $LASTEXITCODE -eq 0
        $results[$config] = @{
            Success = $success
            Output  = $output
        }

        if ($success) {
            Write-Host "✅ $config build succeeded" -ForegroundColor Green
        }
        else {
            Write-Host "❌ $config build failed" -ForegroundColor Red
            $anyFailures = $true
        }
    }
    catch {
        Write-Host "❌ $config build failed with exception" -ForegroundColor Red
        $results[$config] = @{
            Success = $false
            Output  = $_.Exception.Message
        }
        $anyFailures = $true
    }
}

Write-Host "`n=== Build Summary ===" -ForegroundColor Blue
$results.Keys | ForEach-Object {
    $status = if ($results[$_].Success) { "✅" } else { "❌" }
    Write-Host "$status $_"
}

if ($anyFailures) {
    exit 1
}
else {
    Write-Host "`nAll configurations built successfully!" -ForegroundColor Green
}
