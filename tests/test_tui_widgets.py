# tests/test_tui_widgets.py
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.dashboard import build_studio_dashboard  # noqa: E402
from cli.tui.widgets import (  # noqa: E402
    format_error_panel,
    format_form_errors,
    format_home_markdown,
)


def test_format_form_errors() -> None:
    text = format_form_errors(["Title is required", "Bad tier"])
    assert "Title is required" in text
    assert "Bad tier" in text
    # Plain text for Static (not Markdown markers)
    assert "**" not in text
    assert "Validation errors:" in text
    assert "•" in text
    assert format_form_errors([]) == ""


def test_format_home_markdown_from_live_snapshot() -> None:
    snap = build_studio_dashboard()
    text = format_home_markdown(snap)
    assert "Studio" in text or snap["studio_version"] in text
    assert snap["project"]["title"] in text or "Project" in text
    assert "Quota" in text or "quota" in text.lower()
    assert "Models" in text or "compatible" in text.lower() or "issues" in text.lower()
    assert "quota sync" in text.lower() or "**s**" in text or "Keys:" in text


def test_format_home_markdown_shows_alignment() -> None:
    snap = {
        "studio_version": "3.8.6",
        "generated_at": "now",
        "project": {"title": "T", "genre": "G", "has_bible": False},
        "studio": {
            "core_agents": 23,
            "total_agents": 34,
            "role_cards": 34,
            "role_cards_expected": 34,
            "skills": 52,
            "models_compatible": True,
            "model_stack": {"xai_chat": "grok-4.5", "imagine_video": "grok-imagine-video"},
        },
        "quota": {
            "tier_label": "Pro",
            "session_spent": 0,
            "risk_level": "low",
            "reconciliation": {
                "cascade_source": "generation_ledger",
                "burn_rate_multiplier": 1.0,
                "estimated_total": 10,
                "actual_total": 10,
                "entry_count": 2,
            },
        },
        "production": {},
        "quota_alignment": {"status": "aligned", "hint": "ok"},
    }
    text = format_home_markdown(snap)
    assert "generation_ledger" in text
    assert "aligned" in text
    assert "s** quota sync" in text or "quota sync" in text


def test_format_error_panel() -> None:
    text = format_error_panel("boom")
    assert "boom" in text
    assert "Error" in text or "error" in text.lower()


def test_studio_tui_importable() -> None:
    from cli.tui.app import StudioTUI, run_tui

    assert callable(run_tui)
    app = StudioTUI(interval=5.0)
    assert app.refresh_interval == 5.0


def test_cockpit_screens_importable() -> None:
    from cli.tui.screens import (
        CockpitMenuScreen,
        ConfirmScreen,
        FormScreen,
        RunningScreen,
    )

    assert CockpitMenuScreen is not None
    assert FormScreen is not None
    assert ConfirmScreen is not None
    assert RunningScreen is not None
