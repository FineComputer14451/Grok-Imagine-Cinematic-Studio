"""UI-agnostic studio dashboard snapshot aggregation.

Pure data: returns a JSON-serializable dict used by CLI (Rich), TUI (Textual),
Streamlit, and future NiceGUI/API shells. No Rich/Streamlit/Textual imports.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from studio_core.pathutil import ensure_import_paths

ensure_import_paths()

from artifact_pipeline import artifacts_summary  # noqa: E402
from character_dna import list_characters  # noqa: E402
from chain_qa_assist import summarize_sequence_qa  # noqa: E402
from imagine_jobs import job_summary, list_jobs  # noqa: E402
from models import model_stack_summary, verify_model_compatibility  # noqa: E402
from nsfw_orchestrator import list_batches  # noqa: E402
from production_report import build_production_report  # noqa: E402
from project_state import load_project_state  # noqa: E402
from quota_optimizer import assess_budget_risk, quota_dashboard  # noqa: E402
from sequence_chain import find_sequence, list_sequences, load_sequence  # noqa: E402
from sfw_orchestrator import list_batches as list_sfw_batches  # noqa: E402
from studio_health import count_skills  # noqa: E402

# Agent/version metadata still lives in cli.shared (PR later can move to studio_core).
from cli.shared import (  # noqa: E402
    EXPECTED_ROLE_CARD_COUNT,
    STUDIO_VERSION,
    core_agent_count,
    list_role_card_files,
    total_agent_count,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def build_studio_dashboard() -> dict[str, Any]:
    """Aggregate studio snapshot for CLI / TUI / Web / JSON export.

    Contract (stable keys for UI shells):
      generated_at, studio_version, project, studio, quota, production,
      readiness, imagine_jobs, sequences, characters, nsfw_batches,
      sfw_batches, recent_jobs, chain_qa, production_report, artifacts,
      plus phase-3 fields when available (parallel_briefs, convergence, delivery).
    """
    state = load_project_state()
    project = state.get("project") or {}
    dash = quota_dashboard(state)
    model_check = verify_model_compatibility()
    sequences = list_sequences()
    characters = list_characters()
    batches = list_batches()
    sfw_batches = list_sfw_batches()
    imagine_summary = job_summary()
    recent_jobs = list_jobs(limit=8)
    chain_qa_summaries: list[dict[str, Any]] = []
    for s in sequences[:6]:
        seq_path = find_sequence(s["slug"])
        if seq_path:
            try:
                chain_qa_summaries.append(summarize_sequence_qa(load_sequence(seq_path)))
            except (ValueError, OSError):
                pass
    role_cards = list_role_card_files()
    identity_locked = sum(1 for c in characters if c.get("status") == "locked")

    remaining = dash.get("budget_remaining")
    spent = dash.get("session_spent", 0)
    risk = assess_budget_risk(
        {"credits_low": spent, "credits_high": spent},
        tier=dash.get("tier", "supergrok_pro"),
        budget_remaining=remaining,
    )

    production = {
        "sequences": len(sequences),
        "characters": len(characters),
        "identity_locked": identity_locked,
        "nsfw_batches": len(batches),
        "sfw_batches": len(sfw_batches),
        "imagine_jobs": imagine_summary["total"],
        "reference_assets": imagine_summary["reference_assets"],
    }
    try:
        from control_plane_readiness import build_readiness_rollup

        readiness = build_readiness_rollup(
            characters=characters,
            chain_qa=chain_qa_summaries,
            production=production,
            scan_sfw=True,
        )
    except Exception:
        readiness = {
            "overall": "unknown",
            "identity": {
                "total": len(characters),
                "locked": identity_locked,
                "pending": max(0, len(characters) - identity_locked),
                "ready": identity_locked == len(characters),
                "label": f"{identity_locked}/{len(characters)} locked",
            },
            "plate_motion": {"available": False, "scanned_shots": 0},
            "chain_qa": {"go": 0, "no_go": 0, "ready": True, "label": "—"},
            "next_actions": [],
        }

    title = project.get("project_title") or project.get("title") or "Untitled"
    snap: dict[str, Any] = {
        "generated_at": _now_iso(),
        "studio_version": STUDIO_VERSION,
        "project": {
            "title": title,
            "genre": project.get("genre"),
            "has_bible": bool(project),
        },
        "studio": {
            "core_agents": core_agent_count(),
            "total_agents": total_agent_count(),
            "role_cards": len(role_cards),
            "role_cards_expected": EXPECTED_ROLE_CARD_COUNT,
            "skills": count_skills(),
            "models_compatible": model_check["compatible"],
            "model_issues": model_check.get("issues", []),
            "model_stack": model_check.get("model_stack", model_stack_summary()),
        },
        "quota": {**dash, "risk_level": risk.get("risk_level", "unknown")},
        "production": production,
        "readiness": readiness,
        "imagine_jobs": imagine_summary,
        "sequences": sequences[:8],
        "characters": characters[:8],
        "nsfw_batches": batches[:5],
        "sfw_batches": sfw_batches[:5],
        "recent_jobs": recent_jobs,
        "chain_qa": chain_qa_summaries,
        "production_report": build_production_report(state),
        "artifacts": artifacts_summary(),
    }
    try:
        from control_plane_phase3 import build_phase3_snapshot_fields

        snap.update(build_phase3_snapshot_fields(snap))
    except Exception:
        snap["parallel_briefs"] = {"logs": [], "count": 0, "label": "unavailable"}
        snap["convergence"] = {
            "checklist": [],
            "ready": False,
            "ok": 0,
            "fail": 0,
            "label": "unavailable",
        }
        snap["delivery"] = {
            "sequences": [],
            "polish_ready": 0,
            "deliver_ready": 0,
            "total": 0,
            "label": "unavailable",
        }
    return snap
