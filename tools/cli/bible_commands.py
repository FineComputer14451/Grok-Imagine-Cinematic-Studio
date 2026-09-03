"""Production Bible, activation prompt, and memory CLI commands."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import typer
from rich.panel import Panel
from rich.table import Table

from aup_gate import AUPGateError, gate_planning_packet
from models import DEFAULT_IMAGINE_VIDEO_MODEL, DEFAULT_XAI_CHAT_MODEL, resolve_video_model
from project_state import load_project_state, save_project_state
from quota_optimizer import estimate_production

from cli.bible_stages import should_run_wizard, summary_and_next_steps
from cli.bible_wizard_cli import run_bible_wizard
from cli.helpers import assess_risk_from_state, resolve_chat_model_cli
from cli.production import build_activation_prompt, build_production_bible
from cli.quota_display import print_production_estimate_table
from cli.shared import console


def _persist_bible(bible: dict[str, Any], output: str) -> None:
    """Write bible JSON and update project state."""
    Path(output).write_text(json.dumps(bible, indent=2))
    state = load_project_state()
    state["project"] = bible
    save_project_state(state)
    console.print(f"[green]✅ Rich Production Bible created:[/green] {output}")
    console.print("[dim]Includes locked variables, key agents, and recommended phases[/dim]")
    console.print(summary_and_next_steps(bible))


def register(app: typer.Typer) -> None:
    """Register bible / prompt / memory commands on the root CLI app."""

    @app.command(name="generate-prompt")
    def generate_prompt(
        story: str = typer.Argument(..., help="Your story, scene, or project description"),
        signature: str = typer.Option("default", "--signature", "-s", help="Director style"),
        chat_model: str = typer.Option(DEFAULT_XAI_CHAT_MODEL, "--chat-model", help="xAI chat model (grok-4.6 default; grok-4.3 for 1M context)"),
        video_model: str = typer.Option(DEFAULT_IMAGINE_VIDEO_MODEL, "--video-model", "--model", "-m", help="Imagine video model slug or alias"),
        output: str = typer.Option(None, "--output", "-o", help="Save to file"),
    ):
        """Generate a high-quality ready-to-paste prompt."""
        try:
            gate_planning_packet(story)
        except AUPGateError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        chat_slug = resolve_chat_model_cli(chat_model)
        prompt = build_activation_prompt(
            story,
            signature=signature,
            chat_model=chat_slug,
            video_model=video_model,
        )
        try:
            gate_planning_packet(prompt)
        except AUPGateError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
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
        title: str | None = typer.Argument(None, help="Project title (omit with --wizard on a TTY)"),
        genre: str = typer.Option("Cinematic", "--genre", "-g"),
        chat_model: str = typer.Option(DEFAULT_XAI_CHAT_MODEL, "--chat-model", help="xAI chat model (grok-4.6 default; grok-4.3 for 1M context)"),
        video_model: str = typer.Option(DEFAULT_IMAGINE_VIDEO_MODEL, "--video-model", "-m", help="Imagine video model slug or alias"),
        output: str = typer.Option("production_bible.json", "--output", "-o"),
        wizard: bool = typer.Option(False, "--wizard", "-w", help="Guided interactive stages (requires TTY)"),
    ):
        """Generate a rich, structured Production Bible (direct or --wizard)."""
        isatty = sys.stdin.isatty()
        use_wizard = should_run_wizard(
            wizard_flag=wizard,
            title=title,
            stdin_isatty=isatty,
        )

        if use_wizard:
            if not isatty:
                console.print(
                    "[red]create-bible --wizard requires an interactive terminal.[/red]\n"
                    '[dim]Use: create-bible "Title" --genre ... for scripts[/dim]'
                )
                raise typer.Exit(2)
            seed: dict[str, Any] = {
                "genre": genre,
                "chat_model": chat_model,
                "video_model": video_model,
            }
            if title and str(title).strip():
                seed["title"] = str(title).strip()
            run_bible_wizard(seed=seed, output=output, persist=_persist_bible)
            return

        if not title or not str(title).strip():
            console.print(
                "[red]Project title is required for non-interactive create-bible.[/red]\n"
                "[dim]Pass a title, or run with --wizard on a TTY.[/dim]"
            )
            raise typer.Exit(2)

        chat_slug = resolve_chat_model_cli(chat_model)
        bible = build_production_bible(
            str(title).strip(),
            genre=genre,
            chat_model=chat_slug,
            video_model=video_model,
        )
        _persist_bible(bible, output)

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