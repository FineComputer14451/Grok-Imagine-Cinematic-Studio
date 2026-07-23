"""Quota optimizer CLI commands."""

from __future__ import annotations

import typer
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from models import DEFAULT_IMAGINE_VIDEO_MODEL
from quota_sync import (
    get_burn_rate_risk,
    ledger_recon_alignment,
    quota_sync_summary,
    reconcile_from_jobs,
    record_generation_spend,
)
from quota_optimizer import (
    SUBSCRIPTION_TIERS,
    estimate_clip_cost,
    estimate_production,
    estimate_sequence_cost,
    get_optimization_recommendations,
    quota_dashboard,
    record_spend,
    set_budget,
)
from cli.helpers import assess_risk_from_state, require_sequence
from cli.quota_display import print_production_estimate_table
from cli.shared import console

def register(app: typer.Typer) -> None:
    @app.command("estimate")
    def quota_estimate(
        duration: int = typer.Option(60, "--duration", "-d"),
        clips: int = typer.Option(None, "--clips", "-n"),
        clip_duration: float = typer.Option(10.0, "--clip-duration"),
        resolution: str = typer.Option("720p", "--resolution", "-r"),
        video_model: str = typer.Option(DEFAULT_IMAGINE_VIDEO_MODEL, "--video-model", "-m", help="Imagine video model slug or alias"),
        complexity: str = typer.Option("medium", "--complexity", "-c"),
        fast_mode: bool = typer.Option(False, "--fast-mode"),
        quality_pass: bool = typer.Option(False, "--quality-pass"),
        native_audio: bool = typer.Option(True, "--native-audio/--no-native-audio"),
        images: int = typer.Option(0, "--images", "-i"),
        agent_mode: str = typer.Option("standard", "--agents", help="minimal / standard / full_studio"),
    ):
        """Estimate production cost with xAI per-second Imagine pricing."""
        est = estimate_production(
            duration,
            clip_count=clips,
            avg_clip_duration=clip_duration,
            resolution=resolution,
            video_model=video_model,
            fast_mode=fast_mode,
            quality_pass=quality_pass,
            native_audio=native_audio,
            complexity=complexity,
            agent_mode=agent_mode,
            num_images=images,
        )
        risk = assess_risk_from_state(est)
        print_production_estimate_table(
            est,
            risk,
            title="💰 Quota Estimate — Imagine Video",
            duration=duration,
            resolution=resolution,
            fast_mode=fast_mode,
            quality_pass=quality_pass,
            video_model=video_model,
            table_box=box.ROUNDED,
            value_style="white",
        )

    @app.command("clip")
    def quota_clip(
        duration: float = typer.Argument(..., help="Clip duration in seconds"),
        resolution: str = typer.Option("720p", "--resolution", "-r"),
        video_model: str = typer.Option(DEFAULT_IMAGINE_VIDEO_MODEL, "--video-model", "-m"),
        fast_mode: bool = typer.Option(False, "--fast-mode"),
        quality_pass: bool = typer.Option(False, "--quality-pass"),
    ):
        """Estimate cost for a single Imagine video clip."""
        est = estimate_clip_cost(
            duration,
            resolution=resolution,
            video_model=video_model,
            fast_mode=fast_mode,
            quality_pass=quality_pass,
        )
        console.print(Panel(
            f"Model: {est.get('video_model', video_model)} (${est.get('usd_per_second', '?')}/sec)\n"
            f"Duration: {duration}s @ {resolution}\n"
            f"Credits: {est['credits_low']} – {est['credits_high']}\n"
            f"USD: ${est['usd_low']} – ${est['usd_high']}",
            title="Single Clip Estimate",
            border_style="cyan",
        ))

    @app.command("sequence")
    def quota_sequence(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        fast_mode: bool = typer.Option(False, "--fast-mode"),
        quality_pass: bool = typer.Option(False, "--quality-pass"),
    ):
        """Estimate quota cost for an existing sequence blueprint."""
        seq = require_sequence(name)
        est = estimate_sequence_cost(seq.get("clips", []), fast_mode=fast_mode, quality_pass=quality_pass)
        risk = assess_risk_from_state(est)
        recs = get_optimization_recommendations({**est, "clip_count": est["clip_count"], "fast_mode": fast_mode}, risk=risk)

        table = Table(title=f"💰 Sequence Cost — {seq['sequence_name']}", box=box.SIMPLE)
        table.add_column("Clip", style="cyan")
        table.add_column("Duration", style="white")
        table.add_column("Credits", style="green")
        for pc in est.get("per_clip", []):
            table.add_row(pc.get("clip_id", "?"), f"{pc['duration_seconds']}s", f"{pc['credits_low']}–{pc['credits_high']}")
        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {est['credits_low']}–{est['credits_high']} credits (${est['usd_low']}–${est['usd_high']})")
        console.print(f"[bold]Risk:[/bold] {risk['risk_level']} ({risk.get('budget_pct_used', 'N/A')}% of budget)")
        if recs:
            console.print("\n[bold]Recommendations:[/bold]")
            for r in recs[:3]:
                console.print(f"  [{r['priority']}] {r['action']} — {r['savings']}")

    @app.command("dashboard")
    def quota_dash():
        """Show session quota dashboard."""
        dash = quota_dashboard()
        table = Table(title="📊 Quota Dashboard", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Tier", dash["tier_label"])
        table.add_row("Session Spent", f"{dash['session_spent']} credits")
        table.add_row("Generations", str(dash["session_generations"]))
        if dash["budget_remaining"] is not None:
            table.add_row("Budget Remaining", f"{dash['budget_remaining']} credits")
        if dash["budget_pct_used"] is not None:
            table.add_row("Session % of Budget", f"{dash['budget_pct_used']}%")
        console.print(table)
        if dash.get("recent_history"):
            console.print("\n[dim]Recent:[/dim]")
            for h in dash["recent_history"]:
                console.print(f"  {h['at']}: {h['credits']} credits — {h.get('note', '')}")

    @app.command("budget")
    def quota_budget_cmd(
        tier: str = typer.Option("supergrok_pro", "--tier", "-t", help="supergrok_pro / supergrok_heavy / custom"),
        remaining: float = typer.Option(None, "--remaining", "-r", help="Remaining credits"),
    ):
        """Set subscription tier and budget."""
        if tier not in SUBSCRIPTION_TIERS:
            console.print(f"[red]Unknown tier. Choose:[/red] {', '.join(SUBSCRIPTION_TIERS)}")
            raise typer.Exit(1)
        quota = set_budget(tier=tier, remaining=remaining)
        label = SUBSCRIPTION_TIERS[tier]["label"]
        console.print(f"[green]✅ Budget set:[/green] {label}")
        if quota.get("budget_remaining") is not None:
            console.print(f"[dim]Remaining: {quota['budget_remaining']} credits[/dim]")

    @app.command("record")
    def quota_record(
        credits: float = typer.Argument(..., help="Credits spent"),
        note: str = typer.Option("", "--note", "-n"),
    ):
        """Record generation spend to session tracker."""
        quota = record_spend(credits, note=note)
        console.print(f"[green]✅ Recorded {credits} credits[/green] (session total: {quota['session_spent']})")
        if quota.get("budget_remaining") is not None:
            console.print(f"[dim]Remaining: {quota['budget_remaining']} credits[/dim]")

    @app.command("optimize")
    def quota_optimize(
        duration: int = typer.Option(60, "--duration", "-d"),
        clips: int = typer.Option(None, "--clips", "-n"),
        fast_mode: bool = typer.Option(False, "--fast-mode"),
        complexity: str = typer.Option("medium", "--complexity", "-c"),
    ):
        """Get quota optimization recommendations for a production plan."""
        est = estimate_production(duration, clip_count=clips, complexity=complexity, fast_mode=fast_mode)
        risk = assess_risk_from_state(est)
        recs = get_optimization_recommendations(est, risk=risk)

        console.print(Panel(
            f"Estimate: {est['credits_low']}–{est['credits_high']} credits (${est['usd_low']}–${est['usd_high']})\n"
            f"Risk: {risk['risk_level']} ({risk.get('budget_pct_used', 'N/A')}% of budget)",
            title="Optimization Analysis",
            border_style="yellow",
        ))
        for r in recs:
            color = {"critical": "red", "high": "yellow", "medium": "cyan", "low": "dim"}.get(r["priority"], "white")
            console.print(f"  [{color}][{r['priority']}][/{color}] {r['action']}")
            console.print(f"    [dim]Savings: {r['savings']}[/dim]")
        console.print(f"\n[dim]Burn-rate risk (reconciliation): {get_burn_rate_risk()}[/dim]")


    @app.command("sync")
    def quota_sync_cmd(
        json_output: bool = typer.Option(False, "--json", help="Emit JSON summary"),
        show_entries: bool = typer.Option(
            False, "--entries", help="List recon entry notes (source-tagged)"
        ),
    ):
        """Reconcile estimated vs actual spend (exclusive cascade: ledger → jobs → history)."""
        recon = reconcile_from_jobs()
        summary = quota_sync_summary()
        # Read-only alignment vs billable ledger (same helper as Grok Doctor)
        align = ledger_recon_alignment()
        if json_output:
            import json

            payload = {
                **summary,
                "alignment": {
                    "status": align.get("status"),
                    "hint": align.get("hint"),
                    "est_delta": align.get("est_delta"),
                    "act_delta": align.get("act_delta"),
                    "ledger": align.get("ledger"),
                },
                "entries": recon.get("entries") or [],
            }
            console.print(json.dumps(payload, indent=2))
            return

        cascade = summary.get("cascade_source") or "none"
        cascade_labels = {
            "generation_ledger": "generation_ledger (primary)",
            "imagine_jobs_actuals": "imagine_jobs (fallback)",
            "history_est": "history est:N (fallback)",
            "record_spend": "record_spend (incremental)",
            "mixed": "mixed (run quota sync to rebuild)",
            "none": "none (empty)",
        }
        risk = summary.get("risk_level") or "low"
        risk_style = {
            "low": "green",
            "medium": "yellow",
            "high": "red",
            "critical": "bold red",
        }.get(risk, "white")
        align_status = align.get("status") or "idle"
        align_style = {
            "aligned": "green",
            "idle": "dim",
            "mismatch": "red",
            "stale": "yellow",
            "orphan_recon": "yellow",
            "mixed": "yellow",
        }.get(align_status, "white")
        align_detail = align.get("hint") or align_status
        if align_status in ("aligned", "idle"):
            align_cell = f"[{align_style}]{align_status}[/{align_style}]"
        else:
            align_cell = f"[{align_style}]{align_status}[/{align_style}] — {align_detail}"

        table = Table(title="Quota Reconciliation", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value")
        table.add_row("Cascade source", cascade_labels.get(cascade, cascade))
        table.add_row("Sources", ", ".join(summary.get("sources") or []) or "—")
        table.add_row("Ledger alignment", align_cell)
        table.add_row("Estimated total", f"{summary['estimated_total']} credits")
        table.add_row("Actual total", f"{summary['actual_total']} credits")
        table.add_row("Variance", f"{summary['variance_pct']}%")
        table.add_row("Burn rate", f"{summary['burn_rate_multiplier']}x")
        table.add_row("Risk level", f"[{risk_style}]{risk}[/{risk_style}]")
        table.add_row("Entries", str(summary["entry_count"]))
        console.print(table)
        console.print(
            f"[dim]Exclusive cascade: ledger → jobs (actuals) → history · "
            f"Updated: {recon.get('updated_at')}[/dim]"
        )

        entries = recon.get("entries") or []
        if show_entries and entries:
            et = Table(title="Recon entries", box=box.SIMPLE)
            et.add_column("Source", style="cyan")
            et.add_column("Est", justify="right")
            et.add_column("Act", justify="right")
            et.add_column("Δ", justify="right")
            et.add_column("Note")
            for e in entries[:50]:
                et.add_row(
                    str(e.get("source") or "—"),
                    str(e.get("estimated_credits", "")),
                    str(e.get("actual_credits", "")),
                    str(e.get("variance_credits", "")),
                    str(e.get("note") or "")[:72],
                )
            console.print(et)
            if len(entries) > 50:
                console.print(f"[dim]… {len(entries) - 50} more (use --json for full)[/dim]")
        elif entries and not show_entries:
            console.print(
                f"[dim]{len(entries)} entry(ies) · pass --entries to list notes[/dim]"
            )


    @app.command("reconcile")
    def quota_reconcile(
        estimated: float = typer.Option(..., "--estimated", "-e"),
        actual: float = typer.Option(..., "--actual", "-a"),
        note: str = typer.Option("", "--note", "-n"),
    ):
        """Record estimated vs actual credits for a single generation."""
        result = record_generation_spend(actual, estimated_credits=estimated, note=note)
        entry = result["entry"]
        console.print(
            f"[green]Recorded[/green] est={entry['estimated_credits']} actual={entry['actual_credits']} "
            f"variance={entry['variance_credits']} | burn risk={result['reconciliation']['risk_level']}"
        )
