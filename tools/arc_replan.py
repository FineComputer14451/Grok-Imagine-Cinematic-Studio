#!/usr/bin/env python3
"""
Arc replan co-pilot (roadmap #12).

After mid-sequence failure (chain QA No-Go, identity drift, temperature fail),
replan remaining clip beats and temperature targets without rewriting the
Production Bible. Pure functions only — no Imagine calls, no Bible mutation.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

from emotional_temperature import normalize_curve, planned_temp_at
from sequence_chain import get_clip

# Actions allowed in v1 (insert_bridge reserved / notes only)
ACTIONS_V1 = frozenset({"soft_reset", "revise_beat", "keep"})

DEFAULT_SOFT_TEMP = 4.0
MID_TEMP = 5.0
DEFAULT_CLIMAX_TEMP = 7.0
MAX_TEMP_STEP = 1.5
DEFAULT_CLIP_DURATION = 10

SOFT_RESET_BEAT = (
    "Recover continuity from last good frame; re-establish identity and "
    "location before advancing story."
)
REANCHOR_BEAT = (
    "Re-anchor emotion; resume story momentum with controlled intensity."
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _clamp_temp(value: float) -> float:
    return max(0.0, min(10.0, float(value)))


def _sorted_clips(seq: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(list(seq.get("clips") or []), key=lambda c: int(c.get("index", 0)))


def infer_replan_reason(clip: dict[str, Any] | None) -> str:
    """
    Infer why a clip warrants arc replan.

    Priority: no_go > identity_drift fail > temperature fail > qa_hold > manual.
    """
    if not clip:
        return "manual"

    chain_qa = clip.get("chain_qa") or {}
    if isinstance(chain_qa, dict) and chain_qa.get("decision") == "no_go":
        return "chain_qa_no_go"

    drift = clip.get("identity_drift") or {}
    if isinstance(drift, dict) and drift.get("pass") is False:
        return "identity_drift"

    temp_gate = clip.get("temperature_gate") or {}
    if isinstance(temp_gate, dict) and temp_gate.get("severity") == "fail":
        return "temperature_fail"

    if clip.get("status") == "qa_hold":
        return "qa_hold"

    return "manual"


def _default_from_index(seq: dict[str, Any]) -> int:
    """First no_go / qa_hold clip index, else last clip index (or 0 if empty)."""
    clips = _sorted_clips(seq)
    if not clips:
        return 0
    for clip in clips:
        reason = infer_replan_reason(clip)
        if reason in ("chain_qa_no_go", "qa_hold"):
            return int(clip.get("index", 0))
        if clip.get("status") == "qa_hold":
            return int(clip.get("index", 0))
        chain_qa = clip.get("chain_qa") or {}
        if isinstance(chain_qa, dict) and chain_qa.get("decision") == "no_go":
            return int(clip.get("index", 0))
    return int(clips[-1].get("index", 0))


def _resolve_from_index(
    seq: dict[str, Any],
    *,
    from_index: int | None,
    from_clip_id: str | None,
) -> int:
    if from_index is not None:
        return int(from_index)
    if from_clip_id:
        clip = get_clip(seq, from_clip_id)
        if clip is None:
            raise ValueError(f"Clip not found: {from_clip_id}")
        return int(clip.get("index", 0))
    return _default_from_index(seq)


def _toward_mid(temp: float, mid: float = MID_TEMP) -> float:
    """Pull temperature halfway toward mid (soft recover anchor)."""
    return _clamp_temp(temp + (mid - temp) * 0.5)


def _end_target_temp(curve: list[dict[str, Any]], clips: list[dict[str, Any]]) -> float:
    """Original end planned temp, or default climax."""
    if curve:
        return float(curve[-1]["temp"])
    if clips:
        last_idx = int(clips[-1].get("index", 0))
        # also try highest index on curve already checked
        _ = last_idx
    return DEFAULT_CLIMAX_TEMP


def _narrative_beat(
    *,
    action: str,
    offset: int,
    is_last: bool,
    reason: str,
) -> str:
    if action == "soft_reset":
        return SOFT_RESET_BEAT
    if is_last:
        return (
            "Climax / resolution; land the emotional arc cleanly and "
            "preserve identity through the final beat."
        )
    if offset == 1:
        return REANCHOR_BEAT
    beat_n = offset + 1  # 1-based within replan window for prose
    if reason == "temperature_fail":
        return (
            f"Advance plot beat {beat_n}; re-align emotional temperature "
            "with a gentler curve slope."
        )
    return f"Advance plot beat {beat_n}; continue narrative progression after recovery."


def _build_temp_series(
    *,
    n: int,
    start_temp: float,
    end_temp: float,
    max_step: float = MAX_TEMP_STEP,
) -> list[float]:
    """Progressive temps from start toward end with max step cap."""
    if n <= 0:
        return []
    if n == 1:
        return [_clamp_temp(start_temp)]

    temps: list[float] = [_clamp_temp(start_temp)]
    for i in range(1, n):
        raw = start_temp + (end_temp - start_temp) * (i / (n - 1))
        prev = temps[-1]
        delta = raw - prev
        if delta > max_step:
            raw = prev + max_step
        elif delta < -max_step:
            raw = prev - max_step
        temps.append(_clamp_temp(raw))
    return temps


def plan_arc_replan(
    seq: dict[str, Any],
    *,
    from_index: int | None = None,
    from_clip_id: str | None = None,
    reason: str | None = None,
) -> dict[str, Any]:
    """
    Build a deterministic arc replan proposal for clips at index >= from_index.

    Frozen prefix = clips with index < from_index. Actions: soft_reset | revise_beat | keep.
    """
    seq = seq or {}
    clips = _sorted_clips(seq)
    resolved_from = _resolve_from_index(
        seq, from_index=from_index, from_clip_id=from_clip_id
    )

    frozen = [c for c in clips if int(c.get("index", 0)) < resolved_from]
    remaining = [c for c in clips if int(c.get("index", 0)) >= resolved_from]

    # Infer reason from the from_index clip when not provided
    trigger_clip: dict[str, Any] | None = None
    for c in remaining:
        if int(c.get("index", 0)) == resolved_from:
            trigger_clip = c
            break
    if trigger_clip is None and remaining:
        trigger_clip = remaining[0]
    if trigger_clip is None and clips:
        for c in clips:
            if int(c.get("index", 0)) == resolved_from:
                trigger_clip = c
                break

    resolved_reason = reason or (
        infer_replan_reason(trigger_clip) if trigger_clip else "manual"
    )

    curve = normalize_curve(seq.get("emotional_temperature_curve"))
    end_temp = _end_target_temp(curve, clips)

    # Soft recover start: previous planned (from_index-1) or 4.0, pulled toward mid 5.0
    prev_planned = planned_temp_at(curve, resolved_from - 1) if resolved_from > 0 else None
    if prev_planned is None:
        prev_planned = planned_temp_at(curve, resolved_from)
    base = float(prev_planned) if prev_planned is not None else DEFAULT_SOFT_TEMP
    start_temp = _toward_mid(base)

    # For temperature_fail, still replan from from_index with gentle slope from current plan
    at_from = planned_temp_at(curve, resolved_from)
    if resolved_reason == "temperature_fail" and at_from is not None:
        start_temp = _toward_mid(float(at_from))

    n = len(remaining)
    # If no remaining clips (empty sequence or from past end), empty proposal
    temps = _build_temp_series(n=n, start_temp=start_temp, end_temp=end_temp)

    use_soft_reset = resolved_reason in (
        "chain_qa_no_go",
        "identity_drift",
        "temperature_fail",
        "qa_hold",
    )

    replanned: list[dict[str, Any]] = []
    patch: list[dict[str, Any]] = []
    alerts: list[str] = []

    for offset, clip in enumerate(remaining):
        idx = int(clip.get("index", resolved_from + offset))
        if offset == 0 and use_soft_reset:
            action = "soft_reset"
        else:
            action = "revise_beat"

        planned = temps[offset] if offset < len(temps) else start_temp
        is_last = offset == n - 1
        beat = _narrative_beat(
            action=action,
            offset=offset,
            is_last=is_last,
            reason=resolved_reason,
        )
        duration = int(clip.get("duration_seconds") or DEFAULT_CLIP_DURATION)
        notes = ""
        if action == "soft_reset":
            notes = (
                "Soft recover at failure index; re-establish continuity before advancing."
            )
        elif resolved_reason == "temperature_fail":
            notes = f"Gentle slope (max step {MAX_TEMP_STEP}) toward end target {end_temp}."

        entry = {
            "clip_id": clip.get("clip_id"),
            "index": idx,
            "action": action,
            "narrative_beat": beat,
            "planned_temp": round(float(planned), 4),
            "duration_seconds": duration,
            "notes": notes,
        }
        replanned.append(entry)
        patch.append(
            {
                "index": idx,
                "temp": round(float(planned), 4),
                "beat": beat,
            }
        )

    if not remaining and clips:
        alerts.append(
            f"from_index={resolved_from} is past all clips; nothing to replan"
        )
    elif not clips:
        alerts.append("Sequence has no clips; empty replan proposal")

    frozen_ids = [str(c.get("clip_id")) for c in frozen if c.get("clip_id")]

    summary = (
        f"Arc replan from index {resolved_from} ({resolved_reason}): "
        f"{len(frozen_ids)} frozen, {len(replanned)} replanned"
    )
    if replanned:
        summary += f"; first action={replanned[0]['action']}"

    return {
        "from_index": resolved_from,
        "reason": resolved_reason,
        "frozen_clip_ids": frozen_ids,
        "replanned_clips": replanned,
        "temperature_curve_patch": normalize_curve(patch),
        "summary": summary,
        "alerts": alerts,
    }


def apply_arc_replan(seq: dict[str, Any], proposal: dict[str, Any]) -> dict[str, Any]:
    """
    Apply a replan proposal to the sequence in place.

    - Sets narrative_beat (and duration when provided) on matching clips
    - Merges temperature_curve_patch into emotional_temperature_curve
    - Appends arc_replan_history with previous curve/beats
    - Sets seq["arc_replan"] meta to the proposal summary fields
    """
    if not isinstance(proposal, dict):
        raise TypeError("proposal must be a dict")

    seq = seq or {}
    from_index = int(proposal.get("from_index", 0))
    replanned = list(proposal.get("replanned_clips") or [])
    patch = list(proposal.get("temperature_curve_patch") or [])

    # Snapshot previous state for history
    prev_curve = deepcopy(seq.get("emotional_temperature_curve") or [])
    prev_beats: dict[str, Any] = {}
    clips = list(seq.get("clips") or [])
    by_index = {int(c.get("index", -1)): c for c in clips}
    by_id = {str(c.get("clip_id")): c for c in clips if c.get("clip_id")}

    for item in replanned:
        clip = None
        cid = item.get("clip_id")
        if cid and str(cid) in by_id:
            clip = by_id[str(cid)]
        else:
            clip = by_index.get(int(item.get("index", -1)))
        if clip is None:
            continue
        key = str(clip.get("clip_id") or item.get("index"))
        prev_beats[key] = clip.get("narrative_beat")

    history = list(seq.get("arc_replan_history") or [])
    history.append(
        {
            "applied_at": _now_iso(),
            "from_index": from_index,
            "reason": proposal.get("reason"),
            "summary": proposal.get("summary"),
            "previous_curve": prev_curve,
            "previous_beats": prev_beats,
            "replanned_clip_ids": [
                item.get("clip_id") for item in replanned if item.get("clip_id")
            ],
        }
    )
    seq["arc_replan_history"] = history

    # Apply narrative beats / optional duration
    for item in replanned:
        action = item.get("action") or "revise_beat"
        if action not in ACTIONS_V1:
            # v1: ignore insert_bridge and unknown actions for mutation
            continue
        if action == "keep":
            continue
        clip = None
        cid = item.get("clip_id")
        if cid and str(cid) in by_id:
            clip = by_id[str(cid)]
        else:
            idx = item.get("index")
            if idx is not None:
                clip = by_index.get(int(idx))
        if clip is None:
            continue
        if item.get("narrative_beat"):
            clip["narrative_beat"] = str(item["narrative_beat"])
        if item.get("duration_seconds") is not None:
            try:
                clip["duration_seconds"] = int(item["duration_seconds"])
            except (TypeError, ValueError):
                pass

    # Merge curve: keep points with index < from_index; replace >= from_index from patch
    existing = normalize_curve(seq.get("emotional_temperature_curve"))
    kept = [p for p in existing if int(p["index"]) < from_index]
    patch_norm = normalize_curve(patch)
    # Prefer patch points; drop any kept duplicates already filtered
    seq["emotional_temperature_curve"] = normalize_curve(kept + patch_norm)

    seq["arc_replan"] = {
        "from_index": from_index,
        "reason": proposal.get("reason"),
        "summary": proposal.get("summary"),
        "applied_at": history[-1]["applied_at"],
        "replanned_count": len(replanned),
        "frozen_clip_ids": list(proposal.get("frozen_clip_ids") or []),
        "alerts": list(proposal.get("alerts") or []),
    }
    return seq


def format_arc_replan_markdown(proposal: dict[str, Any]) -> str:
    """Render a replan proposal as human-readable Markdown."""
    if not proposal:
        return "# Arc Replan\n\n_(empty proposal)_\n"

    lines: list[str] = [
        "# Arc Replan Proposal",
        "",
        f"**From index:** {proposal.get('from_index')}",
        f"**Reason:** {proposal.get('reason', 'manual')}",
        f"**Summary:** {proposal.get('summary', '')}",
        "",
    ]

    frozen = proposal.get("frozen_clip_ids") or []
    lines.append(f"## Frozen prefix ({len(frozen)})")
    if frozen:
        for cid in frozen:
            lines.append(f"- `{cid}`")
    else:
        lines.append("- _(none)_")
    lines.append("")

    replanned = proposal.get("replanned_clips") or []
    lines.append(f"## Replanned clips ({len(replanned)})")
    lines.append("")
    if not replanned:
        lines.append("_(none)_")
    else:
        for item in replanned:
            lines.append(
                f"### [{item.get('index')}] `{item.get('clip_id')}` — "
                f"**{item.get('action')}**"
            )
            lines.append(f"- **Beat:** {item.get('narrative_beat', '')}")
            lines.append(f"- **Planned temp:** {item.get('planned_temp')}")
            lines.append(f"- **Duration:** {item.get('duration_seconds')}s")
            if item.get("notes"):
                lines.append(f"- **Notes:** {item['notes']}")
            lines.append("")

    patch = proposal.get("temperature_curve_patch") or []
    lines.append(f"## Temperature curve patch ({len(patch)} points)")
    if patch:
        for p in patch:
            beat = p.get("beat") or ""
            extra = f" — {beat}" if beat else ""
            lines.append(f"- index {p.get('index')}: temp={p.get('temp')}{extra}")
    else:
        lines.append("- _(none)_")
    lines.append("")

    alerts = proposal.get("alerts") or []
    if alerts:
        lines.append("## Alerts")
        for a in alerts:
            lines.append(f"- {a}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
