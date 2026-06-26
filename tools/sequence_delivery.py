#!/usr/bin/env python3
"""
Cinematic delivery — concat polished clips and export social crops via ffmpeg.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from assembly_editor import build_edl, load_edl, save_edl
from studio_paths import DELIVERY_DIR, POLISHED_DIR, STUDIO_ROOT

FFMPEG_SCRIPTS = STUDIO_ROOT / ".grok/skills/cinematic-ffmpeg/scripts"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def _run_script(script: str, *args: str, timeout: int = 600) -> tuple[int, str]:
    path = FFMPEG_SCRIPTS / script
    if not path.exists():
        return 1, f"Script not found: {path}"
    try:
        result = subprocess.run(
            ["bash", str(path), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=STUDIO_ROOT,
        )
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode, output.strip()
    except subprocess.TimeoutExpired:
        return 1, "ffmpeg script timed out"


def deliver_sequence(
    seq: dict[str, Any],
    *,
    formats: list[str] | None = None,
    approved_only: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Build delivery masters from polished clips and EDL."""
    slug = seq.get("slug", "sequence")
    formats = formats or ["16:9"]
    valid_formats = {"16:9", "9:16", "1:1"}
    formats = [f for f in formats if f in valid_formats] or ["16:9"]

    edl = load_edl(slug) or build_edl(seq, approved_only=approved_only)
    save_edl(edl)

    polished_dir = POLISHED_DIR / slug
    delivery_dir = DELIVERY_DIR / slug
    delivery_dir.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, str] = {}
    notes: list[str] = []

    if not polished_dir.exists() or not any(polished_dir.glob("*.mp4")):
        notes.append("No polished clips — run sequence polish first")
        if dry_run:
            rough = delivery_dir / "rough_cut_dry_run.mp4"
            rough.write_text("# dry-run delivery placeholder\n")
            outputs["16:9"] = str(rough)
    elif not _ffmpeg_available():
        notes.append("ffmpeg not on PATH — manifest only")
        manifest_only = delivery_dir / "delivery_manifest.json"
    else:
        rough_cut = delivery_dir / "rough_cut.mp4"
        if dry_run:
            shutil.copy2(next(polished_dir.glob("*.mp4")), rough_cut)
            notes.append("Dry-run — single clip stand-in for concat")
        else:
            code, out = _run_script("concat_clips.sh", str(polished_dir), str(rough_cut))
            if code != 0:
                notes.append(f"Concat failed: {out[:200]}")
            else:
                notes.append(out.splitlines()[-1] if out else "Concatenated")

        if rough_cut.exists():
            outputs["16:9"] = str(rough_cut)
            for fmt in formats:
                if fmt == "16:9":
                    continue
                crop_out = delivery_dir / f"delivery_{fmt.replace(':', 'x')}.mp4"
                if dry_run:
                    shutil.copy2(rough_cut, crop_out)
                else:
                    code, out = _run_script("social_crop.sh", str(rough_cut), str(crop_out), fmt)
                    if code == 0:
                        outputs[fmt] = str(crop_out)
                    else:
                        notes.append(f"Crop {fmt} failed: {out[:120]}")

    manifest = {
        "sequence_name": seq.get("sequence_name"),
        "slug": slug,
        "delivered_at": _now_iso(),
        "formats": formats,
        "outputs": outputs,
        "edl_path": edl.get("json_path") or str(DELIVERY_DIR.parent / "edl" / slug / "assembly_edl.json"),
        "assembled_duration_sec": edl.get("assembled_duration_sec"),
        "notes": notes,
        "dry_run": dry_run,
    }
    manifest_path = delivery_dir / "delivery_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2))
    seq["delivery_manifest"] = manifest
    return manifest