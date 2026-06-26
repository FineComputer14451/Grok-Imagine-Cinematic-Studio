"""NSFW orchestrator and sequence extender CLI commands."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import typer
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from models import DEFAULT_IMAGINE_VIDEO_MODEL
from batch_runner import execute_nsfw_shot
from quality_pass_scheduler import apply_quality_pass_promotion, get_pending_quality_passes
from session_runner import run_batch_session
from nsfw_orchestrator import (
    batch_to_markdown,
    build_shot_context,
    decide_generation_mode,
    generate_daily_report,
    get_next_shots,
    list_batches,
    load_batch,
    parse_inline_shot,
    plan_batch,
    record_shot_result,
    save_batch,
    suggest_retry,
)
from nsfw_sequence_extender import (
    TENSION_PROFILES,
    build_nsfw_extend_prompt,
    build_prompt_chain,
    evaluate_nsfw_chain_qa,
    nsfw_sequence_to_markdown,
    plan_nsfw_extension,
    run_nsfw_chain_qa_scaffold,
    save_nsfw_sequence,
    suggest_camera_pacing,
)
from project_state import load_project_state
from sequence_chain import get_clip

from cli.helpers import require_clip, require_sequence
from cli.shared import AGENTS_DIR, STUDIO_ROOT, console


def register(nsfw_app: typer.Typer, extend_app: typer.Typer) -> None:
    @nsfw_app.command("plan")
    def nsfw_plan(
        title: str = typer.Argument(..., help="Batch title"),
        file: str = typer.Option(None, "--file", "-f", help="JSON shot list"),
        shot: list[str] = typer.Option(None, "--shot", "-s", help="Inline shot: tier:description or tier:motion:description"),
        budget: float = typer.Option(None, "--budget", "-b", help="Session budget in credits"),
        tier: str = typer.Option("supergrok_heavy", "--tier", "-t"),
        fast_mode: bool = typer.Option(False, "--fast-mode"),
        two_pass: bool = typer.Option(False, "--two-pass", help="Enable fast→hero quality pass scheduler"),
        output: str = typer.Option(None, "--output", "-o", help="Save markdown plan"),
    ):
        """Plan a prioritized NSFW batch under Heavy subscription limits."""
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

        table = Table(title=f"🔞 NSFW Batch — {title}", box=box.ROUNDED)
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


    @nsfw_app.command("list")
    def nsfw_list():
        """List NSFW production batches."""
        batches = list_batches()
        if not batches:
            console.print("[dim]No NSFW batches yet.[/dim]")
            return
        table = Table(title="🔞 NSFW Batches", box=box.SIMPLE)
        table.add_column("ID", style="cyan")
        table.add_column("Title", style="white")
        table.add_column("Status", style="green")
        table.add_column("Path", style="dim")
        for b in batches:
            table.add_row(b["batch_id"], b.get("title", ""), b.get("status", ""), b.get("path", ""))
        console.print(table)


    @nsfw_app.command("next")
    def nsfw_next(
        batch_name: str = typer.Argument(..., help="Batch slug or ID"),
        count: int = typer.Option(3, "--count", "-n"),
    ):
        """Get next priority shots with mode decisions and cost estimates."""
        batch = load_batch(batch_name)
        shots = get_next_shots(batch, count=count)
        if not shots:
            console.print("[yellow]No pending shots in batch.[/yellow]")
            return

        table = Table(title=f"▶ Next Shots — {batch['title']}", box=box.ROUNDED)
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
        for s in shots:
            reasons = s.get("decision", {}).get("reasons", [])
            if reasons:
                console.print(f"  [dim]{s['shot_id']}:[/dim] {reasons[0]}")


    @nsfw_app.command("decide")
    def nsfw_decide(
        shot_id: str = typer.Argument(..., help="Shot ID for decision context"),
        shot_tier: str = typer.Option("support", "--tier", help="Shot tier"),
        motion: str = typer.Option("medium", "--motion", help="low / medium / high"),
        has_ref: bool = typer.Option(False, "--has-ref", help="Approved reference image exists"),
        explicit: str = typer.Option("moderate", "--explicit", help="suggestive / moderate / explicit"),
        duration: float = typer.Option(10.0, "--duration", "-d"),
    ):
        """Recommend image_prompt vs image_to_video vs video_prompt."""
        shot = build_shot_context(
            shot_id,
            tier=shot_tier,
            motion=motion,
            has_ref=has_ref,
            explicit=explicit,
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
            title="I2V Decision",
            border_style="magenta",
        ))


    @nsfw_app.command("retry")
    def nsfw_retry(
        shot_id: str = typer.Argument(..., help="Failed shot ID"),
        reason: str = typer.Option("physics_failure", "--reason", "-r", help="Failure reason key"),
        score: float = typer.Option(None, "--score", help="QA score received"),
        attempts: int = typer.Option(0, "--attempts", help="Prior attempt count"),
        shot_tier: str = typer.Option("key_explicit", "--tier"),
    ):
        """Suggest retry strategy after insufficient quality."""
        shot = build_shot_context(
            shot_id,
            tier=shot_tier,
            recommended_mode="image_to_video",
        )
        plan = suggest_retry(shot, failure_reason=reason, quality_score=score, attempts=attempts)

        color = "green" if plan["action"] == "retry" else "yellow"
        console.print(Panel(
            f"Action: [{color}]{plan['action']}[/{color}]\n"
            f"Failure: {plan.get('failure_reason', reason)}\n"
            f"Extra credits est.: {plan.get('estimated_extra_credits', 0)}\n\n"
            f"Suggestions:\n" + "\n".join(f"  • {a}" for a in plan.get("suggestions", [])) +
            ("\n\nVariations:\n" + "\n".join(f"  • {v}" for v in plan.get("variation_hints", [])) if plan.get("variation_hints") else ""),
            title=f"Retry Plan — {shot_id}",
            border_style="yellow",
        ))


    @nsfw_app.command("run")
    def nsfw_run(
        batch_name: str = typer.Argument(..., help="Batch slug or ID"),
        shot_id: str = typer.Argument(..., help="Shot ID to execute"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        prompt: str = typer.Option(None, "--prompt", "-p", help="Override generation prompt"),
    ):
        """Execute a batch shot via Imagine API (image / i2v / video)."""
        from imagine_client import ImagineAPIError

        batch = load_batch(batch_name)
        try:
            result = execute_nsfw_shot(
                batch, shot_id,
                dry_run=dry_run,
                prompt_override=prompt,
            )
        except (ValueError, RuntimeError, ImagineAPIError) as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc

        mode = "[yellow]DRY-RUN[/yellow]" if result.get("dry_run") else "[green]LIVE[/green]"
        console.print(Panel(
            f"Shot: {result['shot_id']}\n"
            f"Mode: {result['mode']}\n"
            f"Status: {result['status']}\n"
            f"Job: {result['job_id']}\n"
            f"URL: {result.get('result_url', '—')}\n"
            f"Est. credits: {result.get('estimated_credits')}\n\n"
            f"Next: nsfw record {batch_name} {shot_id} --score <1-10> --credits {result.get('estimated_credits', 10)}",
            title=f"NSFW Shot Run — {mode}",
            border_style="magenta",
        ))


    @nsfw_app.command("session")
    def nsfw_session(
        batch_name: str = typer.Argument(..., help="Batch slug or ID"),
        count: int = typer.Option(3, "--count", "-n"),
        dry_run: bool = typer.Option(False, "--dry-run"),
        stop_on_fail: bool = typer.Option(True, "--stop-on-fail/--continue-on-fail"),
    ):
        """Run automated NSFW session — execute next priority shots."""
        summary = run_batch_session(
            batch_name,
            pipeline="nsfw",
            count=count,
            dry_run=dry_run,
            stop_on_fail=stop_on_fail,
        )
        table = Table(title=f"NSFW Session — {batch_name}", box=box.SIMPLE)
        table.add_column("Shot", style="cyan")
        table.add_column("Status")
        table.add_column("Job", style="dim")
        for r in summary.get("results", []):
            table.add_row(
                r.get("shot_id", "?"),
                r.get("status", r.get("error", "—")),
                (r.get("job_id") or "")[:18],
            )
        console.print(table)
        console.print(
            f"[dim]Executed {summary['executed']} · "
            f"ok {summary.get('succeeded', 0)} · fail {summary.get('failed', 0)}[/dim]"
        )


    @nsfw_app.command("record")
    def nsfw_record(
        batch_name: str = typer.Argument(..., help="Batch slug or ID"),
        shot_id: str = typer.Argument(..., help="Shot ID"),
        score: float = typer.Option(..., "--score", help="QA quality score 1-10"),
        credits: float = typer.Option(..., "--credits", help="Credits spent"),
        failure_reason: str = typer.Option(None, "--reason", help="Failure reason if QA fail"),
        notes: str = typer.Option("", "--note", "-n"),
    ):
        """Record shot result — updates batch, quota tracker, and daily log."""
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
        if not result["qa_pass"] and result["shot"].get("retry_plan"):
            console.print("[dim]Run: nsfw retry {shot_id} --reason ...[/dim]".format(shot_id=shot_id))


    @nsfw_app.command("promote")
    def nsfw_promote(
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


    @nsfw_app.command("quality-pending")
    def nsfw_quality_pending(batch_name: str = typer.Argument(...)):
        """List shots awaiting quality pass (pass 2)."""
        batch = load_batch(batch_name)
        pending = get_pending_quality_passes(batch)
        if not pending:
            console.print("[dim]No pending quality passes.[/dim]")
            return
        for s in pending:
            plan = s.get("quality_pass_plan", {})
            console.print(f"  {s['shot_id']} — est. +{plan.get('estimated_extra_credits', '?')} cr")


    @nsfw_app.command("report")
    def nsfw_report(
        report_date: str = typer.Option(None, "--date", help="YYYY-MM-DD (default today)"),
        output: str = typer.Option(None, "--output", "-o", help="Write markdown report"),
    ):
        """Generate daily NSFW production report (quota vs quality)."""
        out_path = Path(output) if output else None
        report = generate_daily_report(report_date, output_path=out_path)

        table = Table(title=f"📊 NSFW Daily Report — {report['report_date']}", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Tier", report["tier_label"])
        table.add_row("Credits Today", f"{report['credits_used_today']} / {report['daily_soft_cap']} ({report['daily_cap_pct']}%)")
        table.add_row("Shots", f"{report['shots_completed']} done | {report['shots_passed']} pass | {report['shots_failed']} fail")
        table.add_row("Pass Rate", f"{report['pass_rate_pct']}%")
        table.add_row("Avg Quality", f"{report['avg_quality_score']}/10")
        table.add_row("Quality/Credit", str(report["quality_per_credit"]))
        console.print(table)

        if report.get("recommendations"):
            console.print("\n[bold]Recommendations:[/bold]")
            for r in report["recommendations"]:
                console.print(f"  • {r}")
        if report.get("output_path"):
            console.print(f"\n[green]Report saved:[/green] {report['output_path']}")


    @extend_app.command("plan")
    def nsfw_extend_plan(
        title: str = typer.Argument(..., help="Sequence title"),
        duration: int = typer.Option(90, "--duration", "-d", help="Target duration 30-120+ seconds"),
        profile: str = typer.Option("passionate", "--profile", "-p", help="slow_burn / passionate / intense"),
        source: str = typer.Option("reference_frame", "--source", help="reference_frame or short_clip"),
        reference: str = typer.Option("", "--reference", "-r", help="Reference frame or clip description"),
        beat: list[str] = typer.Option(None, "--beat", "-b", help="Custom beat override (in order)"),
        color_grade: str = typer.Option("warm amber intimacy, soft highlight roll-off", "--color-grade"),
        atmosphere: str = typer.Option("candlelit interior, haze, practical warmth", "--atmosphere"),
        output: str = typer.Option(None, "--output", "-o", help="Save markdown plan"),
    ):
        """Plan NSFW sensual extension with prompt chain and tension curve."""
        if profile not in TENSION_PROFILES:
            console.print(f"[red]Unknown profile. Choose:[/red] {', '.join(TENSION_PROFILES)}")
            raise typer.Exit(1)

        seq = plan_nsfw_extension(
            title,
            target_duration=duration,
            source_type=source,
            reference_description=reference,
            tension_profile=profile,
            custom_beats=beat,
            color_grade=color_grade,
            atmosphere=atmosphere,
        )
        path = save_nsfw_sequence(seq)
        md = nsfw_sequence_to_markdown(seq)
        est = seq.get("cost_estimate", {})

        table = Table(title=f"🎬 NSFW Extension — {title}", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")
        table.add_row("Profile", TENSION_PROFILES[profile]["label"])
        table.add_row("Source", source)
        table.add_row("Clips", str(len(seq.get("clips", []))))
        table.add_row("Duration", f"{duration}s target")
        table.add_row("Credits", f"{est.get('credits_low', '?')}–{est.get('credits_high', '?')}")
        table.add_row("Saved", str(path))
        console.print(table)

        ext = seq.get("nsfw_extension", {})
        console.print("\n[bold]Tension curve:[/bold]")
        for point in ext.get("tension_curve", []):
            console.print(f"  t={point['t']}s — {point['phase']} ({point['tension']:.0%})")

        if output:
            Path(output).write_text(md)
            console.print(f"\n[green]Plan:[/green] {output}")
        else:
            console.print(Markdown(md[:4000] + ("..." if len(md) > 4000 else "")))


    @extend_app.command("chain")
    def nsfw_extend_chain(
        sequence_name: str = typer.Argument(..., help="Sequence slug or name"),
        output: str = typer.Option(None, "--output", "-o"),
    ):
        """Export ready-to-use Grok Imagine prompt chain."""
        seq = require_sequence(sequence_name)
        chain = build_prompt_chain(seq)
        if not chain:
            console.print("[yellow]No prompt chain. Run: nsfw extend plan[/yellow]")
            raise typer.Exit(1)

        for item in chain:
            console.print(Panel(
                item.get("prompt", ""),
                title=f"{item['clip_id']} — {item.get('phase', '')} ({item.get('extend_mode', '')})",
                border_style="magenta",
            ))
            for instr in item.get("extend_instructions", []):
                console.print(f"  [dim]→ {instr}[/dim]")

        if output:
            Path(output).write_text(json.dumps(chain, indent=2))
            console.print(f"\n[green]Chain JSON:[/green] {output}")


    @extend_app.command("prompt")
    def nsfw_extend_prompt_cmd(
        sequence_name: str = typer.Argument(..., help="Sequence slug or name"),
        clip: str = typer.Option(..., "--clip", "-c", help="Clip ID to build/regenerate prompt for"),
    ):
        """Build extend-from-frame prompt for a specific clip."""
        seq = require_sequence(sequence_name)
        target = require_clip(seq, clip)

        idx = target.get("index", 0)
        if idx == 0:
            prompt = target.get("prompt", "")
            console.print(Panel(prompt, title=f"{clip} — opening clip", border_style="magenta"))
            return

        prev = seq["clips"][idx - 1]
        beat = target.get("nsfw_beat", {"beat_summary": "Continue intimate sequence", "phase": "contact"})
        prompt = build_nsfw_extend_prompt(seq, prev, beat)
        target["prompt"] = prompt
        save_nsfw_sequence(seq)
        console.print(Panel(prompt, title=f"{clip} — extend from {prev['clip_id']}", border_style="magenta"))


    @extend_app.command("camera")
    def nsfw_extend_camera(
        phase: str = typer.Option("contact", "--phase", help="Erotic phase name"),
        duration: float = typer.Option(10.0, "--duration", "-d"),
    ):
        """Suggest camera movement and pacing for erotic impact."""
        beat = {"phase": phase, "duration_seconds": duration}
        cam = suggest_camera_pacing(beat)

        console.print(Panel(
            f"Primary: [bold]{cam['primary_move']}[/bold]\n"
            f"Alternates: {', '.join(cam.get('alternate_moves', []))}\n"
            f"Lens: {cam['lens']}\n"
            f"Framing: {cam['framing']}\n"
            f"Pacing: {cam['pacing_note']}\n"
            f"Tension: {cam['tension_level']:.0%} | Motion: {cam['motion_intensity']}\n\n"
            f"Timing beats:\n" + "\n".join(f"  t={t['t']:.1f}s: {t['action']}" for t in cam.get("timing_beats", [])),
            title=f"Camera & Pacing — {phase}",
            border_style="cyan",
        ))


    @extend_app.command("qa")
    def nsfw_extend_qa(
        sequence_name: str = typer.Argument(..., help="Sequence slug or name"),
        clip: str = typer.Option(..., "--clip", "-c"),
        scores: str = typer.Option(None, "--scores", help='JSON scores e.g. {"hand_finger_integrity":8,...}'),
    ):
        """NSFW chain QA scaffold or evaluation (artifact-aware)."""
        seq = require_sequence(sequence_name)
        target = require_clip(seq, clip)

        if scores:
            result = evaluate_nsfw_chain_qa(target, json.loads(scores))
            target["nsfw_chain_qa"] = result
            save_nsfw_sequence(seq)
        else:
            result = run_nsfw_chain_qa_scaffold(target)

        table = Table(title=f"NSFW Chain QA — {clip}", box=box.SIMPLE)
        table.add_column("Check", style="cyan")
        table.add_column("Score", style="white")
        table.add_column("Pass", style="green")
        for key, check in result.get("nsfw_checks", {}).items():
            score = check.get("score", "—")
            passed = check.get("pass", "—")
            crit = " [critical]" if check.get("critical") else ""
            table.add_row(check.get("label", key) + crit, str(score), str(passed))

        console.print(table)
        if result.get("weighted_score") is not None:
            console.print(f"\n[bold]Decision:[/bold] {result['decision']} (score: {result['weighted_score']})")
        if result.get("artifact_fixes"):
            console.print("\n[bold]Artifact fixes:[/bold]")
            for fix in result["artifact_fixes"]:
                console.print(f"  • {fix}")


    @extend_app.command("export")
    def nsfw_extend_export(
        sequence_name: str = typer.Argument(..., help="Sequence slug or name"),
        output: str = typer.Option(None, "--output", "-o"),
    ):
        """Export full extension plan markdown."""
        seq = require_sequence(sequence_name)
        md = nsfw_sequence_to_markdown(seq)
        out = output or f"sequences/{seq['slug']}/extension_plan.md"
        Path(out).write_text(md)
        console.print(f"[green]Exported:[/green] {out}")


