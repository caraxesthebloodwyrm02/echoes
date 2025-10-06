# app/cli/tour.py
"""
Tour-guide CLI for user onboarding, content generation, and publishing.
Integrates with swing scheduler and highway router for production-safe workflows.
"""

import typer
from rich.console import Console
import yaml
from pathlib import Path
from datetime import datetime
from ..harmony.swing_scheduler import SamplerState

try:
    from ..domains.arts.investlab.hub_investlab.hub.highway import highway, DataType

    HIGHWAY_AVAILABLE = True
except ImportError:
    HIGHWAY_AVAILABLE = False
    highway = None
    DataType = None

app = typer.Typer(help="Tour-guide for user onboarding, generation, and publishing")
console = Console()

CONFIG_DIR = Path(__file__).parent.parent.parent / "configs" / "ai"


@app.command()
def onboard(
    user: str = typer.Option(..., "--user", help="User name"),
    profile: str = typer.Option(..., "--profile", help="Profile"),
):
    """Onboard a user with a persona profile."""
    user_config = yaml.safe_load((CONFIG_DIR / "user_profiles.yaml").read_text())
    if profile not in user_config["personas"]:
        console.print(f"[red]Invalid profile: {profile}[/red]")
        return

    persona = user_config["personas"][profile]
    console.print(f"Onboarding user '{user}' as '{profile}' (skill: {persona['skill_level']})")
    # Simulate saving to a user DB or file
    with open(f"automation/reports/user_{user}.yaml", "w") as f:
        yaml.dump({"user": user, "persona": profile, **persona}, f)
    console.print(f"[green]User onboarded successfully.[/green]")


@app.command()
def generate(
    user: str = typer.Option(..., "--user", help="User name"),
    goal: str = typer.Option(..., "--goal", help="Generation goal"),
    max_tokens: int = typer.Option(256, "--max-tokens", help="Max tokens"),
):
    """Generate content for a user using swing scheduler."""
    # Load user profile
    try:
        user_data = yaml.safe_load((Path(f"automation/reports/user_{user}.yaml")).read_text())
        profile = user_data["persona"]
        swing_profile = user_data["preferred_swing_profile"]
    except FileNotFoundError:
        console.print(f"[red]User '{user}' not onboarded. Run 'tour onboard' first.[/red]")
        return

    # Initialize scheduler
    state = SamplerState(profile=swing_profile)

    # Simulate generation loop (placeholder for actual LLM call)
    generated = []
    for t in range(max_tokens):
        params = state.next_params(t)
        # Here: call LLM with params (e.g., via transformers or API)
        # For demo: append a placeholder token based on params
        token = f"token_{t}_T{params['temperature']:.2f}_P{params['top_p']:.2f}"
        generated.append(token)

        # Flip on boundaries (simulate every 32 tokens)
        if t % 32 == 0 and t > 0:
            params = state.next_params(t, event=True)  # Trigger flip

    # Log to analytics
    metadata = {
        "user": user,
        "goal": goal,
        "max_tokens": max_tokens,
        "profile": profile,
        "swing_profile": swing_profile,
        "generated_tokens": len(generated),
        "timestamp": datetime.now().isoformat(),
        "ratings": {"perplexity": 2.5, "engagement": 0.8},  # Placeholder for actual metrics
    }
    with open(f"automation/reports/generation_{user}_{goal}.yaml", "w") as f:
        yaml.dump(metadata, f)

    console.print(
        f"[green]Generated {len(generated)} tokens for '{goal}' using profile '{profile}'.[/green]"
    )
    console.print(f"Logs saved to automation/reports/generation_{user}_{goal}.txt")


@app.command()
def publish(
    user: str = typer.Option(..., "--user", help="User name"),
    content_path: str = typer.Option(..., "--content-path", help="Content path"),
    platform: str = typer.Option("youtube", "--platform", help="Platform"),
):
    """Publish content for a user via highway router."""
    if not HIGHWAY_AVAILABLE:
        console.print("[red]Highway not available, cannot publish.[/red]")
        return

    # Load user profile
    try:
        user_data = yaml.safe_load((Path(f"automation/reports/user_{user}.yaml")).read_text())
    except FileNotFoundError:
        console.print(f"[red]User '{user}' not onboarded.[/red]")
        return

    # Simulate publishing via highway
    payload = {
        "user": user,
        "content_path": content_path,
        "platform": platform,
        "persona": user_data["persona"],
    }
    packet_id = highway.send_data(
        source="tour_cli",
        destination="media",
        data_type=DataType.CONTENT,
        payload=payload,
    )

    # Log packet
    with open(f"automation/reports/publish_{user}_{platform}.yaml", "w") as f:
        yaml.dump({"packet_id": packet_id, **payload}, f)

    console.print(
        f"[green]Published content for '{user}' to '{platform}'. Packet ID: {packet_id}[/green]"
    )
