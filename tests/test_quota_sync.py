"""Tests for quota reconciliation and burn-rate risk."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from quota_sync import (  # noqa: E402
    burn_rate_risk_level,
    default_reconciliation,
    get_burn_rate_risk,
    quota_sync_summary,
    record_generation_spend,
)


def test_burn_rate_risk_levels() -> None:
    assert burn_rate_risk_level(1.0) == "low"
    assert burn_rate_risk_level(1.1) == "medium"
    assert burn_rate_risk_level(1.2) == "high"
    assert burn_rate_risk_level(1.4) == "critical"


def test_record_generation_spend_variance() -> None:
    from unittest.mock import patch

    state: dict = {
        "quota": {
            "session_spent": 0,
            "session_generations": 0,
            "history": [],
            "reconciliation": default_reconciliation(),
        }
    }
    noop = lambda *args, **kwargs: None
    with patch("quota_optimizer.save_project_state", noop), patch(
        "project_state.save_project_state", noop
    ):
        result = record_generation_spend(
            12.0,
            estimated_credits=10.0,
            note="test",
            state=state,
        )
    recon = result["reconciliation"]
    assert recon["actual_total"] == 12.0
    assert recon["estimated_total"] == 10.0
    assert recon["burn_rate_multiplier"] == 1.2
    assert recon["risk_level"] == "high"


def test_quota_sync_summary_shape() -> None:
    summary = quota_sync_summary()
    assert "burn_rate_multiplier" in summary
    assert "risk_level" in summary
    assert get_burn_rate_risk() in ("low", "medium", "high", "critical")


def test_reconcile_includes_generation_ledger(tmp_path, monkeypatch) -> None:
    """quota sync should aggregate generation_ledger.json by project."""
    import json
    from unittest.mock import patch

    from quota_sync import reconcile_from_jobs

    ledger = {
        "schema_version": "1.0",
        "entries": [
            {
                "project": "proj-a",
                "status": "completed",
                "credits_estimate": 10.0,
                "credits_actual": 12.0,
                "updated_at": "2026-07-23T00:00:00+00:00",
            },
            {
                "project": "proj-a",
                "status": "completed",
                "credits_estimate": 5.0,
                "credits_actual": 5.0,
                "updated_at": "2026-07-23T01:00:00+00:00",
            },
            {
                "project": "proj-b",
                "status": "failed",
                "credits_estimate": 2.0,
                "credits_actual": 0.0,
                "updated_at": "2026-07-23T02:00:00+00:00",
            },
        ],
    }
    ledger_path = tmp_path / "generation_ledger.json"
    ledger_path.write_text(json.dumps(ledger), encoding="utf-8")

    state: dict = {
        "quota": {
            "session_spent": 0,
            "session_generations": 0,
            "history": [],
            "reconciliation": default_reconciliation(),
        },
        "imagine_jobs": {"jobs": {}},
    }

    with patch("quota_sync._ledger_path", return_value=ledger_path), patch(
        "project_state.save_project_state", lambda *a, **k: None
    ), patch("quota_sync.save_project_state", lambda *a, **k: None):
        recon = reconcile_from_jobs(state)

    assert recon["estimated_total"] == 17.0
    assert recon["actual_total"] == 17.0
    assert recon["burn_rate_multiplier"] == 1.0
    assert any("ledger:proj-a" in (e.get("note") or "") for e in recon["entries"])
    assert any("ledger:proj-b" in (e.get("note") or "") for e in recon["entries"])


if __name__ == "__main__":
    test_burn_rate_risk_levels()
    test_record_generation_spend_variance()
    test_quota_sync_summary_shape()
    print("All quota sync tests passed")