"""Production Bible, activation prompt, and memory CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.panel import Panel
from rich.table import Table

from models import DEFAULT_IMAGINE_VIDEO_MODEL, DEFAULT_XAI_CHAT_MODEL, resolve_video_model
from project_state import load_project_state, save_project_state
from quota_optimizer import estimate_production

from cli.helpers import assess_risk_from_state
from cli.production import build_activation_prompt, build_production_bible
from cli.quota_display import print_production_estimate_table
from cli.shared import console


def register(app: typer.Typer) -> None:
    """Register bible / prompt / memory commands on the root CLI app."""

    @app.command(name="generate-prompt")
    def generate_prompt(
        story: str = typer.Argument(..., help="Your story, scene, or project description"),
        signature: str = typer.Option("default", "--signature", "-s", help="Director style"),
        chat_model: str = typer.Option(DEFAULT_XAI_CHAT_MODEL, "--chat-model", help="xAI chat model (grok-4.3, grok-build-0.1)"),
        video_model: str = typer.Option(DEFAULT_IMAGINE_VIDEO_MODEL, "--video-model", "--model", "-m", help="Imagine video model slug or alias"),
        output: str = typer.Option(None, "--output", "-o", help="Save to file"),
    ):
        """Generate a high-quality ready-to-paste prompt."""
        prompt = build_activation_prompt(
            story,
            signature=signature,
            chat_model=chat_model,
            video_model=video_model,
        )
        if output:
            Path(output).write_text(prompt)
            console.print(f"[green]✅ Prompt saved to[/green] {output}")
        else:
            console.print(Panel(prompt, title="📜 Ready-to-Paste Prompt", border_style="green"))

    @app.command(name="cost-simulate")
    def cost_simulate(
        duration: int = typer.Option(60, "--duration", "-d", help="Target duration in seconds"),
        complexity: str = typer.Option("medium", "--complexity", "-c", help="low / medium / high / extreme"),
        clips: int = typer.Option(None, "--clips", help="Number of clips"),
        fast_mode: bool = typer.Option(False, "--fast-mode", help="Use Fast mode pricing"),
        video_model: str = typer.Option(DEFAULT_IMAGINE_VIDEO_MODEL, "--video-model", "-m", help="Imagine video model slug or alias"),
    ):
        """Estimate generation cost (alias for quota estimate with compact output)."""
        video_slug = resolve_video_model(video_model)
        estimate = estimate_production(
            duration,
            clip_count=clips,
            complexity=complexity,
            fast_mode=fast_mode,
            video_model=video_slug,
        )
        risk = assess_risk_from_state(estimate)
        print_production_estimate_table(
            estimate,
            risk,
            duration=duration,
            complexity=complexity,
            fast_mode=fast_mode,
            video_model=video_slug,
        )
        console.print("[dim]See also: quota estimate · quota optimize[/dim]")

    @app.command(name="create-bible")
    def create_bible(
        title: str = typer.Argument(..., help="Project title"),
        genre: str = typer.Option("Cinematic", "--genre", "-g"),
        chat_model: str = typer.Option(DEFAULT_XAI_CHAT_MODEL, "--chat-model", help="xAI chat model (grok-4.3, grok-build-0.1)"),
        video_model: str = typer.Option(DEFAULT_IMAGINE_VIDEO_MODEL, "--video-model", "-m", help="Imagine video model slug or alias"),
        output: str = typer.Option("production_bible.json", "--output", "-o"),
    ):
        """Generate a rich, structured Production Bible."""
        bible = build_production_bible(
            title,
            genre=genre,
            chat_model=chat_model,
            video_model=video_model,
        )
        Path(output).write_text(json.dumps(bible, indent=2))

        state = load_project_state()
        state["project"] = bible
        save_project_state(state)

        console.print(f"[green]✅ Rich Production Bible created:[/green] {output}")
        console.print("[dim]Includes locked variables, key agents, and recommended phases[/dim]")

    memory_app = typer.Typer(help="Manage project memory entries")
    app.add_typer(memory_app, name="memory")

    @memory_app.command("add")
    def memory_add(
        name: str = typer.Option(..., "--name", "-n", help="Memory entry name"),
        value: str = typer.Option(..., "--value", "-v", help="Value to store"),
    ):
        """Add a project memory entry."""
        state = load_project_state()
        state.setdefault("characters", {})
        state["characters"][name] = value
        save_project_state(state)
        console.print(f"[green]✅ Saved memory for[/green] {name}")

    @memory_app.command("list")
    def memory_list():
        """List project memory entries."""
        state = load_project_state()
        entries = state.get("characters", {})
        if not entries:
            console.print("[yellow]No memory entries yet[/yellow]")
            return
        table = Table(title="🧠 Project Memory")
        table.add_column("Name", style="cyan")
        table.add_column("Value", style="white")
        for k, v in entries.items():
            if isinstance(v, str):
                table.add_row(k, v[:80])
        console.print(table)

    @memory_app.command("load")
    def memory_load(
        name: str = typer.Argument(..., help="Memory entry name"),
    ):
        """Display a project memory entry."""
        state = load_project_state()
        value = state.get("characters", {}).get(name)
        if isinstance(value, str):
            console.print(Panel(value, title=f"Memory: {name}"))
        else:
            console.print("[yellow]Memory entry not found[/yellow]")
            raise typer.Exit(1)