"""Production Bible, activation prompt, and memory CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import box
from rich.panel import Panel
from rich.table import Table

from models import DEFAULT_IMAGINE_VIDEO_MODEL, DEFAULT_XAI_CHAT_MODEL, resolve_video_model
from project_state import load_project_state, save_project_state
from quota_optimizer import assess_budget_risk, estimate_production

from cli.production import build_activation_prompt, build_production_bible
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
        """Generate a high-quality ready-to-paste prompt"""
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
        """Estimate generation cost and quota usage (delegates to quota optimizer)"""
        video_slug = resolve_video_model(video_model)
        estimate = estimate_production(
            duration,
            clip_count=clips,
            complexity=complexity,
            fast_mode=fast_mode,
            video_model=video_slug,
        )
        state = load_project_state()
        quota = state.get("quota", {})
        risk = assess_budget_risk(
            estimate,
            tier=quota.get("tier", "supergrok_pro"),
            budget_remaining=quota.get("budget_remaining"),
        )
        table = Table(title="💰 Production Cost Estimate (1.5 per-second)", box=box.SIMPLE)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="bold green")
        table.add_row("Duration", f"{duration}s")
        table.add_row("Video Model", estimate.get("video_model", video_slug))
        table.add_row("Clips", str(estimate["clip_count"]))
        table.add_row("Complexity", complexity.title())
        table.add_row("Credits", f"{estimate['credits_low']} – {estimate['credits_high']}")
        table.add_row("Est. USD", f"${estimate['usd_low']} – ${estimate['usd_high']}")
        table.add_row("Est. Tokens", f"~{estimate['estimated_tokens']:,}")
        table.add_row("Risk", f"[{risk['risk_level']}]{risk['risk_level']}[/]")
        console.print(table)
        console.print("[dim]Use 'quota optimize' for savings recommendations[/dim]")

    @app.command(name="create-bible")
    def create_bible(
        title: str = typer.Argument(..., help="Project title"),
        genre: str = typer.Option("Cinematic", "--genre", "-g"),
        chat_model: str = typer.Option(DEFAULT_XAI_CHAT_MODEL, "--chat-model", help="xAI chat model (grok-4.3, grok-build-0.1)"),
        video_model: str = typer.Option(DEFAULT_IMAGINE_VIDEO_MODEL, "--video-model", "-m", help="Imagine video model slug or alias"),
        output: str = typer.Option("production_bible.json", "--output", "-o"),
    ):
        """Generate a rich, structured Production Bible"""
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

    @app.command()
    def memory(
        action: str = typer.Argument(..., help="add / list / load"),
        name: str = typer.Option(None, "--name", "-n", help="Character or variable name"),
        value: str = typer.Option(None, "--value", "-v", help="Value to store"),
    ):
        """Manage project memory and character DNA"""
        state = load_project_state()

        if action == "add":
            if not name or not value:
                console.print("[red]Please provide --name and --value[/red]")
                return
            state["characters"][name] = value
            save_project_state(state)
            console.print(f"[green]✅ Saved memory for[/green] {name}")

        elif action == "list":
            if not state.get("characters"):
                console.print("[yellow]No memory entries yet[/yellow]")
                return
            table = Table(title="🧠 Project Memory")
            table.add_column("Name", style="cyan")
            table.add_column("Value", style="white")
            for k, v in state["characters"].items():
                table.add_row(k, str(v)[:80])
            console.print(table)

        elif action == "load":
            if name and name in state.get("characters", {}):
                console.print(Panel(state["characters"][name], title=f"Memory: {name}"))
            else:
                console.print("[yellow]Memory entry not found[/yellow]")

        else:
            console.print("[red]Unknown action. Use: add / list / load[/red]")