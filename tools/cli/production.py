"""Production Bible and activation prompt builders (shared by CLI and Web UI)."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from models import (
    XAI_CHAT_MODELS,
    build_video_pipeline_spec,
    model_stack_summary,
    resolve_chat_model,
    resolve_video_model,
)

from cli.shared import AGENTS_DIR, DIRECTOR_SIGNATURES, STUDIO_VERSION


def production_context(
    *,
    chat_model: str | None = None,
    video_model: str | None = None,
) -> dict[str, Any]:
    """Resolve chat/video models, stack summary, and pipeline spec in one call."""
    chat_slug = resolve_chat_model(chat_model)
    video_slug = resolve_video_model(video_model)
    stack = model_stack_summary(chat_model=chat_slug, video_model=video_slug)
    pipeline_spec = build_video_pipeline_spec(video_slug)
    return {
        "chat_slug": chat_slug,
        "video_slug": video_slug,
        "stack": stack,
        "pipeline_spec": pipeline_spec,
        "chat_label": XAI_CHAT_MODELS.get(chat_slug, {}).get("label", chat_slug),
    }


def _resolve_director_text(*, signature: str = "default", director: str | None = None) -> str:
    if director:
        return director
    return DIRECTOR_SIGNATURES.get(signature.lower(), DIRECTOR_SIGNATURES["default"])


def build_activation_prompt(
    story: str,
    *,
    signature: str = "default",
    director: str | None = None,
    genre: str | None = None,
    duration: int | None = None,
    complexity: str | None = None,
    chat_model: str | None = None,
    video_model: str | None = None,
) -> str:
    """Build ready-to-paste studio activation prompt."""
    ctx = production_context(chat_model=chat_model, video_model=video_model)
    sig_text = _resolve_director_text(signature=signature, director=director)
    stack = ctx["stack"]

    meta_lines = [
        f"**Project:** {story}",
        f"**Director Signature:** {sig_text}",
    ]
    if genre:
        meta_lines.append(f"**Genre:** {genre}")
    if duration is not None:
        meta_lines.append(f"**Duration:** {duration}s")
    if complexity:
        meta_lines.append(f"**Complexity:** {complexity}")
    meta_lines.extend([
        f"**Chat Model:** {ctx['chat_slug']}",
        f"**Video Pipeline:** {ctx['video_slug']}",
        f"**Grok Build CLI:** {stack['grok_build_cli_default']} (fork: {stack['grok_build_cli_fork']})",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    ])

    return f"""# Grok Imagine Cinematic Studio v{STUDIO_VERSION} — ACTIVATED

{chr(10).join(meta_lines)}

You are now running the full **23-agent** Grok Imagine Cinematic Studio v3.6 with complete Role Cards loaded from `references/agents/`.

{ctx['pipeline_spec']}

Please begin by:
1. Confirming activation
2. Asking for my first creative decision, or
3. Immediately building a detailed Production Bible using the Mega Production Architect

Pipelines available: Character DNA (`dna`), Sequence Chain (`sequence`), Quota Optimizer (`quota`).
"""


def build_production_bible(
    title: str,
    *,
    genre: str = "Cinematic",
    director_signature: str | None = None,
    target_duration_seconds: int = 60,
    complexity: str = "Medium",
    locked_title: str | None = None,
    chat_model: str | None = None,
    video_model: str | None = None,
    agents_dir: Path | None = None,
    notes: str | None = None,
) -> dict[str, Any]:
    """Build structured Production Bible dict."""
    cards_dir = agents_dir or AGENTS_DIR
    ctx = production_context(chat_model=chat_model, video_model=video_model)
    director = director_signature or "Cinematic excellence"
    pipeline_spec = ctx["pipeline_spec"]
    project_locked = locked_title or title

    return {
        "project_title": title,
        "genre": genre,
        "director_signature": director,
        "target_duration_seconds": target_duration_seconds,
        "complexity": complexity,
        "total_agents": 23,
        "version": STUDIO_VERSION,
        "role_cards_source": str(cards_dir) if cards_dir.exists() else "references/agents/",
        "model_stack": ctx["stack"],
        "video_pipeline_spec": pipeline_spec,
        "locked_variables": {
            "PROJECT_TITLE": project_locked,
            "GENRE": genre,
            "DIRECTOR_SIGNATURE": director,
            "DURATION": f"{target_duration_seconds}s",
            "VIDEO_PIPELINE_SPEC": pipeline_spec,
        },
        "key_agents_involved": [
            "Character DNA Extractor",
            "Mega Production Architect",
            "Identity Lock Specialist",
            "Director of Photography",
            "Performance & Emotion Director",
            "Cinematic Sequence Extender",
            "Quality Assurance Guardian",
        ],
        "recommended_phases": [
            "Pre-Production (Bible + Character DNA)",
            "Core Production (Direction + Extension)",
            "Polish & Delivery (Audio + Marketing + QA)",
        ],
        "created": datetime.now().isoformat(),
        "status": "Ready for production",
        "notes": notes or "Generated via Grok Imagine Cinematic Studio CLI. Use Web UI for visual simulation and live Grok API.",
    }