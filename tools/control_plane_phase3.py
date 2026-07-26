"""Operator UX Phase 3 — multi-agent Parallel Briefs + delivery + convergence.

Read-only rollups for dashboard / TUI / Web. No Imagine spend.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from studio_paths import ARTIFACTS_DIR, SEQUENCES_DIR, STUDIO_ROOT


def _safe_load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def find_parallel_brief_logs(*, limit: int = 8) -> list[dict[str, Any]]:
    """Discover parallel_brief_dispatch_log packets on disk (best-effort)."""
    roots = [
        ARTIFACTS_DIR,
        SEQUENCES_DIR,
        STUDIO_ROOT / "artifacts",
        Path.cwd() / "artifacts",
    ]
    found: list[dict[str, Any]] = []
    seen: set[str] = set()
    patterns = ("**/briefs_*.json", "**/*brief*log*.json", "**/parallel_brief*.json")

    for root in roots:
        if not root or not Path(root).is_dir():
            continue
        root = Path(root)
        for pattern in patterns:
            for path in sorted(root.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True):
                key = str(path.resolve())
                if key in seen:
                    continue
                data = _safe_load_json(path)
                if not data:
                    continue
                ptype = data.get("packet_type") or ""
                if ptype and ptype != "parallel_brief_dispatch_log":
                    # allow files named briefs_* without type only if they have briefs list
                    if "briefs" not in data:
                        continue
                if "briefs" not in data and ptype != "parallel_brief_dispatch_log":
                    continue
                seen.add(key)
                briefs = data.get("briefs") or []
                found.append(
                    {
                        "path": str(path),
                        "session_id": data.get("session_id") or path.stem,
                        "brief_count": len(briefs) if isinstance(briefs, list) else 0,
                        "non_blocking": bool(data.get("non_blocking", True)),
                        "specialists": [
                            str(b.get("to") or "?")
                            for b in (briefs if isinstance(briefs, list) else [])[:6]
                            if isinstance(b, dict)
                        ],
                        "packet_type": ptype or "parallel_brief_dispatch_log",
                    }
                )
                if len(found) >= limit:
                    return found
    return found


def convergence_checklist(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """Checklist before converging into imagine_agent_mode_handoff (J8)."""
    project = snapshot.get("project") or {}
    readiness = snapshot.get("readiness") or {}
    identity = readiness.get("identity") or {}
    chain = readiness.get("chain_qa") or {}
    pm = readiness.get("plate_motion") or {}
    studio = snapshot.get("studio") or {}
    production = snapshot.get("production") or {}

    items: list[dict[str, Any]] = [
        {
            "id": "bible",
            "label": "Production Bible loaded",
            "ok": bool(project.get("has_bible")),
            "hint": "Cockpit create-bible or Web Production",
        },
        {
            "id": "models",
            "label": "Model stack compatible",
            "ok": bool(studio.get("models_compatible")),
            "hint": "models verify · TUI m",
        },
        {
            "id": "identity",
            "label": "Identity locked (cast)",
            "ok": bool(identity.get("ready", True))
            or int(production.get("characters") or 0) == 0,
            "hint": "DNA lock all cast · handoff validate",
        },
        {
            "id": "chain_qa",
            "label": "Chain QA has no no-gos",
            "ok": int(chain.get("no_go") or 0) == 0,
            "hint": "Fix No-Go clips before extend/stitch",
        },
        {
            "id": "plates",
            "label": "Plates not pending (when scanned)",
            "ok": not pm.get("available") or int(pm.get("plate_pending") or 0) == 0,
            "hint": "Lock plates before still→video",
        },
        {
            "id": "motion",
            "label": "Motion briefs complete (when scanned)",
            "ok": not pm.get("available") or int(pm.get("motion_pending") or 0) == 0,
            "hint": "action/camera/emotion triple on video shots",
        },
        {
            "id": "nsfw_gate",
            "label": "NSFW path explicit (no silent ErosForge)",
            "ok": True,  # soft: operator responsibility; always pass with hint
            "hint": "Never silent NSFW handoff — ACTIVATE EROSFORGE when required",
        },
        {
            "id": "handoff_validate",
            "label": "Validate agent-mode / sequence handoff packet",
            "ok": None,  # unknown until user validates a file
            "hint": "cinematic-studio handoff validate PATH · TUI handoff validate",
        },
    ]
    return items


def convergence_summary(checklist: list[dict[str, Any]]) -> dict[str, Any]:
    known = [c for c in checklist if c.get("ok") is not None]
    ok_n = sum(1 for c in known if c.get("ok"))
    fail_n = sum(1 for c in known if c.get("ok") is False)
    ready = fail_n == 0 and ok_n > 0
    return {
        "ready": ready,
        "ok": ok_n,
        "fail": fail_n,
        "unknown": len(checklist) - len(known),
        "label": f"{ok_n}/{len(known)} gates" if known else "no gates",
    }


def build_delivery_rollup(
    sequences: list[dict[str, Any]] | None = None,
    *,
    limit: int = 6,
) -> dict[str, Any]:
    """Per-sequence polish/deliver readiness (soft)."""
    from delivery_readiness import evaluate_delivery_pipeline_readiness
    from sequence_chain import find_sequence, list_sequences, load_sequence

    seq_metas = sequences if sequences is not None else list_sequences()
    rows: list[dict[str, Any]] = []
    polish_ready = 0
    deliver_ready = 0

    for meta in (seq_metas or [])[:limit]:
        if not isinstance(meta, dict):
            continue
        slug = meta.get("slug") or meta.get("name")
        if not slug:
            continue
        try:
            path = find_sequence(str(slug))
            if not path:
                continue
            seq = load_sequence(path)
        except Exception:
            continue
        name = seq.get("sequence_name") or slug
        polish = evaluate_delivery_pipeline_readiness(seq, stage="polish", approved_only=True)
        deliver = evaluate_delivery_pipeline_readiness(seq, stage="deliver", approved_only=True)
        if polish.get("pass"):
            polish_ready += 1
        if deliver.get("pass"):
            deliver_ready += 1
        rows.append(
            {
                "name": name,
                "slug": seq.get("slug") or slug,
                "polish_pass": bool(polish.get("pass")),
                "deliver_pass": bool(deliver.get("pass")),
                "polish_blockers": list(polish.get("blockers") or [])[:3],
                "deliver_blockers": list(deliver.get("blockers") or [])[:3],
                "polish_warnings": list(polish.get("warnings") or [])[:2],
            }
        )

    return {
        "sequences": rows,
        "polish_ready": polish_ready,
        "deliver_ready": deliver_ready,
        "total": len(rows),
        "label": f"polish {polish_ready}/{len(rows)} · deliver {deliver_ready}/{len(rows)}",
    }


def build_phase3_snapshot_fields(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Attach multi-agent + delivery + convergence to an existing snapshot dict."""
    briefs = find_parallel_brief_logs(limit=8)
    checklist = convergence_checklist(snapshot)
    conv = convergence_summary(checklist)
    delivery = build_delivery_rollup(snapshot.get("sequences"), limit=6)
    return {
        "parallel_briefs": {
            "logs": briefs,
            "count": len(briefs),
            "label": f"{len(briefs)} brief log(s)" if briefs else "no brief logs on disk",
        },
        "convergence": {
            "checklist": checklist,
            **conv,
        },
        "delivery": delivery,
    }
