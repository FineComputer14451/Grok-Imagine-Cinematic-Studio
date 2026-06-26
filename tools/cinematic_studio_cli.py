#!/usr/bin/env python3
"""
Grok Imagine Cinematic Studio CLI v3.6.5 — Enhanced Edition
Professional multi-agent cinematic production toolkit with Role Card integration
"""

import os
import sys
import typer
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))
from studio_paths import STUDIO_ROOT  # noqa: E402

os.chdir(STUDIO_ROOT)
from character_dna import (  # noqa: E402
    PROMPT_MODES,
    build_handoff_packet,
    build_prompt_blocks,
    create_dna_scaffold,
    find_character_dna,
    inject_into_prompt,
    list_characters,
    load_character_dna,
    lock_to_identity_bank,
    save_character_dna,
    validate_dna,
)
from sequence_chain import (  # noqa: E402
    CHAIN_QA_CHECKS,
    add_clip_to_sequence,
    build_extend_prompt,
    build_handoff_from_clip,
    create_clip,
    create_sequence_scaffold,
    find_sequence,
    get_clip,
    list_sequences,
    load_sequence,
    run_chain_qa,
    save_sequence,
    sequence_to_markdown,
    update_sequence_health,
)
from project_state import load_project_state, save_project_state  # noqa: E402
from quota_optimizer import (  # noqa: E402
    SUBSCRIPTION_TIERS,
    assess_budget_risk,
    estimate_clip_cost,
    estimate_production,
    estimate_sequence_cost,
    get_optimization_recommendations,
    quota_dashboard,
    record_spend,
    set_budget,
)
from cli.bible_commands import register as register_bible_commands  # noqa: E402
from cli.models_commands import models_app  # noqa: E402
from cli.shared import AGENTS_DIR, STUDIO_VERSION, console  # noqa: E402
from cli.studio_commands import register as register_studio_commands  # noqa: E402
from nsfw_orchestrator import (  # noqa: E402
    batch_to_markdown,
    decide_generation_mode,
    generate_daily_report,
    get_next_shots,
    list_batches,
    load_batch,
    plan_batch,
    record_shot_result,
    save_batch,
    suggest_retry,
)
from nsfw_sequence_extender import (  # noqa: E402
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
from models import DEFAULT_IMAGINE_VIDEO_MODEL  # noqa: E402
from rich import box
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

try:
    from fpdf import FPDF
except ImportError:
    print("⚠️  fpdf2 not installed. Run: pip install fpdf2 rich typer")
    exit(1)

app = typer.Typer(
    name="cinematic-studio",
    help="🎥 Grok Imagine Cinematic Studio v3.6 — Full 23-Agent Cinematic Production CLI",
    add_completion=False,
    rich_markup_mode="rich"
)

dna_app = typer.Typer(help="Character DNA extraction, Identity Lock handoff, and prompt injection")
app.add_typer(dna_app, name="dna")

seq_app = typer.Typer(help="Long-form 1.5 extend/stitch sequencing, handoffs, and chain QA")
app.add_typer(seq_app, name="sequence")

quota_app = typer.Typer(help="Per-second 1.5 quota estimation, budgeting, and optimization")
app.add_typer(quota_app, name="quota")

app.add_typer(models_app, name="models")

register_studio_commands(app)
register_bible_commands(app)

nsfw_app = typer.Typer(help="Quota-aware NSFW batch planning, sequence extension, and daily reports")
app.add_typer(nsfw_app, name="nsfw")

extend_app = typer.Typer(help="Sensual sequence extension 30-120s+ from reference frame or short clip")
nsfw_app.add_typer(extend_app, name="extend")

# ============================================================
# CHARACTER DNA COMMANDS
# ============================================================

@dna_app.command("init")
def dna_init(
    name: str = typer.Argument(..., help="Character name"),
    core_identity: str = typer.Option("", "--core", help="Core identity description"),
    facial_dna: str = typer.Option("", "--facial", help="Facial DNA description"),
    hair: str = typer.Option("", "--hair", help="Hair & grooming"),
    clothing: str = typer.Option("", "--clothing", help="Clothing & style"),
    movement: str = typer.Option("", "--movement", help="Movement & posture"),
    emotion: str = typer.Option("", "--emotion", help="Emotional baseline"),
    motion: str = typer.Option("", "--motion", help="Motion DNA for video"),
    anchor: list[str] = typer.Option(None, "--anchor", help="Key consistency anchor (repeatable)"),
    output: str = typer.Option(None, "--output", "-o", help="Output dna.json path"),
):
    """Create a new Character DNA profile scaffold."""
    dna = create_dna_scaffold(
        name,
        core_identity=core_identity,
        facial_dna=facial_dna,
        hair_grooming=hair,
        clothing_style=clothing,
        movement_posture=movement,
        emotional_baseline=emotion,
        motion_dna=motion,
        key_anchors=anchor or [],
        source="cli-init",
    )
    if output:
        out_path = Path(output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(dna, indent=2))
        console.print(f"[green]✅ DNA scaffold created:[/green] {out_path}")
    else:
        json_path, md_path = save_character_dna(dna)
        console.print(f"[green]✅ DNA scaffold created:[/green]")
        console.print(f"  JSON: {json_path}")
        console.print(f"  Markdown: {md_path}")
    console.print("[dim]Edit the profile, then run: dna lock --name \"{name}\"[/dim]".format(name=name))

@dna_app.command("save")
def dna_save(
    file: Path = typer.Option(..., "--file", "-f", help="Path to dna.json to validate and persist"),
):
    """Validate and save a Character DNA profile to characters/{slug}/."""
    dna = load_character_dna(file)
    json_path, md_path = save_character_dna(dna)
    console.print(f"[green]✅ DNA saved:[/green] {json_path}")
    console.print(f"[dim]Markdown:[/dim] {md_path}")

@dna_app.command("list")
def dna_list():
    """List all Character DNA profiles."""
    chars = list_characters()
    if not chars:
        console.print("[yellow]No Character DNA profiles yet. Run: dna init \"Character Name\"[/yellow]")
        return
    table = Table(title="🧬 Character DNA Profiles", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Slug", style="dim")
    table.add_column("Version", style="white")
    table.add_column("Lock Status", style="green")
    for c in chars:
        table.add_row(c["name"], c["slug"], str(c["version"]), c["status"])
    console.print(table)

@dna_app.command("show")
def dna_show(
    name: str = typer.Argument(..., help="Character name or slug"),
    mode: str = typer.Option(None, "--mode", "-m", help="Show prompt injection for mode"),
):
    """Display a Character DNA profile or prompt injection block."""
    dna_path = find_character_dna(name)
    if not dna_path:
        console.print(f"[red]No DNA profile found for:[/red] {name}")
        raise typer.Exit(1)
    dna = load_character_dna(dna_path)
    if mode:
        if mode not in PROMPT_MODES:
            console.print(f"[red]Unknown mode. Choose from:[/red] {', '.join(PROMPT_MODES)}")
            raise typer.Exit(1)
        blocks = build_prompt_blocks(dna)
        console.print(Panel(blocks[mode], title=f"Prompt Injection — {mode}", border_style="green"))
    else:
        from character_dna import dna_to_markdown
        console.print(Panel(Markdown(dna_to_markdown(dna)[:4000]), title=f"🧬 {dna['character_name']}", border_style="blue"))

@dna_app.command("handoff")
def dna_handoff(
    name: str = typer.Argument(..., help="Character name or slug"),
    output: str = typer.Option(None, "--output", "-o", help="Output handoff.json path"),
):
    """Generate Identity Lock handoff packet from DNA profile."""
    dna_path = find_character_dna(name)
    if not dna_path:
        console.print(f"[red]No DNA profile found for:[/red] {name}")
        raise typer.Exit(1)
    dna = load_character_dna(dna_path)
    handoff = build_handoff_packet(dna)
    out_path = Path(output) if output else dna_path.parent / "handoff.json"
    out_path.write_text(json.dumps(handoff, indent=2))
    console.print(f"[green]✅ Handoff packet created:[/green] {out_path}")
    console.print("[dim]Next: dna lock --name \"{name}\"[/dim]".format(name=dna["character_name"]))

@dna_app.command("lock")
def dna_lock(
    name: str = typer.Argument(..., help="Character name or slug"),
):
    """Import DNA into Identity Lock memory bank."""
    dna_path = find_character_dna(name)
    if not dna_path:
        console.print(f"[red]No DNA profile found for:[/red] {name}")
        raise typer.Exit(1)
    dna = load_character_dna(dna_path)
    state = lock_to_identity_bank(dna)
    console.print(f"[green]✅ Identity Lock engaged for[/green] {dna['character_name']}")
    console.print(f"[dim]Status: locked | Drift threshold: 2.5 | Anchors: {len(dna.get('key_consistency_anchors', []))}[/dim]")
    console.print(f"[dim]Identity Lock entries: {len(state.get('identity_lock', {}))}[/dim]")

@dna_app.command("inject")
def dna_inject(
    name: str = typer.Argument(..., help="Character name or slug"),
    mode: str = typer.Option("cinematic", "--mode", "-m", help="Injection mode"),
    base_prompt: str = typer.Option("", "--base", "-b", help="Base prompt to prepend injection onto"),
    output: str = typer.Option(None, "--output", "-o", help="Save injected prompt to file"),
):
    """Generate CHARACTER_DNA prompt injection for Imagine Prompt Master."""
    try:
        result = inject_into_prompt(base_prompt, name, mode)
    except FileNotFoundError:
        console.print(f"[red]No DNA profile found for:[/red] {name}")
        raise typer.Exit(1)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1)
    if output:
        Path(output).write_text(result)
        console.print(f"[green]✅ Injected prompt saved:[/green] {output}")
    else:
        console.print(Panel(result, title=f"Prompt Injection — {mode}", border_style="green"))

# ============================================================
# SEQUENCE CHAIN COMMANDS
# ============================================================

@seq_app.command("init")
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

@seq_app.command("list")
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

@seq_app.command("show")
def seq_show(name: str = typer.Argument(..., help="Sequence name or slug")):
    """Display sequence blueprint."""
    seq_path = find_sequence(name)
    if not seq_path:
        console.print(f"[red]Sequence not found:[/red] {name}")
        raise typer.Exit(1)
    seq = load_sequence(seq_path)
    console.print(Panel(Markdown(sequence_to_markdown(seq)[:5000]), title=f"🎬 {seq['sequence_name']}", border_style="blue"))

@seq_app.command("add-clip")
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
    seq_path = find_sequence(name)
    if not seq_path:
        console.print(f"[red]Sequence not found:[/red] {name}")
        raise typer.Exit(1)
    seq = load_sequence(seq_path)
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

@seq_app.command("handoff")
def seq_handoff(
    name: str = typer.Argument(..., help="Sequence name or slug"),
    clip: str = typer.Option(..., "--clip", "-c", help="Source clip ID"),
    output: str = typer.Option(None, "--output", "-o"),
):
    """Generate extend/stitch handoff packet from a clip."""
    seq_path = find_sequence(name)
    if not seq_path:
        console.print(f"[red]Sequence not found:[/red] {name}")
        raise typer.Exit(1)
    seq = load_sequence(seq_path)
    source = get_clip(seq, clip)
    if not source:
        console.print(f"[red]Clip not found:[/red] {clip}")
        raise typer.Exit(1)
    handoff = build_handoff_from_clip(source)
    out_path = Path(output) if output else seq_path.parent / f"handoff_{clip}.json"
    out_path.write_text(json.dumps(handoff, indent=2))
    console.print(f"[green]✅ Handoff packet:[/green] {out_path}")
    console.print(Panel(json.dumps(handoff, indent=2)[:2000], title="Handoff Preview", border_style="cyan"))

@seq_app.command("extend-prompt")
def seq_extend_prompt(
    name: str = typer.Argument(..., help="Sequence name or slug"),
    clip: str = typer.Option(..., "--clip", "-c", help="Previous clip ID"),
    beat: str = typer.Option(..., "--beat", "-b", help="Next narrative beat"),
    character: str = typer.Option("", "--character", help="CHARACTER_DNA injection block"),
    output: str = typer.Option(None, "--output", "-o"),
):
    """Build Grok Imagine Video 1.5 extend prompt for the next clip."""
    seq_path = find_sequence(name)
    if not seq_path:
        console.print(f"[red]Sequence not found:[/red] {name}")
        raise typer.Exit(1)
    seq = load_sequence(seq_path)
    source = get_clip(seq, clip)
    if not source:
        console.print(f"[red]Clip not found:[/red] {clip}")
        raise typer.Exit(1)
    prompt = build_extend_prompt(seq, source, beat, character_injection=character)
    if output:
        Path(output).write_text(prompt)
        console.print(f"[green]✅ Extend prompt saved:[/green] {output}")
    else:
        console.print(Panel(prompt, title="1.5 Extend Prompt", border_style="green"))

@seq_app.command("qa")
def seq_qa(
    name: str = typer.Argument(..., help="Sequence name or slug"),
    clip: str = typer.Option(..., "--clip", "-c", help="Clip ID to evaluate"),
    scores: str = typer.Option(None, "--scores", "-s", help="JSON dict of chain QA scores (1-10 each)"),
):
    """Run chain QA gate on a clip (extend/stitch checks)."""
    seq_path = find_sequence(name)
    if not seq_path:
        console.print(f"[red]Sequence not found:[/red] {name}")
        raise typer.Exit(1)
    seq = load_sequence(seq_path)
    target = get_clip(seq, clip)
    if not target:
        console.print(f"[red]Clip not found:[/red] {clip}")
        raise typer.Exit(1)

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

@seq_app.command("estimate-cost")
def seq_estimate_cost(
    name: str = typer.Argument(..., help="Sequence name or slug"),
    fast_mode: bool = typer.Option(False, "--fast-mode"),
    quality_pass: bool = typer.Option(False, "--quality-pass"),
):
    """Estimate quota cost for a sequence blueprint."""
    seq_path = find_sequence(name)
    if not seq_path:
        console.print(f"[red]Sequence not found:[/red] {name}")
        raise typer.Exit(1)
    seq = load_sequence(seq_path)
    est = estimate_sequence_cost(
        seq.get("clips", []),
        fast_mode=fast_mode,
        quality_pass=quality_pass,
    )
    state = load_project_state()
    quota = state.get("quota", {})
    risk = assess_budget_risk(est, tier=quota.get("tier", "supergrok_pro"), budget_remaining=quota.get("budget_remaining"))
    console.print(Panel(
        f"Clips: {est['clip_count']} | Duration: {est['total_duration_seconds']}s\n"
        f"Credits: {est['credits_low']} – {est['credits_high']}\n"
        f"USD: ${est['usd_low']} – ${est['usd_high']}\n"
        f"Risk: {risk['risk_level']} ({risk.get('budget_pct_used', 'N/A')}% of budget)",
        title=f"💰 {seq['sequence_name']}",
        border_style="green",
    ))

@seq_app.command("health")
def seq_health(name: str = typer.Argument(..., help="Sequence name or slug")):
    """Show sequence health score and chain QA status."""
    seq_path = find_sequence(name)
    if not seq_path:
        console.print(f"[red]Sequence not found:[/red] {name}")
        raise typer.Exit(1)
    seq = load_sequence(seq_path)
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

# ============================================================
# QUOTA OPTIMIZER COMMANDS
# ============================================================

@quota_app.command("estimate")
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
    state = load_project_state()
    quota = state.get("quota", {})
    risk = assess_budget_risk(est, tier=quota.get("tier", "supergrok_pro"), budget_remaining=quota.get("budget_remaining"))

    table = Table(title="💰 Quota Estimate — Imagine Video", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Target Duration", f"{duration}s")
    table.add_row("Video Model", est.get("video_model", video_model))
    table.add_row("Clips", str(est["clip_count"]))
    table.add_row("Avg Clip", f"{est['avg_clip_duration']}s")
    table.add_row("Resolution", resolution)
    table.add_row("Fast Mode", str(fast_mode))
    table.add_row("Quality Pass", str(quality_pass))
    table.add_row("Credits", f"{est['credits_low']} – {est['credits_high']}")
    table.add_row("USD", f"${est['usd_low']} – ${est['usd_high']}")
    table.add_row("Est. Tokens", f"~{est['estimated_tokens']:,}")
    table.add_row("Risk Level", risk["risk_level"])
    console.print(table)

@quota_app.command("clip")
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

@quota_app.command("sequence")
def quota_sequence(
    name: str = typer.Argument(..., help="Sequence name or slug"),
    fast_mode: bool = typer.Option(False, "--fast-mode"),
    quality_pass: bool = typer.Option(False, "--quality-pass"),
):
    """Estimate quota cost for an existing sequence blueprint."""
    seq_path = find_sequence(name)
    if not seq_path:
        console.print(f"[red]Sequence not found:[/red] {name}")
        raise typer.Exit(1)
    seq = load_sequence(seq_path)
    est = estimate_sequence_cost(seq.get("clips", []), fast_mode=fast_mode, quality_pass=quality_pass)
    state = load_project_state()
    quota = state.get("quota", {})
    risk = assess_budget_risk(est, tier=quota.get("tier", "supergrok_pro"), budget_remaining=quota.get("budget_remaining"))
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

@quota_app.command("dashboard")
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

@quota_app.command("budget")
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

@quota_app.command("record")
def quota_record(
    credits: float = typer.Argument(..., help="Credits spent"),
    note: str = typer.Option("", "--note", "-n"),
):
    """Record generation spend to session tracker."""
    quota = record_spend(credits, note=note)
    console.print(f"[green]✅ Recorded {credits} credits[/green] (session total: {quota['session_spent']})")
    if quota.get("budget_remaining") is not None:
        console.print(f"[dim]Remaining: {quota['budget_remaining']} credits[/dim]")

@quota_app.command("optimize")
def quota_optimize(
    duration: int = typer.Option(60, "--duration", "-d"),
    clips: int = typer.Option(None, "--clips", "-n"),
    fast_mode: bool = typer.Option(False, "--fast-mode"),
    complexity: str = typer.Option("medium", "--complexity", "-c"),
):
    """Get quota optimization recommendations for a production plan."""
    est = estimate_production(duration, clip_count=clips, complexity=complexity, fast_mode=fast_mode)
    state = load_project_state()
    quota = state.get("quota", {})
    risk = assess_budget_risk(est, tier=quota.get("tier", "supergrok_pro"), budget_remaining=quota.get("budget_remaining"))
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

# ============================================================
# NSFW QUOTA ORCHESTRATOR COMMANDS
# ============================================================

def _parse_inline_shot(spec: str) -> dict:
    """Parse tier:description or tier:motion:description."""
    parts = spec.split(":", 2)
    if len(parts) == 2:
        tier, desc = parts
        motion = "medium"
    elif len(parts) == 3:
        tier, motion, desc = parts
    else:
        tier, motion, desc = "support", "medium", spec
    return {
        "tier": tier.strip(),
        "description": desc.strip(),
        "motion_complexity": motion.strip(),
    }


@nsfw_app.command("plan")
def nsfw_plan(
    title: str = typer.Argument(..., help="Batch title"),
    file: str = typer.Option(None, "--file", "-f", help="JSON shot list"),
    shot: list[str] = typer.Option(None, "--shot", "-s", help="Inline shot: tier:description or tier:motion:description"),
    budget: float = typer.Option(None, "--budget", "-b", help="Session budget in credits"),
    tier: str = typer.Option("supergrok_heavy", "--tier", "-t"),
    fast_mode: bool = typer.Option(False, "--fast-mode"),
    output: str = typer.Option(None, "--output", "-o", help="Save markdown plan"),
):
    """Plan a prioritized NSFW batch under Heavy subscription limits."""
    shots: list[dict] = []
    if file:
        shots = json.loads(Path(file).read_text())
    if shot:
        for spec in shot:
            shots.append(_parse_inline_shot(spec))
    if not shots:
        console.print("[red]Provide --file or at least one --shot[/red]")
        raise typer.Exit(1)

    batch = plan_batch(title, shots, tier=tier, budget_credits=budget, fast_mode=fast_mode)
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
    shot = {
        "shot_id": shot_id,
        "tier": shot_tier,
        "motion_complexity": motion,
        "has_reference": has_ref,
        "explicit_level": explicit,
        "duration_seconds": duration,
        "consistency_required": True,
    }
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
    shot = {"shot_id": shot_id, "tier": shot_tier, "duration_seconds": 10, "recommended_mode": "image_to_video"}
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


# ============================================================
# NSFW SEQUENCE EXTENDER COMMANDS
# ============================================================

def _load_nsfw_sequence(name: str) -> dict:
    path = find_sequence(name)
    if not path:
        console.print(f"[red]Sequence not found:[/red] {name}")
        raise typer.Exit(1)
    return load_sequence(path)


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
    seq = _load_nsfw_sequence(sequence_name)
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
    seq = _load_nsfw_sequence(sequence_name)
    target = get_clip(seq, clip)
    if not target:
        console.print(f"[red]Clip not found:[/red] {clip}")
        raise typer.Exit(1)

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
    seq = _load_nsfw_sequence(sequence_name)
    target = get_clip(seq, clip)
    if not target:
        console.print(f"[red]Clip not found:[/red] {clip}")
        raise typer.Exit(1)

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
    seq = _load_nsfw_sequence(sequence_name)
    md = nsfw_sequence_to_markdown(seq)
    out = output or f"sequences/{seq['slug']}/extension_plan.md"
    Path(out).write_text(md)
    console.print(f"[green]Exported:[/green] {out}")


@app.command(name="report")
def report(
    output: str = typer.Option("production_report.pdf", "--output", "-o", help="Output PDF filename")
):
    """Generate a basic PDF production report"""
    state = load_project_state()
    project = state.get("project", {})

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=16)
    pdf.cell(0, 10, "Grok Imagine Cinematic Studio — Production Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", size=12)
    project_title = project.get("project_title") or project.get("title", "Untitled")
    pdf.cell(0, 8, f"Project: {project_title}", ln=True)
    pdf.cell(0, 8, f"Genre: {project.get('genre', 'N/A')}", ln=True)
    pdf.cell(0, 8, f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 8, "Status: Production in progress with 23-agent studio", ln=True)

    pdf.output(output)
    console.print(f"[green]✅ PDF Report generated:[/green] {output}")

@app.command(name="validate")
def validate():
    """Run basic local validation (similar to CI)"""
    console.print("[bold]🔍 Running local validation...[/bold]\n")

    issues = 0

    if not AGENTS_DIR.exists():
        console.print("[red]❌ references/agents/ directory missing[/red]")
        issues += 1
    else:
        card_count = len(list(AGENTS_DIR.glob("*.md")))
        console.print(f"[green]✅ Found {card_count} Role Cards in references/agents/[/green]")

    core_files = ["MASTER_PROMPT_v3.6.md", "README.md", "Quick_Start_Guide.md"]
    for f in core_files:
        if (STUDIO_ROOT / f).exists():
            console.print(f"[green]✅ {f} present[/green]")
        else:
            console.print(f"[yellow]⚠️  {f} missing[/yellow]")
            issues += 1

    if issues == 0:
        console.print("\n[bold green]✅ Validation passed[/bold green]")
    else:
        console.print(f"\n[yellow]Validation completed with {issues} issues[/yellow]")

if __name__ == "__main__":
    app()