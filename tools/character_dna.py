#!/usr/bin/env python3
"""
Character DNA pipeline — extraction scaffold, Identity Lock handoff, prompt injection.

Used by:
  - cinematic_studio_cli.py (dna commands)
  - .grok/skills/character-dna-extractor/scripts/
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models import build_video_pipeline_spec
from project_state import load_project_state, save_project_state
from studio_paths import CHARACTERS_DIR

SCHEMA_VERSION = "1.0"
STUDIO_AGENT_VERSION = "v3.8.0"

PROMPT_MODES = (
    "compact",
    "cinematic",
    "close_up",
    "sequence_starter",
    "video_1.0",
    "video_1.5",
)


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-") or "character"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def create_dna_scaffold(
    character_name: str,
    *,
    core_identity: str = "",
    facial_dna: str = "",
    hair_grooming: str = "",
    clothing_style: str = "",
    movement_posture: str = "",
    emotional_baseline: str = "",
    motion_dna: str = "",
    key_anchors: list[str] | None = None,
    reference_image_ids: list[str] | None = None,
    nsfw_notes: str | None = None,
    source: str = "manual",
) -> dict[str, Any]:
    """Create a v1.0 Character DNA profile scaffold."""
    anchors = key_anchors or []
    return {
        "schema_version": SCHEMA_VERSION,
        "character_name": character_name,
        "slug": slugify(character_name),
        "version": 1,
        "extracted_at": _now_iso(),
        "source": source,
        "core_identity": core_identity,
        "facial_dna": facial_dna,
        "hair_grooming": hair_grooming,
        "clothing_style": clothing_style,
        "movement_posture": movement_posture,
        "emotional_baseline": emotional_baseline,
        "motion_dna": motion_dna,
        "key_consistency_anchors": anchors,
        "reference_image_ids": reference_image_ids or [],
        "reference_weights": {
            "primary_ref_weight": 0.85,
            "secondary_ref_weight": 0.15,
        },
        "cinematic_viability_score": None,
        "nsfw_notes": nsfw_notes,
        "identity_lock_status": "pending",
        "studio_agent_version": STUDIO_AGENT_VERSION,
        "video_pipeline_spec": build_video_pipeline_spec(),
    }


def validate_dna(dna: dict[str, Any]) -> list[str]:
    """Return list of validation issues (empty = valid)."""
    issues: list[str] = []
    required = ("character_name", "slug", "core_identity", "facial_dna")
    for field in required:
        if not dna.get(field):
            issues.append(f"Missing required field: {field}")
    if dna.get("schema_version") != SCHEMA_VERSION:
        issues.append(f"Unsupported schema_version: {dna.get('schema_version')}")
    return issues


def build_prompt_blocks(dna: dict[str, Any]) -> dict[str, str]:
    """Build prompt-injection blocks for Imagine Prompt Master."""
    name = dna["character_name"]
    variable = f"[CHARACTER_DNA:{name.upper().replace(' ', '_')}_v{dna.get('version', 1)}]"

    core = dna.get("core_identity", "").strip()
    facial = dna.get("facial_dna", "").strip()
    hair = dna.get("hair_grooming", "").strip()
    clothing = dna.get("clothing_style", "").strip()
    movement = dna.get("movement_posture", "").strip()
    emotion = dna.get("emotional_baseline", "").strip()
    motion = dna.get("motion_dna", "").strip()
    anchors = dna.get("key_consistency_anchors", [])
    anchor_text = "; ".join(anchors) if anchors else ""
    weights = dna.get("reference_weights", {})
    primary_w = weights.get("primary_ref_weight", 0.85)

    compact_parts = [p for p in [core, facial, hair] if p]
    compact = f"{variable} " + ", ".join(compact_parts)
    if anchor_text:
        compact += f". Key anchors: {anchor_text}"

    cinematic = (
        f"{variable}\n"
        f"Subject: {name}. {core}\n"
        f"Face: {facial}\n"
        f"Hair: {hair}\n"
        f"Wardrobe: {clothing}\n"
        f"Movement: {movement}\n"
        f"Emotion: {emotion}\n"
        f"Reference weight primary={primary_w}. Maintain exact identity; drift score must stay below 2.5."
    )
    if anchor_text:
        cinematic += f"\nNon-negotiable anchors: {anchor_text}"

    close_up = (
        f"{variable} Extreme close-up of {name}. "
        f"{facial}. {hair}. Micro-expression fidelity required. "
        f"Preserve skin texture, eye reflections, and subtle asymmetries. "
        f"Reference weight {primary_w}."
    )

    sequence_starter = (
        f"{variable} Opening frame for sequence featuring {name}. "
        f"{core}. {clothing}. {movement}. {emotion}. "
        f"LAST_FRAME_RECAP ready. MOMENTUM_VECTOR: neutral start, identity locked."
    )
    if motion:
        sequence_starter += f" Motion DNA: {motion}"

    ref_ids = dna.get("reference_image_ids", [])
    ref_clause = f" reference_image_id={ref_ids[0]}" if ref_ids else ""
    motion_clause = motion or movement
    video_10 = (
        f"{variable} Grok Imagine Video 1.0 (cost default). {name}: {core}. {facial}. "
        f"Physics-realistic motion. {motion_clause}. "
        f"reference_image_fidelity=high, primary_ref_weight={primary_w}{ref_clause}. "
        f"Identity drift prevention active. Prefer locked hero plate as first frame."
    )
    video_15 = (
        f"{variable} Grok Imagine Video 1.5 native audio capable. {name}: {core}. {facial}. "
        f"Physics-realistic motion with audio-ready performance. {motion_clause}. "
        f"reference_image_fidelity=high, primary_ref_weight={primary_w}{ref_clause}. "
        f"Identity drift prevention active. Sync breath/micro-expression if dialogue."
    )

    return {
        "compact": compact.strip(),
        "cinematic": cinematic.strip(),
        "close_up": close_up.strip(),
        "sequence_starter": sequence_starter.strip(),
        "video_1.0": video_10.strip(),
        "video_1.5": video_15.strip(),
    }


def dna_to_markdown(dna: dict[str, Any], prompts: dict[str, str] | None = None) -> str:
    """Render DNA profile as Markdown."""
    prompts = prompts or build_prompt_blocks(dna)
    anchors = dna.get("key_consistency_anchors", [])
    anchor_lines = "\n".join(f"- {a}" for a in anchors) if anchors else "- (none yet)"

    lines = [
        f"# Character DNA — {dna['character_name']}",
        "",
        f"**Slug:** `{dna['slug']}`  ",
        f"**Version:** {dna.get('version', 1)}  ",
        f"**Extracted:** {dna.get('extracted_at', 'unknown')}  ",
        f"**Source:** {dna.get('source', 'unknown')}  ",
        f"**Identity Lock Status:** {dna.get('identity_lock_status', 'pending')}",
        "",
        "## Core Identity",
        dna.get("core_identity", "") or "_Pending extraction_",
        "",
        "## Facial DNA",
        dna.get("facial_dna", "") or "_Pending extraction_",
        "",
        "## Hair & Grooming",
        dna.get("hair_grooming", "") or "_Pending extraction_",
        "",
        "## Clothing & Style",
        dna.get("clothing_style", "") or "_Pending extraction_",
        "",
        "## Movement & Posture",
        dna.get("movement_posture", "") or "_Pending extraction_",
        "",
        "## Emotional Baseline",
        dna.get("emotional_baseline", "") or "_Pending extraction_",
        "",
        "## Motion DNA",
        dna.get("motion_dna", "") or "_Pending extraction_",
        "",
        "## Key Consistency Anchors",
        anchor_lines,
        "",
        "## Prompt Injection — Compact",
        f"```\n{prompts['compact']}\n```",
        "",
        "## Prompt Injection — Cinematic",
        f"```\n{prompts['cinematic']}\n```",
        "",
        "## Prompt Injection — Close-up",
        f"```\n{prompts['close_up']}\n```",
        "",
        "## Prompt Injection — Sequence Starter",
        f"```\n{prompts['sequence_starter']}\n```",
        "",
        "## Prompt Injection — Video 1.0",
        f"```\n{prompts['video_1.0']}\n```",
        "",
        "## Prompt Injection — Video 1.5",
        f"```\n{prompts['video_1.5']}\n```",
    ]
    if dna.get("nsfw_notes"):
        lines += ["", "## NSFW Consistency Notes", dna["nsfw_notes"]]
    return "\n".join(lines)


def build_handoff_packet(dna: dict[str, Any]) -> dict[str, Any]:
    """Build Identity Lock Handoff Packet from Character DNA Extractor output."""
    prompts = build_prompt_blocks(dna)
    return {
        "packet_type": "identity_lock_handoff",
        "schema_version": SCHEMA_VERSION,
        "created_at": _now_iso(),
        "source_agent": f"Character DNA Extractor {STUDIO_AGENT_VERSION}",
        "target_agent": f"Identity Lock Specialist {STUDIO_AGENT_VERSION}",
        "video_pipeline_spec": build_video_pipeline_spec(),
        "character_name": dna["character_name"],
        "slug": dna["slug"],
        "last_dna_version": dna.get("version", 1),
        "key_consistency_anchors": dna.get("key_consistency_anchors", []),
        "motion_dna": dna.get("motion_dna", ""),
        "reference_image_ids": dna.get("reference_image_ids", []),
        "reference_weights": dna.get("reference_weights", {}),
        "cinematic_viability_score": dna.get("cinematic_viability_score"),
        "dna_profile": dna,
        "prompt_injection": prompts,
        "identity_lock_instructions": [
            "Load dna_profile into Character Memory Bank",
            "Set identity_lock_status to 'locked'",
            "Enforce reference_weights on all Imagine Prompt Master outputs",
            "Run sequence drift-score before every extend; fill drift_evidence (ICP-02/03); status=risk when score >= 2.5 — recommend correction; agent may withhold approval (CLI does not hard-block). Protocol: IDENTITY_CONTINUITY_PROTOCOL v1.0",
            "Cite references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md on long-form handoffs",
            "Propagate CHARACTER_DNA variable verbatim in all handoff packets",
        ],
    }


def character_dir(slug: str) -> Path:
    return CHARACTERS_DIR / slug


def save_character_dna(dna: dict[str, Any], *, characters_root: Path | None = None) -> tuple[Path, Path]:
    """Persist dna.json and dna.md under characters/{slug}/."""
    root = characters_root or CHARACTERS_DIR
    out_dir = root / dna["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    prompts = build_prompt_blocks(dna)
    json_path = out_dir / "dna.json"
    md_path = out_dir / "dna.md"
    json_path.write_text(json.dumps(dna, indent=2))
    md_path.write_text(dna_to_markdown(dna, prompts))
    return json_path, md_path


def load_character_dna(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text())
    issues = validate_dna(data)
    if issues:
        raise ValueError("; ".join(issues))
    return data


def find_character_dna(name_or_slug: str, *, characters_root: Path | None = None) -> Path | None:
    root = characters_root or CHARACTERS_DIR
    if not root.exists():
        return None
    slug = slugify(name_or_slug)
    direct = root / slug / "dna.json"
    if direct.exists():
        return direct
    for dna_file in root.glob("*/dna.json"):
        data = json.loads(dna_file.read_text())
        if data.get("character_name", "").lower() == name_or_slug.lower():
            return dna_file
    return None


def lock_to_identity_bank(
    dna: dict[str, Any],
    *,
    state: dict[str, Any] | None = None,
    state_file: Path | None = None,
) -> dict[str, Any]:
    """
    Import DNA into Identity Lock memory bank (project state).
    Returns updated state.
    """
    if state is None:
        state = load_project_state(state_file)

    prompts = build_prompt_blocks(dna)
    handoff = build_handoff_packet(dna)
    name = dna["character_name"]
    slug = dna["slug"]

    state.setdefault("characters", {})
    state.setdefault("identity_lock", {})

    state["characters"][name] = {
        "slug": slug,
        "dna_version": dna.get("version", 1),
        "locked_at": _now_iso(),
        "compact_injection": prompts["compact"],
        "profile_path": str(CHARACTERS_DIR / slug / "dna.json"),
    }

    state["identity_lock"][slug] = {
        "character_name": name,
        "status": "locked",
        "last_dna_version": dna.get("version", 1),
        "key_consistency_anchors": dna.get("key_consistency_anchors", []),
        "reference_weights": dna.get("reference_weights", {}),
        "reference_image_ids": dna.get("reference_image_ids", []),
        "prompt_injection": prompts,
        "handoff_packet": handoff,
        "drift_threshold": 2.5,
    }

    dna_locked = dict(dna)
    dna_locked["identity_lock_status"] = "locked"
    save_character_dna(dna_locked)
    save_project_state(state, state_file)
    return state


def list_characters(*, characters_root: Path | None = None) -> list[dict[str, Any]]:
    root = characters_root or CHARACTERS_DIR
    if not root.exists():
        return []
    results = []
    for dna_file in sorted(root.glob("*/dna.json")):
        try:
            data = load_character_dna(dna_file)
            results.append({
                "name": data["character_name"],
                "slug": data["slug"],
                "version": data.get("version", 1),
                "status": data.get("identity_lock_status", "pending"),
                "path": str(dna_file),
            })
        except (json.JSONDecodeError, ValueError):
            continue
    return results


def inject_into_prompt(
    base_prompt: str,
    character_name: str,
    mode: str = "cinematic",
    *,
    characters_root: Path | None = None,
) -> str:
    """Prepend CHARACTER_DNA injection block to a base prompt."""
    if mode not in PROMPT_MODES:
        raise ValueError(f"Unknown mode '{mode}'. Choose from: {', '.join(PROMPT_MODES)}")

    dna_path = find_character_dna(character_name, characters_root=characters_root)
    if not dna_path:
        raise FileNotFoundError(f"No DNA profile found for: {character_name}")

    dna = load_character_dna(dna_path)
    blocks = build_prompt_blocks(dna)
    injection = blocks[mode]
    return f"{injection}\n\n---\n\n{base_prompt.strip()}"