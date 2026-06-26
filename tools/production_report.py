#!/usr/bin/env python3
"""
Unified production report — batches, sequences, jobs, quota, and artifacts.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from artifact_pipeline import artifacts_summary
from imagine_jobs import job_summary, list_jobs
from nsfw_orchestrator import list_batches as list_nsfw_batches
from project_state import load_project_state
from quota_optimizer import quota_dashboard
from quota_sync import quota_sync_summary
from sequence_chain import list_sequences
from sfw_orchestrator import list_batches as list_sfw_batches


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_production_report(state: dict[str, Any] | None = None) -> dict[str, Any]:
    if state is None:
        state = load_project_state()

    dash = quota_dashboard(state)
    sync = quota_sync_summary(state)
    jobs = job_summary()
    artifacts = artifacts_summary()
    recent = list_jobs(limit=10)

    sfw = list_sfw_batches()
    nsfw = list_nsfw_batches()
    sequences = list_sequences()

    sfw_pending = 0
    nsfw_pending = 0
    for b_meta in sfw:
        try:
            from sfw_orchestrator import load_batch
            b = load_batch(b_meta["batch_id"])
            sfw_pending += sum(
                1 for s in b.get("shots", [])
                if s.get("status") in ("scheduled", "pending", "qa_fail")
            )
        except (FileNotFoundError, OSError):
            pass
    for b_meta in nsfw:
        try:
            from nsfw_orchestrator import load_batch
            b = load_batch(b_meta["batch_id"])
            nsfw_pending += sum(
                1 for s in b.get("shots", [])
                if s.get("status") in ("scheduled", "pending", "qa_fail")
            )
        except (FileNotFoundError, OSError):
            pass

    qa_pending_jobs = jobs.get("by_status", {}).get("qa_pending", 0)
    approved_jobs = jobs.get("by_status", {}).get("approved", 0) + jobs.get("by_status", {}).get("extend_ready", 0)

    return {
        "generated_at": _now_iso(),
        "quota": {
            "session_spent": dash.get("session_spent", 0),
            "budget_remaining": dash.get("budget_remaining"),
            "burn_rate_risk": sync.get("risk_level", "low"),
            "variance_pct": sync.get("variance_pct", 0),
        },
        "batches": {
            "sfw_total": len(sfw),
            "nsfw_total": len(nsfw),
            "sfw_pending_shots": sfw_pending,
            "nsfw_pending_shots": nsfw_pending,
        },
        "sequences": {"total": len(sequences)},
        "imagine_jobs": {
            **jobs,
            "qa_pending": qa_pending_jobs,
            "approved": approved_jobs,
        },
        "artifacts": artifacts,
        "recent_jobs": recent,
    }


def report_to_markdown(report: dict[str, Any]) -> str:
    q = report["quota"]
    b = report["batches"]
    j = report["imagine_jobs"]
    a = report["artifacts"]
    lines = [
        f"# Production Report — {report['generated_at']}",
        "",
        "## Quota",
        f"- Session spent: {q['session_spent']} credits",
        f"- Budget remaining: {q.get('budget_remaining', '—')}",
        f"- Burn-rate risk: {q['burn_rate_risk']} ({q['variance_pct']:+.1f}% variance)",
        "",
        "## Batches",
        f"- SFW: {b['sfw_total']} batches, {b['sfw_pending_shots']} pending shots",
        f"- NSFW: {b['nsfw_total']} batches, {b['nsfw_pending_shots']} pending shots",
        "",
        "## Imagine Jobs",
        f"- Total: {j['total']} | QA pending: {j['qa_pending']} | Approved: {j['approved']}",
        "",
        "## Artifacts",
        f"- Registered: {a['total']} | Downloaded: {a['downloaded']}",
        f"- Dir: `{a['generations_dir']}`",
    ]
    if report.get("recent_jobs"):
        lines += ["", "## Recent jobs"]
        for job in report["recent_jobs"][:5]:
            lines.append(
                f"- {job.get('job_id', '?')[:20]} · {job.get('job_type')} · "
                f"{job.get('status')} · {job.get('shot_id') or job.get('clip_id') or '—'}"
            )
    return "\n".join(lines)