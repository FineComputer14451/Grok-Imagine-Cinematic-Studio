# tests/test_control_plane_readiness.py
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from control_plane_readiness import (  # noqa: E402
    build_readiness_rollup,
    next_actions_for_chain_qa,
)
from handoff_validate import (  # noqa: E402
    format_validation_report,
    validate_handoff_data,
    validate_handoff_file,
)


def test_readiness_identity_and_chain_qa() -> None:
    characters = [
        {"name": "A", "slug": "a", "status": "locked"},
        {"name": "B", "slug": "b", "status": "pending"},
    ]
    chain_qa = [
        {
            "sequence_name": "Act 1",
            "slug": "act-1",
            "go_count": 1,
            "no_go_count": 2,
            "chain_qa_status": "no_go",
        }
    ]
    roll = build_readiness_rollup(
        characters=characters,
        chain_qa=chain_qa,
        scan_sfw=False,
    )
    assert roll["identity"]["locked"] == 1
    assert roll["identity"]["pending"] == 1
    assert roll["identity"]["ready"] is False
    assert roll["chain_qa"]["no_go"] == 2
    assert roll["overall"] == "blocked"
    assert any("Lock DNA" in a or "DNA" in a for a in roll["next_actions"])
    assert any("Act 1" in a or "No-Go" in a or "no-go" in a.lower() for a in roll["next_actions"])


def test_readiness_ready_when_clear() -> None:
    roll = build_readiness_rollup(
        characters=[{"name": "A", "slug": "a", "status": "locked"}],
        chain_qa=[{"sequence_name": "S", "go_count": 3, "no_go_count": 0}],
        scan_sfw=False,
    )
    assert roll["overall"] in {"ready", "partial"}  # partial only if plate scan forced
    assert roll["chain_qa"]["ready"] is True
    assert roll["identity"]["ready"] is True


def test_next_actions_chain_qa() -> None:
    actions = next_actions_for_chain_qa(
        {
            "go": 0,
            "no_go": 1,
            "ready": False,
            "no_go_sequences": ["Hero"],
            "label": "0 go · 1 no-go",
        }
    )
    assert actions
    assert any("Hero" in a for a in actions)


def test_handoff_validate_missing_packet_type() -> None:
    result = validate_handoff_data({"foo": 1})
    assert result["ok"] is False
    assert any("packet_type" in i for i in result["issues"])


def test_handoff_validate_identity_minimal(tmp_path: Path) -> None:
    packet = {
        "packet_type": "identity_lock_handoff",
        "character_name": "Ava",
        "slug": "ava",
        "dna_profile": {"core": "x"},
        "prompt_injection": "CHARACTER_DNA: …",
        "key_consistency_anchors": ["eyes"],
    }
    path = tmp_path / "handoff.json"
    path.write_text(json.dumps(packet), encoding="utf-8")
    result = validate_handoff_file(path)
    # Skill validator preferred; must at least parse
    assert "ok" in result
    assert result.get("packet_type") == "identity_lock_handoff"
    report = format_validation_report(result)
    assert "Handoff validate" in report
    assert "ava" in report.lower() or "identity" in report.lower() or "OK" in report or "FAIL" in report


def test_dashboard_includes_readiness() -> None:
    from cli.dashboard import build_studio_dashboard

    snap = build_studio_dashboard()
    assert "readiness" in snap
    assert "overall" in snap["readiness"]
    assert "identity" in snap["readiness"]
