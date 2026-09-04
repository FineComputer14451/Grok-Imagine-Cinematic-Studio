#!/usr/bin/env python3
"""
Assembly Editor (studio v3.7.1 / Grok 4.6) — rough-cut EDL export from QA-approved clips.

Orchestration defaults to grok-4.6; no Imagine spend. See skill assembly-editor.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from studio_paths import ARTIFACTS_DIR, EDL_DIR, SEQUENCES_DIR

SCHEMA_VERSION = "1.0"
STUDIO_AGENT_VERSION = "v3.9.0"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clip_source_path(seq: dict[str, Any], clip: dict[str, Any]) -> str:
    for key in ("polished_url", "result_url", "video_url"):
        val = clip.get(key)
        if val:
            return str(val)
    slug = seq.get("slug", "sequence")
    return str(ARTIFACTS_DIR / "sequences" / slug / f"{clip['clip_id']}.mp4")


def build_edl(
    seq: dict[str, Any],
    *,
    approved_only: bool = True,
    hero_clips: list[str] | None = None,
) -> dict[str, Any]:
    """Build editorial decision list from sequence clips."""
    clips = seq.get("clips", [])
    entries: list[dict[str, Any]] = []
    timeline = 0.0
    skipped: list[str] = []

    for clip in clips:
        cid = clip["clip_id"]
        if hero_clips and cid not in hero_clips:
            skipped.append(cid)
            continue

        status = clip.get("status", "pending")
        qa = clip.get("chain_qa") or clip.get("nsfw_chain_qa") or {}
        decision = qa.get("decision", "pending")

        if approved_only and status not in ("approved", "qa_pass") and decision != "go":
            skipped.append(cid)
            continue

        duration = float(clip.get("duration_seconds", 10))
        in_sec = float(clip.get("edl_in_sec", 0))
        out_sec = float(clip.get("edl_out_sec", duration))
        clip_duration = max(0.1, out_sec - in_sec)

        entries.append({
            "clip_id": cid,
            "index": clip.get("index", 0),
            "in_sec": in_sec,
            "out_sec": out_sec,
            "duration_sec": round(clip_duration, 2),
            "timeline_in_sec": round(timeline, 2),
            "timeline_out_sec": round(timeline + clip_duration, 2),
            "transition": clip.get("transition_to_next", "invisible_edit"),
            "beat_label": clip.get("beat_label") or clip.get("narrative_beat") or f"Beat {cid}",
            "source_path": _clip_source_path(seq, clip),
            "status": status,
            "chain_qa_decision": decision,
            "chain_qa_score": qa.get("weighted_score"),
        })
        timeline += clip_duration

    target = float(seq.get("target_duration_seconds", 0))
    assembled = round(timeline, 2)
    pacing_notes: list[str] = []
    if target and assembled < target * 0.85:
        pacing_notes.append(f"Assembled {assembled}s is {round((1 - assembled / target) * 100)}% under target {target}s")
    elif target and assembled > target * 1.15:
        pacing_notes.append(f"Assembled {assembled}s exceeds target {target}s — trim or defer clips")
    if len(entries) < 2:
        pacing_notes.append("Fewer than 2 clips in EDL — add coverage or B-roll")
    if skipped:
        pacing_notes.append(f"Skipped {len(skipped)} clip(s): {', '.join(skipped[:5])}")

    return {
        "schema_version": SCHEMA_VERSION,
        "studio_agent_version": STUDIO_AGENT_VERSION,
        "cut_name": f"ROUGH_CUT_{seq.get('slug', 'sequence')}",
        "sequence_name": seq.get("sequence_name"),
        "slug": seq.get("slug"),
        "created_at": _now_iso(),
        "approved_only": approved_only,
        "runtime_target_sec": target,
        "assembled_duration_sec": assembled,
        "clip_count": len(entries),
        "skipped_clips": skipped,
        "entries": entries,
        "pacing_diagnosis": pacing_notes,
        "director_cut_priorities": _director_priorities(seq, entries, pacing_notes),
        "handoff": {
            "color_grade": "Apply sequence color_grade notes before polish",
            "ai_polish": [
                e["clip_id"]
                for e in entries
                if (e.get("chain_qa_score") or 0) >= 8
            ],
            "next_agents": [
                "Post-Production Color Grading Supervisor",
                "AI Polish Director",
            ],
        },
    }


def _director_priorities(
    seq: dict[str, Any],
    entries: list[dict[str, Any]],
    pacing: list[str],
) -> list[str]:
    priorities: list[str] = []
    for clip in seq.get("clips", []):
        qa = clip.get("chain_qa") or {}
        if qa.get("decision") == "conditional_go":
            priorities.append(f"Tighten {clip['clip_id']} — conditional chain QA")
        if not clip.get("last_frame_recap") and clip.get("index", 0) > 0:
            priorities.append(f"Capture LAST_FRAME_RECAP for {clip['clip_id']} before extend")
    for note in pacing[:2]:
        priorities.append(note)
    if not priorities:
        priorities.append("EDL ready — proceed to color grade and AI polish")
    return priorities[:5]


def edl_to_markdown(edl: dict[str, Any]) -> str:
    lines = [
        f"# Assembly EDL — {edl['sequence_name']}",
        "",
        f"**Assembled:** {edl['assembled_duration_sec']}s / target {edl['runtime_target_sec']}s  ",
        f"**Clips:** {edl['clip_count']}  ",
        f"**Created:** {edl['created_at']}",
        "",
        "## Timeline",
        "",
        "| # | Clip | In→Out | Duration | Transition | Beat | QA |",
        "|---|------|--------|----------|------------|------|-----|",
    ]
    for i, e in enumerate(edl["entries"], 1):
        lines.append(
            f"| {i} | {e['clip_id']} | {e['in_sec']}–{e['out_sec']}s | {e['duration_sec']}s | "
            f"{e['transition']} | {e['beat_label'][:24]} | {e.get('chain_qa_decision', '—')} |"
        )
    if edl.get("pacing_diagnosis"):
        lines.extend(["", "## Pacing Diagnosis"])
        for p in edl["pacing_diagnosis"]:
            lines.append(f"- {p}")
    if edl.get("director_cut_priorities"):
        lines.extend(["", "## Director's Cut Priorities"])
        for p in edl["director_cut_priorities"]:
            lines.append(f"- {p}")
    return "\n".join(lines) + "\n"


def save_edl(edl: dict[str, Any], *, output: Path | None = None) -> Path:
    slug = edl.get("slug", "sequence")
    out_dir = EDL_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    path = output or out_dir / "assembly_edl.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(edl, indent=2))
    md_path = path.with_suffix(".md")
    md_path.write_text(edl_to_markdown(edl))
    edl["markdown_path"] = str(md_path)
    edl["json_path"] = str(path)
    return path


def load_edl(slug: str) -> dict[str, Any] | None:
    path = EDL_DIR / slug / "assembly_edl.json"
    if not path.exists():
        alt = SEQUENCES_DIR / slug / "assembly_edl.json"
        if alt.exists():
            path = alt
        else:
            return None
    return json.loads(path.read_text())