"""Shared CLI constants and helpers (Grok 4.6 · studio version from VERSION)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from studio_paths import AGENTS_DIR, STUDIO_ROOT


def _read_studio_version() -> str:
    vf = STUDIO_ROOT / "VERSION"
    if vf.is_file():
        return vf.read_text(encoding="utf-8").strip() or "3.11.2"
    return "3.11.2"


STUDIO_VERSION = _read_studio_version()
ACTIVATION_PHRASE = f"Activate Grok Imagine Cinematic Studio v{STUDIO_VERSION}"
MODEL_LAYER_DOC = "references/agents/MODEL_LAYER_v4.5.md"
MODELS_DOC = "references/MODELS.md"
MASTER_PROMPT_DOC = "MASTER_PROMPT.md"
console = Console()

DIRECTOR_SIGNATURES = {
    "nolan": "Christopher Nolan style — IMAX, practical effects, non-linear storytelling, Hans Zimmer sound",
    "villeneuve": "Denis Villeneuve — Epic scale, slow-burn tension, breathtaking visuals, Blade Runner 2047 aesthetic",
    "fincher": "David Fincher — Dark, precise, psychological, Se7en / Gone Girl tension",
    "snyder": "Zack Snyder — Hyper-stylized, slow-motion, mythic, 300 / Watchmen energy",
    "deakins": "Roger Deakins — God-tier cinematography, natural light, emotional realism",
    "default": "Cinematic excellence — emotionally powerful, technically perfect, audience-resonant",
}

CORE_AGENT_CATEGORIES = frozenset({
    "Core Leadership",
    "Visual & Camera",
    "Story & Performance",
    "Technical & Continuity",
    "Audio",
    "Action / VFX / SFX",
    "Marketing & Distribution",
    "Post-Production & Delivery",
})

# Display labels keep heritage Role Card stamps (v3.6.5 / v4.5). Studio pin is VERSION (v3.11.2).
AGENTS = {
    "Core Leadership": [
        "Studio Director v3.6.5",
        "Mega Production Architect v3.6.5",
    ],
    "Visual & Camera": [
        "Director of Photography (DoP) v3.6.5",
        "Post-Production Color Grading Supervisor v3.6.5",
        "Production Designer / Set Decorator v3.6.5",
    ],
    "Story & Performance": [
        "Character DNA Extractor v3.6.5",
        "Performance & Emotion Director v3.6.5",
        "Identity Lock Specialist v3.6.5",
        "Narrative Arc & Pacing Strategist v3.6.5",
        "Sequence Director v3.6.5",
        "Cinematic Sequence Extender v3.6.5",
    ],
    "Technical & Continuity": [
        "Continuity & Consistency Guardian v3.6.5",
        "Multi-Clip Continuity Orchestrator v4.5",
        "Quality Assurance Guardian v3.6.5",
        "Grok Doctor v4.5",
        "Imagine Prompt Master v3.6.5",
        "Workflow & Quota Optimizer v3.6.5",
    ],
    "Audio": [
        "Sonic Architect Native Audio Virtuoso v3.6.5",
        "Foley Sound Design Specialist v3.6.5",
    ],
    "Action / VFX / SFX": [
        "Stunt & Action Choreographer v3.6.5",
        "VFX & SFX Supervisor v3.6.5",
    ],
    "Marketing & Distribution": [
        "Key Art & Poster Designer v3.6.5",
        "Trailer & Teaser Director v3.6.5",
        "Localization & Subtitle Specialist v3.6.5",
    ],
    "Post-Production & Delivery": [
        "AI Polish Director v3.6.5",
    ],
    "Refinement (i2i)": [
        "I2I Cinematic Refiner v3.6.5",
        "I2I Refiner v3.6.5",
    ],
    "Production Pipeline": [
        "Reference & Asset Curator v3.6.5",
        "Image-to-Video Specialist v3.6.5",
        "SFW Batch Orchestrator v1.0",
        "Assembly Editor v3.6.5",
        "Multi-Character Identity Arbiter v3.6.5",
        "Costume & Wardrobe Continuity v4.5",
    ],
    # Wave A P0 only (8). Grok Doctor + Multi-Clip Continuity are core Technical.
    "Wave A Specialists": [
        "Plate & Motion Readiness Lead v4.5",
        "Contact & Micro-Physics Specialist v4.5",
        "Hair & Makeup Continuity v4.5",
        "Dialogue & ADR Director v4.5",
        "Score & Temp Music Supervisor v4.5",
        "Title & Motion Graphics Lead v4.5",
        "Distribution & Crop Strategist v4.5",
        "Parallel Brief Dispatcher v4.5",
    ],
    "Specialist (Opt-in)": [
        "ErosForge NSFW Director v3.6.5",
        "NSFW Quota Orchestrator v1.0",
        "NSFW Sequence Extender v1.0",
    ],
    "Meta & Tools": [
        "GitHub Repo Manager v4.5",
        "Quota Dashboard v4.5",
        "Extend Frame to Video v4.5",
    ],
}

AGENT_ROLE_CARDS: dict[str, str] = {
    "Studio Director v3.6.5": "Studio_Director.md",
    "Mega Production Architect v3.6.5": "Mega_Production_Architect.md",
    "Director of Photography (DoP) v3.6.5": "Director_of_Photography_DoP_v3.5.md",
    "Post-Production Color Grading Supervisor v3.6.5": "Post_Production_Color_Grading_Supervisor_v3.5.md",
    "Production Designer / Set Decorator v3.6.5": "Production_Designer_Set_Decorator_v3.5.md",
    "Character DNA Extractor v3.6.5": "Character_DNA_Extractor_v3.5.md",
    "Performance & Emotion Director v3.6.5": "Performance_Emotion_Director.md",
    "Identity Lock Specialist v3.6.5": "Identity_Lock_Specialist.md",
    "Narrative Arc & Pacing Strategist v3.6.5": "Narrative_Arc_Pacing_Strategist_v3.5.md",
    "Sequence Director v3.6.5": "Sequence_Director.md",
    "Cinematic Sequence Extender v3.6.5": "Cinematic_Sequence_Extender.md",
    "Continuity & Consistency Guardian v3.6.5": "Continuity_Consistency_Guardian.md",
    "Costume & Wardrobe Continuity v4.5": "Costume_Wardrobe_Continuity.md",
    "Quality Assurance Guardian v3.6.5": "Quality_Assurance_Guardian_v3.5.md",
    "Imagine Prompt Master v3.6.5": "Imagine_Prompt_Master.md",
    "Workflow & Quota Optimizer v3.6.5": "Workflow_Quota_Optimizer.md",
    "Sonic Architect Native Audio Virtuoso v3.6.5": "Sonic_Architect_Native_Audio_Virtuoso.md",
    "Foley Sound Design Specialist v3.6.5": "Foley_Sound_Design_Specialist_v3.5.md",
    "Stunt & Action Choreographer v3.6.5": "Stunt_Action_Choreographer_v3.5.md",
    "VFX & SFX Supervisor v3.6.5": "VFX_and_SFX_Supervisor_v3.5.md",
    "Key Art & Poster Designer v3.6.5": "Key_Art_Poster_Designer_v3.5.md",
    "Trailer & Teaser Director v3.6.5": "Trailer_Teaser_Director_v3.5.md",
    "Localization & Subtitle Specialist v3.6.5": "Localization_Subtitle_Specialist_v3.5.md",
    "AI Polish Director v3.6.5": "AI_Polish_Director.md",
    "I2I Cinematic Refiner v3.6.5": "I2I_Cinematic_Refiner.md",
    "I2I Refiner v3.6.5": "I2I_Refiner.md",
    "Reference & Asset Curator v3.6.5": "Reference_Asset_Curator.md",
    "Image-to-Video Specialist v3.6.5": "Image_to_Video_Specialist.md",
    "SFW Batch Orchestrator v1.0": "SFW_Batch_Orchestrator.md",
    "Assembly Editor v3.6.5": "Assembly_Editor.md",
    "Multi-Character Identity Arbiter v3.6.5": "Multi_Character_Identity_Arbiter.md",
    "ErosForge NSFW Director v3.6.5": "ErosForge_NSFW_Director.md",
    "NSFW Quota Orchestrator v1.0": "NSFW_Quota_Orchestrator.md",
    "NSFW Sequence Extender v1.0": "NSFW_Sequence_Extender.md",
    "Plate & Motion Readiness Lead v4.5": "Plate_Motion_Readiness_Lead.md",
    "Contact & Micro-Physics Specialist v4.5": "Contact_Micro_Physics_Specialist.md",
    "Hair & Makeup Continuity v4.5": "Hair_Makeup_Continuity.md",
    "Dialogue & ADR Director v4.5": "Dialogue_ADR_Director.md",
    "Score & Temp Music Supervisor v4.5": "Score_Temp_Music_Supervisor.md",
    "Title & Motion Graphics Lead v4.5": "Title_Motion_Graphics_Lead.md",
    "Distribution & Crop Strategist v4.5": "Distribution_Crop_Strategist.md",
    "Parallel Brief Dispatcher v4.5": "Parallel_Brief_Dispatcher.md",
    "Grok Doctor v4.5": "Grok_Doctor.md",
    "Multi-Clip Continuity Orchestrator v4.5": "Multi_Clip_Continuity_Orchestrator.md",
    "GitHub Repo Manager v4.5": "GitHub_Repo_Manager.md",
    "Quota Dashboard v4.5": "Quota_Dashboard.md",
    "Extend Frame to Video v4.5": "Extend_Frame_to_Video.md",
}

ROLE_CARD_INDEX_FILE = "AGENT_INDEX.md"
# Shared docs in references/agents/ that are not per-agent Role Cards
# (protocol docs, model layer, index — keep in sync when adding non-role .md files)
ROLE_CARD_SHARED_DOCS = frozenset({
    ROLE_CARD_INDEX_FILE,
    "MODEL_LAYER_v3.6.7.md",  # pointer → MODEL_LAYER_v3.7.1 / v4.5
    "MODEL_LAYER_v3.7.1.md",
    "MODEL_LAYER_v4.5.md",  # v3.8.6 v9-4p5 dual-model layer
    "IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md",
    "IMAGINE_SURFACES.md",  # v3.10.0 official Imagine 1.0/1.5/2.0 + Agent Mode map
    "IMAGINE_EXECUTION_BRIDGE.md",  # v3.8.6 surface-C bridge protocol
    "IDENTITY_CONTINUITY_PROTOCOL_v3.8.md",
    "Parallel_Brief_Protocol.md",
})
# Skill SKILL.md filename aliases → canonical _v3.5 stems. Not mapped agents.
ROLE_CARD_ALIAS_FILES = frozenset({
    "Character_DNA_Extractor.md",
    "Quality_Assurance_Guardian.md",
})
EXPECTED_ROLE_CARD_COUNT = len(AGENT_ROLE_CARDS)


def core_agent_count() -> int:
    """Count core production agents (excludes i2i refinement and opt-in specialists)."""
    return sum(len(AGENTS[c]) for c in CORE_AGENT_CATEGORIES if c in AGENTS)


def total_agent_count() -> int:
    return sum(len(names) for names in AGENTS.values())


def list_role_card_files() -> list[Path]:
    """Return sorted Role Card paths (excludes index, shared docs, filename aliases)."""
    if not AGENTS_DIR.exists():
        return []
    skip = ROLE_CARD_SHARED_DOCS | ROLE_CARD_ALIAS_FILES
    return sorted(p for p in AGENTS_DIR.glob("*.md") if p.name not in skip)


def get_role_card_path(agent_name: str) -> Path | None:
    """Find the Role Card file for a given agent name."""
    if not AGENTS_DIR.exists():
        return None
    mapped = AGENT_ROLE_CARDS.get(agent_name)
    if mapped:
        path = AGENTS_DIR / mapped
        if path.is_file():
            return path
    needle = agent_name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    exact = AGENTS_DIR / f"{needle}.md"
    if exact.is_file():
        return exact
    for path in list_role_card_files():
        stem = path.stem.lower()
        if stem == needle or needle in stem or stem in needle:
            return path
    return None


def format_stack_panel(stack: dict[str, Any] | None = None) -> Panel:
    """Rich panel for the Grok 4.6 model stack (status / activate / stack cmd)."""
    try:
        from models import (
            RECOMMENDED_GROK_BUILD_CLI_VERSION,
            build_video_pipeline_spec,
            model_stack_summary,
        )
    except ImportError:
        return Panel(
            "[red]models registry unavailable[/red]",
            title="Model Stack",
            border_style="red",
        )

    s = stack or model_stack_summary()
    body = (
        f"[bold cyan]Grok 4.6[/bold cyan] cinematic+Build · studio [bold]v{STUDIO_VERSION}[/bold]\n\n"
        f"  Grok Build CLI: [green]{s.get('grok_build_cli_default', 'grok-4.6')}[/green] "
        f"(+ fork {s.get('grok_build_cli_fork', 'grok-build')}, "
        f"≥ {s.get('grok_build_cli_min_version', RECOMMENDED_GROK_BUILD_CLI_VERSION)})\n"
        f"  xAI Chat: [green]{s.get('xai_chat', 'grok-4.6')}[/green] "
        f"| Build API: [green]{s.get('xai_build', 'grok-4.6')}[/green]\n"
        f"  Imagine Video: [green]{s.get('imagine_video', 'grok-imagine-video')}[/green] "
        f"| Image: {s.get('imagine_image', 'grok-imagine-image')}\n\n"
        f"[dim]1M opt-in: --chat-model grok-4.3 · "
        f"Video 1.0 cost default · 1.5 native audio · "
        f"{MODEL_LAYER_DOC}[/dim]\n\n"
        f"{build_video_pipeline_spec(s.get('imagine_video'))}"
    )
    return Panel.fit(
        body,
        title=f"Model Layer (Grok 4.6 · studio v{STUDIO_VERSION})",
        border_style="cyan",
    )


def format_stack_table(stack: dict[str, Any] | None = None) -> Table:
    """Compact key/value table of the resolved model stack."""
    try:
        from models import model_stack_summary
    except ImportError:
        t = Table(title="Model Stack")
        t.add_column("Key")
        t.add_column("Value")
        t.add_row("error", "models unavailable")
        return t

    s = stack or model_stack_summary()
    table = Table(title=f"Model Stack · Grok 4.6 · v{STUDIO_VERSION}", show_header=True)
    table.add_column("Layer", style="cyan")
    table.add_column("Slug", style="green")
    rows = [
        ("Orchestration (default)", s.get("xai_chat", "grok-4.6")),
        ("Build / coding API", s.get("xai_build", "grok-4.6")),
        ("Grok Build CLI", s.get("grok_build_cli_default", "grok-4.6")),
        ("CLI fork", s.get("grok_build_cli_fork", "grok-build")),
        ("CLI min version", s.get("grok_build_cli_min_version", "1.0.5")),
        ("Imagine Video", s.get("imagine_video", "grok-imagine-video")),
        ("Imagine Image", s.get("imagine_image", "grok-imagine-image")),
    ]
    for k, v in rows:
        table.add_row(k, str(v))
    return table