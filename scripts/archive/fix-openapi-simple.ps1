# Simple OpenAPI Security Fixer

Write-Host '🔧 Fixing OpenAPI Security Issues...' -ForegroundColor Cyan

# Read the current OpenAPI spec
try {
    $spec = Get-Content 'openapi-spec.json' | ConvertFrom-Json -Depth 10
    Write-Host '✅ Loaded OpenAPI spec' -ForegroundColor Green
} catch {
    Write-Host '❌ Could not load OpenAPI spec' -ForegroundColor Red
    exit 1
}

# Fix security issues
Write-Host '🔒 Adding security schemes...' -ForegroundColor Yellow

# Add components if missing
if (-not $spec.components) {
    $spec | Add-Member -Name 'components' -Value @{} -MemberType NoteProperty
}

# Add securitySchemes
$spec.components | Add-Member -Name 'securitySchemes' -Value @{
    bearerAuth = @{
        type = 'http'
        scheme = 'bearer'
        bearerFormat = 'JWT'
    }
    apiKey = @{
        type = 'apiKey'
        in = 'header'
        name = 'X-API-Key'
    }
} -MemberType NoteProperty

# Add global security
$spec | Add-Member -Name 'security' -Value @(
    @{ bearerAuth = @() }
) -MemberType NoteProperty -Force

# Save fixed spec
$spec | ConvertTo-Json -Depth 10 | Set-Content 'openapi-spec-fixed.json'
Write-Host '✅ Fixed OpenAPI spec saved as openapi-spec-fixed.json' -ForegroundColor Green

Write-Host '' -ForegroundColor White
Write-Host '🎯 Next Steps:' -ForegroundColor Yellow
Write-Host '1. Open openapi-spec-fixed.json in VS Code' -ForegroundColor White
Write-Host '2. Run: Ctrl+Shift+P → \
OpenAPI:
API
Audit\' -ForegroundColor White
Write-Host '3. Export: Ctrl+Shift+P → \42Crunch:
Export
Scan
Report\' -ForegroundColor White
