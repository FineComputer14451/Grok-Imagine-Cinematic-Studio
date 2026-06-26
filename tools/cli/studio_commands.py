"""Core studio status, agents, and role card CLI commands."""

from __future__ import annotations

from datetime import datetime

import typer
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from models import model_stack_summary

from cli.dashboard import (
    build_studio_dashboard,
    dashboard_renderables,
    render_dashboard_json,
    render_studio_dashboard,
)
from cli.shared import (
    AGENTS,
    STUDIO_VERSION,
    console,
    core_agent_count,
    get_role_card_path,
    list_role_card_files,
    total_agent_count,
)


def register(app: typer.Typer) -> None:
    """Register studio overview commands on the root CLI app."""

    @app.command()
    def dashboard(
        json_output: bool = typer.Option(False, "--json", help="Emit machine-readable JSON"),
        compact: bool = typer.Option(False, "--compact", "-c", help="Summary panels only"),
        watch: bool = typer.Option(False, "--watch", "-w", help="Live refresh"),
        interval: float = typer.Option(5.0, "--interval", "-i", help="Refresh seconds (--watch)"),
    ):
        """Unified studio dashboard — health, quota, sequences, DNA, and batches."""
        if watch:
            import time

            from rich.live import Live

            with Live(console=console, refresh_per_second=4, screen=False) as live:
                while True:
                    snapshot = build_studio_dashboard()
                    if json_output:
                        import json

                        live.update(json.dumps(snapshot, indent=2))
                    else:
                        live.update(dashboard_renderables(snapshot, compact=compact))
                    time.sleep(max(1.0, interval))
        else:
            snapshot = build_studio_dashboard()
            if json_output:
                render_dashboard_json(snapshot)
            else:
                render_studio_dashboard(snapshot, compact=compact)

    @app.command()
    def status():
        """Show current studio status"""
        stack = model_stack_summary()
        console.print(Panel.fit(
            f"[bold cyan]🎥 Grok Imagine Cinematic Studio v{STUDIO_VERSION}[/bold cyan]\n"
            "[green]Status:[/green] Enhanced CLI Active\n"
            f"[green]Agents:[/green] {core_agent_count()} core + {total_agent_count() - core_agent_count()} specialists\n"
            "[green]Role Cards:[/green] Loaded from references/agents/\n"
            "[green]Mode:[/green] Production Ready\n\n"
            "[bold]Model Stack[/bold]\n"
            f"  Grok Build CLI: {stack['grok_build_cli_default']} (+ fork {stack['grok_build_cli_fork']})\n"
            f"  xAI Chat: {stack['xai_chat']} | Build API: {stack['xai_build']}\n"
            f"  Imagine Video: {stack['imagine_video']} | Image: {stack['imagine_image']}",
            title="Studio Status",
            border_style="cyan",
        ))

    @app.command()
    def version():
        """Show CLI version"""
        console.print(f"[bold]cinematic-studio[/bold] v{STUDIO_VERSION} (June 2026)")

    @app.command(name="list-agents")
    def list_agents():
        """List all agents grouped by category"""
        table = Table(
            title=f"🎬 Grok Imagine Cinematic Studio — {core_agent_count()} Core Agents",
            box=box.ROUNDED,
        )
        table.add_column("Category", style="bold cyan", no_wrap=True)
        table.add_column("Agents", style="white")

        for category, agents in AGENTS.items():
            agent_list = "\n".join([f"• {a}" for a in agents])
            table.add_row(category, agent_list)

        console.print(table)
        console.print(
            f"\n[italic dim]Core: {core_agent_count()} · "
            f"Total roster: {total_agent_count()} (incl. i2i + opt-in NSFW)[/italic dim]"
        )

    @app.command(name="list-role-cards")
    def list_role_cards():
        """List all available Role Cards in references/agents/"""
        from cli.shared import AGENTS_DIR

        if not AGENTS_DIR.exists():
            console.print("[red]references/agents/ directory not found[/red]")
            return

        cards = list_role_card_files()
        table = Table(title="📋 Available Role Cards", box=box.SIMPLE)
        table.add_column("Role Card", style="cyan")
        table.add_column("File", style="dim")

        for card in cards:
            table.add_row(card.stem.replace("_", " "), str(card))

        console.print(table)
        console.print(f"\n[green]Total Role Cards:[/green] {len(cards)}")

    @app.command(name="show-role-card")
    def show_role_card(
        agent: str = typer.Argument(..., help="Agent name (partial match OK)"),
    ):
        """Display a Role Card from references/agents/"""
        card_path = get_role_card_path(agent)
        if not card_path or not card_path.exists():
            console.print(f"[red]Role Card not found for:[/red] {agent}")
            return

        content = card_path.read_text()
        console.print(Panel(Markdown(content[:3000]), title=f"📋 {card_path.stem}", border_style="blue", expand=False))

    @app.command()
    def activate():
        """Print the official activation command"""
        console.print(Panel(
            f"[bold]Activate Grok Imagine Cinematic Studio v{STUDIO_VERSION}[/bold]\n\n"
            "Load the master prompt first, then paste the activation command.",
            title="🚀 Activation",
            border_style="magenta",
        ))