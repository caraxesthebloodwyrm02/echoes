#!/usr/bin/env python3
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
from rich.panel import Panel
from rich.table import Table

from automation.integration.symphony_assistant_integration import (
    CreditEfficientPatterns,
    MasterChannelIntegration,
    SymphonyAssistantClient
)

app = typer.Typer()
console = Console()


@app.command()
def query(
    prompt: str = typer.Argument(..., help="Question or prompt for assistance"),
    model: Optional[str] = typer.Option(None, help="Override model (gpt-4o-mini, gpt-4o)"),
    temperature: float = typer.Option(0.2, help="Creativity level (0.0-1.0)"),
    max_tokens: Optional[int] = typer.Option(512, help="Maximum response length"),
    no_cache: bool = typer.Option(False, help="Skip cache and force fresh response"),
    batch_file: Optional[Path] = typer.Option(None, help="File with multiple queries to batch"),
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
                console.print(f"[blue]Batched {len(queries)} queries into single request[/blue]")
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
            cache_status = "[green]Fresh[/green]" if not response.get("cached", False) else "[blue]Cached[/blue]"
            console.print(f"Response ({cache_status}):")

            # Display content in a nice panel
            content = response.get("content", "No content")
            console.print(Panel(content, title="Assistant Response"))

            # Show usage if available
            if "usage" in response and response["usage"]:
                usage = response["usage"]
                console.print(f"\n[yellow]Usage: {usage.get('total_tokens', 'N/A')} tokens[/yellow]")

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
                    "GPT-4": [m for m in model_list if "gpt-4" in m and not "mini" in m],
                    "GPT-4 Mini": [m for m in model_list if "gpt-4" in m and "mini" in m],
                    "GPT-3.5": [m for m in model_list if "gpt-3.5" in m],
                    "Other": [m for m in model_list if not any(x in m for x in ["gpt-4", "gpt-3.5", "dall-e", "whisper", "tts"])]
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
                    json={"key_type": key_type.upper()}
                )
                response.raise_for_status()
                result = response.json()

                if result["status"] == "ok":
                    console.print(f"[green]Switched to {result['active_key']} API key[/green]")
                else:
                    console.print(f"[red]Switch failed[/red]")

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
            "status": "demonstration"
        }

        console.print("[blue]Compressing and gluing with AI assistance...[/blue]")
        compressed = await integrator.assisted_compress_and_glue(test_data)

        console.print("[blue]Finalizing with AI-enhanced summary...[/blue]")
        final_result = await integrator.assisted_finalize({"compressed_data": compressed})

        console.print("[green]Integration complete![/green]")
        console.print(Panel(final_result, title="AI-Enhanced Master Channel Result"))

    asyncio.run(run_integration())


@app.command()
def stats():
    """Show assistant usage statistics"""
    cache_dir = Path("automation/cache/assistant")

    if not cache_dir.exists():
        console.print("[yellow]No cache directory found - no statistics available[/yellow]")
        return

    # Count cached responses
    cache_files = list(cache_dir.glob("*.json"))
    total_cached = len(cache_files)

    if total_cached == 0:
        console.print("[yellow]No cached responses yet[/yellow]")
        return

    # Estimate token savings (rough calculation)
    avg_tokens_per_response = 256  # Conservative estimate
    estimated_savings = total_cached * avg_tokens_per_response * 0.00015  # GPT-4o-mini cost

    console.print("[green]Assistant Usage Statistics:[/green]")
    console.print(f"  Cached Responses: {total_cached}")
    console.print(f"  Cache Directory: {cache_dir}")
    console.print(".2f"    console.print(f"  Efficiency: {(total_cached / max(total_cached + 1, 1)) * 100:.1f}% of queries served from cache")

    # Show recent cache files
    if cache_files:
        console.print(f"\n[yellow]Recent cached queries:[/yellow]")
        recent_files = sorted(cache_files, key=lambda x: x.stat().st_mtime, reverse=True)[:5]
        for cache_file in recent_files:
            try:
                with open(cache_file, "r") as f:
                    data = json.load(f)
                    if "content" in data:
                        preview = data["content"][:80] + "..." if len(data["content"]) > 80 else data["content"]
                        console.print(f"  • {preview}")
            except:
                console.print(f"  • [Error reading {cache_file.name}]")


if __name__ == "__main__":
    app()
