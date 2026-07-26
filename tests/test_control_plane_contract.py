# tests/test_control_plane_contract.py
"""Phase 1: shared severity/attention contract (TUI + Web adapters)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "web_ui"))


def _snap(**overrides: object) -> dict:
    base: dict = {
        "studio_version": "3.8.9",
        "generated_at": "now",
        "project": {"title": "CP", "genre": "Drama", "has_bible": True},
        "studio": {
            "core_agents": 25,
            "total_agents": 34,
            "role_cards": 34,
            "role_cards_expected": 34,
            "skills": 54,
            "models_compatible": True,
            "model_issues": [],
            "model_stack": {"xai_chat": "grok-4.5", "imagine_video": "grok-imagine-video"},
        },
        "quota": {
            "tier_label": "Pro",
            "session_spent": 0,
            "risk_level": "low",
            "reconciliation": {},
        },
        "production": {
            "sequences": 1,
            "characters": 2,
            "identity_locked": 2,
            "nsfw_batches": 0,
            "sfw_batches": 0,
            "imagine_jobs": 0,
        },
        "sequences": [],
        "chain_qa": [],
        "characters": [
            {"name": "A", "slug": "a", "status": "locked"},
            {"name": "B", "slug": "b", "status": "locked"},
        ],
        "recent_jobs": [],
        "quota_alignment": {"status": "aligned", "hint": "ok"},
    }
    base.update(overrides)
    return base


def test_severity_levels_contract() -> None:
    from cli.tui.widgets import strip_severity

    assert strip_severity(_snap()) == "ok"

    no_bible = _snap(project={"title": "CP", "genre": "D", "has_bible": False})
    assert strip_severity(no_bible) == "warn"

    models_bad = _snap()
    models_bad["studio"]["models_compatible"] = False
    assert strip_severity(models_bad) == "critical"

    no_go = _snap(
        chain_qa=[
            {
                "sequence_name": "Act",
                "go_count": 0,
                "no_go_count": 2,
                "chain_qa_status": "no_go",
                "clip_count": 2,
            }
        ]
    )
    assert strip_severity(no_go) == "critical"

    high_risk = _snap()
    high_risk["quota"]["risk_level"] = "high"
    assert strip_severity(high_risk) == "critical"


def test_attention_families_contract() -> None:
    from cli.tui.widgets import collect_home_alerts

    clear = collect_home_alerts(_snap())
    assert clear == []

    alerts = collect_home_alerts(
        _snap(project={"title": "CP", "genre": "D", "has_bible": False})
    )
    assert any("Bible" in a for a in alerts)

    bad = _snap()
    bad["studio"]["models_compatible"] = False
    bad["studio"]["model_issues"] = ["mismatch"]
    bad["quota"]["risk_level"] = "critical"
    alerts = collect_home_alerts(bad)
    assert any("Model" in a for a in alerts)
    assert any("risk" in a.lower() for a in alerts)


def test_web_dashboard_ui_shares_tui_severity() -> None:
    from cli.tui.widgets import strip_severity
    from lib import dashboard_ui as dui

    for snap in (
        _snap(),
        _snap(project={"title": "X", "genre": "G", "has_bible": False}),
    ):
        assert dui.severity(snap) == strip_severity(snap)
        assert dui.attention_rows(snap) == list(
            __import__("cli.tui.widgets", fromlist=["collect_home_alerts"]).collect_home_alerts(
                snap
            )
        )


def test_live_snapshot_contract() -> None:
    from cli.dashboard import build_studio_dashboard
    from cli.tui.widgets import collect_home_alerts, strip_severity
    from lib import dashboard_ui as dui

    snap = dui.attach_quota_alignment(build_studio_dashboard())
    sev = strip_severity(snap)
    assert sev in {"ok", "warn", "critical"}
    assert dui.severity(snap) == sev
    assert isinstance(collect_home_alerts(snap), list)
    assert isinstance(dui.attention_rows(snap), list)
    html = dui.status_strip_html(snap, studio_version="3.8.9")
    assert f"sev-{sev}" in html
