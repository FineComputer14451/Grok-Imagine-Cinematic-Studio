"""Generation Tracker CLI — image/video ledger."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.table import Table

from generation_tracker import (
    export_markdown,
    import_from_imagine_jobs,
    list_entries,
    log_generation,
    summarize,
    update_entry,
)

from cli.shared import console


def register(app: typer.Typer) -> None:
    gen_app = typer.Typer(help="Generation ledger — log image/video spend and artifacts")
    app.add_typer(gen_app, name="generation")

    @gen_app.command("log")
    def log_cmd(
        kind: Optional[str] = typer.Option(None, "--kind", "-k"),
        tool: Optional[str] = typer.Option(None, "--tool", "-t"),
        model: Optional[str] = typer.Option(None, "--model", "-m"),
        prompt: Optional[str] = typer.Option(None, "--prompt", "-p"),
        status: str = typer.Option("completed", "--status", "-s"),
        surface: str = typer.Option("grok_build_tools", "--surface"),
        duration: Optional[float] = typer.Option(None, "--duration", "-d"),
        aspect: Optional[str] = typer.Option(None, "--aspect"),
        artifact: Optional[str] = typer.Option(None, "--artifact", "-a"),
        job_id: Optional[str] = typer.Option(None, "--job-id"),
        shot_id: Optional[str] = typer.Option(None, "--shot-id"),
        sequence: Optional[str] = typer.Option(None, "--sequence"),
        character: Optional[str] = typer.Option(None, "--character"),
        project: Optional[str] = typer.Option(None, "--project"),
        note: str = typer.Option("", "--note", "-n"),
        credits_actual: Optional[float] = typer.Option(None, "--credits-actual"),
        images: int = typer.Option(1, "--images"),
        sync_quota: bool = typer.Option(False, "--sync-quota"),
    ):
        """Log a generation to the ledger."""
        if not kind and not tool:
            console.print("[red]Provide --kind or --tool[/red]")
            raise typer.Exit(1)
        entry = log_generation(
            kind=kind,
            tool=tool,
            model=model,
            prompt=prompt,
            status=status,
            surface=surface,
            duration_seconds=duration,
            aspect_ratio=aspect,
            artifact_path=artifact,
            job_id=job_id,
            shot_id=shot_id,
            sequence_slug=sequence,
            character_slug=character,
            project=project,
            note=note,
            credits_actual=credits_actual,
            image_count=images,
            sync_quota=sync_quota,
        )
        console.print(f"[green]✅ Logged[/green] {entry['entry_id']} · {entry['kind']} · "
                      f"{entry['credits_estimate']} cr est · {entry.get('status')}")

    @gen_app.command("list")
    def list_cmd(
        kind: Optional[str] = typer.Option(None, "--kind", "-k"),
        status: Optional[str] = typer.Option(None, "--status", "-s"),
        model: Optional[str] = typer.Option(None, "--model", "-m"),
        limit: int = typer.Option(20, "--limit", "-n"),
        json_out: bool = typer.Option(False, "--json"),
    ):
        """List recent ledger entries."""
        rows = list_entries(kind=kind, status=status, model=model, limit=limit)
        if json_out:
            console.print_json(json.dumps(rows))
            return
        table = Table(title="Generation Ledger")
        table.add_column("ID", style="cyan", max_width=28)
        table.add_column("Kind")
        table.add_column("Status")
        table.add_column("Cr est")
        table.add_column("Note / artifact", max_width=40)
        for e in rows:
            label = e.get("note") or e.get("artifact_path") or e.get("prompt_preview") or ""
            table.add_row(
                e.get("entry_id", "")[-22:],
                str(e.get("kind")),
                str(e.get("status")),
                str(e.get("credits_estimate")),
                str(label)[:40],
            )
        console.print(table)

    @gen_app.command("summary")
    def summary_cmd():
        """Aggregate ledger summary."""
        s = summarize()
        table = Table(title="📊 Generation Summary")
        table.add_column("Metric")
        table.add_column("Value")
        table.add_row("Entries", str(s["entry_count"]))
        table.add_row("Images (units)", str(s["image_count"]))
        table.add_row("Video seconds", str(s["video_seconds"]))
        table.add_row("Est. USD", f"${s['usd_estimate']}")
        table.add_row("Est. credits", str(s["credits_estimate"]))
        table.add_row("By kind", str(s["by_kind"]))
        table.add_row("By status", str(s["by_status"]))
        table.add_row("Ledger", s["ledger_file"])
        console.print(table)

    @gen_app.command("report")
    def report_cmd(
        output: Optional[Path] = typer.Option(None, "--output", "-o"),
        limit: int = typer.Option(50, "--limit", "-n"),
    ):
        """Markdown ledger report."""
        md = export_markdown(limit=limit)
        if output:
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(md, encoding="utf-8")
            console.print(f"[green]Wrote[/green] {output}")
        else:
            console.print(md)

    @gen_app.command("update")
    def update_cmd(
        entry_id: str = typer.Argument(...),
        status: Optional[str] = typer.Option(None, "--status", "-s"),
        artifact: Optional[str] = typer.Option(None, "--artifact", "-a"),
        credits_actual: Optional[float] = typer.Option(None, "--credits-actual"),
        note: Optional[str] = typer.Option(None, "--note", "-n"),
    ):
        """Update an existing ledger entry."""
        try:
            entry = update_entry(
                entry_id,
                status=status,
                artifact_path=artifact,
                credits_actual=credits_actual,
                note=note,
            )
        except KeyError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1)
        console.print(f"[green]Updated[/green] {entry['entry_id']}")

    @gen_app.command("import-jobs")
    def import_cmd(limit: int = typer.Option(100, "--limit", "-n")):
        """Import from Imagine jobs queue file if present."""
        result = import_from_imagine_jobs(limit=limit)
        console.print(result)
