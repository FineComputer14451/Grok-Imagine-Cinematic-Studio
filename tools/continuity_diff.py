#!/usr/bin/env python3
"""
Continuity state diff — clip-to-clip and clip-vs-memory-bank reports (roadmap #9).

Pure functions. Diff what changed; leave scoring to chain QA / drift / seam tools.
"""

from __future__ import annotations

from typing import Any

from sequence_memory import mirror_bank_to_continuity_state

# List-valued continuity keys compared as sets (stable sorted lists in report).
_SET_LIKE_KEYS = frozenset({"props", "visual_motifs", "music_cue_points", "motifs"})


def _scalar(v: Any) -> str:
    if v is None:
        return ""
    if isinstance(v, list):
        return ", ".join(str(x) for x in v)
    return str(v).strip()


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, list):
        return len(v) == 0
    return str(v).strip() == ""


def _normalize_list(v: Any) -> list[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return sorted(str(x).strip() for x in v if str(x).strip())
    if isinstance(v, str):
        return sorted(p.strip() for p in v.split(",") if p.strip())
    s = str(v).strip()
    return [s] if s else []


def _change(
    path: str,
    kind: str,
    before: Any,
    after: Any,
) -> dict[str, Any]:
    return {
        "path": path,
        "kind": kind,
        "before": before,
        "after": after,
    }


def _diff_value(path: str, left: Any, right: Any, *, set_like: bool = False) -> dict[str, Any] | None:
    """Return a change record or None if equal / both empty."""
    if set_like or (isinstance(left, list) or isinstance(right, list)):
        lb = _normalize_list(left)
        rb = _normalize_list(right)
        if lb == rb:
            return None
        if not lb and not rb:
            return None
        if not lb and rb:
            return _change(path, "added", [], rb)
        if lb and not rb:
            return _change(path, "removed", lb, [])
        return _change(path, "changed", lb, rb)

    ls = _scalar(left)
    rs = _scalar(right)
    if ls == rs:
        return None
    if not ls and not rs:
        return None
    if not ls and rs:
        return _change(path, "added", ls, rs)
    if ls and not rs:
        return _change(path, "removed", ls, rs)
    return _change(path, "changed", ls, rs)


def diff_maps(left: dict[str, Any], right: dict[str, Any], prefix: str) -> list[dict[str, Any]]:
    """Union of keys; skip when both sides empty. Props-like keys use set semantics."""
    left = left or {}
    right = right or {}
    if not isinstance(left, dict):
        left = {}
    if not isinstance(right, dict):
        right = {}
    changes: list[dict[str, Any]] = []
    keys = sorted(set(left.keys()) | set(right.keys()), key=str)
    for key in keys:
        path = f"{prefix}.{key}" if prefix else str(key)
        lv = left.get(key)
        rv = right.get(key)
        set_like = str(key) in _SET_LIKE_KEYS
        if _is_empty(lv) and _is_empty(rv):
            continue
        rec = _diff_value(path, lv, rv, set_like=set_like)
        if rec is not None:
            changes.append(rec)
    return changes


def _summarize(changes: list[dict[str, Any]]) -> dict[str, int]:
    added = removed = changed = 0
    for c in changes:
        kind = c.get("kind")
        if kind == "added":
            added += 1
        elif kind == "removed":
            removed += 1
        elif kind == "changed":
            changed += 1
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "total": added + removed + changed,
    }


def _recap_snapshot(text: Any) -> str:
    """Short stable representation for last_frame_recap diffs."""
    s = (text or "").strip() if isinstance(text, str) else _scalar(text)
    if not s:
        return ""
    head = s[:80]
    return f"len={len(s)} | {head}"


def _diff_clip_surfaces(
    left_clip: dict[str, Any],
    right_clip: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """Compare continuity_state, momentum, AMV, reference_image_id, optional recap."""
    changes: list[dict[str, Any]] = []
    sections: list[str] = []
    warnings: list[str] = []

    left_cs = left_clip.get("continuity_state") or {}
    right_cs = right_clip.get("continuity_state") or {}
    if not isinstance(left_cs, dict):
        left_cs = {}
    if not isinstance(right_cs, dict):
        right_cs = {}
    sections.append("continuity_state")
    changes.extend(diff_maps(left_cs, right_cs, "continuity_state"))
    if not left_cs and not right_cs:
        warnings.append("empty continuity_state both sides")

    left_mv = left_clip.get("momentum_vector") or {}
    right_mv = right_clip.get("momentum_vector") or {}
    if not isinstance(left_mv, dict):
        left_mv = {}
    if not isinstance(right_mv, dict):
        right_mv = {}
    sections.append("momentum_vector")
    changes.extend(diff_maps(left_mv, right_mv, "momentum_vector"))

    left_amv = left_clip.get("audio_momentum_vector") or {}
    right_amv = right_clip.get("audio_momentum_vector") or {}
    if not isinstance(left_amv, dict):
        left_amv = {}
    if not isinstance(right_amv, dict):
        right_amv = {}
    sections.append("audio_momentum_vector")
    changes.extend(diff_maps(left_amv, right_amv, "audio_momentum_vector"))

    sections.append("reference_image_id")
    ref_change = _diff_value(
        "reference_image_id",
        left_clip.get("reference_image_id"),
        right_clip.get("reference_image_id"),
    )
    if ref_change is not None:
        changes.append(ref_change)

    left_recap = left_clip.get("last_frame_recap")
    right_recap = right_clip.get("last_frame_recap")
    if not _is_empty(left_recap) or not _is_empty(right_recap):
        sections.append("last_frame_recap")
        recap_change = _diff_value(
            "last_frame_recap",
            _recap_snapshot(left_recap),
            _recap_snapshot(right_recap),
        )
        if recap_change is not None:
            changes.append(recap_change)

    return changes, sections, warnings


def _clip_label(clip: dict[str, Any], fallback: str = "clip") -> str:
    return str(clip.get("clip_id") or fallback)


def diff_clip_pair(
    left_clip: dict[str, Any],
    right_clip: dict[str, Any],
) -> dict[str, Any]:
    """Diff continuity surfaces between two clips (left=previous, right=current)."""
    left_clip = left_clip or {}
    right_clip = right_clip or {}
    changes, sections, warnings = _diff_clip_surfaces(left_clip, right_clip)
    return {
        "mode": "clip_pair",
        "left_label": _clip_label(left_clip, "left"),
        "right_label": _clip_label(right_clip, "right"),
        "changes": changes,
        "summary": _summarize(changes),
        "sections_compared": sections,
        "warnings": warnings,
    }


def diff_clip_vs_bank(
    clip: dict[str, Any],
    memory_bank: dict[str, Any],
) -> dict[str, Any]:
    """
    Diff clip.continuity_state against mirror_bank_to_continuity_state(bank).

    Left = clip, right = memory bank projection (paths under continuity_state.*).
    """
    clip = clip or {}
    projected = mirror_bank_to_continuity_state(memory_bank or {})
    left_cs = clip.get("continuity_state") or {}
    if not isinstance(left_cs, dict):
        left_cs = {}

    changes = diff_maps(left_cs, projected, "continuity_state")
    warnings: list[str] = []
    if not left_cs and not projected:
        warnings.append("empty continuity_state both sides")

    return {
        "mode": "clip_vs_bank",
        "left_label": _clip_label(clip, "clip"),
        "right_label": "memory_bank",
        "changes": changes,
        "summary": _summarize(changes),
        "sections_compared": ["continuity_state"],
        "warnings": warnings,
    }


def format_continuity_diff_table_rows(
    report: dict[str, Any],
) -> list[tuple[str, str, str, str]]:
    """Optional Rich-friendly rows: (path, kind, before, after)."""
    rows: list[tuple[str, str, str, str]] = []
    for c in report.get("changes") or []:
        before = c.get("before")
        after = c.get("after")
        if isinstance(before, list):
            before_s = ", ".join(str(x) for x in before)
        else:
            before_s = _scalar(before)
        if isinstance(after, list):
            after_s = ", ".join(str(x) for x in after)
        else:
            after_s = _scalar(after)
        rows.append(
            (
                str(c.get("path") or ""),
                str(c.get("kind") or ""),
                before_s or "—",
                after_s or "—",
            )
        )
    return rows


def format_continuity_diff_markdown(report: dict[str, Any]) -> str:
    """Human-readable markdown report for CLI / Continuity Guardian."""
    report = report or {}
    mode = report.get("mode") or "clip_pair"
    left = report.get("left_label") or "left"
    right = report.get("right_label") or "right"
    summary = report.get("summary") or {}
    changes = report.get("changes") or []
    sections = report.get("sections_compared") or []
    warnings = report.get("warnings") or []

    lines = [
        "# Continuity Diff",
        "",
        f"**Mode:** `{mode}`  ",
        f"**Left:** {left}  ",
        f"**Right:** {right}  ",
        "",
        "## Summary",
        "",
        f"- added: {summary.get('added', 0)}",
        f"- removed: {summary.get('removed', 0)}",
        f"- changed: {summary.get('changed', 0)}",
        f"- total: {summary.get('total', 0)}",
        "",
        "## Sections compared",
        "",
    ]
    if sections:
        for s in sections:
            lines.append(f"- `{s}`")
    else:
        lines.append("- (none)")
    lines.append("")

    lines.extend(["## Changes", ""])
    if not changes:
        lines.append("_No continuity changes detected._")
        lines.append("")
    else:
        lines.append("| Path | Kind | Before | After |")
        lines.append("|------|------|--------|-------|")
        for path, kind, before, after in format_continuity_diff_table_rows(report):
            # Escape pipes for markdown tables
            before_e = before.replace("|", "\\|")
            after_e = after.replace("|", "\\|")
            lines.append(f"| `{path}` | {kind} | {before_e} | {after_e} |")
        lines.append("")

    if warnings:
        lines.extend(["## Warnings", ""])
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
