#!/usr/bin/env python3
"""
Grok Imagine Cinematic Studio CLI v3.6.1 — Enhanced Edition
Professional multi-agent cinematic production toolkit with Role Card integration
"""

import sys
import typer
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent))
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
from quota_optimizer import (  # noqa: E402
    SUBSCRIPTION_TIERS,
    assess_budget_risk,
    estimate_clip_cost,
    estimate_production,
    estimate_sequence_cost,
    get_optimization_recommendations,
    load_project_state as quota_load_state,
    quota_dashboard,
    record_spend,
    set_budget,
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.markdown import Markdown

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

console = Console()

# ============================================================
# CONFIG
# ============================================================
AGENTS_DIR = Path("references/agents")
PROJECT_STATE_FILE = Path(".cinematic_project_state.json")

# Director Signature Presets
DIRECTOR_SIGNATURES = {
    "nolan": "Christopher Nolan style — IMAX, practical effects, non-linear storytelling, Hans Zimmer sound",
    "villeneuve": "Denis Villeneuve — Epic scale, slow-burn tension, breathtaking visuals, Blade Runner 2047 aesthetic",
    "fincher": "David Fincher — Dark, precise, psychological, Se7en / Gone Girl tension",
    "snyder": "Zack Snyder — Hyper-stylized, slow-motion, mythic, 300 / Watchmen energy",
    "deakins": "Roger Deakins — God-tier cinematography, natural light, emotional realism",
    "default": "Cinematic excellence — emotionally powerful, technically perfect, audience-resonant"
}

AGENTS = {
    "Core Leadership": ["Studio Director v3.5", "Mega Production Architect v3.5"],
    "Visual & Camera": [
        "Director of Photography (DoP) v3.5",
        "Post-Production Color Grading Supervisor v3.5",
        "Production Designer / Set Decorator v3.5"
    ],
    "Story & Performance": [
        "Character DNA Extractor v3.5",
        "Performance & Emotion Director v3.5",
        "Identity Lock Specialist v3.5",
        "Narrative Arc & Pacing Strategist v3.5",
        "Sequence Director v3.5",
        "Cinematic Sequence Extender v3.5"
    ],
    "Technical & Continuity": [
        "Continuity & Consistency Guardian v3.5",
        "Quality Assurance Guardian v3.5",
        "Imagine Prompt Master v3.5",
        "Workflow & Quota Optimizer v3.5"
    ],
    "Audio": [
        "Sonic Architect Native Audio Virtuoso v3.5",
        "Foley Sound Design Specialist v3.5"
    ],
    "Action / VFX / SFX": [
        "Stunt & Action Choreographer v3.5",
        "VFX & SFX Supervisor v3.5"
    ],
    "Marketing & Distribution": [
        "Key Art & Poster Designer v3.6",
        "Trailer & Teaser Director v3.6",
        "Localization & Subtitle Specialist v3.6",
    ],
    "Post-Production & Delivery": [
        "AI Polish Director v3.6",
    ],
    "Specialist (Opt-in)": [
        "ErosForge NSFW Director v3.6",
    ],
}

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_role_card_path(agent_name: str) -> Path | None:
    """Find the Role Card file for a given agent name."""
    if not AGENTS_DIR.exists():
        return None
    
    for f in AGENTS_DIR.glob("*.md"):
        if agent_name.lower().replace(" ", "_") in f.stem.lower() or f.stem.lower() in agent_name.lower().replace(" ", "_"):
            return f
    return None

def load_project_state() -> dict:
    if PROJECT_STATE_FILE.exists():
        return json.loads(PROJECT_STATE_FILE.read_text())
    return {"project": None, "characters": {}, "locked_variables": {}}

def save_project_state(state: dict):
    PROJECT_STATE_FILE.write_text(json.dumps(state, indent=2))

# ============================================================
# COMMANDS
# ============================================================

@app.command()
def status():
    """Show current studio status"""
    console.print(Panel.fit(
        "[bold cyan]🎥 Grok Imagine Cinematic Studio v3.6.1[/bold cyan]\n"
        "[green]Status:[/green] Enhanced CLI Active\n"
        "[green]Agents:[/green] 23 Online\n"
        "[green]Role Cards:[/green] Loaded from references/agents/\n"
        "[green]Mode:[/green] Production Ready",
        title="Studio Status",
        border_style="cyan"
    ))

@app.command()
def version():
    """Show CLI version"""
    console.print("[bold]cinematic-studio[/bold] v3.6.1 (June 2026)")

@app.command(name="list-agents")
def list_agents():
    """List all 23 agents grouped by category"""
    table = Table(title="🎬 Grok Imagine Cinematic Studio — 23 Agents", box=box.ROUNDED)
    table.add_column("Category", style="bold cyan", no_wrap=True)
    table.add_column("Agents", style="white")

    for category, agents in AGENTS.items():
        agent_list = "\n".join([f"• {a}" for a in agents])
        table.add_row(category, agent_list)

    console.print(table)
    total = sum(len(a) for a in AGENTS.values())
    console.print(f"\n[italic dim]Total: {total} specialized agents ready for production[/italic dim]")

@app.command(name="list-role-cards")
def list_role_cards():
    """List all available Role Cards in references/agents/"""
    if not AGENTS_DIR.exists():
        console.print("[red]references/agents/ directory not found[/red]")
        return

    cards = sorted(AGENTS_DIR.glob("*.md"))
    table = Table(title="📋 Available Role Cards", box=box.SIMPLE)
    table.add_column("Role Card", style="cyan")
    table.add_column("File", style="dim")

    for card in cards:
        table.add_row(card.stem.replace("_", " "), str(card))

    console.print(table)
    console.print(f"\n[green]Total Role Cards:[/green] {len(cards)}")

@app.command(name="show-role-card")
def show_role_card(
    agent: str = typer.Argument(..., help="Agent name or partial match (e.g. 'Identity Lock' or 'ErosForge')")
):
    """Display a specific Role Card"""
    card_path = get_role_card_path(agent)
    
    if not card_path or not card_path.exists():
        console.print(f"[red]Role Card not found for:[/red] {agent}")
        return

    content = card_path.read_text()
    console.print(Panel(Markdown(content[:3000]), title=f"📋 {card_path.stem}", border_style="blue", expand=False))

@app.command(name="generate-prompt")
def generate_prompt(
    story: str = typer.Argument(..., help="Your story, scene, or project description"),
    signature: str = typer.Option("default", "--signature", "-s", help="Director style"),
    output: str = typer.Option(None, "--output", "-o", help="Save to file")
):
    """Generate a high-quality ready-to-paste prompt"""
    sig_text = DIRECTOR_SIGNATURES.get(signature.lower(), DIRECTOR_SIGNATURES["default"])

    prompt = f"""# Grok Imagine Cinematic Studio v3.6.1 — ACTIVATED

**Project:** {story}
**Director Signature:** {sig_text}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

You are now running the full **23-agent** Grok Imagine Cinematic Studio v3.6 with complete Role Cards loaded from `references/agents/`.

Please begin by:
1. Confirming activation
2. Asking for my first creative decision, or
3. Immediately building a detailed Production Bible using the Mega Production Architect

Pipelines available: Character DNA (`dna`), Sequence Chain (`sequence`), Quota Optimizer (`quota`).
"""

    if output:
        Path(output).write_text(prompt)
        console.print(f"[green]✅ Prompt saved to[/green] {output}")
    else:
        console.print(Panel(prompt, title="📜 Ready-to-Paste Prompt", border_style="green"))

@app.command(name="cost-simulate")
def cost_simulate(
    duration: int = typer.Option(60, "--duration", "-d", help="Target duration in seconds"),
    complexity: str = typer.Option("medium", "--complexity", "-c", help="low / medium / high / extreme"),
    clips: int = typer.Option(None, "--clips", help="Number of clips"),
    fast_mode: bool = typer.Option(False, "--fast-mode", help="Use Fast mode pricing"),
):
    """Estimate generation cost and quota usage (delegates to quota optimizer)"""
    estimate = estimate_production(
        duration,
        clip_count=clips,
        complexity=complexity,
        fast_mode=fast_mode,
    )
    state = quota_load_state()
    quota = state.get("quota", {})
    risk = assess_budget_risk(
        estimate,
        tier=quota.get("tier", "supergrok_pro"),
        budget_remaining=quota.get("budget_remaining"),
    )
    table = Table(title="💰 Production Cost Estimate (1.5 per-second)", box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold green")
    table.add_row("Duration", f"{duration}s")
    table.add_row("Clips", str(estimate["clip_count"]))
    table.add_row("Complexity", complexity.title())
    table.add_row("Credits", f"{estimate['credits_low']} – {estimate['credits_high']}")
    table.add_row("Est. USD", f"${estimate['usd_low']} – ${estimate['usd_high']}")
    table.add_row("Est. Tokens", f"~{estimate['estimated_tokens']:,}")
    table.add_row("Risk", f"[{risk['risk_level']}]{risk['risk_level']}[/]")
    console.print(table)
    console.print("[dim]Use 'quota optimize' for savings recommendations[/dim]")

@app.command(name="create-bible")
def create_bible(
    title: str = typer.Argument(..., help="Project title"),
    genre: str = typer.Option("Cinematic", "--genre", "-g"),
    output: str = typer.Option("production_bible.json", "--output", "-o")
):
    """Generate a rich, structured Production Bible"""
    state = load_project_state()
    
    bible = {
        "project_title": title,
        "genre": genre,
        "director_signature": "Cinematic excellence",
        "target_duration_seconds": 60,
        "complexity": "Medium",
        "total_agents": 23,
        "version": "3.6.1",
        "role_cards_source": str(AGENTS_DIR) if AGENTS_DIR.exists() else "Not found",
        "locked_variables": {
            "PROJECT_TITLE": title,
            "GENRE": genre,
            "DIRECTOR_SIGNATURE": "Cinematic excellence",
            "DURATION": "60s"
        },
        "key_agents_involved": [
            "Character DNA Extractor",
            "Mega Production Architect",
            "Identity Lock Specialist",
            "Director of Photography",
            "Performance & Emotion Director",
            "Cinematic Sequence Extender",
            "Quality Assurance Guardian"
        ],
        "recommended_phases": [
            "Pre-Production (Bible + Character DNA)",
            "Core Production (Direction + Extension)",
            "Polish & Delivery (Audio + Marketing + QA)"
        ],
        "created": datetime.now().isoformat(),
        "status": "Ready for production",
        "notes": "Generated via Grok Imagine Cinematic Studio CLI. Use Web UI for visual simulation and live Grok API."
    }

    Path(output).write_text(json.dumps(bible, indent=2))
    
    state["project"] = bible
    save_project_state(state)

    console.print(f"[green]✅ Rich Production Bible created:[/green] {output}")
    console.print("[dim]Includes locked variables, key agents, and recommended phases[/dim]")

@app.command()
def memory(
    action: str = typer.Argument(..., help="add / list / load"),
    name: str = typer.Option(None, "--name", "-n", help="Character or variable name"),
    value: str = typer.Option(None, "--value", "-v", help="Value to store")
):
    """Manage project memory and character DNA"""
    state = load_project_state()

    if action == "add":
        if not name or not value:
            console.print("[red]Please provide --name and --value[/red]")
            return
        state["characters"][name] = value
        save_project_state(state)
        console.print(f"[green]✅ Saved memory for[/green] {name}")

    elif action == "list":
        if not state.get("characters"):
            console.print("[yellow]No memory entries yet[/yellow]")
            return
        table = Table(title="🧠 Project Memory")
        table.add_column("Name", style="cyan")
        table.add_column("Value", style="white")
        for k, v in state["characters"].items():
            table.add_row(k, str(v)[:80])
        console.print(table)

    elif action == "load":
        if name and name in state.get("characters", {}):
            console.print(Panel(state["characters"][name], title=f"Memory: {name}"))
        else:
            console.print("[yellow]Memory entry not found[/yellow]")

    else:
        console.print("[red]Unknown action. Use: add / list / load[/red]")

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
    state = quota_load_state()
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
    complexity: str = typer.Option("medium", "--complexity", "-c"),
    fast_mode: bool = typer.Option(False, "--fast-mode"),
    quality_pass: bool = typer.Option(False, "--quality-pass"),
    native_audio: bool = typer.Option(True, "--native-audio/--no-native-audio"),
    images: int = typer.Option(0, "--images", "-i"),
    agent_mode: str = typer.Option("standard", "--agents", help="minimal / standard / full_studio"),
):
    """Estimate production cost with per-second 1.5 pricing."""
    est = estimate_production(
        duration,
        clip_count=clips,
        avg_clip_duration=clip_duration,
        resolution=resolution,
        fast_mode=fast_mode,
        quality_pass=quality_pass,
        native_audio=native_audio,
        complexity=complexity,
        agent_mode=agent_mode,
        num_images=images,
    )
    state = quota_load_state()
    quota = state.get("quota", {})
    risk = assess_budget_risk(est, tier=quota.get("tier", "supergrok_pro"), budget_remaining=quota.get("budget_remaining"))

    table = Table(title="💰 Quota Estimate — Imagine Video 1.5", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("Target Duration", f"{duration}s")
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
    fast_mode: bool = typer.Option(False, "--fast-mode"),
    quality_pass: bool = typer.Option(False, "--quality-pass"),
):
    """Estimate cost for a single 1.5 clip."""
    est = estimate_clip_cost(duration, resolution=resolution, fast_mode=fast_mode, quality_pass=quality_pass)
    console.print(Panel(
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
    state = quota_load_state()
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
    state = quota_load_state()
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
    pdf.cell(0, 8, f"Project: {project.get('title', 'Untitled')}", ln=True)
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
        if Path(f).exists():
            console.print(f"[green]✅ {f} present[/green]")
        else:
            console.print(f"[yellow]⚠️  {f} missing[/yellow]")
            issues += 1

    if issues == 0:
        console.print("\n[bold green]✅ Validation passed[/bold green]")
    else:
        console.print(f"\n[yellow]Validation completed with {issues} issues[/yellow]")

@app.command()
def activate():
    """Print the official activation command"""
    console.print(Panel(
        "[bold]Activate Grok Imagine Cinematic Studio v3.6[/bold]\n\n"
        "Load the master prompt first, then paste the activation command.",
        title="🚀 Activation",
        border_style="magenta"
    ))

if __name__ == "__main__":
    app()