"""Animatic Director CLI — pre-vis boards and hero promotion."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from animatic_orchestrator import (
    animatic_to_markdown,
    list_animatics,
    load_animatic,
    parse_beat_line,
    plan_animatic,
    promote_frame,
    save_animatic,
)

from cli.shared import console


def register(app: typer.Typer) -> None:
    @app.command("plan")
    def animatic_plan(
        title: str = typer.Argument(..., help="Animatic board title"),
        beat: list[str] = typer.Option(None, "--beat", "-b", help="tier:description:seconds or description:seconds"),
        file: str = typer.Option(None, "--file", "-f", help="JSON beat list"),
        duration: int = typer.Option(60, "--duration", "-d"),
        output: str = typer.Option(None, "--output", "-o"),
    ):
        """Plan low-cost animatic board before hero 1.5 spend."""
        beats: list = []
        if file:
            beats = json.loads(Path(file).read_text())
        if beat:
            beats.extend(beat)
        if not beats:
            console.print("[red]Provide --beat or --file[/red]")
            raise typer.Exit(1)

        board = plan_animatic(title, beats, target_duration=duration)
        path = save_animatic(board)
        md = animatic_to_markdown(board)
        est = board["cost_estimate"]

        table = Table(title=f"Animatic — {title}", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value")
        table.add_row("Frames", str(board["frame_count"]))
        table.add_row("Animatic credits", f"{est['animatic_credits']} cr")
        table.add_row("% of full est.", f"{est['animatic_pct_of_full']}%")
        table.add_row("Within budget", "yes" if est["within_budget"] else "no")
        table.add_row("Saved", str(path))
        console.print(table)

        if output:
            Path(output).write_text(md)
        else:
            console.print(Markdown(md))


    @app.command("list")
    def animatic_list():
        """List animatic boards."""
        boards = list_animatics()
        if not boards:
            console.print("[dim]No animatic boards yet.[/dim]")
            return
        table = Table(title="Animatic Boards", box=box.SIMPLE)
        table.add_column("Slug", style="cyan")
        table.add_column("Title")
        table.add_column("Frames", justify="right")
        table.add_column("Status")
        for b in boards:
            table.add_row(b["slug"], b.get("title", ""), str(b.get("frame_count", "")), b.get("status", ""))
        console.print(table)


    @app.command("show")
    def animatic_show(name: str = typer.Argument(..., help="Board slug or title")):
        """Show animatic board."""
        board = load_animatic(name)
        console.print(Panel(Markdown(animatic_to_markdown(board)[:4000]), title=board["title"], border_style="cyan"))


    @app.command("promote")
    def animatic_promote(
        name: str = typer.Argument(..., help="Board slug or title"),
        frame: str = typer.Option(..., "--frame", "-f"),
        tier: str = typer.Option("hero", "--tier", "-t", help="draft | standard | hero"),
        score: float = typer.Option(None, "--score", help="QA score that triggered promotion"),
    ):
        """Promote animatic frame to higher asset tier."""
        board = load_animatic(name)
        try:
            promoted = promote_frame(board, frame, to_tier=tier, qa_score=score)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        save_animatic(board)
        console.print(Panel(
            f"Frame: {promoted['frame_id']}\n"
            f"Tier: {promoted.get('promoted_from')} → [bold]{promoted['tier']}[/bold]\n"
            f"Image: {promoted['image_model']}\n"
            f"Video: {promoted['video_model']}\n"
            f"Anchors: {', '.join(board.get('locked_anchors', [])) or '—'}",
            title="Promoted",
            border_style="green",
        ))