#!/usr/bin/env python3
"""
Echoes AI Command Line Interface

Provides CLI commands for managing Echoes AI agents, workflows,
and cluster operations.
"""

import os
import sys

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

app = typer.Typer(
    name="echoes",
    help="Echoes AI Multi-Agent System CLI",
    no_args_is_help=True,
)

console = Console()


@app.command()
def version():
    """Show Echoes AI version."""
    from . import __version__

    rprint(f"[bold green]Echoes AI[/bold green] version [blue]{__version__}[/blue]")


@app.command()
def info():
    """Show Echoes AI package information."""
    from . import get_info

    info = get_info()

    table = Table(title="Echoes AI Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    for key, value in info.items():
        if isinstance(value, list):
            value = ", ".join(value)
        table.add_row(key.replace("_", " ").title(), str(value))

    console.print(table)


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind to"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind to"),
    reload: bool = typer.Option(False, "--reload", "-r", help="Enable auto-reload"),
    workers: int = typer.Option(
        1, "--workers", "-w", help="Number of worker processes"
    ),
):
    """Start the Echoes AI server."""
    rprint("[bold green]Starting Echoes AI server...[/bold green]")
    rprint(f"[cyan]Host:[/cyan] {host}")
    rprint(f"[cyan]Port:[/cyan] {port}")
    rprint(f"[cyan]Workers:[/cyan] {workers}")
    rprint(f"[cyan]Reload:[/cyan] {reload}")

    try:
        import uvicorn

        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers if not reload else 1,
        )
    except ImportError:
        rprint("[bold red]Error:[/bold red] uvicorn not installed")
        rprint("Install with: pip install echoes-ai[dev]")
        sys.exit(1)
    except Exception as e:
        rprint(f"[bold red]Error starting server:[/bold red] {e}")
        sys.exit(1)


@app.command()
def cluster(
    action: str = typer.Argument(..., help="Action: start, stop, status, setup"),
    name: str = typer.Option("echoes-cluster", "--name", "-n", help="Cluster name"),
):
    """Manage Echoes AI cluster."""
    rprint(f"[bold green]Managing cluster:[/bold green] {name}")

    if action == "setup":
        rprint("[cyan]Setting up cluster...[/cyan]")
        try:
            from .cluster import main as cluster_main

            cluster_main()
        except ImportError:
            rprint("[bold red]Error:[/bold red] cluster module not found")
            sys.exit(1)
    elif action == "start":
        rprint("[cyan]Starting cluster...[/cyan]")
        try:
            import subprocess

            result = subprocess.run(
                ["python", "cluster_start.py"], capture_output=True, text=True, cwd="."
            )
            if result.returncode == 0:
                rprint("[bold green]✅ Cluster started successfully[/bold green]")
                rprint(result.stdout)
            else:
                rprint(
                    f"[bold red]❌ Failed to start cluster:[/bold red] {result.stderr}"
                )
        except Exception as e:
            rprint(f"[bold red]Error starting cluster:[/bold red] {e}")
    elif action == "stop":
        rprint("[cyan]Stopping cluster...[/cyan]")
        try:
            import subprocess

            result = subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    "clusters/echoes-cluster/docker-compose.yaml",
                    "down",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                rprint("[bold green]✅ Cluster stopped successfully[/bold green]")
            else:
                rprint(
                    f"[bold red]❌ Failed to stop cluster:[/bold red] {result.stderr}"
                )
        except Exception as e:
            rprint(f"[bold red]Error stopping cluster:[/bold red] {e}")
    elif action == "status":
        rprint("[cyan]Checking cluster status...[/cyan]")
        try:
            import subprocess

            result = subprocess.run(
                ["python", "cluster_status.py"], capture_output=True, text=True, cwd="."
            )
            rprint(result.stdout)
        except Exception as e:
            rprint(f"[bold red]Error checking status:[/bold red] {e}")
    else:
        rprint(f"[bold red]Unknown action:[/bold red] {action}")
        rprint("Available actions: setup, start, stop, status")
        sys.exit(1)


@app.command()
def test(
    path: str = typer.Option("tests", "--path", "-p", help="Test path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
    coverage: bool = typer.Option(
        False, "--coverage", "-c", help="Generate coverage report"
    ),
):
    """Run Echoes AI tests."""
    rprint("[bold green]Running tests...[/bold green]")

    cmd = ["pytest", path]
    if verbose:
        cmd.append("-v")
    if coverage:
        cmd.extend(["--cov=echoes", "--cov-report=html", "--cov-report=term"])

    try:
        import subprocess

        result = subprocess.run(cmd, capture_output=True, text=True)
        rprint(result.stdout)
        if result.stderr:
            rprint(f"[bold red]Errors:[/bold red] {result.stderr}")
    except Exception as e:
        rprint(f"[bold red]Error running tests:[/bold red] {e}")


@app.command()
def lint(
    fix: bool = typer.Option(False, "--fix", "-f", help="Fix auto-fixable issues"),
):
    """Run code linting and formatting."""
    rprint("[bold green]Running linting...[/bold green]")

    try:
        import subprocess

        # Run ruff
        rprint("[cyan]Running ruff...[/cyan]")
        ruff_cmd = ["ruff", "check", "."]
        if fix:
            ruff_cmd.append("--fix")
        result = subprocess.run(ruff_cmd, capture_output=True, text=True)
        rprint(result.stdout)

        # Run black
        rprint("[cyan]Running black...[/cyan]")
        black_cmd = ["black", "."]
        if fix:
            result = subprocess.run(black_cmd, capture_output=True, text=True)
            rprint(result.stdout)
        else:
            black_cmd.append("--check")
            result = subprocess.run(black_cmd, capture_output=True, text=True)
            rprint(result.stdout)

        # Run mypy
        rprint("[cyan]Running mypy...[/cyan]")
        mypy_cmd = ["mypy", "echoes"]
        result = subprocess.run(mypy_cmd, capture_output=True, text=True)
        rprint(result.stdout)

        rprint("[bold green]✅ Linting completed[/bold green]")

    except Exception as e:
        rprint(f"[bold red]Error running linting:[/bold red] {e}")


@app.command()
def build(
    output: str = typer.Option("dist", "--output", "-o", help="Output directory"),
):
    """Build the Echoes AI package."""
    rprint("[bold green]Building package...[/bold green]")

    try:
        import subprocess

        result = subprocess.run(
            ["python", "-m", "build", "--outdir", output],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            rprint("[bold green]✅ Package built successfully[/bold green]")
            rprint(f"[cyan]Output directory:[/cyan] {output}")
        else:
            rprint(f"[bold red]❌ Build failed:[/bold red] {result.stderr}")
    except Exception as e:
        rprint(f"[bold red]Error building package:[/bold red] {e}")


@app.command()
def publish(
    repository: str = typer.Option(
        "pypi", "--repository", "-r", help="Repository to publish to"
    ),
    test: bool = typer.Option(False, "--test", "-t", help="Publish to test PyPI"),
):
    """Publish the Echoes AI package to PyPI."""
    rprint(f"[bold green]Publishing package to {repository}...[/bold green]")

    if test:
        repository = "testpypi"
        rprint("[yellow]Publishing to Test PyPI[/yellow]")

    try:
        import subprocess

        result = subprocess.run(
            ["python", "-m", "twine", "upload", "--repository", repository, "dist/*"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            rprint("[bold green]✅ Package published successfully[/bold green]")
            rprint(f"[cyan]Repository:[/cyan] {repository}")
        else:
            rprint(f"[bold red]❌ Publish failed:[/bold red] {result.stderr}")
    except Exception as e:
        rprint(f"[bold red]Error publishing package:[/bold red] {e}")


if __name__ == "__main__":
    app()
