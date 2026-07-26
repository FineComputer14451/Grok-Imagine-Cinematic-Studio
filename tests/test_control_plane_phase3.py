# tests/test_control_plane_phase3.py
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from control_plane_phase3 import (  # noqa: E402
    build_delivery_rollup,
    build_phase3_snapshot_fields,
    convergence_checklist,
    convergence_summary,
    find_parallel_brief_logs,
)
from cli.dashboard import build_studio_dashboard  # noqa: E402
from cli.tui.widgets import (  # noqa: E402
    format_convergence_panel,
    format_delivery_panel,
    format_parallel_briefs_panel,
)
from cli.tui.actions import ACTIONS, answers_to_argv, validate_answers  # noqa: E402


def test_convergence_checklist_shape() -> None:
    snap = {
        "project": {"has_bible": True},
        "studio": {"models_compatible": True},
        "production": {"characters": 0},
        "readiness": {
            "identity": {"ready": True},
            "chain_qa": {"no_go": 0},
            "plate_motion": {"available": False},
        },
    }
    items = convergence_checklist(snap)
    assert len(items) >= 6
    summary = convergence_summary(items)
    assert summary["fail"] == 0
    assert summary["ready"] is True


def test_convergence_fails_on_no_go() -> None:
    snap = {
        "project": {"has_bible": True},
        "studio": {"models_compatible": True},
        "production": {"characters": 1},
        "readiness": {
            "identity": {"ready": True},
            "chain_qa": {"no_go": 2},
            "plate_motion": {"available": False},
        },
    }
    items = convergence_checklist(snap)
    summary = convergence_summary(items)
    assert summary["fail"] >= 1
    assert summary["ready"] is False


def test_find_brief_logs_and_phase3_fields(tmp_path: Path, monkeypatch) -> None:
    art = tmp_path / "artifacts"
    art.mkdir()
    packet = {
        "packet_type": "parallel_brief_dispatch_log",
        "session_id": "t1",
        "briefs": [{"brief_id": "pb-1", "to": "director-of-photography", "priority": "high"}],
        "non_blocking": True,
    }
    path = art / "briefs_t1.json"
    path.write_text(json.dumps(packet), encoding="utf-8")

    import control_plane_phase3 as cp3

    monkeypatch.setattr(cp3, "ARTIFACTS_DIR", art)
    monkeypatch.setattr(cp3, "SEQUENCES_DIR", tmp_path / "no_seq")
    monkeypatch.setattr(cp3, "STUDIO_ROOT", tmp_path)

    logs = find_parallel_brief_logs(limit=5)
    assert any(lg.get("session_id") == "t1" for lg in logs)

    snap = {
        "project": {"has_bible": False},
        "studio": {"models_compatible": True},
        "production": {},
        "readiness": {
            "identity": {"ready": True},
            "chain_qa": {"no_go": 0},
            "plate_motion": {"available": False},
        },
        "sequences": [],
    }
    fields = build_phase3_snapshot_fields(snap)
    assert "parallel_briefs" in fields
    assert "convergence" in fields
    assert "delivery" in fields


def test_dashboard_has_phase3_keys() -> None:
    snap = build_studio_dashboard()
    assert "parallel_briefs" in snap
    assert "convergence" in snap
    assert "delivery" in snap
    assert "checklist" in snap["convergence"]


def test_phase3_panel_formatters() -> None:
    snap = build_studio_dashboard()
    assert "PARALLEL" in format_parallel_briefs_panel(snap) or "brief" in format_parallel_briefs_panel(snap).lower()
    assert "CONVERGENCE" in format_convergence_panel(snap)
    assert "DELIVERY" in format_delivery_panel(snap)


def test_polish_deliver_dry_argv() -> None:
    assert validate_answers("sequence_polish_dry", {"name": "Act1"}) == []
    argv = answers_to_argv(
        "sequence_polish_dry",
        {"name": "Act1", "dry_run": "--dry-run"},
    )
    assert argv[:2] == ["sequence", "polish"]
    assert "Act1" in argv
    assert "--dry-run" in argv

    argv2 = answers_to_argv(
        "sequence_deliver_dry",
        {"name": "Act1", "dry_run": "--dry-run"},
    )
    assert argv2[:2] == ["sequence", "deliver"]
    assert "--dry-run" in argv2


def test_imagine_bridge_and_briefs_actions_registered() -> None:
    assert ACTIONS["imagine_bridge"].base_argv == ("imagine", "bridge")
    assert ACTIONS["wave_a_briefs"].base_argv == ("wave-a", "briefs")
    assert "cockpit" in ACTIONS["sequence_polish_dry"].surfaces
