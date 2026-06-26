"""Shared CLI constants and helpers."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console

from studio_paths import AGENTS_DIR, STUDIO_ROOT

STUDIO_VERSION = "3.6.5"
console = Console()

DIRECTOR_SIGNATURES = {
    "nolan": "Christopher Nolan style — IMAX, practical effects, non-linear storytelling, Hans Zimmer sound",
    "villeneuve": "Denis Villeneuve — Epic scale, slow-burn tension, breathtaking visuals, Blade Runner 2047 aesthetic",
    "fincher": "David Fincher — Dark, precise, psychological, Se7en / Gone Girl tension",
    "snyder": "Zack Snyder — Hyper-stylized, slow-motion, mythic, 300 / Watchmen energy",
    "deakins": "Roger Deakins — God-tier cinematography, natural light, emotional realism",
    "default": "Cinematic excellence — emotionally powerful, technically perfect, audience-resonant",
}

AGENTS = {
    "Core Leadership": ["Studio Director v3.6", "Mega Production Architect v3.6"],
    "Visual & Camera": [
        "Director of Photography (DoP) v3.6",
        "Post-Production Color Grading Supervisor v3.6",
        "Production Designer / Set Decorator v3.6",
    ],
    "Story & Performance": [
        "Character DNA Extractor v3.6",
        "Performance & Emotion Director v3.6",
        "Identity Lock Specialist v3.6",
        "Narrative Arc & Pacing Strategist v3.6",
        "Sequence Director v3.6",
        "Cinematic Sequence Extender v3.6",
    ],
    "Technical & Continuity": [
        "Continuity & Consistency Guardian v3.6",
        "Quality Assurance Guardian v3.6",
        "Imagine Prompt Master v3.6",
        "Workflow & Quota Optimizer v3.6",
    ],
    "Audio": [
        "Sonic Architect Native Audio Virtuoso v3.6",
        "Foley Sound Design Specialist v3.6",
    ],
    "Action / VFX / SFX": [
        "Stunt & Action Choreographer v3.6",
        "VFX & SFX Supervisor v3.6",
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


def get_role_card_path(agent_name: str) -> Path | None:
    """Find the Role Card file for a given agent name."""
    if not AGENTS_DIR.exists():
        return None
    for f in AGENTS_DIR.glob("*.md"):
        if agent_name.lower().replace(" ", "_") in f.stem.lower() or f.stem.lower() in agent_name.lower().replace(" ", "_"):
            return f
    return None