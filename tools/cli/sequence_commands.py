"""Sequence chain CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from quota_optimizer import estimate_sequence_cost
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