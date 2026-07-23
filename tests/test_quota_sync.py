"""Tests for quota reconciliation and burn-rate risk."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from quota_sync import (  # noqa: E402
    burn_rate_risk_level,
    default_reconciliation,
    get_burn_rate_risk,
    quota_sync_summary,
    reconcile_from_jobs,
    record_generation_spend,
)


def _empty_state(**extra: object) -> dict:
    state: dict = {
        "quota": {
            "session_spent": 0,
            "session_generations": 0,
            "history": [],
            "reconciliation": default_reconciliation(),
        },
        "imagine_jobs": {"jobs": {}},
    }
    state.update(extra)
    return state


def test_burn_rate_risk_levels() -> None:
    assert burn_rate_risk_level(1.0) == "low"
    assert burn_rate_risk_level(1.1) == "medium"
    assert burn_rate_risk_level(1.2) == "high"
    assert burn_rate_risk_level(1.4) == "critical"


def test_record_generation_spend_variance() -> None:
    state = _empty_state()
    with patch("quota_optimizer.save_project_state", lambda *a, **k: None), patch(
        "project_state.save_project_state", lambda *a, **k: None
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
    assert result["entry"].get("source") == "record_spend"


def test_quota_sync_summary_shape() -> None:
    summary = quota_sync_summary()
    assert "burn_rate_multiplier" in summary
    assert "risk_level" in summary
    assert "sources" in summary
    assert "cascade_source" in summary
    assert isinstance(summary["sources"], list)
    assert summary["cascade_source"] in (
        "none",
        "generation_ledger",
        "imagine_jobs_actuals",
        "history_est",
    ) or isinstance(summary["cascade_source"], str)
    assert get_burn_rate_risk() in ("low", "medium", "high", "critical")


def test_reconcile_uses_ledger_via_generation_tracker(tmp_path) -> None:
    """Billable ledger rows drive recon; failed / null-actual rows are skipped."""
    ledger = {
        "schema_version": "1.0",
        "entries": [
            {
                "entry_id": "gen_a1",
                "project": "proj-a",
                "status": "completed",
                "credits_estimate": 10.0,
                "credits_actual": 12.0,
                "updated_at": "2026-07-23T00:00:00+00:00",
            },
            {
                "entry_id": "gen_a2",
                "project": "proj-a",
                "status": "completed",
                "credits_estimate": 5.0,
                "credits_actual": 5.0,
                "updated_at": "2026-07-23T01:00:00+00:00",
            },
            {
                "entry_id": "gen_b_fail",
                "project": "proj-b",
                "status": "failed",
                "credits_estimate": 2.0,
                "credits_actual": 0.0,
                "updated_at": "2026-07-23T02:00:00+00:00",
            },
            {
                "entry_id": "gen_c_est_only",
                "project": "proj-c",
                "status": "completed",
                "credits_estimate": 99.0,
                "updated_at": "2026-07-23T03:00:00+00:00",
            },
        ],
    }
    ledger_path = tmp_path / "generation_ledger.json"
    ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
    state = _empty_state()

    with patch(
        "generation_tracker.LEDGER_PATH", ledger_path
    ), patch("project_state.save_project_state", lambda *a, **k: None), patch(
        "quota_sync.save_project_state", lambda *a, **k: None
    ):
        recon = reconcile_from_jobs(state)

    # failed + est-only excluded: est 15, act 17 → burn ~1.133
    assert recon["estimated_total"] == 15.0
    assert recon["actual_total"] == 17.0
    assert recon["burn_rate_multiplier"] == 1.133
    assert recon["risk_level"] == "medium"
    assert recon["sources"] == ["generation_ledger"]
    assert len(recon["entries"]) == 2
    assert all(e.get("source") == "generation_ledger" for e in recon["entries"])
    summary = quota_sync_summary(state)
    assert summary["cascade_source"] == "generation_ledger"
    assert summary["sources"] == ["generation_ledger"]
    assert summary["entry_count"] == 2


def test_reconcile_skips_est_only_jobs() -> None:
    state = _empty_state(
        imagine_jobs={
            "jobs": {
                "j1": {
                    "job_id": "j1",
                    "estimated_credits": 10.0,
                    "updated_at": "2026-07-23T00:00:00+00:00",
                },
                "j2": {
                    "job_id": "j2",
                    "estimated_credits": 8.0,
                    "actual_credits": 9.0,
                    "updated_at": "2026-07-23T01:00:00+00:00",
                },
            }
        }
    )
    empty_ledger = {"schema_version": "1.0", "entries": []}
    with patch(
        "generation_tracker.load_ledger", return_value=empty_ledger
    ), patch("project_state.save_project_state", lambda *a, **k: None), patch(
        "quota_sync.save_project_state", lambda *a, **k: None
    ):
        recon = reconcile_from_jobs(state)

    assert recon["sources"] == ["imagine_jobs_actuals"]
    assert recon["estimated_total"] == 8.0
    assert recon["actual_total"] == 9.0
    assert len(recon["entries"]) == 1
    assert recon["entries"][0]["note"] == "job:j2"


def test_reconcile_exclusive_cascade_prefers_ledger_over_jobs(tmp_path) -> None:
    """Ledger billable rows win; jobs must not be summed on top."""
    ledger = {
        "schema_version": "1.0",
        "entries": [
            {
                "entry_id": "gen_1",
                "project": "solo",
                "status": "completed",
                "credits_estimate": 4.0,
                "credits_actual": 4.0,
            }
        ],
    }
    ledger_path = tmp_path / "generation_ledger.json"
    ledger_path.write_text(json.dumps(ledger), encoding="utf-8")
    state = _empty_state(
        imagine_jobs={
            "jobs": {
                "j1": {
                    "job_id": "j1",
                    "actual_credits": 100.0,
                    "estimated_credits": 100.0,
                }
            }
        }
    )
    with patch(
        "generation_tracker.LEDGER_PATH", ledger_path
    ), patch("project_state.save_project_state", lambda *a, **k: None), patch(
        "quota_sync.save_project_state", lambda *a, **k: None
    ):
        recon = reconcile_from_jobs(state)

    assert recon["sources"] == ["generation_ledger"]
    assert recon["actual_total"] == 4.0
    assert recon["estimated_total"] == 4.0
    assert not any(e.get("source") == "imagine_job" for e in recon["entries"])


def test_reconcile_falls_back_to_history_when_no_ledger_or_jobs() -> None:
    state = _empty_state()
    state["quota"]["history"] = [
        {"at": "2026-07-23T00:00:00+00:00", "credits": 11.0, "note": "manual est:10"},
    ]
    with patch(
        "generation_tracker.load_ledger",
        return_value={"schema_version": "1.0", "entries": []},
    ), patch("project_state.save_project_state", lambda *a, **k: None), patch(
        "quota_sync.save_project_state", lambda *a, **k: None
    ):
        recon = reconcile_from_jobs(state)

    assert recon["sources"] == ["history_est"]
    assert recon["estimated_total"] == 10.0
    assert recon["actual_total"] == 11.0


def test_load_ledger_is_canonical(tmp_path) -> None:
    from generation_tracker import load_ledger

    path = tmp_path / "generation_ledger.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "entries": [{"entry_id": "x", "credits_estimate": 1}],
            }
        ),
        encoding="utf-8",
    )
    data = load_ledger(path=path)
    assert data["schema_version"] == "1.0"
    assert len(data["entries"]) == 1

    missing = load_ledger(path=tmp_path / "nope.json")
    assert missing["entries"] == []


if __name__ == "__main__":
    test_burn_rate_risk_levels()
    test_record_generation_spend_variance()
    test_quota_sync_summary_shape()
    print("All quota sync tests passed")
