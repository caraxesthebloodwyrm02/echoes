#!/usr/bin/env python3
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

"""
Symphony Assistant CLI
Command-line interface for credit-efficient OpenAI assistance
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table

from automation.notifications.notify import Notifier

# Ensure project root is on sys.path when running as a script
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from automation.integration.symphony_assistant_integration import (
    CreditEfficientPatterns,
    MasterChannelIntegration,
    SymphonyAssistantClient,
)

app = typer.Typer()
console = Console()


@app.command()
def query(
    prompt: str = typer.Argument(..., help="Question or prompt for assistance"),
    model: Optional[str] = typer.Option(
        None, help="Override model (gpt-4o-mini, gpt-4o)"
    ),
    temperature: float = typer.Option(0.2, help="Creativity level (0.0-1.0)"),
    max_tokens: Optional[int] = typer.Option(512, help="Maximum response length"),
    no_cache: bool = typer.Option(False, help="Skip cache and force fresh response"),
    batch_file: Optional[Path] = typer.Option(
        None, help="File with multiple queries to batch"
    ),
):
    """Query the Symphony assistant with intelligent caching"""

    async def run_query():
        async with SymphonyAssistantClient() as assistant:
            queries = [prompt]

            # Handle batch queries
            if batch_file and batch_file.exists():
                try:
                    with open(batch_file, "r") as f:
                        batch_queries = [line.strip() for line in f if line.strip()]
                    if batch_queries:
                        queries = batch_queries
                except Exception as e:
                    console.print(f"[red]Error reading batch file: {e}[/red]")
                    return

            # Batch similar queries for efficiency
            if len(queries) > 1:
                combined_prompt = CreditEfficientPatterns.batch_similar_queries(queries)
                console.print(
                    f"[blue]Batched {len(queries)} queries into single request[/blue]"
                )
            else:
                combined_prompt = queries[0]

            # Make the query
            response = await assistant.query_with_cache(
                combined_prompt,
                use_cache=not no_cache,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Display results
            if "error" in response:
                console.print(f"[red]Error: {response['error']}[/red]")
                if "fallback" in response:
                    console.print("[yellow]Fallback response:[/yellow]")
                    console.print(response["fallback"])
                return

            # Show cache status
            cache_status = (
                "[green]Fresh[/green]"
                if not response.get("cached", False)
                else "[blue]Cached[/blue]"
            )
            console.print(f"Response ({cache_status}):")

            # Display content in a nice panel
            content = response.get("content", "No content")
            console.print(Panel(content, title="Assistant Response"))

            # Show usage if available
            if "usage" in response and response["usage"]:
                usage = response["usage"]
                console.print(
                    f"\n[yellow]Usage: {usage.get('total_tokens', 'N/A')} tokens[/yellow]"
                )

    asyncio.run(run_query())


@app.command()
def templates():
    """Show available query templates"""
    templates = CreditEfficientPatterns.create_contextual_templates()

    table = Table(title="Available Templates")
    table.add_column("Template", style="cyan")
    table.add_column("Description", style="white")

    for name, template in templates.items():
        # Show simplified template
        simplified = template.replace("{", "[").replace("}", "]")
        table.add_row(name, simplified)

    console.print(table)
    # Emit completion notification
    Notifier.notify(
        "Assistant cache-list",
        f"Displayed {len(recent)} cached entries (showing up to {limit})",
    )


@app.command()
def models():
    """List available OpenAI models"""

    async def list_models():
        async with SymphonyAssistantClient() as assistant:
            try:
                model_list = await assistant.get_models()
                console.print(f"[green]Available models ({len(model_list)}):[/green]")

                # Group models by category
                categories = {
                    "GPT-4": [
                        m for m in model_list if "gpt-4" in m and "mini" not in m
                    ],
                    "GPT-4 Mini": [
                        m for m in model_list if "gpt-4" in m and "mini" in m
                    ],
                    "GPT-3.5": [m for m in model_list if "gpt-3.5" in m],
                    "Other": [
                        m
                        for m in model_list
                        if not any(
                            x in m
                            for x in ["gpt-4", "gpt-3.5", "dall-e", "whisper", "tts"]
                        )
                    ],
                }

                for category, models in categories.items():
                    if models:
                        console.print(f"\n[yellow]{category}:[/yellow]")
                        for model in sorted(models):
                            console.print(f"  • {model}")

            except Exception as e:
                console.print(f"[red]Error fetching models: {e}[/red]")

    asyncio.run(list_models())


@app.command()
def switch_key(key_type: str = typer.Argument(..., help="PRIMARY or SECONDARY")):
    """Switch between OpenAI API keys"""
    import httpx

    async def switch():
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "http://127.0.0.1:8000/assistant/switch-key",
                    json={"key_type": key_type.upper()},
                )
                response.raise_for_status()
                result = response.json()

                if result["status"] == "ok":
                    console.print(
                        f"[green]Switched to {result['active_key']} API key[/green]"
                    )
                else:
                    console.print("[red]Switch failed[/red]")

            except httpx.RequestError as e:
                console.print(f"[red]Connection error: {e}[/red]")
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")

    asyncio.run(switch())


@app.command()
def integrate_master_channel():
    """Run master channel with AI assistance"""

    async def run_integration():
        integrator = MasterChannelIntegration()

        # Example data
        test_data = {
            "operation": "symphony_assistant_integration",
            "components": ["assistant_api", "caching", "templates"],
            "status": "demonstration",
        }

        console.print("[blue]Compressing and gluing with AI assistance...[/blue]")
        compressed = await integrator.assisted_compress_and_glue(test_data)

        console.print("[blue]Finalizing with AI-enhanced summary...[/blue]")
        final_result = await integrator.assisted_finalize(
            {"compressed_data": compressed}
        )

        console.print("[green]Integration complete![/green]")
        console.print(Panel(final_result, title="AI-Enhanced Master Channel Result"))

    asyncio.run(run_integration())


@app.command()
def stats():
    """Show assistant usage statistics"""
    cache_dir = Path("automation/cache/assistant")

    if not cache_dir.exists():
        console.print(
            "[yellow]No cache directory found - no statistics available[/yellow]"
        )
        return

    # Count cached responses
    cache_files = list(cache_dir.glob("*.json"))
    total_cached = len(cache_files)

    if total_cached == 0:
        console.print("[yellow]No cached responses yet[/yellow]")
        return

    # Estimate token savings (rough calculation)
    avg_tokens_per_response = 256  # Conservative estimate
    estimated_savings = (
        total_cached * avg_tokens_per_response * 0.00015
    )  # GPT-4o-mini cost

    console.print("[green]Assistant Usage Statistics:[/green]")
    console.print(f"  Cached Responses: {total_cached}")
    console.print(f"  Cache Directory: {cache_dir}")
    console.print(f"  Estimated Cost Savings: ${estimated_savings:.2f}")
    console.print(
        f"  Efficiency: {(total_cached / max(total_cached + 1, 1)) * 100:.1f}% of queries served from cache"
    )

    # Show recent cache files
    if cache_files:
        console.print("\n[yellow]Recent cached queries:[/yellow]")
        recent_files = sorted(
            cache_files, key=lambda x: x.stat().st_mtime, reverse=True
        )[:5]
        for cache_file in recent_files:
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    if "content" in data:
                        preview = (
                            data["content"][:80] + "..."
                            if len(data["content"]) > 80
                            else data["content"]
                        )
                        console.print(f"  • {preview}")
            except:
                console.print(f"  • [Error reading {cache_file.name}]")


@app.command()
def trajectory(
    run_tests: bool = typer.Option(
        False, help="Run focused pytest checks as part of trajectory"
    ),
):
    """Run a short trajectory check (API, cache, optional tests) and report completion percentage."""
    from pathlib import Path

    import httpx

    checks = []

    # 1) API reachability: /assistant/models
    api_ok = False
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get("http://127.0.0.1:8000/assistant/models")
            if r.status_code == 200:
                api_ok = True
    except Exception:
        api_ok = False

    checks.append(("API reachable", api_ok))

    # 2) Cache stats available
    cache_ok = False
    cache_dir = Path("automation/cache/assistant")
    try:
        files = list(cache_dir.glob("*.json")) if cache_dir.exists() else []
        cache_ok = len(files) > 0
    except Exception:
        cache_ok = False

    # 3) Health endpoint check
    health_ok = False
    try:
        with httpx.Client(timeout=5.0) as client:
            r = client.get("http://127.0.0.1:8000/assistant/health")
            if r.status_code == 200:
                health_data = r.json()
                health_ok = health_data.get(
                    "openai_client_initialized", False
                ) and health_data.get("cache_writable", False)
    except Exception:
        health_ok = False

    checks.append(("Health endpoint", health_ok))

    # 4) Optional: run focused tests
    tests_ok = None
    if run_tests:
        import subprocess

        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "tests/test_assistant_cache_and_config.py",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            tests_ok = proc.returncode == 0
        except Exception:
            tests_ok = False
    checks.append(("Focused tests", tests_ok if tests_ok is not None else "skipped"))

    score_items = [api_ok, cache_ok]
    if run_tests:
        score_items.append(bool(tests_ok))

    true_count = sum(1 for v in score_items if v)
    possible = len(score_items)
    percent = int((true_count / possible) * 100) if possible else 0

    # Print summary
    console.print(f"\n[bold]Trajectory Check — Completion: {percent}%[/bold]")
    table = Table()
    table.add_column("Check")
    table.add_column("Status")
    for name, ok in checks:
        status = (
            "[green]OK[/green]"
            if ok is True
            else ("[yellow]SKIPPED[/yellow]" if ok == "skipped" else "[red]FAIL[/red]")
        )
        table.add_row(escape(name), status)

    console.print(table)
    # Emit completion notification
    Notifier.notify("Assistant trajectory", f"Completion: {percent}%")


@app.command()
def vector_search(query: str, top_k: int = 5, hybrid: bool = True):
    """Search the codebase index using vector analysis."""
    from automation.core.unified_vector_module import UnifiedVectorModule

    index_path = "codebase_index.pkl"
    try:
        module = UnifiedVectorModule()
        module.load_module(index_path)

        if hybrid:
            results = module.hybrid_search(query, top_k=top_k)
        else:
            results = module.search(query, top_k=top_k)

        console.print(f"[green]Search results for '{query}':[/green]")
        table = Table()
        table.add_column("File")
        table.add_column("Score")
        table.add_column("Preview")
        for result in results:
            file = result.get("file", "unknown")
            score = f"{result.get('score', 0):.2f}"
            preview = result.get("content", "")[:50] + "..."
            table.add_row(file, score, preview)
        console.print(table)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    app()
