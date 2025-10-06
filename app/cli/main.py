import typer
from rich.console import Console

app = typer.Typer(help="HarmonyHub CLI")
console = Console()

# Mount sub-apps
try:
    from . import audit as audit_cli

    app.add_typer(audit_cli.app, name="audit", help="AI safety auditing commands")
except ImportError:
    console.print("[yellow]Audit module not available (missing torch)[/yellow]")

try:
    from . import tour as tour_cli

    app.add_typer(
        tour_cli.app, name="tour", help="Tour-guide for user onboarding, generation, and publishing"
    )
except ImportError as e:
    console.print(f"[red]Tour module not available: {e}[/red]")


@app.command()
def version():
    """Show CLI version."""
    console.print("HarmonyHub CLI v0.1.0")


if __name__ == "__main__":
    app()
