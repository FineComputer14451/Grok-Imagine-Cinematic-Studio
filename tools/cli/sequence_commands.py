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
from audio_momentum import build_audio_momentum_report
from chain_qa_assist import apply_assisted_qa, assist_chain_qa
from continuity_diff import (
    diff_clip_pair,
    diff_clip_vs_bank,
    format_continuity_diff_markdown,
    format_continuity_diff_table_rows,
)
from extend_regen import apply_regen_plan, ensure_clip_regen, plan_regen, prepare_regen_run
from identity_drift import (
    DEFAULT_DRIFT_THRESHOLD,
    evaluate_identity_strict_gate,
    score_identity_drift,
)
from quota_optimizer import estimate_sequence_cost
from imagine_client import is_dry_run
from seam_report import build_seam_report
from sequence_delivery import deliver_sequence
from sequence_health_dashboard import build_longform_health, format_longform_health_markdown
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
    sync_memory_from_clip,
    update_sequence_health,
)
from sequence_runner import run_sequence_clip
from stitch_artifact_lexicon import (
    build_negative_pack,
    build_positive_guards,
    format_lexicon_markdown,
    list_entries,
    suggest_entries_from_chain_qa,
    suggest_entries_from_seam,
)

from cli.helpers import assess_risk_from_state, require_clip, require_sequence, require_sequence_bundle
from cli.shared import console


def _load_dna_optional(dna: str | None) -> dict | None:
    """Load Character DNA from a path or character slug; None if missing."""
    if not dna:
        return None
    from character_dna import find_character_dna, load_character_dna

    p = Path(dna)
    if p.is_file():
        return load_character_dna(p)
    found = find_character_dna(dna)
    if found:
        return load_character_dna(found)
    console.print(f"[yellow]DNA not found: {dna} — scoring without DNA[/yellow]")
    return None


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
        aspect: str = typer.Option("16:9", "--aspect", "-a", help="16:9 | 9:16 | 1:1"),
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
            aspect_ratio=aspect,
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
        strict_identity: bool = typer.Option(
            False,
            "--strict-identity",
            help="Exit 1 if drift evidence missing or identity risk (opt-in hard fail)",
        ),
    ):
        """Generate extend/stitch handoff packet from a clip."""
        seq, seq_path = require_sequence_bundle(name)
        source = require_clip(seq, clip)

        if strict_identity:
            gate = evaluate_identity_strict_gate(clip=source)
            if not gate.get("pass"):
                console.print(
                    f"[red]Identity strict gate failed[/red] "
                    f"(status={gate.get('status')}, score={gate.get('score')})"
                )
                for r in gate.get("reasons") or []:
                    console.print(f"  • {r}")
                if gate.get("fixes"):
                    console.print("[yellow]Fixes:[/yellow]")
                    for fix in gate["fixes"]:
                        console.print(f"  → {fix}")
                raise typer.Exit(1)

        handoff = build_handoff_from_clip(source, memory_bank=seq.get("memory_bank"))
        out_path = Path(output) if output else seq_path.parent / f"handoff_{clip}.json"
        out_path.write_text(json.dumps(handoff, indent=2))
        console.print(f"[green]✅ Handoff packet:[/green] {out_path}")
        if strict_identity:
            console.print("[dim]Identity strict gate: pass[/dim]")
        console.print(Panel(json.dumps(handoff, indent=2)[:2000], title="Handoff Preview", border_style="cyan"))

    @app.command("extend-prompt")
    def seq_extend_prompt(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Previous clip ID"),
        beat: str = typer.Option(..., "--beat", "-b", help="Next narrative beat"),
        character: str = typer.Option("", "--character", help="CHARACTER_DNA injection block"),
        output: str = typer.Option(None, "--output", "-o"),
        strict_identity: bool = typer.Option(
            False,
            "--strict-identity",
            help="Exit 1 if drift evidence missing or identity risk (opt-in hard fail)",
        ),
    ):
        """Build Grok Imagine Video 1.5 extend prompt for the next clip."""
        seq = require_sequence(name)
        source = require_clip(seq, clip)

        if strict_identity:
            gate = evaluate_identity_strict_gate(clip=source)
            if not gate.get("pass"):
                console.print(
                    f"[red]Identity strict gate failed[/red] "
                    f"(status={gate.get('status')}, score={gate.get('score')})"
                )
                for r in gate.get("reasons") or []:
                    console.print(f"  • {r}")
                if gate.get("fixes"):
                    console.print("[yellow]Fixes:[/yellow]")
                    for fix in gate["fixes"]:
                        console.print(f"  → {fix}")
                raise typer.Exit(1)

        prompt = build_extend_prompt(seq, source, beat, character_injection=character)
        if output:
            Path(output).write_text(prompt)
            console.print(f"[green]✅ Extend prompt saved:[/green] {output}")
        else:
            console.print(Panel(prompt, title="1.5 Extend Prompt", border_style="green"))
        if strict_identity:
            console.print("[dim]Identity strict gate: pass[/dim]")

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
        dna: str = typer.Option(None, "--dna", help="DNA path or character slug"),
        prev_frame: str = typer.Option(None, "--prev-frame", help="Path to previous last-frame still"),
        curr_frame: str = typer.Option(None, "--curr-frame", help="Path to current first-frame still"),
    ):
        """Pre-fill chain QA scores from metadata heuristics (assist mode)."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)
        clips = seq.get("clips", [])
        idx = target["index"]
        prev = clips[idx - 1] if idx > 0 else None
        dna_obj = _load_dna_optional(dna)
        evidence_kwargs = {
            "previous_last_frame_path": prev_frame,
            "current_first_frame_path": curr_frame,
        }

        if apply:
            result = apply_assisted_qa(
                seq,
                target,
                previous_clip=prev,
                nsfw=nsfw or bool(seq.get("nsfw_extension")),
                dna=dna_obj,
                **evidence_kwargs,
            )
            assist = result["assist"]
            qa = result["chain_qa"]
            update_sequence_health(seq)
            save_sequence(seq)
        else:
            assist = assist_chain_qa(
                target,
                previous_clip=prev,
                sequence=seq,
                nsfw=nsfw or bool(seq.get("nsfw_extension")),
                dna=dna_obj,
                **evidence_kwargs,
            )
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
        ev = assist.get("evidence") or {}
        if ev.get("identity_drift"):
            d = ev["identity_drift"]
            console.print(
                f"[dim]Evidence drift_score={d.get('drift_score')} "
                f"seam_risk={ev.get('seam_report', {}).get('seam_risk')}[/dim]"
            )
        if apply:
            console.print(f"[dim]Applied — sequence health: {seq.get('sequence_health_score')}[/dim]")
        else:
            console.print("[dim]Review scores, then: sequence qa-assist \"{name}\" --clip {clip} --apply[/dim]".format(
                name=name, clip=clip,
            ))

    @app.command("drift-score")
    def seq_drift_score(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c"),
        dna: str = typer.Option(None, "--dna", help="Path to dna.json or character slug"),
        threshold: float = typer.Option(None, "--threshold", help="Default 2.5"),
    ):
        """Score identity drift for a clip against Character DNA (evidence loop #1)."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)
        clips = seq.get("clips", [])
        idx = target["index"]
        prev = clips[idx - 1] if idx > 0 else None
        dna_obj = _load_dna_optional(dna)
        thr = DEFAULT_DRIFT_THRESHOLD if threshold is None else threshold
        report = score_identity_drift(
            target, dna=dna_obj, previous_clip=prev, threshold=thr
        )
        target["identity_drift"] = report
        save_sequence(seq)
        color = "green" if report["pass"] else "red"
        console.print(
            f"[{color}]drift_score={report['drift_score']} "
            f"(threshold={report['threshold']}) pass={report['pass']}[/{color}]"
        )
        for factor in report.get("factors") or []:
            console.print(f"  • {factor}")
        if report.get("fixes"):
            console.print("[yellow]Fixes:[/yellow]")
            for fix in report["fixes"]:
                console.print(f"  → {fix}")

    @app.command("seam-report")
    def seq_seam_report(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c"),
        prev_frame: str = typer.Option(None, "--prev-frame", help="Path to previous last-frame still"),
        curr_frame: str = typer.Option(None, "--curr-frame", help="Path to current first-frame still"),
    ):
        """Last-frame seam risk report (evidence loop #2)."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)
        clips = seq.get("clips", [])
        idx = target["index"]
        prev = clips[idx - 1] if idx > 0 else None
        report = build_seam_report(
            target,
            previous_clip=prev,
            previous_last_frame_path=prev_frame,
            current_first_frame_path=curr_frame,
        )
        target["seam_report"] = report
        save_sequence(seq)
        color = "green" if report["pass"] else "yellow"
        console.print(
            f"[{color}]seam_risk={report['seam_risk']} pass={report['pass']} "
            f"mode={report['mode']}[/{color}]"
        )
        for factor in report.get("factors") or []:
            console.print(f"  • {factor}")
        if report.get("fixes"):
            console.print("[yellow]Fixes:[/yellow]")
            for fix in report["fixes"]:
                console.print(f"  → {fix}")

    @app.command("amv-check")
    def seq_amv_check(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c"),
    ):
        """Audio momentum integrity check across stitch (roadmap #6)."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)
        clips = seq.get("clips", [])
        idx = target["index"]
        prev = clips[idx - 1] if idx > 0 else None
        report = build_audio_momentum_report(
            target,
            previous_clip=prev,
            memory_bank=seq.get("memory_bank"),
        )
        target["audio_momentum_report"] = report
        save_sequence(seq)
        color = "green" if report["pass"] else "red"
        console.print(
            f"[{color}]integrity_score={report['integrity_score']} "
            f"pass={report['pass']} mode={report['mode']}[/{color}]"
        )
        console.print(
            f"[dim]suggested_audio_momentum_sync="
            f"{report['suggested_audio_momentum_sync']}[/dim]"
        )
        for factor in report.get("factors") or []:
            console.print(f"  • {factor}")
        if report.get("field_status"):
            console.print("[dim]Field status:[/dim]")
            for key, status in report["field_status"].items():
                console.print(f"  {key}: {status}")
        if report.get("fixes"):
            console.print("[yellow]Fixes:[/yellow]")
            for fix in report["fixes"]:
                console.print(f"  → {fix}")

    @app.command("continuity-diff")
    def seq_continuity_diff(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Right-hand clip ID"),
        against: str = typer.Option(
            "prev",
            "--against",
            help="prev | bank | <clip_id>",
        ),
        save: bool = typer.Option(False, "--save", help="Store report on right clip"),
        output: str = typer.Option(None, "--output", "-o", help="Write markdown file"),
    ):
        """Diff continuity_state / momentum / AMV for Continuity Guardian (roadmap #9)."""
        seq = require_sequence(name)
        right = require_clip(seq, clip)
        against_raw = (against or "prev").strip()
        against_key = against_raw.lower()
        clips = seq.get("clips") or []

        if against_key == "bank":
            report = diff_clip_vs_bank(right, seq.get("memory_bank") or {})
        elif against_key == "prev":
            idx = right.get("index")
            if idx is None:
                # Fall back to position in clips list
                try:
                    idx = next(
                        i for i, c in enumerate(clips)
                        if c.get("clip_id") == right.get("clip_id")
                    )
                except StopIteration:
                    idx = 0
            if idx <= 0:
                console.print(
                    "[red]No previous clip — opening clip cannot use --against prev[/red]"
                )
                raise typer.Exit(1)
            left = clips[idx - 1]
            report = diff_clip_pair(left, right)
        else:
            left = require_clip(seq, against_raw)
            report = diff_clip_pair(left, right)

        summary = report.get("summary") or {}
        total = summary.get("total", 0)
        color = "green" if total == 0 else "yellow"
        console.print(
            f"[{color}]mode={report.get('mode')} "
            f"left={report.get('left_label')} right={report.get('right_label')} "
            f"added={summary.get('added', 0)} removed={summary.get('removed', 0)} "
            f"changed={summary.get('changed', 0)} total={total}[/{color}]"
        )
        for w in report.get("warnings") or []:
            console.print(f"[yellow]⚠ {w}[/yellow]")

        table = Table(title="Continuity Diff", box=box.ROUNDED)
        table.add_column("Path", style="cyan")
        table.add_column("Kind", style="yellow")
        table.add_column("Before", style="dim")
        table.add_column("After", style="white")
        rows = format_continuity_diff_table_rows(report)
        if not rows:
            table.add_row("—", "—", "—", "No continuity changes detected")
        else:
            for path, kind, before, after in rows:
                table.add_row(path, kind, before, after)
        console.print(table)

        md = format_continuity_diff_markdown(report)
        console.print(
            Panel(
                Markdown(md[:4000]),
                title="Continuity Diff Report",
                border_style="blue",
            )
        )

        if save:
            right["continuity_diff"] = report
            save_sequence(seq)
            console.print(
                f"[green]✅ Saved continuity_diff on {right.get('clip_id')}[/green]"
            )

        if output:
            out_path = Path(output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md, encoding="utf-8")
            console.print(f"[green]✅ Markdown report:[/green] {out_path}")

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
    def seq_health(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        json_out: bool = typer.Option(False, "--json", help="Emit JSON report"),
        markdown: bool = typer.Option(False, "--markdown", help="Emit markdown report"),
        output: str | None = typer.Option(None, "--output", "-o", help="Write report to file"),
    ):
        """Long-form health dashboard — QA, drift, seam, regen, cost (roadmap #10)."""
        seq = require_sequence(name)
        update_sequence_health(seq)
        save_sequence(seq)
        report = build_longform_health(seq)

        def _fmt(value: object) -> str:
            return "—" if value is None else str(value)

        # JSON path
        if json_out:
            payload = json.dumps(report, indent=2)
            if output:
                out_path = Path(output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(payload, encoding="utf-8")
                console.print(f"[green]✅ JSON report:[/green] {out_path}")
            else:
                console.print(payload)
            return

        # Markdown path (--markdown or -o *.md)
        want_md = markdown or (output is not None and str(output).lower().endswith(".md"))
        if want_md:
            md = format_longform_health_markdown(report)
            if output:
                out_path = Path(output)
                out_path.parent.mkdir(parents=True, exist_ok=True)
                out_path.write_text(md, encoding="utf-8")
                console.print(f"[green]✅ Markdown report:[/green] {out_path}")
            else:
                console.print(Markdown(md))
            return

        # Rich default dashboard
        health = report.get("health_score")
        health_disp = _fmt(health)
        cq = report.get("chain_qa") or {}
        alerts = report.get("alerts") or []
        alert_block = (
            "\n".join(f"⚠ {a}" for a in alerts) if alerts else "None"
        )
        overview = (
            f"Health Score: [bold]{health_disp}[/bold] / 10\n"
            f"Chain QA Status: [bold]{report.get('chain_qa_status', 'pending')}[/bold]\n"
            f"Clips: {report.get('clip_count', 0)} "
            f"(approved {report.get('clips_approved', 0)}, "
            f"qa_hold {report.get('clips_qa_hold', 0)}, "
            f"pending {report.get('clips_pending', 0)})\n"
            f"Target Duration: {report.get('target_duration_seconds', 0)}s\n"
            f"Chain QA: go={cq.get('go', 0)} no_go={cq.get('no_go', 0)} "
            f"conditional={cq.get('conditional_go', 0)} pending={cq.get('pending', 0)} "
            f"(avg {_fmt(cq.get('avg_weighted_score'))})\n"
            f"Alerts:\n{alert_block}"
        )
        border = "red" if alerts else "cyan"
        console.print(Panel(
            overview,
            title=f"🎬 Long-Form Health — {report.get('sequence_name') or name}",
            border_style=border,
        ))

        table = Table(title="Clip Health Rows", box=box.ROUNDED)
        table.add_column("Clip", style="cyan")
        table.add_column("Status", style="white")
        table.add_column("QA", style="yellow")
        table.add_column("Score", justify="right")
        table.add_column("Drift", justify="right")
        table.add_column("Seam", justify="right")
        table.add_column("AMV", justify="right")
        table.add_column("Regen", justify="right")
        table.add_column("Temp", style="dim")
        table.add_column("ContDiff", justify="right")
        rows = report.get("clip_rows") or []
        if not rows:
            table.add_row("—", "—", "—", "—", "—", "—", "—", "—", "—", "No clips")
        else:
            for r in rows:
                table.add_row(
                    str(r.get("clip_id") or "—"),
                    str(r.get("status") or "—"),
                    _fmt(r.get("qa_decision")),
                    _fmt(r.get("weighted_score")),
                    _fmt(r.get("drift_score")),
                    _fmt(r.get("seam_risk")),
                    _fmt(r.get("amv_integrity")),
                    str(r.get("regen_attempts", 0)),
                    _fmt(r.get("temp_severity")),
                    _fmt(r.get("cont_diff_total")),
                )
        console.print(table)

        cost = report.get("cost") or {}
        drift = report.get("drift") or {}
        seam = report.get("seam") or {}
        amv = report.get("audio_momentum") or {}
        regen = report.get("regen") or {}
        temp = report.get("temperature") or {}
        cdiff = report.get("continuity_diff") or {}
        cost_body = (
            f"Remaining: {cost.get('remaining_clips', 0)} clips "
            f"({cost.get('remaining_duration_seconds', 0)}s)\n"
            f"Credits: {_fmt(cost.get('credits_low'))} – {_fmt(cost.get('credits_high'))}\n"
            f"USD: ${_fmt(cost.get('usd_low'))} – ${_fmt(cost.get('usd_high'))}\n"
            f"Drift fails: {drift.get('fail_count', 0)} | "
            f"Seam fails: {seam.get('fail_count', 0)} | "
            f"AMV fails: {amv.get('fail_count', 0)}\n"
            f"Regen attempts: {regen.get('total_attempts', 0)} "
            f"(seq used {regen.get('sequence_attempts_used', 0)}) | "
            f"Temp fail/warn: {temp.get('fail_count', 0)}/{temp.get('warn_count', 0)} | "
            f"ContDiff changes: {cdiff.get('total_changes', 0)}"
        )
        console.print(Panel(cost_body, title="💰 Remaining Cost & Gate Summary", border_style="green"))

        if output:
            # Non-.md output without --json: write markdown as portable default
            md = format_longform_health_markdown(report)
            out_path = Path(output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(md, encoding="utf-8")
            console.print(f"[green]✅ Report written:[/green] {out_path}")


    memory_app = typer.Typer(help="Sequence memory bank (roadmap #4)")
    app.add_typer(memory_app, name="memory")

    @memory_app.command("show")
    def memory_show(name: str = typer.Argument(..., help="Sequence name or slug")):
        """Show running sequence memory bank."""
        seq = require_sequence(name)
        bank = seq.get("memory_bank") or {}
        from sequence_memory import ensure_memory_bank, memory_bank_summary

        bank = ensure_memory_bank(bank)
        console.print(memory_bank_summary(bank))
        console.print(Panel(json.dumps(bank, indent=2)[:3000], title="memory_bank", border_style="cyan"))

    @memory_app.command("sync")
    def memory_sync(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Clip ID to merge into memory bank"),
        character: str = typer.Option(None, "--character", help="Character slug for cast entry"),
        character_name: str = typer.Option(None, "--character-name", help="Display name"),
    ):
        """Merge a clip's continuity/momentum/AMV into the sequence memory bank."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)
        sync_memory_from_clip(seq, target, character_slug=character, character_name=character_name)
        save_sequence(seq)
        from sequence_memory import ensure_memory_bank, memory_bank_summary

        console.print(f"[green]Memory bank synced from {clip}[/green]")
        console.print(memory_bank_summary(ensure_memory_bank(seq.get("memory_bank"))))

    regen_app = typer.Typer(help="Re-gen loop after chain QA No-Go (roadmap #5)")
    app.add_typer(regen_app, name="regen")

    def _previous_clip(seq: dict, target: dict) -> dict | None:
        clips = seq.get("clips", [])
        idx = target.get("index", 0)
        return clips[idx - 1] if idx > 0 else None

    @regen_app.command("plan")
    def regen_plan(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Clip ID to plan re-gen for"),
        beat: str = typer.Option(None, "--beat", "-b", help="Optional narrative beat override"),
        character: str = typer.Option("", "--character", help="DNA inject block text"),
    ):
        """Build fix prompt + show budget (no spend; does not set regen_ready)."""
        from datetime import datetime, timezone

        seq = require_sequence(name)
        target = require_clip(seq, clip)
        prev = _previous_clip(seq, target)
        plan = plan_regen(
            seq,
            target,
            previous_clip=prev,
            next_beat=beat,
            character_injection=character or "",
        )

        allowed_style = "green" if plan["allowed"] else "red"
        console.print(
            f"[{allowed_style}]Allowed: {plan['allowed']}[/{allowed_style}] — {plan['reason']}"
        )
        console.print(
            f"Attempts: {plan['attempts']}/{plan['max_attempts']} | "
            f"Sequence used: {plan['sequence_attempts_used']} | "
            f"Prior decision: {plan.get('prior_decision') or '—'}"
        )

        fixes = plan.get("fixes") or []
        if fixes:
            table = Table(title="Fixes", box=box.ROUNDED)
            table.add_column("#", style="dim")
            table.add_column("Fix", style="white")
            for i, fix in enumerate(fixes, 1):
                table.add_row(str(i), str(fix))
            console.print(table)
        else:
            console.print("[dim]No fixes listed on clip chain_qa / drift / seam[/dim]")

        prompt = plan.get("fix_prompt") or ""
        console.print(Panel(
            prompt[:4000] + ("…" if len(prompt) > 4000 else ""),
            title=f"regen fix_prompt — {clip}",
            border_style="yellow" if plan["allowed"] else "red",
        ))

        # Plan is free: store last prompt for inspect without status → regen_ready
        ensure_clip_regen(target, seq)
        target["regen_fix_prompt"] = prompt
        target["regen"]["last_plan_at"] = (
            datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        )
        save_sequence(seq)
        console.print(f"[dim]Saved regen_fix_prompt on {clip} (status unchanged)[/dim]")

    @regen_app.command("apply")
    def regen_apply(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Clip ID to apply re-gen plan"),
        beat: str = typer.Option(None, "--beat", "-b", help="Optional narrative beat override"),
        character: str = typer.Option("", "--character", help="DNA inject block text"),
    ):
        """Write fix prompt onto clip as prompt (status=regen_ready). No Imagine call."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)
        prev = _previous_clip(seq, target)
        plan = apply_regen_plan(
            seq,
            target,
            previous_clip=prev,
            next_beat=beat,
            character_injection=character or "",
        )
        save_sequence(seq)
        console.print(
            f"[green]Applied re-gen plan → {clip} status={target.get('status')}[/green] "
            f"(attempts {plan['attempts']}/{plan['max_attempts']}, budget not consumed)"
        )
        if not plan["allowed"]:
            console.print(
                f"[yellow]Warning: re-gen currently blocked — {plan['reason']}[/yellow]"
            )

    @regen_app.command("run")
    def regen_run(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Clip ID to re-generate"),
        beat: str = typer.Option(None, "--beat", "-b", help="Optional narrative beat override"),
        character: str = typer.Option("", "--character", help="DNA inject block text"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Force mock generation (no API key)"),
        force: bool = typer.Option(
            False, "--force", help="Run even if last chain QA decision was go"
        ),
    ):
        """Consume one attempt and call run_sequence_clip with the fix prompt."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)
        prev = _previous_clip(seq, target)

        decision = (target.get("chain_qa") or {}).get("decision")
        if decision == "go" and not force:
            console.print(
                "[yellow]Last decision is go — use --force to re-gen anyway[/yellow]"
            )
            raise typer.Exit(1)

        try:
            plan = prepare_regen_run(
                seq,
                target,
                previous_clip=prev,
                next_beat=beat,
                character_injection=character or "",
            )
        except ValueError as exc:
            console.print(f"[red]Re-gen blocked:[/red] {exc}")
            raise typer.Exit(1) from exc

        save_sequence(seq)  # persist counters before API

        use_dry = dry_run or is_dry_run()
        if use_dry:
            console.print("[dim]Dry-run mode — mock URLs and auto chain QA[/dim]")

        try:
            result = run_sequence_clip(seq, clip, dry_run=use_dry)
        except RuntimeError as exc:
            console.print(f"[red]Blocked:[/red] {exc}")
            raise typer.Exit(1) from exc
        except Exception as exc:
            console.print(f"[red]Re-gen run failed:[/red] {exc}")
            raise typer.Exit(1) from exc

        save_sequence(seq)

        decision_color = {
            "go": "green",
            "conditional_go": "yellow",
            "no_go": "red",
            "awaiting_scores": "dim",
            "pending": "dim",
        }.get(result.get("chain_qa", {}).get("decision", ""), "white")

        console.print(Panel(
            f"Re-gen attempt: {plan['attempts'] + 1}/{plan['max_attempts']} "
            f"(sequence used: {seq.get('regen_budget', {}).get('sequence_attempts_used', '?')})\n"
            f"Job: {result.get('job_id')}\n"
            f"Clip: {result.get('clip_id')} → {result.get('status')}\n"
            f"URL: {result.get('result_url') or '—'}\n"
            f"Chain QA: [{decision_color}]{result.get('chain_qa', {}).get('decision', 'pending')}"
            f"[/{decision_color}] "
            f"(score: {result.get('chain_qa', {}).get('weighted_score', 'N/A')})\n"
            f"Sequence health: {result.get('sequence_health')} | Status: {result.get('chain_qa_status')}",
            title=f"Sequence Re-gen Run — {seq['sequence_name']}",
            border_style="green" if result.get("status") == "approved" else "yellow",
        ))

    temp_app = typer.Typer(help="Emotional temperature curve gate (roadmap #7)")
    app.add_typer(temp_app, name="temp")

    @temp_app.command("set")
    def temp_set(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        index: int = typer.Option(..., "--index", "-i", help="Clip index for this curve point"),
        temp: float = typer.Option(..., "--temp", "-t", help="Planned emotional temperature 0–10"),
        label: str = typer.Option("", "--label", help="Optional emotion label"),
        beat: str = typer.Option("", "--beat", help="Optional narrative beat"),
    ):
        """Upsert a curve point for a clip index."""
        from emotional_temperature import normalize_curve

        seq = require_sequence(name)
        raw = list(seq.get("emotional_temperature_curve") or [])
        # Drop existing points for this index (upsert)
        kept: list = []
        for item in raw:
            if isinstance(item, dict):
                idx = item.get("index", item.get("i"))
                try:
                    if idx is not None and int(idx) == index:
                        continue
                except (TypeError, ValueError):
                    pass
            kept.append(item)

        point: dict = {"index": index, "temp": temp}
        if label and str(label).strip():
            point["label"] = str(label).strip()
        if beat and str(beat).strip():
            point["beat"] = str(beat).strip()
        kept.append(point)

        curve = normalize_curve(kept)
        seq["emotional_temperature_curve"] = curve
        save_sequence(seq)

        label_s = f" label={point.get('label')}" if point.get("label") else ""
        beat_s = f" beat={point.get('beat')}" if point.get("beat") else ""
        console.print(
            f"[green]Curve point set:[/green] index={index} temp={temp}{label_s}{beat_s} "
            f"({len(curve)} points total)"
        )

    @temp_app.command("show")
    def temp_show(name: str = typer.Argument(..., help="Sequence name or slug")):
        """Show normalized emotional temperature curve."""
        from emotional_temperature import normalize_curve

        seq = require_sequence(name)
        curve = normalize_curve(seq.get("emotional_temperature_curve"))
        seq["emotional_temperature_curve"] = curve

        if not curve:
            console.print("[yellow]No emotional_temperature_curve points set.[/yellow]")
            console.print(
                "[dim]Use: sequence temp set <name> --index N --temp T [--label ...] [--beat ...][/dim]"
            )
            return

        table = Table(
            title=f"Emotional temperature curve — {seq.get('sequence_name', name)}",
            box=box.ROUNDED,
        )
        table.add_column("Index", style="cyan")
        table.add_column("Temp", style="bold")
        table.add_column("Label", style="white")
        table.add_column("Beat", style="dim")
        for p in curve:
            table.add_row(
                str(p.get("index")),
                f"{float(p.get('temp', 0)):.1f}",
                str(p.get("label") or "—"),
                str(p.get("beat") or "—"),
            )
        console.print(table)
        console.print(Panel(json.dumps(curve, indent=2)[:3000], title="normalized curve", border_style="cyan"))

    @temp_app.command("gate")
    def temp_gate(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(..., "--clip", "-c", help="Clip ID to evaluate"),
        strict: bool = typer.Option(
            False, "--strict", help="Exit 1 if gate does not pass (severity fail)"
        ),
    ):
        """Evaluate temperature gate for a clip."""
        from emotional_temperature import evaluate_temperature_gate

        seq = require_sequence(name)
        target = require_clip(seq, clip)
        prev = _previous_clip(seq, target)
        report = evaluate_temperature_gate(seq, target, previous_clip=prev)
        target["temperature_gate"] = report
        save_sequence(seq)

        passed = report.get("pass", False)
        severity = report.get("severity", "ok")
        style = {"ok": "green", "warn": "yellow", "fail": "red"}.get(severity, "white")
        planned = report.get("planned_temp")
        observed = report.get("observed_temp")
        delta = report.get("delta")

        def _fmt(v: float | None) -> str:
            return f"{v:.2f}" if v is not None else "—"

        console.print(
            Panel(
                f"Pass: [{style}]{passed}[/{style}] | Severity: [{style}]{severity}[/{style}]\n"
                f"Planned: {_fmt(planned)} | Observed: {_fmt(observed)} | Delta: {_fmt(delta)}\n"
                f"Flags: {', '.join(report.get('flags') or []) or '—'}\n"
                f"Suggested emotion score: {report.get('suggested_emotion_score', '—')}",
                title=f"Temperature gate — {clip}",
                border_style=style,
            )
        )
        factors = report.get("factors") or []
        if factors:
            for f in factors:
                console.print(f"  [dim]•[/dim] {f}")
        fixes = report.get("fixes") or []
        if fixes:
            console.print("[bold]Fixes:[/bold]")
            for fix in fixes:
                console.print(f"  → {fix}")

        console.print(f"[dim]Stored temperature_gate on {clip}[/dim]")
        if strict and not passed:
            raise typer.Exit(1)

    cast_app = typer.Typer(help="Multi-character identity arbitration (roadmap #8)")
    app.add_typer(cast_app, name="cast")

    def _parse_cast_slugs(characters: str) -> list[str]:
        return [s.strip() for s in characters.split(",") if s.strip()]

    def _parse_cast_weights(weights: str | None) -> dict[str, float] | None:
        if not weights or not str(weights).strip():
            return None
        out: dict[str, float] = {}
        for part in str(weights).split(","):
            part = part.strip()
            if not part:
                continue
            if "=" not in part:
                console.print(f"[red]Invalid weight entry (expected slug=0.7): {part}[/red]")
                raise typer.Exit(1)
            slug, raw = part.split("=", 1)
            slug = slug.strip()
            try:
                out[slug] = float(raw.strip())
            except ValueError as exc:
                console.print(f"[red]Invalid weight value for '{slug}': {raw}[/red]")
                raise typer.Exit(1) from exc
        return out or None

    def _print_cast_plan(plan: dict) -> None:
        style = "green" if plan.get("pass") else "red"
        console.print(
            Panel(
                f"Pass: [{style}]{plan.get('pass')}[/{style}]\n"
                f"Primary: {plan.get('primary_name') or '—'} "
                f"({plan.get('primary_slug') or '—'})\n"
                f"Cast: {len(plan.get('cast') or [])} | "
                f"Rules: {', '.join(plan.get('rules_applied') or []) or '—'}",
                title="Cast arbitration",
                border_style=style,
            )
        )
        cast = plan.get("cast") or []
        if cast:
            table = Table(title="Cast", box=box.ROUNDED)
            table.add_column("Role", style="cyan")
            table.add_column("Slug", style="white")
            table.add_column("Name")
            table.add_column("Weight", justify="right")
            table.add_column("Locked")
            for entry in cast:
                table.add_row(
                    str(entry.get("role") or "—"),
                    str(entry.get("slug") or "—"),
                    str(entry.get("name") or "—"),
                    f"{float(entry.get('ref_weight', 0)):.2f}",
                    "yes" if entry.get("locked") else "no",
                )
            console.print(table)
        conflicts = plan.get("conflicts") or []
        if conflicts:
            console.print("[bold]Conflicts:[/bold]")
            for c in conflicts:
                sev = c.get("severity", "info")
                color = {"error": "red", "warn": "yellow", "info": "dim"}.get(sev, "white")
                console.print(
                    f"  [{color}]{sev}[/{color}] {c.get('code', '?')}: {c.get('message', '')}"
                )
        else:
            console.print("[dim]No conflicts[/dim]")

    def _arbitrate_from_options(
        characters: str,
        primary: str | None,
        weights: str | None,
    ) -> dict:
        from multi_character_arbiter import arbitrate_cast, load_cast_dnas

        slugs = _parse_cast_slugs(characters)
        if not slugs:
            console.print("[red]--characters requires at least one slug[/red]")
            raise typer.Exit(1)
        weight_map = _parse_cast_weights(weights)
        try:
            dnas = load_cast_dnas(slugs)
        except ValueError as exc:
            console.print(f"[red]{exc}[/red]")
            raise typer.Exit(1) from exc
        return arbitrate_cast(dnas, primary_slug=primary, weights=weight_map)

    @cast_app.command("arbitrate")
    def cast_arbitrate(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        characters: str = typer.Option(
            ..., "--characters", "-c", help="Comma-separated character DNA slugs"
        ),
        primary: str = typer.Option(
            None, "--primary", "-p", help="Primary slug (default: first character)"
        ),
        weights: str = typer.Option(
            None, "--weights", help="Explicit weights: slug=0.7,other=0.3"
        ),
        save: bool = typer.Option(True, "--save/--no-save", help="Persist plan on sequence"),
    ):
        """Arbitrate cast lock for a sequence; store on sequence.cast_arbitration."""
        seq = require_sequence(name)
        plan = _arbitrate_from_options(characters, primary, weights)
        _print_cast_plan(plan)

        if save:
            seq["cast_arbitration"] = plan
            # Optional: ensure memory bank cast entries exist for each cast member
            bank = seq.get("memory_bank")
            if isinstance(bank, dict):
                cast_bank = bank.setdefault("cast", {})
                if isinstance(cast_bank, dict):
                    for entry in plan.get("cast") or []:
                        slug = entry.get("slug")
                        if slug and slug not in cast_bank:
                            cast_bank[slug] = {
                                "slug": slug,
                                "name": entry.get("name") or slug,
                                "role": entry.get("role"),
                                "ref_weight": entry.get("ref_weight"),
                            }
            path = save_sequence(seq)
            console.print(f"[green]✅ Saved cast_arbitration on sequence:[/green] {path}")
        else:
            console.print("[dim]--no-save: plan not written to sequence[/dim]")

    @cast_app.command("inject")
    def cast_inject(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        characters: str = typer.Option(
            None, "--characters", "-c", help="Comma-separated slugs (or use saved plan)"
        ),
        primary: str = typer.Option(
            None, "--primary", "-p", help="Primary slug (with --characters)"
        ),
        weights: str = typer.Option(
            None, "--weights", help="Explicit weights: slug=0.7,other=0.3"
        ),
        output: str = typer.Option(None, "--output", "-o", help="Write inject block to file"),
    ):
        """Print multi-character inject block (from saved plan or fresh arbitrate)."""
        seq = require_sequence(name)

        if characters:
            plan = _arbitrate_from_options(characters, primary, weights)
        else:
            plan = seq.get("cast_arbitration")
            if not plan or not isinstance(plan, dict):
                console.print(
                    "[red]No saved cast_arbitration on sequence. "
                    "Run: sequence cast arbitrate <name> -c slug1,slug2 "
                    "or pass --characters[/red]"
                )
                raise typer.Exit(1)

        inject_block = plan.get("inject_block") or ""
        if not inject_block and plan.get("cast"):
            from multi_character_arbiter import build_multi_inject

            inject_block = build_multi_inject(
                plan["cast"],
                plan.get("primary_slug") or "",
            )

        if output:
            out_path = Path(output)
            out_path.write_text(inject_block)
            console.print(f"[green]✅ Inject block saved:[/green] {out_path}")
        else:
            console.print(
                Panel(
                    inject_block or "[empty]",
                    title="Multi-character inject block",
                    border_style="cyan",
                )
            )

    # --- Stitch artifact lexicon (roadmap #11) ---
    lex_app = typer.Typer(help="Stitch artifact lexicon (roadmap #11)")
    app.add_typer(lex_app, name="artifact-lexicon")

    @lex_app.command("list")
    def artifact_lexicon_list(
        category: str = typer.Option(
            None, "--category", "-c", help="Filter by category (temporal, identity, …)"
        ),
        markdown: bool = typer.Option(
            False, "--markdown", "-m", help="Print full markdown catalog"
        ),
    ):
        """List stitch artifact lexicon entries (ids, names, categories)."""
        if markdown:
            ids = None
            if category:
                ids = [e["id"] for e in list_entries(category=category)]
            console.print(Markdown(format_lexicon_markdown(ids)))
            return

        entries = list_entries(category=category)
        if not entries:
            console.print(
                f"[yellow]No lexicon entries"
                f"{f' for category={category}' if category else ''}[/yellow]"
            )
            return
        table = Table(title="Stitch Artifact Lexicon", box=box.ROUNDED)
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="white")
        table.add_column("Category", style="yellow")
        table.add_column("Aliases", style="dim")
        for e in entries:
            aliases = ", ".join(e.get("aliases") or [])
            table.add_row(
                e["id"],
                e.get("name") or "",
                e.get("category") or "",
                aliases[:60] + ("…" if len(aliases) > 60 else ""),
            )
        console.print(table)

    @lex_app.command("pack")
    def artifact_lexicon_pack(
        tags: str = typer.Option(
            None,
            "--tags",
            "-t",
            help="Comma-separated entry ids (e.g. flicker,morph,halo)",
        ),
        all_entries: bool = typer.Option(
            False,
            "--all",
            help="Use default core pack (flicker, morph, halo, …)",
        ),
        positives: bool = typer.Option(
            False,
            "--positives",
            "-p",
            help="Also print positive guard phrases",
        ),
    ):
        """Build negative phrase pack (and optional positive guards) from lexicon tags."""
        if not tags and not all_entries:
            console.print(
                "[red]Provide --tags a,b or --all for the default core pack[/red]"
            )
            raise typer.Exit(1)
        if tags and all_entries:
            console.print(
                "[yellow]Both --tags and --all given; using --tags only[/yellow]"
            )

        entry_ids: list[str] | None = None
        if tags:
            entry_ids = [t.strip() for t in tags.split(",") if t.strip()]
            pack = build_negative_pack(entry_ids, all_default=False)
            guard_ids = entry_ids
        else:
            pack = build_negative_pack(None, all_default=True)
            guard_ids = None

        if not pack:
            console.print("[yellow]Empty pack (unknown tags or no phrases)[/yellow]")
        else:
            console.print(Panel(pack, title="NEGATIVES pack", border_style="red"))

        if positives:
            guards = build_positive_guards(guard_ids)
            if guards:
                console.print(
                    Panel(guards, title="POSITIVE guards", border_style="green")
                )
            else:
                console.print("[dim]No positive guards resolved[/dim]")

    @lex_app.command("suggest")
    def artifact_lexicon_suggest(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(
            ..., "--clip", "-c", help="Clip ID with seam_report / chain_qa"
        ),
        positives: bool = typer.Option(
            False, "--positives", "-p", help="Also print positive guards"
        ),
    ):
        """Suggest lexicon tags from clip seam_report + chain_qa; print tags + pack."""
        seq = require_sequence(name)
        target = require_clip(seq, clip)
        seam = target.get("seam_report")
        qa = target.get("chain_qa")

        tags = list(
            dict.fromkeys(
                suggest_entries_from_seam(seam if isinstance(seam, dict) else None)
                + suggest_entries_from_chain_qa(qa if isinstance(qa, dict) else None)
            )
        )
        pack = build_negative_pack(tags if tags else None, all_default=not tags)

        if tags:
            console.print(f"[cyan]Suggested tags:[/cyan] {', '.join(tags)}")
        else:
            console.print(
                "[dim]No tags from seam_report/chain_qa — using default core pack[/dim]"
            )

        if pack:
            console.print(Panel(pack, title="NEGATIVES pack", border_style="red"))
        else:
            console.print("[yellow]Empty pack[/yellow]")

        if positives:
            guards = build_positive_guards(tags if tags else None)
            if guards:
                console.print(
                    Panel(guards, title="POSITIVE guards", border_style="green")
                )

    replan_app = typer.Typer(help="Arc replan co-pilot (roadmap #12)")
    app.add_typer(replan_app, name="replan")

    @replan_app.command("plan")
    def replan_plan(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(
            None, "--clip", "-c", help="Clip ID to start replan from"
        ),
        from_index: int = typer.Option(
            None, "--from-index", help="Clip index to start replan from"
        ),
        reason: str = typer.Option(
            None, "--reason", help="Replan reason override (e.g. chain_qa_no_go)"
        ),
    ):
        """Build arc replan proposal (plan only; does not mutate beats/curve)."""
        from arc_replan import format_arc_replan_markdown, plan_arc_replan

        seq = require_sequence(name)
        try:
            proposal = plan_arc_replan(
                seq,
                from_index=from_index,
                from_clip_id=clip,
                reason=reason,
            )
        except ValueError as exc:
            console.print(f"[red]Replan plan failed:[/red] {exc}")
            raise typer.Exit(1) from exc

        md = format_arc_replan_markdown(proposal)
        console.print(
            Panel(Markdown(md), title="Arc replan proposal", border_style="cyan")
        )
        console.print(f"[cyan]{proposal.get('summary', '')}[/cyan]")
        for alert in proposal.get("alerts") or []:
            console.print(f"[yellow]Alert:[/yellow] {alert}")

        # Plan only: store proposal; do not apply beats / curve
        seq["arc_replan_proposal"] = proposal
        path = save_sequence(seq)
        console.print(
            f"[dim]Saved arc_replan_proposal (beats/curve not applied) → {path}[/dim]"
        )

    @replan_app.command("apply")
    def replan_apply(
        name: str = typer.Argument(..., help="Sequence name or slug"),
        clip: str = typer.Option(
            None, "--clip", "-c", help="Clip ID to start replan from"
        ),
        from_index: int = typer.Option(
            None, "--from-index", help="Clip index to start replan from"
        ),
        reason: str = typer.Option(
            None, "--reason", help="Replan reason override (e.g. chain_qa_no_go)"
        ),
        yes: bool = typer.Option(
            False, "--yes", "-y", help="Suppress apply notice (always applies)"
        ),
    ):
        """Plan then apply arc replan (mutates narrative beats + temperature curve)."""
        from arc_replan import (
            apply_arc_replan,
            format_arc_replan_markdown,
            plan_arc_replan,
        )

        seq = require_sequence(name)
        try:
            proposal = plan_arc_replan(
                seq,
                from_index=from_index,
                from_clip_id=clip,
                reason=reason,
            )
        except ValueError as exc:
            console.print(f"[red]Replan apply failed:[/red] {exc}")
            raise typer.Exit(1) from exc

        md = format_arc_replan_markdown(proposal)
        console.print(
            Panel(Markdown(md), title="Arc replan proposal", border_style="yellow")
        )
        console.print(f"[cyan]{proposal.get('summary', '')}[/cyan]")
        for alert in proposal.get("alerts") or []:
            console.print(f"[yellow]Alert:[/yellow] {alert}")

        if not yes:
            console.print(
                "[yellow]Applying replan (use --yes to suppress this notice). "
                "Mutates narrative beats + emotional_temperature_curve.[/yellow]"
            )

        seq["arc_replan_proposal"] = proposal
        apply_arc_replan(seq, proposal)
        path = save_sequence(seq)
        n = len(proposal.get("replanned_clips") or [])
        console.print(
            f"[green]Applied arc replan from index {proposal.get('from_index')} "
            f"({proposal.get('reason')}): {n} clip(s) → {path}[/green]"
        )
