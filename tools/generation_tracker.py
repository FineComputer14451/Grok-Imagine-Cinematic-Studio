"""Generation ledger — track Imagine image/video generations (schema v1.0)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from models import (
    DEFAULT_IMAGINE_IMAGE_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
    USD_PER_CREDIT,
    image_usd_per_image,
    resolve_image_model,
    resolve_video_model,
    usd_to_credits,
    video_usd_per_second,
)

LEDGER_PATH = Path("artifacts/generation_ledger.json")
MAX_ENTRIES = 2000
SCHEMA_VERSION = "1.0"

TOOL_KIND_MAP = {
    "image_gen": "image",
    "image_edit": "image_edit",
    "image_to_video": "video",
    "reference_to_video": "multi_ref_video",
    "extend": "video_extend",
    "stitch": "video_extend",
    "imagine_submit_image": "image",
    "imagine_submit_video": "video",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _entry_id() -> str:
    return "gen_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")


def load_ledger(*, path: Path | None = None) -> dict[str, Any]:
    """Load generation ledger JSON (canonical path owner for quota + CLI).

    ``path`` overrides ``LEDGER_PATH`` (tests / alternate artifact roots).
    Missing or unreadable files yield an empty ledger shell.
    """
    ledger_path = path if path is not None else LEDGER_PATH
    if not ledger_path.exists():
        return {"schema_version": SCHEMA_VERSION, "entries": [], "updated_at": _utc_now()}
    try:
        data = json.loads(ledger_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        data = {"schema_version": SCHEMA_VERSION, "entries": [], "updated_at": _utc_now()}
    if not isinstance(data, dict):
        data = {"schema_version": SCHEMA_VERSION, "entries": [], "updated_at": _utc_now()}
    data.setdefault("schema_version", SCHEMA_VERSION)
    data.setdefault("entries", [])
    if not isinstance(data["entries"], list):
        data["entries"] = []
    return data


def _load() -> dict[str, Any]:
    return load_ledger()


def _save(data: dict[str, Any]) -> None:
    data["updated_at"] = _utc_now()
    entries = data.get("entries") or []
    if len(entries) > MAX_ENTRIES:
        data["entries"] = entries[-MAX_ENTRIES:]
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    _update_project_pointer(data)


def _update_project_pointer(data: dict[str, Any]) -> None:
    state_path = Path(".cinematic_project_state.json")
    try:
        state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    except (json.JSONDecodeError, OSError):
        state = {}
    entries = data.get("entries") or []
    last = entries[-1] if entries else {}
    state["generation_ledger"] = {
        "schema_version": SCHEMA_VERSION,
        "ledger_file": str(LEDGER_PATH).replace("\\", "/"),
        "entry_count": len(entries),
        "last_entry_id": last.get("entry_id"),
        "last_kind": last.get("kind"),
        "updated_at": data.get("updated_at"),
    }
    try:
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    except OSError:
        pass


def _preview(prompt: str | None, limit: int = 120) -> str:
    if not prompt:
        return ""
    text = " ".join(str(prompt).split())
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _estimate_cost(
    kind: str,
    model: str | None,
    duration_seconds: float | None,
    image_count: int,
) -> tuple[float, float, str]:
    """Return (usd, credits, cost_basis)."""
    k = (kind or "image").lower()
    if k in ("video", "video_extend", "multi_ref_video"):
        slug = resolve_video_model(model or DEFAULT_IMAGINE_VIDEO_MODEL)
        rate = video_usd_per_second(slug)
        dur = float(duration_seconds or 10.0)
        usd = round(rate * dur, 4)
        basis = f"{slug} @ ${rate}/s × {dur}s"
    else:
        slug = resolve_image_model(model or DEFAULT_IMAGINE_IMAGE_MODEL)
        rate = image_usd_per_image(slug)
        n = max(1, int(image_count or 1))
        usd = round(rate * n, 4)
        basis = f"{slug} @ ${rate}/image × {n}"
    return usd, usd_to_credits(usd), basis


def log_generation(
    kind: str | None = None,
    tool: str | None = None,
    model: str | None = None,
    prompt: str | None = None,
    status: str = "completed",
    surface: str = "grok_build_tools",
    duration_seconds: float | None = None,
    aspect_ratio: str | None = None,
    artifact_path: str | None = None,
    job_id: str | None = None,
    shot_id: str | None = None,
    sequence_slug: str | None = None,
    character_slug: str | None = None,
    project: str | None = None,
    note: str = "",
    credits_actual: float | None = None,
    image_count: int = 1,
    sync_quota: bool = False,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    resolved_kind = kind or (TOOL_KIND_MAP.get(tool or "", "image") if tool else "image")
    if resolved_kind in ("video", "video_extend", "multi_ref_video"):
        model_slug = resolve_video_model(model or DEFAULT_IMAGINE_VIDEO_MODEL)
    else:
        model_slug = resolve_image_model(model or DEFAULT_IMAGINE_IMAGE_MODEL)

    usd_est, cr_est, basis = _estimate_cost(
        resolved_kind, model_slug, duration_seconds, image_count
    )
    now = _utc_now()
    entry: dict[str, Any] = {
        "entry_id": _entry_id(),
        "kind": resolved_kind,
        "tool": tool,
        "model": model_slug,
        "status": status or "completed",
        "surface": surface or "unknown",
        "prompt_preview": _preview(prompt),
        "duration_seconds": duration_seconds,
        "image_count": image_count if resolved_kind in ("image", "image_edit") else None,
        "aspect_ratio": aspect_ratio,
        "artifact_path": artifact_path,
        "job_id": job_id,
        "shot_id": shot_id,
        "sequence_slug": sequence_slug,
        "character_slug": character_slug,
        "project": project,
        "note": note or "",
        "usd_estimate": usd_est,
        "credits_estimate": cr_est,
        "credits_actual": credits_actual,
        "cost_basis": basis,
        "metadata": metadata or {},
        "created_at": now,
        "updated_at": now,
    }

    data = _load()
    data["entries"].append(entry)
    _save(data)

    if sync_quota and status not in ("dry_run", "cancelled"):
        spend = credits_actual if credits_actual is not None else cr_est
        try:
            from quota_optimizer import record_spend

            record_spend(float(spend), note=note or f"generation {entry['entry_id']}")
        except Exception:
            pass

    return entry


def list_entries(
    kind: str | None = None,
    status: str | None = None,
    model: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    entries = list(_load().get("entries") or [])
    if kind:
        entries = [e for e in entries if e.get("kind") == kind]
    if status:
        entries = [e for e in entries if e.get("status") == status]
    if model:
        entries = [e for e in entries if e.get("model") == model]
    return list(reversed(entries[-limit:])) if limit else list(reversed(entries))


def summarize() -> dict[str, Any]:
    entries = _load().get("entries") or []
    by_kind: dict[str, int] = {}
    by_status: dict[str, int] = {}
    images = 0
    video_sec = 0.0
    usd = 0.0
    credits = 0.0
    credits_actual = 0.0
    has_actual = False
    for e in entries:
        k = e.get("kind") or "unknown"
        by_kind[k] = by_kind.get(k, 0) + 1
        s = e.get("status") or "unknown"
        by_status[s] = by_status.get(s, 0) + 1
        if k in ("image", "image_edit"):
            images += int(e.get("image_count") or 1)
        if k in ("video", "video_extend", "multi_ref_video"):
            video_sec += float(e.get("duration_seconds") or 0)
        usd += float(e.get("usd_estimate") or 0)
        credits += float(e.get("credits_estimate") or 0)
        if e.get("credits_actual") is not None:
            has_actual = True
            credits_actual += float(e["credits_actual"])
    return {
        "entry_count": len(entries),
        "by_kind": by_kind,
        "by_status": by_status,
        "image_count": images,
        "video_seconds": round(video_sec, 2),
        "usd_estimate": round(usd, 4),
        "credits_estimate": round(credits, 2),
        "credits_actual_sum": round(credits_actual, 2) if has_actual else None,
        "ledger_file": str(LEDGER_PATH),
        "usd_per_credit": USD_PER_CREDIT,
    }


def update_entry(
    entry_id: str,
    status: str | None = None,
    artifact_path: str | None = None,
    credits_actual: float | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    data = _load()
    for e in data.get("entries") or []:
        if e.get("entry_id") == entry_id:
            if status is not None:
                e["status"] = status
            if artifact_path is not None:
                e["artifact_path"] = artifact_path
            if credits_actual is not None:
                e["credits_actual"] = credits_actual
            if note is not None:
                e["note"] = note
            e["updated_at"] = _utc_now()
            _save(data)
            return e
    raise KeyError(f"entry not found: {entry_id}")


def export_markdown(limit: int = 50) -> str:
    summary = summarize()
    rows = list_entries(limit=limit)
    lines = [
        "# Generation Ledger Report",
        "",
        f"**Schema:** {SCHEMA_VERSION}  ",
        f"**Entries:** {summary['entry_count']}  ",
        f"**Images (units):** {summary['image_count']}  ",
        f"**Video seconds:** {summary['video_seconds']}  ",
        f"**Est. USD:** ${summary['usd_estimate']}  ",
        f"**Est. credits:** {summary['credits_estimate']}  ",
        f"**By kind:** `{summary['by_kind']}`  ",
        f"**By status:** `{summary['by_status']}`  ",
        "",
        "## Recent entries",
        "",
        "| ID | Kind | Model | Status | Credits | Artifact |",
        "|----|------|-------|--------|---------|----------|",
    ]
    for e in rows:
        art = e.get("artifact_path") or "—"
        if len(str(art)) > 48:
            art = "…" + str(art)[-45:]
        lines.append(
            f"| `{e.get('entry_id', '')}` | {e.get('kind')} | {e.get('model')} | "
            f"{e.get('status')} | {e.get('credits_estimate')} | {art} |"
        )
    lines.append("")
    lines.append(f"_Ledger: `{LEDGER_PATH}`_")
    lines.append("")
    return "\n".join(lines)


def import_from_imagine_jobs(limit: int = 100) -> dict[str, Any]:
    """Import from artifacts/imagine_jobs if present."""
    jobs_path = Path("artifacts/imagine_jobs.json")
    if not jobs_path.exists():
        # try common alternate
        for alt in (Path("artifacts/jobs.json"), Path(".imagine_jobs.json")):
            if alt.exists():
                jobs_path = alt
                break
        else:
            return {"imported": 0, "reason": "no jobs file"}

    try:
        payload = json.loads(jobs_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return {"imported": 0, "reason": str(exc)}

    jobs = payload if isinstance(payload, list) else payload.get("jobs") or payload.get("entries") or []
    imported = 0
    for job in list(jobs)[-limit:]:
        if not isinstance(job, dict):
            continue
        jtype = (job.get("type") or job.get("job_type") or "image").lower()
        kind = "video" if "video" in jtype else "image"
        log_generation(
            kind=kind,
            tool="imagine_submit_" + kind,
            model=job.get("model"),
            prompt=job.get("prompt"),
            status=job.get("status") or "completed",
            surface="api",
            duration_seconds=job.get("duration"),
            artifact_path=job.get("artifact_path") or job.get("output"),
            job_id=job.get("id") or job.get("job_id"),
            note="import-jobs",
            image_count=1,
        )
        imported += 1
    return {"imported": imported, "source": str(jobs_path)}
