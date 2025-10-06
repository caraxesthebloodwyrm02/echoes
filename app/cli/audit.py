import typer
from rich.console import Console
from typing import Optional
from app.domains.audit.audit_core import AuditEngine, AuditConfig

app = typer.Typer(help="AI safety auditing commands")
console = Console()


@app.command()
def quick(
    prompt: str = typer.Argument(..., help="Input text or scenario for quick probe"),
    domain: str = typer.Option("general", help="Domain: arts|commerce|finance|general"),
):
    """Run a quick black-box audit probe."""
    config = AuditConfig(model_path="", audit_type="black_box", domain=domain)
    engine = AuditEngine(config)
    result = engine.run_quick_audit(prompt)
    console.print(result)


@app.command()
def full(
    domain: str = typer.Option("general", help="Domain: arts|commerce|finance|general"),
    white_box: bool = typer.Option(True, help="Include interpretability/white-box steps"),
    monetize: bool = typer.Option(False, help="Generate monetization content"),
):
    """Run a full audit workflow (blind game + interpretability + scoring)."""
    audit_type = "full" if white_box else "black_box"
    config = AuditConfig(model_path="", audit_type=audit_type, domain=domain, monetization_mode=monetize)
    engine = AuditEngine(config)
    result = engine.run_full_audit()
    console.print(result)


@app.command()
def report(out: Optional[str] = typer.Option(None, help="Output path for audit report (MD)")):
    """Placeholder report command (to be expanded in Phase 1)."""
    console.print("Report generation will be implemented in Phase 1.")
    if out:
        console.print(f"Planned output: {out}")
