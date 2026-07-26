# tests/test_tui_widgets.py
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.dashboard import build_studio_dashboard  # noqa: E402
from cli.tui.widgets import (  # noqa: E402
    collect_home_alerts,
    format_attention_panel,
    format_chain_qa_panel,
    format_characters_panel,
    format_error_panel,
    format_form_errors,
    format_home_error,
    format_home_hints,
    format_home_markdown,
    format_jobs_panel,
    format_quota_panel,
    format_sequences_panel,
    format_status_strip,
    format_studio_panel,
    strip_severity,
)


def _sample_snap(**overrides: object) -> dict:
    snap: dict = {
        "studio_version": "3.8.7",
        "generated_at": "now",
        "project": {"title": "Demo Film", "genre": "Noir", "has_bible": True},
        "studio": {
            "core_agents": 25,
            "total_agents": 34,
            "role_cards": 34,
            "role_cards_expected": 34,
            "skills": 54,
            "models_compatible": True,
            "model_issues": [],
            "model_stack": {
                "xai_chat": "grok-4.5",
                "imagine_video": "grok-imagine-video",
            },
        },
        "quota": {
            "tier_label": "Pro",
            "session_spent": 12,
            "budget_remaining": 100,
            "risk_level": "low",
            "reconciliation": {
                "cascade_source": "generation_ledger",
                "burn_rate_multiplier": 1.0,
                "estimated_total": 10,
                "actual_total": 10,
                "entry_count": 2,
            },
        },
        "production": {
            "sequences": 2,
            "characters": 3,
            "identity_locked": 1,
            "nsfw_batches": 0,
            "sfw_batches": 1,
            "imagine_jobs": 2,
        },
        "sequences": [
            {
                "name": "Act 1",
                "slug": "act-1",
                "clips": 4,
                "health": "ok",
                "target_duration": 60,
            }
        ],
        "chain_qa": [
            {
                "sequence_name": "Act 1",
                "slug": "act-1",
                "go_count": 4,
                "no_go_count": 0,
                "chain_qa_status": "go",
                "clip_count": 4,
            }
        ],
        "characters": [
            {"name": "Ava", "slug": "ava", "status": "locked"},
            {"name": "Ben", "slug": "ben", "status": "pending"},
        ],
        "recent_jobs": [
            {
                "job_id": "j1",
                "job_type": "image",
                "status": "succeeded",
                "model": "grok-imagine-image",
            }
        ],
        "quota_alignment": {"status": "aligned", "hint": "ok"},
    }
    snap.update(overrides)
    return snap


def test_format_form_errors() -> None:
    text = format_form_errors(["Title is required", "Bad tier"])
    assert "Title is required" in text
    assert "Bad tier" in text
    assert "**" not in text
    assert "Validation errors:" in text
    assert "•" in text
    assert format_form_errors([]) == ""


def test_format_status_strip_rollup() -> None:
    text = format_status_strip(_sample_snap())
    assert "Demo Film" in text
    assert "bible:loaded" in text
    assert "models:OK" in text
    assert "risk:low" in text
    assert "DNA 1/3 locked" in text
    assert "QA 4 go · 0 no-go" in text
    assert "3.8.7" in text
    assert "[WARN]" in text or "[OK]" in text or "[CRITICAL]" in text


def test_format_status_strip_models_issues() -> None:
    snap = _sample_snap()
    snap["studio"]["models_compatible"] = False
    text = format_status_strip(snap)
    assert "models:ISSUES" in text


def test_format_quota_panel_alignment() -> None:
    text = format_quota_panel(_sample_snap())
    assert "QUOTA" in text
    assert "Pro" in text
    assert "generation_ledger" in text
    assert "aligned" in text
    assert "risk" in text.lower() or "low" in text


def test_format_studio_panel() -> None:
    text = format_studio_panel(_sample_snap())
    assert "STUDIO" in text
    assert "grok-4.5" in text
    assert "compatible" in text


def test_format_sequences_panel_empty() -> None:
    text = format_sequences_panel(_sample_snap(sequences=[]))
    assert "No sequences yet" in text


def test_format_sequences_panel_rows() -> None:
    text = format_sequences_panel(_sample_snap())
    assert "Act 1" in text
    assert "4 clips" in text
    assert "health ok" in text


def test_format_chain_qa_panel_empty() -> None:
    text = format_chain_qa_panel(_sample_snap(chain_qa=[]))
    assert "No sequence QA data" in text


def test_format_chain_qa_panel_rows() -> None:
    text = format_chain_qa_panel(_sample_snap())
    assert "CHAIN QA" in text
    assert "go 4" in text
    assert "no-go 0" in text
    assert "go" in text


def test_format_characters_panel_empty() -> None:
    text = format_characters_panel(_sample_snap(characters=[]))
    assert "No DNA profiles yet" in text


def test_format_characters_panel_rows() -> None:
    text = format_characters_panel(_sample_snap())
    assert "Ava" in text
    assert "locked" in text


def test_format_jobs_panel_none_when_empty() -> None:
    assert format_jobs_panel(_sample_snap(recent_jobs=[])) is None


def test_format_jobs_panel_rows() -> None:
    text = format_jobs_panel(_sample_snap())
    assert text is not None
    assert "j1" in text
    assert "succeeded" in text


def test_format_home_hints() -> None:
    hints = format_home_hints()
    assert "quota sync" in hints
    assert "launcher" in hints
    assert "doctor" in hints
    assert "validate" in hints
    assert "models" in hints
    assert "stack" in hints


def test_strip_severity_and_attention() -> None:
    ok = _sample_snap()
    # ok sample: bible loaded, models OK, DNA 1/3 → warn for unlocked DNA
    assert strip_severity(ok) == "warn"
    assert any("Identity lock" in a for a in collect_home_alerts(ok))

    clear = _sample_snap()
    clear["production"]["identity_locked"] = 3
    clear["production"]["characters"] = 3
    clear["characters"] = [
        {"name": "Ava", "slug": "ava", "status": "locked"},
        {"name": "Ben", "slug": "ben", "status": "locked"},
        {"name": "Cy", "slug": "cy", "status": "locked"},
    ]
    assert strip_severity(clear) == "ok"
    assert "All clear" in format_attention_panel(clear)

    bad = _sample_snap()
    bad["studio"]["models_compatible"] = False
    bad["studio"]["model_issues"] = ["chat model mismatch"]
    bad["chain_qa"][0]["no_go_count"] = 2
    assert strip_severity(bad) == "critical"
    alerts = collect_home_alerts(bad)
    assert any("Model stack" in a for a in alerts)
    assert any("no-go" in a.lower() for a in alerts)
    assert "ATTENTION" in format_attention_panel(bad)

    warn = _sample_snap(project={"title": "T", "genre": "G", "has_bible": False})
    warn["production"]["identity_locked"] = 3
    warn["production"]["characters"] = 3
    assert strip_severity(warn) == "warn"
    assert any("Bible" in a for a in collect_home_alerts(warn))


def test_format_home_markdown_from_live_snapshot() -> None:
    snap = build_studio_dashboard()
    text = format_home_markdown(snap)
    assert "Studio" in text or snap["studio_version"] in text
    assert snap["project"]["title"] in text or "Untitled" in text or "Project" in text
    assert "QUOTA" in text or "Quota" in text
    assert "quota sync" in text.lower() or "Keys:" in text
    assert "CHAIN QA" in text


def test_format_home_markdown_shows_alignment() -> None:
    text = format_home_markdown(_sample_snap())
    assert "generation_ledger" in text
    assert "aligned" in text
    assert "quota sync" in text


def test_format_error_panel() -> None:
    text = format_error_panel("boom")
    assert "boom" in text
    assert "Error" in text or "error" in text.lower()


def test_format_home_error() -> None:
    text = format_home_error("snap failed")
    assert "snap failed" in text
    assert "r to retry" in text


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
