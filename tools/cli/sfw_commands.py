"""SFW batch orchestrator CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from quality_pass_scheduler import apply_quality_pass_promotion, get_pending_quality_passes
from sfw_orchestrator import (
    batch_to_markdown,
    build_shot_context,
    decide_generation_mode,
    get_next_shots,
    list_batches,
    load_batch,
    parse_inline_shot,
    plan_batch,
    record_shot_result,
    save_batch,
    suggest_retry,
)
from project_state import load_project_state

from cli.shared import console


def register(app: typer.Typer) -> None:
    @app.command("plan")
    def sfw_plan(
        title: str = typer.Argument(..., help="Batch title"),
        file: str = typer.Option(None, "--file", "-f", help="JSON shot list"),
        shot: list[str] = typer.Option(None, "--shot", "-s", help="Inline: tier:description or tier:motion:description"),
        budget: float = typer.Option(None, "--budget", "-b", help="Session budget in credits"),
        tier: str = typer.Option("supergrok_pro", "--tier", "-t"),
        fast_mode: bool = typer.Option(False, "--fast-mode"),
        two_pass: bool = typer.Option(False, "--two-pass", help="Enable fast→hero quality pass scheduler"),
        output: str = typer.Option(None, "--output", "-o", help="Save markdown plan"),
    ):
        """Plan a prioritized SFW batch under quota limits."""
        shots: list[dict] = []
        if file:
            shots = json.loads(Path(file).read_text())
        if shot:
            for spec in shot:
                shots.append(parse_inline_shot(spec))
        if not shots:
            console.print("[red]Provide --file or at least one --shot[/red]")
            raise typer.Exit(1)

        batch = plan_batch(title, shots, tier=tier, budget_credits=budget, fast_mode=fast_mode, two_pass=two_pass)
        path = save_batch(batch)
        md = batch_to_markdown(batch)

        table = Table(title=f"SFW Batch — {title}", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Batch ID", batch["batch_id"])
        table.add_row("Budget", f"{batch['budget_credits']} credits")
        table.add_row("Scheduled", f"{batch['shots_scheduled']}/{batch['shots_total']} shots")
        table.add_row("Credits", f"{batch['scheduled_credits']} (+{batch['retry_reserve_credits']} reserve)")
        table.add_row("Risk", batch["risk"]["risk_level"])
        table.add_row("Saved", str(path))
        console.print(table)

        if output:
            Path(output).write_text(md)
            console.print(f"[green]Plan written:[/green] {output}")
        else:
            console.print(Markdown(md))


    @app.command("list")
    def sfw_list():
        """List SFW production batches."""
        batches = list_batches()
        if not batches:
            console.print("[dim]No SFW batches yet.[/dim]")
            return
        table = Table(title="SFW Batches", box=box.SIMPLE)
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Status", style="green")
        table.add_column("Path", style="dim")
        for b in batches:
            table.add_row(b["batch_id"], b.get("title", ""), b.get("status", ""), b.get("path", ""))
        console.print(table)


    @app.command("next")
    def sfw_next(
        batch_name: str = typer.Argument(..., help="Batch slug or ID"),
        count: int = typer.Option(3, "--count", "-n"),
    ):
        """Get next priority shots with mode decisions and cost estimates."""
        batch = load_batch(batch_name)
        shots = get_next_shots(batch, count=count)
        if not shots:
            console.print("[yellow]No pending shots in batch.[/yellow]")
            return

        table = Table(title=f"Next Shots — {batch['title']}", box=box.ROUNDED)
        table.add_column("#", style="dim")
        table.add_column("Shot", style="cyan")
        table.add_column("Tier", style="magenta")
        table.add_column("Mode", style="green")
        table.add_column("Credits", style="yellow")
        table.add_column("Description", style="white", max_width=40)
        for i, s in enumerate(shots, 1):
            table.add_row(
                str(i),
                s["shot_id"],
                s.get("tier", ""),
                s.get("decision", {}).get("mode", s.get("recommended_mode", "")),
                str(s.get("cost_estimate", {}).get("credits", "?")),
                (s.get("description", "")[:40] + "...") if len(s.get("description", "")) > 40 else s.get("description", ""),
            )
        console.print(table)


    @app.command("decide")
    def sfw_decide(
        shot_id: str = typer.Argument(..., help="Shot ID for decision context"),
        shot_tier: str = typer.Option("coverage", "--tier"),
        motion: str = typer.Option("medium", "--motion", help="low / medium / high"),
        has_ref: bool = typer.Option(False, "--has-ref", help="Approved reference image exists"),
        duration: float = typer.Option(10.0, "--duration", "-d"),
    ):
        """Recommend image_prompt vs image_to_video vs video_prompt."""
        shot = build_shot_context(
            shot_id,
            tier=shot_tier,
            motion=motion,
            has_ref=has_ref,
            duration=duration,
        )
        state = load_project_state()
        quota = state.get("quota", {})
        decision = decide_generation_mode(
            shot,
            budget_remaining=quota.get("budget_remaining"),
        )

        console.print(Panel(
            f"Shot: {shot_id}\n"
            f"Mode: [bold green]{decision['mode']}[/bold green] (confidence {decision['confidence']:.0%})\n"
            f"Reasons:\n" + "\n".join(f"  • {r}" for r in decision["reasons"]) +
            (f"\nFollow-up: {decision['follow_up']}" if decision.get("follow_up") else ""),
            title="SFW I2V Decision",
            border_style="cyan",
        ))


    @app.command("record")
    def sfw_record(
        batch_name: str = typer.Argument(..., help="Batch slug or ID"),
        shot_id: str = typer.Argument(..., help="Shot ID"),
        score: float = typer.Option(..., "--score", help="QA quality score 1-10"),
        credits: float = typer.Option(..., "--credits", help="Credits spent"),
        failure_reason: str = typer.Option(None, "--reason", help="Failure reason if QA fail"),
        notes: str = typer.Option("", "--note", "-n"),
    ):
        """Record shot result — updates batch and quota tracker."""
        batch = load_batch(batch_name)
        result = record_shot_result(
            batch, shot_id,
            quality_score=score,
            credits_spent=credits,
            failure_reason=failure_reason,
            notes=notes,
        )
        status = "[green]PASS[/green]" if result["qa_pass"] else "[red]FAIL[/red]"
        console.print(f"{status} {shot_id} — score {score}/10, {credits} credits")


    @app.command("promote")
    def sfw_promote(
        batch_name: str = typer.Argument(..., help="Batch slug or ID"),
        shot_id: str = typer.Argument(..., help="Shot with pending quality pass"),
    ):
        """Apply quality pass promotion (pass 1 → pass 2 hero models)."""
        batch = load_batch(batch_name)
        shot = None
        for s in batch.get("shots", []):
            if s["shot_id"] == shot_id:
                shot = s
                break
        if not shot:
            console.print(f"[red]Shot not found:[/red] {shot_id}")
            raise typer.Exit(1)
        try:
            apply_quality_pass_promotion(shot)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        save_batch(batch)
        console.print(Panel(
            f"Shot: {shot_id}\n"
            f"Pass: 2\n"
            f"Video: {shot['video_model']}\n"
            f"Mode: {shot.get('recommended_mode')}",
            title="Quality Pass Applied",
            border_style="green",
        ))


    @app.command("quality-pending")
    def sfw_quality_pending(batch_name: str = typer.Argument(...)):
        """List shots awaiting quality pass (pass 2)."""
        batch = load_batch(batch_name)
        pending = get_pending_quality_passes(batch)
        if not pending:
            console.print("[dim]No pending quality passes.[/dim]")
            return
        for s in pending:
            plan = s.get("quality_pass_plan", {})
            console.print(f"  {s['shot_id']} — est. +{plan.get('estimated_extra_credits', '?')} cr")


    @app.command("retry")
    def sfw_retry(
        shot_id: str = typer.Argument(..., help="Failed shot ID"),
        reason: str = typer.Option("physics_failure", "--reason", "-r"),
        score: float = typer.Option(None, "--score"),
        attempts: int = typer.Option(0, "--attempts"),
        shot_tier: str = typer.Option("story_beat", "--tier"),
    ):
        """Suggest retry strategy after insufficient quality."""
        shot = build_shot_context(shot_id, tier=shot_tier, recommended_mode="image_to_video")
        plan = suggest_retry(shot, failure_reason=reason, quality_score=score, attempts=attempts)
        color = "green" if plan["action"] == "retry" else "yellow"
        console.print(Panel(
            f"Action: [{color}]{plan['action']}[/{color}]\n"
            f"Failure: {plan.get('failure_reason', reason)}\n"
            f"Extra credits est.: {plan.get('estimated_extra_credits', 0)}\n\n"
            f"Suggestions:\n" + "\n".join(f"  • {a}" for a in plan.get("suggestions", [])),
            title=f"Retry Plan — {shot_id}",
            border_style="yellow",
        ))