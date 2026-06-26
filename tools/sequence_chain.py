#!/usr/bin/env python3
"""
Long-form sequence chain — 1.5 extend/stitch protocols, handoffs, and chain QA gates.

Used by:
  - cinematic_studio_cli.py (sequence commands)
  - .grok/skills/cinematic-sequence-extender/scripts/
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models import (
    DEFAULT_IMAGINE_VIDEO_MODEL,
    build_video_pipeline_spec,
    model_stack_summary,
)

SCHEMA_VERSION = "1.0"
SEQUENCES_DIR = Path("sequences")

DEFAULT_PIPELINE = {
    "model": DEFAULT_IMAGINE_VIDEO_MODEL,
    "resolution": "720p",
    "native_audio": True,
    "clip_length_preferred": "8-12s",
    "extend_protocol": "LAST_FRAME + MOTION_VECTOR + AUDIO_CUE",
    "stitch_priority": "high",
}

# Chain QA: extend/stitch-specific checks (1–10 each)
CHAIN_QA_CHECKS = (
    ("last_frame_continuity", "Last frame continuity — clip N+1 starts from clip N end state", 1.5),
    ("momentum_carryover", "Momentum vector carry-over (action, camera, emotion)", 1.2),
    ("audio_momentum_sync", "Audio momentum sync (dialogue state, SFX, music cues)", 1.3),
    ("physics_realism", "Physics realism at stitch boundary", 1.2),
    ("reference_propagation", "reference_image_id propagation fidelity", 1.0),
    ("character_drift_boundary", "Character drift at stitch point", 1.3),
    ("lighting_color_match", "Lighting & color continuity at boundary", 1.0),
    ("prop_environment_state", "Prop & environment state match", 1.0),
    ("transition_readiness", "Previous clip transition readiness", 1.2),
    ("stitch_artifact_risk", "Temporal flicker / morphing / halo risk at stitch", 1.3),
)

CHAIN_QA_PASS_THRESHOLD = 7.0
CHAIN_QA_CRITICAL = frozenset({
    "last_frame_continuity",
    "audio_momentum_sync",
    "character_drift_boundary",
    "transition_readiness",
})


def slugify(name: str) -> str:
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-") or "sequence"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def locked_video_pipeline_spec(pipeline: dict[str, Any] | None = None) -> str:
    """Derive locked VIDEO_PIPELINE_SPEC string from a pipeline dict."""
    spec = pipeline or DEFAULT_PIPELINE
    return build_video_pipeline_spec(spec.get("model"))


def create_sequence_scaffold(
    sequence_name: str,
    *,
    target_duration: int = 60,
    genre: str = "",
    pipeline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "sequence_name": sequence_name,
        "slug": slugify(sequence_name),
        "target_duration_seconds": target_duration,
        "genre": genre,
        "video_pipeline_spec": pipeline or dict(DEFAULT_PIPELINE),
        "model_stack": model_stack_summary(
            video_model=(pipeline or DEFAULT_PIPELINE).get("model")
        ),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
        "clips": [],
        "emotional_temperature_curve": [],
        "sequence_health_score": None,
        "chain_qa_status": "pending",
    }


def create_clip(
    *,
    clip_id: str | None = None,
    index: int = 0,
    duration_seconds: int = 10,
    prompt: str = "",
    reference_image_id: str = "",
    status: str = "pending",
    last_frame_recap: str = "",
    momentum_vector: dict[str, Any] | None = None,
    audio_momentum_vector: dict[str, Any] | None = None,
    continuity_state: dict[str, Any] | None = None,
    transition_to_next: str = "invisible_edit",
    qa_scores: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "clip_id": clip_id or f"clip_{index + 1:03d}",
        "index": index,
        "duration_seconds": duration_seconds,
        "status": status,
        "prompt": prompt,
        "reference_image_id": reference_image_id,
        "last_frame_recap": last_frame_recap,
        "momentum_vector": momentum_vector or _empty_momentum(),
        "audio_momentum_vector": audio_momentum_vector or _empty_audio_momentum(),
        "continuity_state": continuity_state or {},
        "transition_to_next": transition_to_next,
        "qa_scores": qa_scores or {},
        "chain_qa": None,
        "created_at": _now_iso(),
    }


def _empty_momentum() -> dict[str, Any]:
    return {
        "last_action": "",
        "emotional_state": "",
        "camera_velocity": "",
        "lighting_state": "",
        "physics_state": "",
        "visual_motifs": [],
    }


def _empty_audio_momentum() -> dict[str, Any]:
    return {
        "dialogue_state": "",
        "sfx_timing": "",
        "emotional_tone_audio": "",
        "music_cue_points": [],
        "lip_sync_state": "",
    }


def validate_sequence(seq: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not seq.get("sequence_name"):
        issues.append("Missing sequence_name")
    if seq.get("schema_version") != SCHEMA_VERSION:
        issues.append(f"Unsupported schema_version: {seq.get('schema_version')}")
    return issues


def sequence_dir(slug: str) -> Path:
    return SEQUENCES_DIR / slug


def save_sequence(seq: dict[str, Any], *, root: Path | None = None) -> Path:
    seq["updated_at"] = _now_iso()
    base = root or SEQUENCES_DIR
    out_dir = base / seq["slug"]
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "sequence.json"
    path.write_text(json.dumps(seq, indent=2))
    return path


def load_sequence(path: Path) -> dict[str, Any]:
    seq = json.loads(path.read_text())
    issues = validate_sequence(seq)
    if issues:
        raise ValueError("; ".join(issues))
    return seq


def find_sequence(name_or_slug: str, *, root: Path | None = None) -> Path | None:
    base = root or SEQUENCES_DIR
    if not base.exists():
        return None
    slug = slugify(name_or_slug)
    direct = base / slug / "sequence.json"
    if direct.exists():
        return direct
    for seq_file in base.glob("*/sequence.json"):
        data = json.loads(seq_file.read_text())
        if data.get("sequence_name", "").lower() == name_or_slug.lower():
            return seq_file
    return None


def list_sequences(*, root: Path | None = None) -> list[dict[str, Any]]:
    base = root or SEQUENCES_DIR
    if not base.exists():
        return []
    results = []
    for seq_file in sorted(base.glob("*/sequence.json")):
        try:
            data = load_sequence(seq_file)
            results.append({
                "name": data["sequence_name"],
                "slug": data["slug"],
                "clips": len(data.get("clips", [])),
                "target_duration": data.get("target_duration_seconds", 0),
                "health": data.get("sequence_health_score"),
                "chain_qa_status": data.get("chain_qa_status", "pending"),
                "path": str(seq_file),
            })
        except (json.JSONDecodeError, ValueError):
            continue
    return results


def add_clip_to_sequence(seq: dict[str, Any], clip: dict[str, Any]) -> dict[str, Any]:
    clips = seq.setdefault("clips", [])
    clip["index"] = len(clips)
    clip["clip_id"] = f"clip_{clip['index'] + 1:03d}"
    clips.append(clip)
    return seq


def get_clip(seq: dict[str, Any], clip_id: str) -> dict[str, Any] | None:
    for clip in seq.get("clips", []):
        if clip["clip_id"] == clip_id:
            return clip
    return None


def build_handoff_from_clip(clip: dict[str, Any]) -> dict[str, Any]:
    """Generate handoff packet for the next clip in the chain."""
    return {
        "packet_type": "sequence_extend_handoff",
        "schema_version": SCHEMA_VERSION,
        "created_at": _now_iso(),
        "source_clip_id": clip["clip_id"],
        "last_frame_recap": clip.get("last_frame_recap", ""),
        "momentum_vector": clip.get("momentum_vector", _empty_momentum()),
        "audio_momentum_vector": clip.get("audio_momentum_vector", _empty_audio_momentum()),
        "continuity_state": clip.get("continuity_state", {}),
        "reference_image_id": clip.get("reference_image_id", ""),
        "transition_recommendation": clip.get("transition_to_next", "invisible_edit"),
        "extend_instructions": [
            "extend_from_last=true",
            "stitch_to_previous=true",
            "Use LAST_FRAME_RECAP as authoritative starting state",
            "Propagate AUDIO_MOMENTUM_VECTOR for native audio continuity",
            "Maintain reference_image_id unless deliberate scene change",
            "Run chain QA before approving next clip",
        ],
    }


def build_extend_prompt(
    seq: dict[str, Any],
    previous_clip: dict[str, Any],
    next_beat: str,
    *,
    character_injection: str = "",
) -> str:
    """Build a Grok Imagine Video 1.5 native extend prompt for the next clip."""
    handoff = build_handoff_from_clip(previous_clip)
    pipeline = seq.get("video_pipeline_spec", DEFAULT_PIPELINE)
    mv = handoff["momentum_vector"]
    amv = handoff["audio_momentum_vector"]

    lines = []
    if character_injection:
        lines.append(character_injection.strip())
        lines.append("")

    lines += [
        f"[VIDEO_PIPELINE_SPEC: model=\"{pipeline.get('model', 'grok-imagine-video-1.5')}\", "
        f"resolution=\"{pipeline.get('resolution', '720p')}\", native_audio={str(pipeline.get('native_audio', True)).lower()}, "
        f"extend_from_last=true, stitch_to_previous=true]",
        "",
        f"LAST_FRAME_RECAP: {handoff['last_frame_recap']}",
        "",
        "MOMENTUM_VECTOR:",
        f"  last_action: {mv.get('last_action', '')}",
        f"  emotional_state: {mv.get('emotional_state', '')}",
        f"  camera_velocity: {mv.get('camera_velocity', '')}",
        f"  lighting_state: {mv.get('lighting_state', '')}",
        f"  physics_state: {mv.get('physics_state', '')}",
        "",
        "AUDIO_MOMENTUM_VECTOR:",
        f"  dialogue_state: {amv.get('dialogue_state', '')}",
        f"  lip_sync_state: {amv.get('lip_sync_state', '')}",
        f"  sfx_timing: {amv.get('sfx_timing', '')}",
        f"  emotional_tone_audio: {amv.get('emotional_tone_audio', '')}",
        f"  music_cue_points: {', '.join(amv.get('music_cue_points', []))}",
        "",
        f"Next beat: {next_beat}",
        f"Transition: {handoff['transition_recommendation']}",
    ]
    if handoff.get("reference_image_id"):
        lines.append(f"reference_image_id={handoff['reference_image_id']}")
    lines += [
        "",
        "Sound Layer: lip-synced dialogue continuation, SFX carry-over, ambience match, music cue at t=0",
        "Physics: weighty momentum, realistic cloth/hair dynamics, no morphing at stitch boundary",
    ]
    return "\n".join(lines)


def run_chain_qa(
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    scores: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Run 10-point chain QA gate for extend/stitch clips.
    If scores not provided, returns scaffold for manual/agent scoring.
    """
    result: dict[str, Any] = {
        "clip_id": clip["clip_id"],
        "evaluated_at": _now_iso(),
        "checks": {},
        "weighted_score": None,
        "decision": "pending",
        "critical_failures": [],
        "fixes": [],
    }

    if scores is None:
        for key, label, _weight in CHAIN_QA_CHECKS:
            result["checks"][key] = {"label": label, "score": None, "pass": None}
        result["decision"] = "awaiting_scores"
        return result

    total_weight = 0.0
    weighted_sum = 0.0
    critical_failures: list[str] = []

    for key, label, weight in CHAIN_QA_CHECKS:
        score = scores.get(key)
        if score is None:
            result["checks"][key] = {"label": label, "score": None, "pass": None}
            continue
        passed = score >= 7.0
        result["checks"][key] = {"label": label, "score": score, "pass": passed, "weight": weight}
        weighted_sum += score * weight
        total_weight += weight
        if not passed and key in CHAIN_QA_CRITICAL:
            critical_failures.append(key)

    if total_weight > 0:
        result["weighted_score"] = round(weighted_sum / total_weight, 2)

    # Cross-clip validation hints when previous clip exists
    if previous_clip:
        prev_ready = previous_clip.get("qa_scores", {}).get("transition_readiness")
        if prev_ready is not None and prev_ready < 7.0:
            result["fixes"].append(
                f"Previous clip {previous_clip['clip_id']} transition_readiness={prev_ready} — "
                "regenerate ending frames before extending"
            )
        if not previous_clip.get("last_frame_recap"):
            result["fixes"].append(
                f"Previous clip {previous_clip['clip_id']} missing LAST_FRAME_RECAP — capture before extend"
            )

    result["critical_failures"] = critical_failures

    if critical_failures:
        result["decision"] = "no_go"
        result["fixes"].append("Critical chain QA failure — do not extend until fixed")
    elif result["weighted_score"] is not None:
        if result["weighted_score"] >= CHAIN_QA_PASS_THRESHOLD:
            result["decision"] = "go"
        elif result["weighted_score"] >= 5.5:
            result["decision"] = "conditional_go"
            result["fixes"].append("Conditional approval — address low scores before final stitch")
        else:
            result["decision"] = "no_go"
            result["fixes"].append("Weighted score below threshold — regenerate clip")

    return result


def compute_sequence_health(seq: dict[str, Any]) -> float:
    """Compute sequence health score (0–10) from clip QA and chain status."""
    clips = seq.get("clips", [])
    if not clips:
        return 0.0

    scores: list[float] = []
    for i, clip in enumerate(clips):
        chain_qa = clip.get("chain_qa") or {}
        ws = chain_qa.get("weighted_score")
        if ws is not None:
            scores.append(ws)
        elif clip.get("status") == "approved":
            scores.append(8.0)
        elif clip.get("status") == "rejected":
            scores.append(3.0)

        # Penalize broken handoff chain
        if i > 0 and not clips[i - 1].get("last_frame_recap"):
            scores.append(4.0)

    if not scores:
        return 5.0
    return round(sum(scores) / len(scores), 2)


def update_sequence_health(seq: dict[str, Any]) -> dict[str, Any]:
    health = compute_sequence_health(seq)
    seq["sequence_health_score"] = health

    clips = seq.get("clips", [])
    if not clips:
        seq["chain_qa_status"] = "pending"
    elif any((c.get("chain_qa") or {}).get("decision") == "no_go" for c in clips):
        seq["chain_qa_status"] = "no_go"
    elif all((c.get("chain_qa") or {}).get("decision") == "go" for c in clips if c.get("chain_qa")):
        seq["chain_qa_status"] = "go"
    elif health >= CHAIN_QA_PASS_THRESHOLD:
        seq["chain_qa_status"] = "conditional"
    else:
        seq["chain_qa_status"] = "at_risk"

    return seq


def sequence_to_markdown(seq: dict[str, Any]) -> str:
    clips = seq.get("clips", [])
    lines = [
        f"# Sequence Blueprint — {seq['sequence_name']}",
        "",
        f"**Target Duration:** {seq.get('target_duration_seconds', 0)}s  ",
        f"**Clips:** {len(clips)}  ",
        f"**Health Score:** {seq.get('sequence_health_score', 'N/A')}  ",
        f"**Chain QA Status:** {seq.get('chain_qa_status', 'pending')}",
        "",
        "## Video Pipeline Spec",
        locked_video_pipeline_spec(seq.get("video_pipeline_spec")),
        "",
        f"```json\n{json.dumps(seq.get('video_pipeline_spec', {}), indent=2)}\n```",
        "",
        "## Clip Chain",
    ]
    for clip in clips:
        qa = clip.get("chain_qa") or {}
        lines += [
            f"### {clip['clip_id']} ({clip.get('duration_seconds', '?')}s) — {clip.get('status', 'pending')}",
            f"- Transition: {clip.get('transition_to_next', 'invisible_edit')}",
            f"- Chain QA: {qa.get('decision', 'pending')} (score: {qa.get('weighted_score', 'N/A')})",
            f"- LAST_FRAME_RECAP: {clip.get('last_frame_recap', '')[:200] or '(not set)'}",
            "",
        ]
    return "\n".join(lines)