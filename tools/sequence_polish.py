#!/usr/bin/env python3
"""
AI Polish Director hook (studio v3.7.1 / Grok 4.5) — upscale approved sequence clips for delivery.

Orchestration defaults to grok-4.5; execution is local via ai-video-upscaler (not Imagine API).
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from studio_paths import ARTIFACTS_DIR, POLISHED_DIR, STUDIO_ROOT

UPSCALER_SCRIPT = STUDIO_ROOT / ".grok/skills/ai-video-upscaler/scripts/ai_video_upscale.py"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _resolve_clip_file(seq: dict[str, Any], clip: dict[str, Any]) -> Path | None:
    slug = seq.get("slug", "sequence")
    candidates = [
        ARTIFACTS_DIR / "sequences" / slug / f"{clip['clip_id']}.mp4",
        ARTIFACTS_DIR / "raw" / slug / f"{clip['clip_id']}.mp4",
    ]
    for key in ("result_url", "video_url", "polished_url"):
        val = clip.get(key)
        if val and not str(val).startswith("http"):
            candidates.insert(0, Path(val))
    for path in candidates:
        if path.exists():
            return path
    return None


def _run_upscale(
    input_path: Path,
    output_path: Path,
    *,
    scale: int = 2,
    face_restore: bool = False,
    dry_run: bool = False,
) -> dict[str, Any]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if dry_run or not input_path.exists():
        if input_path.exists():
            shutil.copy2(input_path, output_path)
        else:
            output_path.write_text(f"# placeholder polish manifest for {input_path.name}\n")
        return {
            "method": "dry_run",
            "input": str(input_path),
            "output": str(output_path),
            "scale": scale,
            "face_restore": face_restore,
        }

    if not UPSCALER_SCRIPT.exists():
        shutil.copy2(input_path, output_path)
        return {
            "method": "copy_fallback",
            "input": str(input_path),
            "output": str(output_path),
            "note": "ai_video_upscale.py not found — copied source",
        }

    cmd = [
        sys.executable,
        str(UPSCALER_SCRIPT),
        "--input", str(input_path),
        "--output", str(output_path),
        "--scale", str(scale),
    ]
    if face_restore:
        cmd.append("--face-restore")

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, timeout=3600)
        return {"method": "upscale", "input": str(input_path), "output": str(output_path), "scale": scale}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError) as exc:
        shutil.copy2(input_path, output_path)
        return {
            "method": "copy_on_fail",
            "input": str(input_path),
            "output": str(output_path),
            "error": str(exc),
        }


def polish_sequence(
    seq: dict[str, Any],
    *,
    scale: int = 2,
    face_restore: bool = False,
    clip_ids: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Polish approved clips — upscale via AI Polish Director / ai-video-upscaler."""
    slug = seq.get("slug", "sequence")
    out_dir = POLISHED_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    skipped: list[str] = []

    for clip in seq.get("clips", []):
        cid = clip["clip_id"]
        if clip_ids and cid not in clip_ids:
            continue

        qa = clip.get("chain_qa") or clip.get("nsfw_chain_qa") or {}
        if clip.get("status") not in ("approved", "qa_pass") and qa.get("decision") != "go":
            skipped.append(cid)
            continue

        src = _resolve_clip_file(seq, clip)
        out_path = out_dir / f"{cid}_polished.mp4"

        if src is None and dry_run:
            out_path.write_bytes(b"")
            result = {"method": "dry_run_placeholder", "input": None, "output": str(out_path)}
        elif src is None:
            skipped.append(f"{cid}(no_file)")
            continue
        else:
            use_face = face_restore or bool(clip.get("hero_shot"))
            result = _run_upscale(src, out_path, scale=scale, face_restore=use_face, dry_run=dry_run)

        clip["polished_url"] = str(out_path)
        clip["polish_meta"] = {**result, "polished_at": _now_iso()}
        results.append({"clip_id": cid, **result})

    polish_spec = {
        "preset": "custom",
        "scale": scale,
        "face_restore": face_restore,
        "face_restore_policy": "flag_or_hero_shot",
        "studio_version": "v3.7.1",
        "engine": "ai-video-upscaler",
    }
    manifest = {
        "sequence_name": seq.get("sequence_name"),
        "slug": slug,
        "polished_at": _now_iso(),
        "scale": scale,
        "face_restore": face_restore,
        "polish_spec": polish_spec,
        "clips_polished": len(results),
        "clips_skipped": skipped,
        "output_dir": str(out_dir),
        "results": results,
        "bible_log_line": (
            f"[POLISH_SPEC: preset=custom, scale={scale}, "
            f"face_restore={str(face_restore).lower()}, method=sequence_polish, "
            f"studio=v3.7.1, sequence=\"{seq.get('sequence_name', slug)}\"]"
        ),
    }
    manifest_path = out_dir / "polish_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    seq["polish_manifest"] = manifest
    return manifest