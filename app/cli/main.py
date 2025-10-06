import typer
from rich.console import Console
from . import audit as audit_cli

app = typer.Typer(help="HarmonyHub CLI")
console = Console()

# Mount sub-apps
app.add_typer(audit_cli.app, name="audit", help="AI safety auditing commands")


@app.command()
def version():
    """Show CLI version."""
    console.print("HarmonyHub CLI v0.1.0")


if __name__ == "__main__":
    app()
