# Docker Development Workflow Script (PowerShell)
# Provides easy commands for Docker-based development

param(
    [Parameter(Mandatory=$false)]
    [ArgumentCompleter({
        param(
            [string] $CommandName,
            [string] $ParameterName,
            [string] $WordToComplete,
            [System.Management.Automation.Language.CommandAst] $CommandAst,
            [System.Collections.IDictionary] $FakeBoundParameters
        )

        $CompletionResults = [System.Collections.Generic.List[System.Management.Automation.CompletionResult]]::new()

        # Example completions. Replace or extend with your logic.
        $candidates = @('help','get-help','start','stop','status') |
                      Where-Object { $_ -like "$WordToComplete*" }

        foreach ($c in $candidates) {
            $CompletionResults.Add(
                [System.Management.Automation.CompletionResult]::new(
                    $c,               # CompletionText
                    $c,               # ListItemText
                    'ParameterValue', # ResultType
                    "Complete: $c"    # ToolTip
                )
            )
        }

        return $CompletionResults
    })]
    [string]$Command = 'help',

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)


# Project configuration
$ProjectName = "semantic-resonance"
$DockerImage = "${ProjectName}:dev"

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Test-DockerRunning {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Test-DockerComposeAvailable {
    try {
        docker-compose --version | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Invoke-Build {
    Write-Info "Building Docker image: $DockerImage"
    docker build -t $DockerImage .
    Write-Success "Docker image built successfully"
}

function Invoke-Up {
    if (-not (Test-DockerRunning)) {
        Write-Error "Docker is not running. Please start Docker and try again."
        exit 1
    }

    if (-not (Test-DockerComposeAvailable)) {
        Write-Error "docker-compose is not installed. Please install docker-compose and try again."
        exit 1
    }

    Write-Info "Starting development environment..."
    docker-compose up -d
    Write-Success "Development environment started"

    Write-Info "Services available at:"
    Write-Host "  - Application: http://localhost:8000"
    Write-Host "  - Grafana: http://localhost:3000 (admin/admin)"
    Write-Host "  - Prometheus: http://localhost:9090"
    Write-Host "  - Redis: localhost:6379"
    Write-Host "  - PostgreSQL: localhost:5432"
}

function Invoke-Down {
    if (-not (Test-DockerComposeAvailable)) {
        Write-Error "docker-compose is not installed."
        exit 1
    }

    Write-Info "Stopping development environment..."
    docker-compose down
    Write-Success "Development environment stopped"
}

function Invoke-Logs {
    $service = if ($Arguments.Count -gt 0) { $Arguments[0] } else { "app" }

    if (-not (Test-DockerComposeAvailable)) {
        Write-Error "docker-compose is not installed."
        exit 1
    }

    docker-compose logs -f $service
}

function Invoke-Test {
    if (-not (Test-DockerRunning)) {
        Write-Error "Docker is not running."
        exit 1
    }

    Write-Info "Running tests in Docker container..."
    docker run --rm -v "${PWD}/6/coffee_house/coffee_house:/app/coffee_house" $DockerImage python run_tests.py
}

function Invoke-TestCoverage {
    if (-not (Test-DockerRunning)) {
        Write-Error "Docker is not running."
        exit 1
    }

    Write-Info "Running tests with coverage in Docker container..."
    docker run --rm -v "${PWD}/6/coffee_house/coffee_house:/app/coffee_house" $DockerImage python run_tests.py coverage
}

function Invoke-Security {
    if (-not (Test-DockerRunning)) {
        Write-Error "Docker is not running."
        exit 1
    }

    Write-Info "Running security scan on Docker image..."
    docker run --rm -v "/var/run/docker.sock:/var/run/docker.sock" aquasecurity/trivy:latest image $DockerImage
}

function Invoke-Clean {
    Write-Info "Cleaning up Docker resources..."

    # Stop and remove containers
    docker-compose down --volumes --remove-orphans 2>$null | Out-Null

    # Remove dangling images
    docker image prune -f

    # Remove unused volumes
    docker volume prune -f

    Write-Success "Cleanup completed"
}

function Invoke-Reset {
    Write-Info "Resetting development environment..."
    try {
        Invoke-Down
    }
    catch {
        Write-Warning "Containers were not running or failed to stop cleanly. Continuing reset."
    }

    Invoke-Clean
    Invoke-Up
}

function Invoke-Status {
    if (-not (Test-DockerComposeAvailable)) {
        Write-Error "docker-compose is not installed."
        exit 1
    }

    Write-Info "Container status:"
    docker-compose ps

    Write-Host ""
    Write-Info "Resource usage:"
    docker stats --no-stream
}

function Invoke-Exec {
    if ($Arguments.Count -lt 2) {
        Write-Error "Usage: .\docker-dev.ps1 exec <service> <command>"
        exit 1
    }

    $service = $Arguments[0]
    $command = $Arguments[1..($Arguments.Count-1)] -join " "

    Write-Info "Executing '$command' in $service container..."
    docker-compose exec $service $command
}

function Show-Help {
    Write-Host "Docker Development Workflow Script (PowerShell)"
    Write-Host ""
    Write-Host "Usage: .\docker-dev.ps1 <command>"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  build         Build Docker image"
    Write-Host "  up            Start development environment"
    Write-Host "  down          Stop development environment"
    Write-Host "  logs [service] View logs (default: app)"
    Write-Host "  test          Run tests in container"
    Write-Host "  test-coverage Run tests with coverage"
    Write-Host "  security      Run security scan"
    Write-Host "  clean         Clean up Docker resources"
    Write-Host "  reset         Reset containers (down + clean + up)"
    Write-Host "  status        Show container status"
    Write-Host "  exec <service> <cmd> Execute command in container"
    Write-Host "  help          Show this help"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\docker-dev.ps1 up"
    Write-Host "  .\docker-dev.ps1 logs app"
    Write-Host "  .\docker-dev.ps1 test"
    Write-Host "  .\docker-dev.ps1 exec app python -c `"print('Hello from container!')`""
}

# Main command handler
switch ($Command) {
    "build" { Invoke-Build }
    "up" { Invoke-Up }
    "down" { Invoke-Down }
    "logs" { Invoke-Logs }
    "test" { Invoke-Test }
    "test-coverage" { Invoke-TestCoverage }
    "security" { Invoke-Security }
    "clean" { Invoke-Clean }
    "reset" { Invoke-Reset }
    "status" { Invoke-Status }
    "exec" { Invoke-Exec }
    "help" { Show-Help }
    default {
        Write-Error "Unknown command: $Command"
        Write-Host ""
        Show-Help
        exit 1
    }
}
