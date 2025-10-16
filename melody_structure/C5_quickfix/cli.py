# MIT License
#
# Copyright (c) 2024 Echoes Project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from automation.core.lumina_client import LuminaClient  # Import the client

app = typer.Typer()
console = Console()


@app.command()
def quickfix(
    file_path: str = typer.Argument(..., help="Path to the file to QuickFix"),
    line: Optional[int] = typer.Option(None, help="Specific line number to focus on"),
    dry_run: bool = typer.Option(True, help="Preview changes without applying"),
):
    file_path = Path(file_path).resolve()
    if not file_path.exists():
        console.print(f"[red]File not found: {file_path}[/red]")
        raise typer.Exit(1)

    if file_path.suffix != ".py":
        console.print("[red]Only Python files are supported.[/red]")
        raise typer.Exit(1)

    # Gather context
    context = gather_context(file_path, line)

    # Initialize Lumina client
    lumina = LuminaClient()  # Assumes API key is set in env or config

    # Get QuickFix suggestions
    suggestions = lumina.get_quickfix_suggestions(context)

    if not suggestions:
        console.print(
            "[yellow]No QuickFix suggestions found for this context.[/yellow]"
        )
        return

    # Display suggestions
    for i, sug in enumerate(suggestions, 1):
        console.print(
            Panel(
                f"[bold]{sug['label']}[/bold]\n{sug['summary']}",
                title=f"Suggestion {i}",
            )
        )

    # User selects
    selection = typer.prompt("Select suggestion (number) or 'q' to quit", type=str)
    if selection.lower() == "q":
        return

    try:
        idx = int(selection) - 1
        chosen = suggestions[idx]
    except (ValueError, IndexError):
        console.print("[red]Invalid selection.[/red]")
        return

    # Apply or preview
    if dry_run:
        console.print("[blue]Preview Mode - No changes will be applied.[/blue]")
        console.print(
            Panel(chosen.get("preview", "Preview unavailable"), title="Preview")
        )
        if Confirm.ask("Apply this change?"):
            dry_run = False

    if not dry_run:
        apply_change(file_path, chosen)
        console.print("[green]QuickFix applied successfully![/green]")
    else:
        console.print("[cyan]Preview completed. No changes made.[/cyan]")


def gather_context(file_path: Path, line: Optional[int]):
    """
    Gather context around the file and line.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if line is not None and 1 <= line <= len(lines):
        start = max(0, line - 10)
        end = min(len(lines), line + 10)
        selection = "".join(lines[start:end])
        before = "".join(lines[:start])
        after = "".join(lines[end:])
    else:
        selection = ""
        before = "".join(lines)
        after = ""

    return {
        "file_path": str(file_path),
        "language_id": "python",
        "selected_text": selection,
        "before": before,
        "after": after,
        "cursor": {"line": line or 1, "character": 0},
        "diagnostics": [],  # Could integrate with pylint or similar
    }


def apply_change(file_path: Path, suggestion):
    """
    Apply the suggested change to the file.
    """
    # Placeholder: In real implementation, use diff application logic
    console.print("[yellow]Applying change (placeholder implementation)[/yellow]")
    # Would parse suggestion['unidiff'] and apply to file


if __name__ == "__main__":
    app()
