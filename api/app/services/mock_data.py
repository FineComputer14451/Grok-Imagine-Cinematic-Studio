from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def mock_snapshot() -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "generated_at": now,
        "project": {
            "title": "Neon Harbor",
            "has_bible": True,
            "slug": "neon-harbor",
        },
        "studio": {
            "core_agents": 12,
            "total_agents": 23,
            "role_cards": 23,
            "role_cards_expected": 23,
            "skills": 52,
            "models_compatible": True,
            "model_issues": [],
            "model_stack": {
                "cinematic": "grok-4.5",
                "build": "grok-4.5",
                "imagine_video": "grok-imagine-video-1.5",
            },
        },
        "quota": {
            "tier": "supergrok_pro",
            "tier_label": "SuperGrok Pro · heavy",
            "session_spent": 660,
            "session_generations": 51,
            "budget_remaining": 1840,
            "risk_level": "moderate",
            "daily_soft_cap": 900,
            "reconciliation": {
                "cascade_source": "session-ledger",
                "burn_rate_multiplier": 1.15,
                "estimated_total": 640,
                "actual_total": 660,
                "entry_count": 12,
            },
            "recent_history": [],
        },
        "production": {
            "sequences": 4,
            "characters": 4,
            "identity_locked": 3,
            "sfw_batches": 2,
            "nsfw_batches": 0,
            "imagine_jobs": 8,
        },
        "readiness": {
            "overall": "hold",
            "identity": {"label": "READY", "ok": True},
            "chain_qa": {"label": "HOLD", "ok": False},
            "plate_motion": {
                "available": True,
                "plate_ok": 4,
                "motion_ok": 2,
            },
            "next_actions": [
                "Fix chain QA no-go on Alley confrontation",
                "Lock Sol Arden DNA before principal plates",
            ],
        },
        "convergence": {
            "ready": False,
            "label": "HOLD · chain QA",
            "checklist": [
                {"id": "bible", "label": "Production Bible present", "ok": True},
                {"id": "identity", "label": "Identity Continuity Protocol", "ok": True},
                {
                    "id": "chain_qa",
                    "label": "Chain QA clear",
                    "ok": False,
                    "hint": "Fix Alley confrontation no-go",
                },
                {
                    "id": "handoff",
                    "label": "Handoff packet validated",
                    "ok": False,
                    "hint": "Re-run after QA pass",
                },
                {"id": "quota", "label": "Quota within soft cap", "ok": True},
            ],
        },
        "delivery": {
            "label": "0 deliver-pass",
            "sequences": [
                {
                    "name": "Harbor approach",
                    "polish_pass": True,
                    "deliver_pass": False,
                    "polish_blockers": [],
                    "deliver_blockers": ["missing delivery package"],
                },
                {
                    "name": "Alley confrontation",
                    "polish_pass": False,
                    "deliver_pass": False,
                    "polish_blockers": ["chain QA hold"],
                    "deliver_blockers": ["polish hold"],
                },
            ],
        },
        "sequences": [
            {
                "name": "Harbor approach",
                "slug": "harbor-approach",
                "clips": 6,
                "target_duration": 42,
                "health": "polish",
            },
            {
                "name": "Alley confrontation",
                "slug": "alley-confrontation",
                "clips": 4,
                "target_duration": 28,
                "health": "qa-hold",
            },
        ],
        "characters": [
            {"name": "Mira Vale", "slug": "mira-vale", "status": "locked"},
            {"name": "Kade Renn", "slug": "kade-renn", "status": "locked"},
            {"name": "Sol Arden", "slug": "sol-arden", "status": "pending"},
            {"name": "Unit 7", "slug": "unit-7", "status": "locked"},
        ],
        "chain_qa": [
            {
                "sequence_name": "Harbor approach",
                "slug": "harbor-approach",
                "go_count": 6,
                "no_go_count": 0,
                "chain_qa_status": "pass",
                "clip_count": 6,
            },
            {
                "sequence_name": "Alley confrontation",
                "slug": "alley-confrontation",
                "go_count": 3,
                "no_go_count": 1,
                "chain_qa_status": "hold",
                "clip_count": 4,
            },
        ],
        "recent_jobs": [
            {
                "job_id": "job_corridor_01",
                "job_type": "video",
                "status": "running",
                "model": "grok-imagine-video-1.5",
            }
        ],
        "sfw_batches": [],
        "nsfw_batches": [],
        "parallel_briefs": {"label": "none", "logs": []},
        "quota_alignment": {
            "status": "aligned",
            "hint": None,
        },
    }


def mock_attention() -> list[str]:
    return [
        "Sequence “Alley confrontation” chain QA holds — 1 no-go clip before handoff",
        "Sol Arden DNA unlocked · lock before principal plates",
        "Quota cascade burn 1.15× — soft cap elevated for session",
    ]
