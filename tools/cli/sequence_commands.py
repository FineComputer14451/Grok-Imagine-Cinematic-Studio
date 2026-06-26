"""Sequence chain CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from assembly_editor import build_edl, edl_to_markdown, save_edl
from chain_qa_assist import apply_assisted_qa, assist_chain_qa
from quota_optimizer import estimate_sequence_cost
from imagine_client import is_dry_run
from sequence_delivery import deliver_sequence
from sequence_polish import polish_sequence
from sequence_chain import (
    CHAIN_QA_CHECKS,
    add_clip_to_sequence,
    build_extend_prompt,
    build_handoff_from_clip,
    create_clip,
    create_sequence_scaffold,
    list_sequences,
    run_chain_qa,
    save_sequence,
    sequence_to_markdown,
    update_sequence_health,
)
from sequence_runner import run_sequence_clip

from cli.helpers import assess_risk_from_state, require_clip, require_sequence, require_sequence_bundle
from cli.shared import console


def register(app: typer.Typer) -> None:
    @app.command("init")
    def seq_init(
        name: str = typer.Argument(..., help="Sequence name"),
        duration: int = typer.Option(60, "--duration", "-d", help="Target duration in seconds"),
        genre: str = typer.Option("", "--genre", "-g", help="Genre"),
    ):
        """Create a new long-form sequence blueprint."""
        seq = create_sequence_scaffold(name, target_duration=duration, genre=genre)
        path = save_sequence(seq)
        console.print(f"[green]✅ Sequence created:[/green] {path}")
        console.print("[dim]Next: sequence add-clip \"{name}\" --prompt \"...\" --recap \"...\"[/dim]".format(name=name))

    @app.command("list")
    def seq_list():
        """List all sequence blueprints."""
        seqs = list_sequences()
        if not seqs:
            console.print("[yellow]No sequences yet. Run: sequence init \"Sequence Name\"[/yellow]")
            return
        table = Table(title="🎬 Sequence Blueprints", box=box.ROUNDED)
        table.add_column("Name", style="cyan")
        table.add_column("Clips", style="white")
        table.add_column("Target", style="dim")
        table.add_column("Health", style="green")
        table.add_column("Chain QA", style="yellow")
        for s in seqs:
            table.add_row(
                s["name"], str(s["clips"]), f"{s['target_duration']}s",
                str(s["health"] or "—"), s["chain_qa_status"],
            )
        console.print(table)

    @app.command("show")
    def seq_show(name: str = typer.Argument(..., help="Sequence name or slug")):
        """Display sequence blueprint."""
        seq = require_sequence(name)
        console.print(Panel(Markdown(sequence_to_markdown(seq)[:5000]), title=f"🎬 {seq['sequence_name']}", border_style="blue"))

    @app.command("add-clip")
    def seq_add_clip(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        prompt: str = typer.Option("", "--prompt", "-p"),
        recap: str = typer.Option("", "--recap", "-r", help="LAST_FRAME_RECAP for this clip"),
        duration: int = typer.Option(10, "--duration", "-d"),
        reference_id: str = typer.Option("", "--ref", help="reference_image_id"),
        transition: str = typer.Option("invisible_edit", "--transition", "-t"),
        last_action: str = typer.Option("", "--action", help="Momentum: last action"),
        emotion: str = typer.Option("", "--emotion", help="Momentum: emotional state"),
        dialogue: str = typer.Option("", "--dialogue", help="Audio momentum: dialogue state"),
    ):
        """Add a clip to the sequence chain."""
        seq = require_sequence(name)
        clip = create_clip(
            duration_seconds=duration,
            prompt=prompt,
            reference_image_id=reference_id,
            last_frame_recap=recap,
            transition_to_next=transition,
        )
        if last_action or emotion:
            clip["momentum_vector"]["last_action"] = last_action
            clip["momentum_vector"]["emotional_state"] = emotion
        if dialogue:
            clip["audio_momentum_vector"]["dialogue_state"] = dialogue
        add_clip_to_sequence(seq, clip)
        update_sequence_health(seq)
        save_sequence(seq)
        console.print(f"[green]✅ Added {clip['clip_id']} to {seq['sequence_name']}[/green]")
        console.print(f"[dim]Clips: {len(seq['clips'])} | Health: {seq.get('sequence_health_score')}[/dim]")

    @app.command("handoff")
    def seq_handoff(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Source clip ID"),
        output: str = typer.Option(None, "--output", "-o"),
    ):
        """Generate extend/stitch handoff packet from a clip."""
        seq, seq_path = require_sequence_bundle(name)
        source = require_clip(seq, clip)
        handoff = build_handoff_from_clip(source)
        out_path = Path(output) if output else seq_path.parent / f"handoff_{clip}.json"
        out_path.write_text(json.dumps(handoff, indent=2))
        console.print(f"[green]✅ Handoff packet:[/green] {out_path}")
        console.print(Panel(json.dumps(handoff, indent=2)[:2000], title="Handoff Preview", border_style="cyan"))

    @app.command("extend-prompt")
    def seq_extend_prompt(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Previous clip ID"),
        beat: str = typer.Option(..., "--beat", "-b", help="Next narrative beat"),
        character: str = typer.Option("", "--character", help="CHARACTER_DNA injection block"),
        output: str = typer.Option(None, "--output", "-o"),
    ):
        """Build Grok Imagine Video 1.5 extend prompt for the next clip."""
        seq = require_sequence(name)
        source = require_clip(seq, clip)
        prompt = build_extend_prompt(seq, source, beat, character_injection=character)
        if output:
            Path(output).write_text(prompt)
            console.print(f"[green]✅ Extend prompt saved:[/green] {output}")
        else:
            console.print(Panel(prompt, title="1.5 Extend Prompt", border_style="green"))

    @app.command("qa")
    def seq_qa(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Clip ID to evaluate"),
        scores: str = typer.Option(None, "--scores", "-s", help="JSON dict of chain QA scores (1-10 each)"),
    ):
        """Run chain QA gate on a clip (extend/stitch checks)."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)

        clips = seq.get("clips", [])
        idx = target["index"]
        prev = clips[idx - 1] if idx > 0 else None

        score_dict = json.loads(scores) if scores else None
        qa = run_chain_qa(target, previous_clip=prev, scores=score_dict)
        target["chain_qa"] = qa

        if qa["decision"] == "go":
            target["status"] = "approved"
        elif qa["decision"] == "no_go":
            target["status"] = "qa_hold"

        update_sequence_health(seq)
        save_sequence(seq)

        if score_dict is None:
            table = Table(title=f"Chain QA Scaffold — {clip}", box=box.SIMPLE)
            table.add_column("Key", style="cyan")
            table.add_column("Check", style="white")
            table.add_column("Weight", style="dim")
            for key, label, weight in CHAIN_QA_CHECKS:
                table.add_row(key, label, str(weight))
            console.print(table)
            console.print("[dim]Provide scores: --scores '{\"last_frame_continuity\":8,...}'[/dim]")
        else:
            decision_color = {"go": "green", "conditional_go": "yellow", "no_go": "red"}.get(qa["decision"], "white")
            console.print(f"[{decision_color}]Decision: {qa['decision']}[/{decision_color}] | Weighted: {qa.get('weighted_score', 'N/A')}")
            if qa.get("critical_failures"):
                console.print(f"[red]Critical failures:[/red] {', '.join(qa['critical_failures'])}")
            if qa.get("fixes"):
                for fix in qa["fixes"]:
                    console.print(f"  [yellow]Fix:[/yellow] {fix}")
        console.print(f"[dim]Sequence health: {seq.get('sequence_health_score')} | Status: {seq.get('chain_qa_status')}[/dim]")

    @app.command("estimate-cost")
    def seq_estimate_cost(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        fast_mode: bool = typer.Option(False, "--fast-mode"),
        quality_pass: bool = typer.Option(False, "--quality-pass"),
    ):
        """Estimate quota cost for a sequence blueprint."""
        seq = require_sequence(name)
        est = estimate_sequence_cost(
            seq.get("clips", []),
            fast_mode=fast_mode,
            quality_pass=quality_pass,
        )
        risk = assess_risk_from_state(est)
        console.print(Panel(
            f"Clips: {est['clip_count']} | Duration: {est['total_duration_seconds']}s\n"
            f"Credits: {est['credits_low']} – {est['credits_high']}\n"
            f"USD: ${est['usd_low']} – ${est['usd_high']}\n"
            f"Risk: {risk['risk_level']} ({risk.get('budget_pct_used', 'N/A')}% of budget)",
            title=f"💰 {seq['sequence_name']}",
            border_style="green",
        ))

    @app.command("qa-assist")
    def seq_qa_assist(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c"),
        apply: bool = typer.Option(False, "--apply", help="Apply suggested scores to chain QA"),
        nsfw: bool = typer.Option(False, "--nsfw", help="Use NSFW 8-point assist"),
    ):
        """Pre-fill chain QA scores from metadata heuristics (assist mode)."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)
        clips = seq.get("clips", [])
        idx = target["index"]
        prev = clips[idx - 1] if idx > 0 else None

        if apply:
            result = apply_assisted_qa(seq, target, previous_clip=prev, nsfw=nsfw or bool(seq.get("nsfw_extension")))
            assist = result["assist"]
            qa = result["chain_qa"]
            update_sequence_health(seq)
            save_sequence(seq)
        else:
            assist = assist_chain_qa(target, previous_clip=prev, sequence=seq, nsfw=nsfw or bool(seq.get("nsfw_extension")))
            qa = assist["evaluation"]

        table = Table(title=f"QA Assist — {clip} ({assist['mode']})", box=box.SIMPLE)
        table.add_column("Check", style="cyan")
        table.add_column("Score", justify="right")
        table.add_column("Reason", style="dim", max_width=36)
        for key, score in assist["suggested_scores"].items():
            table.add_row(key, str(score), assist["reasons"].get(key, "")[:36])
        console.print(table)

        decision_color = {"go": "green", "conditional_go": "yellow", "no_go": "red"}.get(qa.get("decision", ""), "white")
        console.print(
            f"Confidence: {assist['confidence']} | "
            f"[{decision_color}]Decision: {qa.get('decision')}[/{decision_color}] | "
            f"Weighted: {qa.get('weighted_score', 'N/A')}"
        )
        if apply:
            console.print(f"[dim]Applied — sequence health: {seq.get('sequence_health_score')}[/dim]")
        else:
            console.print("[dim]Review scores, then: sequence qa-assist \"{name}\" --clip {clip} --apply[/dim]".format(
                name=name, clip=clip,
            ))


    @app.command("edl")
    def seq_edl(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        all_clips: bool = typer.Option(False, "--all-clips", help="Include non-approved clips"),
        output: str = typer.Option(None, "--output", "-o"),
    ):
        """Export Assembly Editor EDL from sequence clips."""
        seq = require_sequence(name)
        edl = build_edl(seq, approved_only=not all_clips)
        path = save_edl(edl, output=Path(output) if output else None)
        console.print(f"[green]EDL saved:[/green] {path}")
        console.print(f"[dim]Markdown:[/dim] {edl.get('markdown_path', path.with_suffix('.md'))}")
        console.print(Panel(
            f"Assembled: {edl['assembled_duration_sec']}s / target {edl['runtime_target_sec']}s\n"
            f"Clips: {edl['clip_count']} | Skipped: {len(edl.get('skipped_clips', []))}",
            title="Assembly EDL",
            border_style="cyan",
        ))
        if not output:
            console.print(Markdown(edl_to_markdown(edl)[:3000]))


    @app.command("polish")
    def seq_polish(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        scale: int = typer.Option(2, "--scale", "-s", help="Upscale factor 2-4"),
        face_restore: bool = typer.Option(False, "--face-restore"),
        clip: list[str] = typer.Option(None, "--clip", "-c", help="Polish specific clips only"),
        dry_run: bool = typer.Option(False, "--dry-run"),
    ):
        """AI Polish pass — upscale approved clips via ai-video-upscaler."""
        seq = require_sequence(name)
        manifest = polish_sequence(
            seq,
            scale=scale,
            face_restore=face_restore,
            clip_ids=list(clip) if clip else None,
            dry_run=dry_run,
        )
        save_sequence(seq)
        console.print(Panel(
            f"Polished: {manifest['clips_polished']} clips\n"
            f"Skipped: {len(manifest.get('clips_skipped', []))}\n"
            f"Output: {manifest['output_dir']}\n"
            f"Manifest: {manifest['output_dir']}/polish_manifest.json",
            title=f"AI Polish — {seq['sequence_name']}",
            border_style="green",
        ))


    @app.command("deliver")
    def seq_deliver(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        formats: str = typer.Option("16:9", "--formats", "-f", help="Comma-separated: 16:9,9:16,1:1"),
        all_clips: bool = typer.Option(False, "--all-clips"),
        dry_run: bool = typer.Option(False, "--dry-run"),
    ):
        """Build delivery masters — concat + social crops via cinematic-ffmpeg."""
        seq = require_sequence(name)
        fmt_list = [x.strip() for x in formats.split(",") if x.strip()]
        manifest = deliver_sequence(
            seq,
            formats=fmt_list,
            approved_only=not all_clips,
            dry_run=dry_run,
        )
        save_sequence(seq)
        lines = [f"{k}: {v}" for k, v in manifest.get("outputs", {}).items()]
        console.print(Panel(
            f"Formats: {', '.join(fmt_list)}\n"
            f"Duration: {manifest.get('assembled_duration_sec')}s\n"
            + ("\n".join(lines) if lines else "No outputs — check polish step")
            + ("\n\nNotes:\n" + "\n".join(f"  • {n}" for n in manifest.get("notes", [])) if manifest.get("notes") else ""),
            title=f"Delivery — {seq['sequence_name']}",
            border_style="cyan",
        ))


    @app.command("run")
    def seq_run(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Clip ID to generate"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Force mock generation (no API key)"),
        no_poll: bool = typer.Option(False, "--no-poll", help="Submit only; do not poll video job"),
    ):
        """Submit clip to Imagine API, poll job, run chain QA, update sequence health."""
        seq = require_sequence(name)
        require_clip(seq, clip)

        use_dry = dry_run or is_dry_run()
        if use_dry:
            console.print("[dim]Dry-run mode — mock URLs and auto chain QA[/dim]")

        try:
            result = run_sequence_clip(
                seq,
                clip,
                dry_run=use_dry,
                poll=not no_poll,
            )
        except RuntimeError as exc:
            console.print(f"[red]Blocked:[/red] {exc}")
            raise typer.Exit(1) from exc
        except Exception as exc:
            console.print(f"[red]Run failed:[/red] {exc}")
            raise typer.Exit(1) from exc

        decision_color = {
            "go": "green",
            "conditional_go": "yellow",
            "no_go": "red",
            "awaiting_scores": "dim",
            "pending": "dim",
        }.get(result.get("chain_qa", {}).get("decision", ""), "white")

        console.print(Panel(
            f"Job: {result['job_id']}\n"
            f"Clip: {result['clip_id']} → {result['status']}\n"
            f"URL: {result.get('result_url') or '—'}\n"
            f"Chain QA: [{decision_color}]{result.get('chain_qa', {}).get('decision', 'pending')}[/{decision_color}] "
            f"(score: {result.get('chain_qa', {}).get('weighted_score', 'N/A')})\n"
            f"Sequence health: {result.get('sequence_health')} | Status: {result.get('chain_qa_status')}",
            title=f"Sequence Run — {seq['sequence_name']}",
            border_style="green" if result["status"] == "approved" else "yellow",
        ))
        if result.get("chain_qa", {}).get("decision") == "no_go":
            console.print("[red]Extend blocked — resolve chain QA failures before next clip[/red]")
            raise typer.Exit(2)


    @app.command("health")
    def seq_health(name: str = typer.Argument(..., help="Sequence name or slug")):
        """Show sequence health score and chain QA status."""
        seq = require_sequence(name)
        update_sequence_health(seq)
        save_sequence(seq)
        console.print(Panel(
            f"Health Score: [bold]{seq.get('sequence_health_score')}[/bold] / 10\n"
            f"Chain QA Status: [bold]{seq.get('chain_qa_status')}[/bold]\n"
            f"Clips: {len(seq.get('clips', []))}\n"
            f"Target Duration: {seq.get('target_duration_seconds')}s",
            title=f"🎬 {seq['sequence_name']}",
            border_style="cyan",
        ))