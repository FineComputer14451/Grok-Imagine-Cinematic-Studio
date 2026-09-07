#!/usr/bin/env python3
"""Portable Character DNA init — scaffold dna.json (+ markdown) without Studio CLI.

Compatible with Grok-Imagine-Cinematic-Studio schema_version 1.0
(create_dna_scaffold / `cinematic_studio_cli.py dna init`).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "1.0"
STUDIO_AGENT_VERSION = "v3.9.0-portable"


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-") or "character"


def now_iso() -> str:
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
    source: str = "skill-dna-init",
    subject_kind: str = "unspecified",
) -> dict:
    anchors = key_anchors or []
    return {
        "schema_version": SCHEMA_VERSION,
        "character_name": character_name,
        "slug": slugify(character_name),
        "version": 1,
        "extracted_at": now_iso(),
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
        "subject_kind": subject_kind or "unspecified",
        "identity_lock_status": "pending",
        "studio_agent_version": STUDIO_AGENT_VERSION,
        "video_pipeline_spec": {
            "primary": "grok-imagine-video-1.5",
            "fallback": "grok-imagine-video",
            "note": "portable scaffold — refresh via Studio dna lock when available",
        },
    }


def dna_to_markdown(dna: dict) -> str:
    name = dna["character_name"]
    lines = [
        f"# Character DNA — {name}",
        "",
        f"- **slug:** `{dna['slug']}`",
        f"- **version:** {dna.get('version', 1)}",
        f"- **status:** {dna.get('identity_lock_status', 'pending')}",
        f"- **extracted_at:** {dna.get('extracted_at', '')}",
        f"- **source:** {dna.get('source', '')}",
        "",
        "## Core identity",
        dna.get("core_identity") or "_(fill in)_",
        "",
        "## Facial DNA",
        dna.get("facial_dna") or "_(fill in)_",
        "",
        "## Hair & grooming",
        dna.get("hair_grooming") or "_(fill in)_",
        "",
        "## Clothing & style",
        dna.get("clothing_style") or "_(fill in)_",
        "",
        "## Movement & posture",
        dna.get("movement_posture") or "_(fill in)_",
        "",
        "## Emotional baseline",
        dna.get("emotional_baseline") or "_(fill in)_",
        "",
        "## Motion DNA (video)",
        dna.get("motion_dna") or "_(fill in)_",
        "",
        "## Key consistency anchors",
    ]
    anchors = dna.get("key_consistency_anchors") or []
    if anchors:
        lines.extend(f"- {a}" for a in anchors)
    else:
        lines.append("- _(none yet)_")
    lines.extend(["", "## Next", "", "1. Fill empty fields (or run forensic extract).", "2. `ACTIVATE CHARACTER_DNA_EXTRACTOR` if you have reference stills.", "3. Studio: `python tools/cinematic_studio_cli.py dna lock \"" + name + "\"`", ""])
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Initialize a Character DNA scaffold (portable dna init)",
    )
    p.add_argument("name", help="Character name")
    p.add_argument("--core", default="", help="Core identity traits")
    p.add_argument("--facial", default="", help="Facial structure, eyes, skin tone")
    p.add_argument("--hair", default="", help="Hair and grooming")
    p.add_argument("--clothing", default="", help="Clothing & style")
    p.add_argument("--movement", default="", help="Movement & posture")
    p.add_argument("--emotion", default="", help="Emotional baseline")
    p.add_argument("--motion", default="", help="Motion DNA for video")
    p.add_argument("--anchor", action="append", default=[], help="Key consistency anchor (repeatable)")
    p.add_argument("--output", "-o", type=Path, help="Write dna.json only to this path")
    p.add_argument(
        "--characters-dir",
        type=Path,
        default=Path("characters"),
        help="Root for characters/{slug}/ (default: ./characters)",
    )
    p.add_argument("--stdout", action="store_true", help="Print JSON to stdout only (no files)")
    args = p.parse_args()

    dna = create_dna_scaffold(
        args.name,
        core_identity=args.core,
        facial_dna=args.facial,
        hair_grooming=args.hair,
        clothing_style=args.clothing,
        movement_posture=args.movement,
        emotional_baseline=args.emotion,
        motion_dna=args.motion,
        key_anchors=args.anchor or [],
        source="skill-dna-init",
    )

    if args.stdout:
        json.dump(dna, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    if args.output:
        out = args.output
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(dna, indent=2) + "\n")
        print(f"DNA scaffold created: {out}")
        return

    char_dir = args.characters_dir / dna["slug"]
    char_dir.mkdir(parents=True, exist_ok=True)
    json_path = char_dir / "dna.json"
    md_path = char_dir / "DNA.md"
    json_path.write_text(json.dumps(dna, indent=2) + "\n")
    md_path.write_text(dna_to_markdown(dna))
    print("DNA scaffold created:")
    print(f"  JSON: {json_path}")
    print(f"  Markdown: {md_path}")
    print(f"Next: edit fields, then ACTIVATE CHARACTER_DNA_EXTRACTOR or Studio dna lock \"{args.name}\"")


if __name__ == "__main__":
    main()
