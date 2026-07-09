#!/usr/bin/env python3
"""
Emotional temperature curve normalize + gate (roadmap #7).

Enforces sequence emotional_temperature_curve against planned beats at
extend time. Warns on flat arcs / off-plan deltas; fails on unplanned spikes.
Observed temperature is heuristic (momentum labels, optional memory bank).
"""

from __future__ import annotations

from typing import Any

# Keyword → 0–10 emotional intensity (substring match, case-insensitive)
LABEL_TEMP: dict[str, float] = {
    "numb": 1,
    "flat": 1,
    "calm": 2,
    "wary": 3,
    "tense": 5,
    "anxious": 6,
    "fear": 7,
    "dread": 7,
    "rage": 9,
    "ecstatic": 9,
    "hopeful": 4,
    "grief": 6,
    "tender": 3,
    "urgent": 6,
    "panicked": 8,
    "determined": 5,
    "intimate": 4,
    "euphoric": 9,
    "despair": 8,
}

_DELTA_WARN = 2.5
_DELTA_FAIL = 4.0
_SPIKE_OBS = 3.0
_SPIKE_PLAN_MAX = 1.5
_DROP_OBS = 3.0
_DROP_PLAN_MAX = 1.5
_FLAT_SPREAD = 0.5
_FLAT_MIN_POINTS = 3


def _clamp_temp(value: float) -> float:
    return max(0.0, min(10.0, float(value)))


def _as_float(value: Any) -> float | None:
    if value is None or value is False:
        return None
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_curve(raw: Any) -> list[dict[str, Any]]:
    """
    Normalize emotional_temperature_curve to sorted list of points:
    {index: int, temp: float, label?: str, beat?: str}.

    Accepts bare numbers, canonical dicts, and aliases (temperature/emotion/t).
    Invalid points (missing temp) are dropped; temp clamped to 0–10.
    """
    if not raw:
        return []
    if not isinstance(raw, (list, tuple)):
        return []

    points: list[dict[str, Any]] = []
    for i, item in enumerate(raw):
        if isinstance(item, (int, float)) and not isinstance(item, bool):
            points.append({"index": i, "temp": _clamp_temp(float(item))})
            continue
        if not isinstance(item, dict):
            continue

        temp = _as_float(item.get("temp"))
        if temp is None:
            temp = _as_float(item.get("temperature"))
        if temp is None:
            # alias t → temp when temperature/temp absent
            temp = _as_float(item.get("t"))
        if temp is None:
            continue

        idx = item.get("index")
        if idx is None:
            idx = item.get("i")
        if idx is None:
            idx = i
        try:
            index = int(idx)
        except (TypeError, ValueError):
            continue

        point: dict[str, Any] = {
            "index": index,
            "temp": _clamp_temp(temp),
        }
        label = item.get("label")
        if label is None or label == "":
            label = item.get("emotion")
        if label is not None and str(label).strip():
            point["label"] = str(label).strip()
        beat = item.get("beat")
        if beat is not None and str(beat).strip():
            point["beat"] = str(beat).strip()
        points.append(point)

    points.sort(key=lambda p: p["index"])
    return points


def planned_temp_at(curve: list[dict[str, Any]] | None, index: int) -> float | None:
    """
    Planned temperature at clip index.

    Exact index match; else linear interpolate between nearest neighbors;
    None if curve empty or index outside neighbor range with no bracket.
    """
    if not curve:
        return None

    # Exact match (first if duplicates after normalize)
    for p in curve:
        if p["index"] == index:
            return float(p["temp"])

    # Need neighbors for interpolation
    lower: dict[str, Any] | None = None
    upper: dict[str, Any] | None = None
    for p in curve:
        if p["index"] < index:
            lower = p
        elif p["index"] > index:
            upper = p
            break

    if lower is not None and upper is not None:
        i0, t0 = int(lower["index"]), float(lower["temp"])
        i1, t1 = int(upper["index"]), float(upper["temp"])
        if i1 == i0:
            return t0
        ratio = (index - i0) / (i1 - i0)
        return round(t0 + ratio * (t1 - t0), 4)

    # Outside range: no extrapolation — None
    return None


def _map_label_temp(text: str) -> float | None:
    """Substring match against LABEL_TEMP; max if multiple hits."""
    if not text or not str(text).strip():
        return None
    lower = str(text).lower()
    hits = [v for k, v in LABEL_TEMP.items() if k in lower]
    if not hits:
        return None
    return float(max(hits))


def infer_observed_temp(
    clip: dict[str, Any] | None,
    memory_bank: dict[str, Any] | None = None,
) -> float | None:
    """
    Infer observed emotional temperature 0–10 from clip / memory bank.

    Priority: numeric fields → momentum emotional_state keywords → bank emotion.
    """
    if not clip:
        clip = {}

    # 1. Explicit numeric on clip
    direct = _as_float(clip.get("emotional_temperature"))
    if direct is not None:
        return _clamp_temp(direct)

    qa = clip.get("qa_scores") or {}
    if isinstance(qa, dict):
        qa_temp = _as_float(qa.get("emotion_temp"))
        if qa_temp is not None:
            return _clamp_temp(qa_temp)

    # 2. Momentum vector emotional_state keywords
    mv = clip.get("momentum_vector") or {}
    if isinstance(mv, dict):
        mapped = _map_label_temp(str(mv.get("emotional_state") or ""))
        if mapped is not None:
            return mapped

    # 3. Memory bank emotion
    bank = memory_bank
    if bank is None and isinstance(clip, dict):
        # allow callers to pass bank only; clip-local bank not standard
        pass
    if isinstance(bank, dict):
        emotion = bank.get("emotion") or {}
        if isinstance(emotion, dict):
            mapped = _map_label_temp(str(emotion.get("last_emotional_state") or ""))
            if mapped is not None:
                return mapped

    return None


def _severity_rank(sev: str) -> int:
    return {"ok": 0, "warn": 1, "fail": 2}.get(sev, 0)


def _raise_severity(current: str, new: str) -> str:
    return new if _severity_rank(new) > _severity_rank(current) else current


def _flat_arc_temps(
    seq: dict[str, Any],
    curve: list[dict[str, Any]],
    clip: dict[str, Any],
    observed: float | None,
    memory_bank: dict[str, Any] | None,
) -> list[float] | None:
    """Collect last 3 temps (observed preferred, else planned) if flat check applies."""
    clips = list(seq.get("clips") or [])
    # Include current clip if not already last in list
    clip_ids = {c.get("clip_id") for c in clips}
    if clip.get("clip_id") not in clip_ids:
        clips = clips + [clip]
    elif clips:
        # refresh current clip entry
        for i, c in enumerate(clips):
            if c.get("clip_id") == clip.get("clip_id"):
                clips[i] = clip
                break

    if len(clips) < _FLAT_MIN_POINTS:
        return None
    if len(curve) < _FLAT_MIN_POINTS:
        return None

    # Span of curve indices
    indices = [int(p["index"]) for p in curve]
    if max(indices) - min(indices) + 1 < _FLAT_MIN_POINTS and len(curve) < _FLAT_MIN_POINTS:
        # curve span ≥3 points means at least 3 curve points
        pass
    if len(curve) < _FLAT_MIN_POINTS:
        return None

    recent = sorted(clips, key=lambda c: int(c.get("index", 0)))[-3:]
    temps: list[float] = []
    for c in recent:
        obs = infer_observed_temp(c, memory_bank)
        if obs is not None:
            temps.append(obs)
        else:
            pt = planned_temp_at(curve, int(c.get("index", 0)))
            if pt is not None:
                temps.append(pt)
    if len(temps) < 3:
        # fall back: use planned for last 3 curve points if we only have current observed
        if observed is not None and len(curve) >= 3:
            planned_tail = [float(p["temp"]) for p in curve[-3:]]
            return planned_tail
        return None
    return temps


def evaluate_temperature_gate(
    seq: dict[str, Any],
    clip: dict[str, Any],
    previous_clip: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Evaluate emotional temperature gate for a clip against sequence curve.

    Returns report with pass, severity, flags, factors, fixes, delta, etc.
    pass is True unless severity is fail.
    """
    seq = seq or {}
    clip = clip or {}
    curve = normalize_curve(seq.get("emotional_temperature_curve"))
    memory_bank = seq.get("memory_bank")
    clip_index = int(clip.get("index", 0))

    planned = planned_temp_at(curve, clip_index)
    observed = infer_observed_temp(clip, memory_bank if isinstance(memory_bank, dict) else None)

    flags: list[str] = []
    factors: list[str] = []
    fixes: list[str] = []
    severity = "ok"
    delta: float | None = None

    # Missing / empty curve
    if not curve or planned is None and not curve:
        flags.append("missing_curve")
        factors.append("emotional_temperature_curve is empty")
        fixes.append("Set curve points via sequence temp set --index N --temp T")
        severity = _raise_severity(severity, "warn")
    elif planned is None:
        factors.append(f"No planned temp at index {clip_index} (outside curve range)")
        fixes.append("Add curve points covering this clip index")
        severity = _raise_severity(severity, "warn")

    # Unobserved
    if observed is None:
        flags.append("unobserved")
        factors.append("Could not infer observed temperature from clip or memory bank")
        fixes.append(
            "Set momentum_vector.emotional_state to a known label "
            "or clip emotional_temperature numeric"
        )
        severity = _raise_severity(severity, "warn")

    # Off-plan delta
    if planned is not None and observed is not None:
        delta = round(observed - planned, 4)
        abs_delta = abs(delta)
        if abs_delta > _DELTA_FAIL:
            flags.append("off_plan")
            factors.append(
                f"|observed-planned|={abs_delta:.2f} > {_DELTA_FAIL} (fail threshold)"
            )
            fixes.append("Re-align clip emotion with planned curve or revise the plan")
            severity = _raise_severity(severity, "fail")
        elif abs_delta > _DELTA_WARN:
            if "off_plan" not in flags:
                flags.append("off_plan")
            factors.append(
                f"|observed-planned|={abs_delta:.2f} > {_DELTA_WARN} (warn threshold)"
            )
            fixes.append("Nudge emotional_state toward planned temperature")
            severity = _raise_severity(severity, "warn")
        else:
            factors.append(f"On-plan delta={delta:.2f} (within warn threshold)")

    # Spike / drop vs previous
    if previous_clip is not None and observed is not None:
        prev_obs = infer_observed_temp(
            previous_clip,
            memory_bank if isinstance(memory_bank, dict) else None,
        )
        prev_index = int(previous_clip.get("index", clip_index - 1))
        prev_planned = planned_temp_at(curve, prev_index)
        if prev_obs is not None:
            obs_rise = observed - prev_obs
            obs_drop = prev_obs - observed
            plan_rise = 0.0
            plan_drop = 0.0
            if planned is not None and prev_planned is not None:
                plan_rise = planned - prev_planned
                plan_drop = prev_planned - planned

            if obs_rise > _SPIKE_OBS and plan_rise < _SPIKE_PLAN_MAX:
                flags.append("unplanned_spike")
                factors.append(
                    f"Observed rise {obs_rise:.2f} > {_SPIKE_OBS} but planned rise "
                    f"{plan_rise:.2f} < {_SPIKE_PLAN_MAX}"
                )
                fixes.append(
                    "Plan the spike on the curve or reduce emotional intensity jump"
                )
                severity = _raise_severity(severity, "fail")

            if obs_drop > _DROP_OBS and plan_drop < _DROP_PLAN_MAX:
                flags.append("unplanned_drop")
                factors.append(
                    f"Observed drop {obs_drop:.2f} > {_DROP_OBS} but planned drop "
                    f"{plan_drop:.2f} < {_DROP_PLAN_MAX}"
                )
                fixes.append(
                    "Plan the emotional drop on the curve or soften the cool-down"
                )
                severity = _raise_severity(severity, "warn")

    # Flat arc
    flat_temps = _flat_arc_temps(seq, curve, clip, observed, memory_bank if isinstance(memory_bank, dict) else None)
    if flat_temps is not None and len(flat_temps) >= 3:
        spread = max(flat_temps) - min(flat_temps)
        if spread <= _FLAT_SPREAD:
            flags.append("flat_arc")
            factors.append(
                f"Last {len(flat_temps)} temps within {_FLAT_SPREAD} "
                f"(spread={spread:.2f}) — arc may be flat"
            )
            fixes.append("Introduce planned rise/fall on emotional_temperature_curve")
            severity = _raise_severity(severity, "warn")

    # suggested_emotion_score
    if planned is not None and observed is not None and delta is not None:
        suggested = 10.0 - min(10.0, abs(delta) * 1.5)
    else:
        suggested = 7.0

    # Deduplicate flags preserving order
    seen: set[str] = set()
    uniq_flags: list[str] = []
    for f in flags:
        if f not in seen:
            seen.add(f)
            uniq_flags.append(f)

    return {
        "clip_id": clip.get("clip_id"),
        "clip_index": clip_index,
        "planned_temp": planned,
        "observed_temp": observed,
        "delta": delta,
        "pass": severity != "fail",
        "severity": severity,
        "flags": uniq_flags,
        "factors": factors,
        "fixes": fixes,
        "curve_length": len(curve),
        "suggested_emotion_score": round(suggested, 2),
    }
