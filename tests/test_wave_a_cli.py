"""CLI smoke tests for wave-a command group."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "tools" / "cinematic_studio_cli.py"


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd or ROOT),
    )


def test_wave_a_help() -> None:
    r = run_cli("wave-a", "--help")
    assert r.returncode == 0, r.stderr
    assert "plate-motion" in r.stdout
    assert "attach" in r.stdout


def test_wave_a_plate_motion_build(tmp_path: Path) -> None:
    out = tmp_path / "pm.json"
    r = run_cli(
        "wave-a",
        "plate-motion",
        "shot_t1",
        "--status",
        "locked",
        "--action",
        "coat lifts",
        "--camera",
        "dolly in",
        "--emotion",
        "tense",
        "-o",
        str(out),
    )
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(out.read_text())
    assert data["packet_type"] == "plate_motion_readiness"
    assert data["plate_status"] == "locked"


def test_wave_a_validate(tmp_path: Path) -> None:
    out = tmp_path / "contact.json"
    r = run_cli(
        "wave-a",
        "contact",
        "s1",
        "--brief",
        "hand on rail",
        "-o",
        str(out),
    )
    assert r.returncode == 0, r.stdout + r.stderr
    r2 = run_cli("wave-a", "validate", str(out))
    assert r2.returncode == 0, r2.stdout + r2.stderr


def test_wave_a_attach(tmp_path: Path) -> None:
    pm = tmp_path / "pm.json"
    img = tmp_path / "img.json"
    merged = tmp_path / "merged.json"
    run_cli(
        "wave-a",
        "plate-motion",
        "shot_a",
        "--status",
        "locked",
        "--action",
        "walk",
        "--camera",
        "static",
        "--emotion",
        "calm",
        "-o",
        str(pm),
    )
    img.write_text(
        json.dumps(
            {
                "packet_type": "imagine_agent_mode_handoff",
                "protocol_version": "3.8.7",
                "studio_version": "3.8.7",
                "target_surface": "grok_build_tools",
                "execution_mode": "image_to_video",
                "subject_id": "shot_a",
                "prompt": "Slow dolly push-in, first frame lock, coat motion",
                "video_pipeline_spec": '[VIDEO_PIPELINE_SPEC: model="grok-imagine-video"]',
                "sound_layer": "rain",
                "reference_hints": ["plate_a"],
                "model_stack": {"chat": "grok-4.5", "imagine_video": "grok-imagine-video"},
                "quota_note": "1 i2v",
                "return_path": "QA Guardian then record",
                "handoff_steps": ["1. gen", "2. record"],
            }
        )
    )
    r = run_cli(
        "wave-a",
        "attach",
        str(img),
        "--plate-motion",
        str(pm),
        "-o",
        str(merged),
        "--strict-wave-a",
    )
    assert r.returncode == 0, r.stdout + r.stderr
    data = json.loads(merged.read_text())
    assert data["plate_status"] == "locked"
    assert "wave_a" in data
