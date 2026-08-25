"""Core studio status, agents, role cards, and Grok 4.6 stack CLI commands."""

from __future__ import annotations

import json

import typer
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from models import model_stack_summary

from cli.help_ia import collect_catalog, filter_catalog
from cli.dashboard import (
    build_studio_dashboard,
    dashboard_renderables,
    render_dashboard_json,
    render_studio_dashboard,
)
from cli.shared import (
    ACTIVATION_PHRASE,
    AGENTS,
    MASTER_PROMPT_DOC,
    MODEL_LAYER_DOC,
    MODELS_DOC,
    STUDIO_VERSION,
    console,
    core_agent_count,
    format_stack_panel,
    format_stack_table,
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
        """Show studio status and Grok 4.6 model stack."""
        stack = model_stack_summary()
        console.print(
            Panel.fit(
                f"[bold cyan]🎥 Grok Imagine Cinematic Studio v{STUDIO_VERSION}[/bold cyan]\n"
                "[green]Status:[/green] Enhanced CLI Active · Grok 4.6 orchestration\n"
                f"[green]Agents:[/green] {core_agent_count()} core + "
                f"{total_agent_count() - core_agent_count()} specialists\n"
                "[green]Role Cards:[/green] Loaded from references/agents/\n"
                f"[green]Activation:[/green] {ACTIVATION_PHRASE}\n"
                f"[dim]Docs: {MASTER_PROMPT_DOC} · {MODEL_LAYER_DOC} · {MODELS_DOC}[/dim]",
                title="Studio Status",
                border_style="cyan",
            )
        )
        console.print(format_stack_table(stack))

    @app.command()
    def version():
        """Show CLI and model stack version."""
        stack = model_stack_summary()
        console.print(
            f"[bold]cinematic-studio[/bold] v{STUDIO_VERSION} · "
            f"Grok [bold]4.6[/bold] cinematic+Build · "
            f"chat [green]{stack.get('xai_chat')}[/green] · "
            f"video [green]{stack.get('imagine_video')}[/green] · "
            f"CLI ≥ {stack.get('grok_build_cli_min_version', '1.0.5')} · August 2026"
        )

    @app.command("doctor")
    def doctor(
        quick: bool = typer.Option(
            False, "--quick", "-q", help="Skip pytest and full plugin verify"
        ),
        json_out: bool = typer.Option(False, "--json", help="Machine-readable JSON summary"),
        strict: bool = typer.Option(False, "--strict", help="Exit 1 on warnings"),
    ):
        """Grok Doctor — health check for Grok Build + Cinematic Studio."""
        from doctor import exit_code, format_human_report, report_to_dict, run_doctor

        report = run_doctor(quick=quick)
        if json_out:
            # Stable machine contract — plain JSON on stdout (no Rich chrome).
            print(json.dumps(report_to_dict(report), indent=2))
        else:
            console.print(format_human_report(report))
        raise typer.Exit(exit_code(report, strict=strict))

    @app.command(name="stack")
    def stack_cmd(
        json_output: bool = typer.Option(False, "--json", help="Emit model_stack JSON"),
    ):
        """Print the locked Grok 4.6 model stack and VIDEO_PIPELINE_SPEC."""
        stack = model_stack_summary()
        if json_output:
            import json

            from models import build_video_pipeline_spec

            console.print(
                json.dumps(
                    {
                        "studio_version": STUDIO_VERSION,
                        "model_stack": stack,
                        "video_pipeline_spec": build_video_pipeline_spec(
                            stack.get("imagine_video")
                        ),
                    },
                    indent=2,
                )
            )
            return
        console.print(format_stack_panel(stack))

    @app.command(name="list-agents")
    def list_agents():
        """List all agents grouped by category (Role Card labels · studio pin)."""
        table = Table(
            title=(
                f"🎬 Grok Imagine Cinematic Studio v{STUDIO_VERSION} — "
                f"{core_agent_count()} Core Agents · Grok 4.6"
            ),
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
            f"Total roster: {total_agent_count()} (incl. i2i + opt-in NSFW) · "
            f"Role Card labels may show v3.6.5; studio release is v{STUDIO_VERSION} · "
            f"orchestration default grok-4.6[/italic dim]"
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
        console.print(
            f"\n[green]Total Role Cards:[/green] {len(cards)} · "
            f"Model Layer: {MODEL_LAYER_DOC}"
        )

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
        console.print(
            Panel(
                Markdown(content[:3000]),
                title=f"📋 {card_path.stem}",
                border_style="blue",
                expand=False,
            )
        )

    @app.command()
    def activate():
        """Print the official Grok 4.6 activation command and stack."""
        console.print(
            Panel(
                f"[bold]{ACTIVATION_PHRASE}[/bold]\n\n"
                f"1. Paste [cyan]{MASTER_PROMPT_DOC}[/cyan] into a Grok 4.6 chat\n"
                "2. Run the activation phrase above\n"
                "3. Lock Bible with [cyan]create-bible[/cyan] / "
                "[cyan]create-bible --wizard[/cyan]\n"
                "4. Prefer still → i2v; video [green]1.0[/green] cost default · "
                "[green]1.5[/green] for native audio\n"
                f"5. Verify stack: [cyan]models verify[/cyan] · [cyan]stack[/cyan]\n\n"
                f"[dim]{MODEL_LAYER_DOC} · optional 1M: --chat-model grok-4.3[/dim]",
                title="🚀 Activation · Grok 4.6",
                border_style="magenta",
            )
        )
        console.print(format_stack_table())

    @app.command("commands")
    def commands_search(
        query: str = typer.Argument(
            "", help="Substring to match in command path or help text"
        ),
    ):
        """Search CLI command names and help text."""
        hits = filter_catalog(collect_catalog(app), query)
        if query.strip() and not hits:
            console.print(f"[yellow]No commands matching[/yellow] {query!r}")
            raise typer.Exit(1)
        table = Table(box=box.SIMPLE, show_header=True, header_style="bold")
        table.add_column("Command", style="cyan", overflow="fold")
        table.add_column("Summary", overflow="fold")
        for path, summary in hits:
            table.add_row(path, summary)
        console.print(table)
        console.print(f"[dim]{len(hits)} command(s)[/dim]")
