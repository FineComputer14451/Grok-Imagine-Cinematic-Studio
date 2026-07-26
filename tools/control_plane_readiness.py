"""Cheap readiness rollup for Operator UX control plane (Phase 2 / J3–J5).

Aggregates identity lock, SFW plate/motion signals, and chain QA without
strict spend gates. Used by build_studio_dashboard and pure UI formatters.
"""

from __future__ import annotations

from typing import Any

from motion_readiness import extract_motion_vector, is_complete_motion_triple
from plate_readiness import normalize_plate_status


def _count_identity(characters: list[dict[str, Any]] | None) -> dict[str, Any]:
    chars = characters or []
    total = len(chars)
    locked = sum(1 for c in chars if isinstance(c, dict) and c.get("status") == "locked")
    pending = total - locked
    return {
        "total": total,
        "locked": locked,
        "pending": pending,
        "ready": total == 0 or locked == total,
        "label": f"{locked}/{total} locked" if total else "no DNA",
    }


def _scan_sfw_shots(limit_batches: int = 5, limit_shots: int = 80) -> dict[str, Any]:
    """Scan open SFW batches for plate_status / motion_vector (best-effort)."""
    plate_ok = 0
    plate_pending = 0
    motion_ok = 0
    motion_pending = 0
    video_shots = 0
    scanned = 0
    try:
        from sfw_orchestrator import list_batches, load_batch
    except Exception:
        return {
            "scanned_shots": 0,
            "plate_ok": 0,
            "plate_pending": 0,
            "motion_ok": 0,
            "motion_pending": 0,
            "video_shots": 0,
            "available": False,
        }

    try:
        batches = list_batches()[:limit_batches]
    except Exception:
        batches = []

    for meta in batches:
        if scanned >= limit_shots:
            break
        slug = meta.get("slug") or meta.get("batch_id")
        if not slug:
            continue
        try:
            batch = load_batch(str(slug))
        except Exception:
            continue
        for shot in batch.get("shots") or []:
            if scanned >= limit_shots:
                break
            if not isinstance(shot, dict):
                continue
            scanned += 1
            mode = str(shot.get("recommended_mode") or shot.get("mode") or "").lower()
            wants_video = any(
                x in mode for x in ("video", "i2v", "image_to_video", "extend")
            ) or bool(shot.get("motion_vector") or shot.get("i2v_motion_block"))

            status = normalize_plate_status(shot.get("plate_status"))
            if status in ("approved", "locked"):
                plate_ok += 1
            elif shot.get("plate_status") is not None or wants_video:
                plate_pending += 1

            if wants_video:
                video_shots += 1
                mv = extract_motion_vector(shot)
                if is_complete_motion_triple(mv):
                    motion_ok += 1
                else:
                    motion_pending += 1

    return {
        "scanned_shots": scanned,
        "plate_ok": plate_ok,
        "plate_pending": plate_pending,
        "motion_ok": motion_ok,
        "motion_pending": motion_pending,
        "video_shots": video_shots,
        "available": True,
    }


def _chain_qa_gate(chain_qa: list[dict[str, Any]] | None) -> dict[str, Any]:
    rows = chain_qa or []
    go = 0
    no_go = 0
    no_go_sequences: list[str] = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        g = int(r.get("go_count") or 0)
        n = int(r.get("no_go_count") or 0)
        go += g
        no_go += n
        if n > 0:
            no_go_sequences.append(str(r.get("sequence_name") or r.get("slug") or "?"))
    return {
        "go": go,
        "no_go": no_go,
        "ready": no_go == 0,
        "no_go_sequences": no_go_sequences[:6],
        "label": f"{go} go · {no_go} no-go" if rows else "no QA data",
    }


def next_actions_for_chain_qa(chain_qa_gate: dict[str, Any]) -> list[str]:
    """Human next steps when chain QA is blocking extend."""
    if chain_qa_gate.get("ready") and chain_qa_gate.get("go", 0) >= 0:
        if chain_qa_gate.get("no_go", 0) == 0 and (
            chain_qa_gate.get("go", 0) > 0 or chain_qa_gate.get("label") == "no QA data"
        ):
            if chain_qa_gate.get("label") == "no QA data":
                return ["Run chain QA after first clips (sequence generate → QA review)"]
            return []
    actions: list[str] = []
    for name in chain_qa_gate.get("no_go_sequences") or []:
        actions.append(
            f"No-Go on '{name}': fix clip, re-run chain QA, then sequence handoff/extend"
        )
    if chain_qa_gate.get("no_go", 0) > 0 and not actions:
        actions.append("Resolve chain QA no-gos before extend/stitch spend")
    return actions[:6]


def build_readiness_rollup(
    *,
    characters: list[dict[str, Any]] | None = None,
    chain_qa: list[dict[str, Any]] | None = None,
    production: dict[str, Any] | None = None,
    scan_sfw: bool = True,
) -> dict[str, Any]:
    """Return readiness block for dashboard snapshot."""
    # Prefer live character list; fall back to production counts only
    if characters is None and production:
        identity = {
            "total": int(production.get("characters") or 0),
            "locked": int(production.get("identity_locked") or 0),
            "pending": max(
                0,
                int(production.get("characters") or 0)
                - int(production.get("identity_locked") or 0),
            ),
            "ready": int(production.get("characters") or 0)
            == int(production.get("identity_locked") or 0)
            or int(production.get("characters") or 0) == 0,
            "label": (
                f"{production.get('identity_locked', 0)}/"
                f"{production.get('characters', 0)} locked"
            ),
        }
    else:
        identity = _count_identity(characters)

    plates_motion = _scan_sfw_shots() if scan_sfw else {
        "scanned_shots": 0,
        "plate_ok": 0,
        "plate_pending": 0,
        "motion_ok": 0,
        "motion_pending": 0,
        "video_shots": 0,
        "available": False,
    }
    chain = _chain_qa_gate(chain_qa)
    next_actions = next_actions_for_chain_qa(chain)
    if identity.get("pending", 0) > 0:
        next_actions.insert(
            0,
            f"Lock DNA: {identity['pending']} profile(s) pending → Cockpit DNA lock or Web DNA",
        )
    if plates_motion.get("plate_pending", 0) > 0:
        next_actions.append(
            f"Plate lock: {plates_motion['plate_pending']} shot(s) need approved/locked plates"
        )
    if plates_motion.get("motion_pending", 0) > 0:
        next_actions.append(
            f"Motion brief: {plates_motion['motion_pending']} video shot(s) lack action/camera/emotion"
        )

    # Overall gate: critical blockers = identity incomplete for multi-char OR any no-go
    blockers = 0
    if identity.get("pending", 0) > 0 and identity.get("total", 0) > 0:
        blockers += 1
    if chain.get("no_go", 0) > 0:
        blockers += 1
    if plates_motion.get("plate_pending", 0) > 0:
        blockers += 1
    if plates_motion.get("motion_pending", 0) > 0:
        blockers += 1

    if blockers == 0:
        overall = "ready"
    elif chain.get("no_go", 0) > 0:
        overall = "blocked"
    else:
        overall = "partial"

    return {
        "overall": overall,
        "identity": identity,
        "plate_motion": plates_motion,
        "chain_qa": chain,
        "next_actions": next_actions[:8],
    }
