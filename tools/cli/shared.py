"""Shared CLI constants and helpers."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from studio_paths import AGENTS_DIR, STUDIO_ROOT

STUDIO_VERSION = "3.7.1"
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
        "Quality Assurance Guardian v3.6.5",
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
    ],
    "Specialist (Opt-in)": [
        "ErosForge NSFW Director v3.6.5",
        "NSFW Quota Orchestrator v1.0",
        "NSFW Sequence Extender v1.0",
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
}

ROLE_CARD_INDEX_FILE = "AGENT_INDEX.md"
# Shared docs in references/agents/ that are not per-agent Role Cards
ROLE_CARD_SHARED_DOCS = frozenset({
    ROLE_CARD_INDEX_FILE,
    "MODEL_LAYER_v3.7.1.md",
})
EXPECTED_ROLE_CARD_COUNT = len(AGENT_ROLE_CARDS)


def core_agent_count() -> int:
    """Count core production agents (excludes i2i refinement and opt-in specialists)."""
    return sum(len(AGENTS[c]) for c in CORE_AGENT_CATEGORIES if c in AGENTS)


def total_agent_count() -> int:
    return sum(len(names) for names in AGENTS.values())


def list_role_card_files() -> list[Path]:
    """Return sorted Role Card paths (excludes index + shared model docs)."""
    if not AGENTS_DIR.exists():
        return []
    return sorted(
        p for p in AGENTS_DIR.glob("*.md") if p.name not in ROLE_CARD_SHARED_DOCS
    )


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