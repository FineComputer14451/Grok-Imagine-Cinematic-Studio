#!/usr/bin/env python3
"""Nested wardrobe_lock helpers for Costume & Wardrobe Continuity (P1).

No CLI. Nested under Character DNA as dna["wardrobe_lock"].
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

WARDROBE_SCHEMA_VERSION = "1.0"
CONDITION_VALUES = frozenset({"clean", "worn", "damaged", "wet"})
STATUS_VALUES = frozenset({"pending", "locked", "drift_review"})
SOURCE_VALUES = frozenset({"manual", "extracted", "refined"})


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def create_wardrobe_lock(
    *,
    look_id: str = "look_default",
    label: str = "",
    silhouette: str = "",
    garments: list[dict[str, Any]] | None = None,
    accessories: list[dict[str, Any]] | None = None,
    layer_order: list[str] | None = None,
    condition_default: str = "worn",
    inject_anchors: list[str] | None = None,
    secondary_notes: str = "",
    source: str = "manual",
) -> dict[str, Any]:
    if condition_default not in CONDITION_VALUES:
        raise ValueError(f"Invalid condition_default: {condition_default}")
    if source not in SOURCE_VALUES:
        raise ValueError(f"Invalid source: {source}")
    look = {
        "look_id": look_id,
        "label": label,
        "silhouette": silhouette,
        "garments": list(garments or []),
        "accessories": list(accessories or []),
        "layer_order_bottom_to_top": list(layer_order or []),
        "condition_default": condition_default,
        "inject_anchors": list(inject_anchors or []),
    }
    return {
        "schema_version": WARDROBE_SCHEMA_VERSION,
        "status": "pending",
        "active_look_id": look_id,
        "looks": [look],
        "secondary_notes": secondary_notes or "",
        "locked_at": None,
        "source": source,
    }


def active_look(wardrobe: dict[str, Any]) -> dict[str, Any] | None:
    if not wardrobe:
        return None
    aid = wardrobe.get("active_look_id")
    for look in wardrobe.get("looks") or []:
        if look.get("look_id") == aid:
            return look
    return None


def validate_wardrobe_lock(wardrobe: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    if not isinstance(wardrobe, dict):
        return ["wardrobe_lock must be an object"]
    if wardrobe.get("schema_version") != WARDROBE_SCHEMA_VERSION:
        issues.append(f"Unsupported wardrobe schema_version: {wardrobe.get('schema_version')}")
    status = wardrobe.get("status")
    if status not in STATUS_VALUES:
        issues.append(f"Invalid status: {status}")
    source = wardrobe.get("source")
    if source is not None and source not in SOURCE_VALUES:
        issues.append(f"Invalid source: {source}")
    looks = wardrobe.get("looks") or []
    if not isinstance(looks, list):
        issues.append("looks must be a list")
        return issues
    look_ids = []
    for i, look in enumerate(looks):
        if not isinstance(look, dict):
            issues.append(f"looks[{i}] must be an object")
            continue
        lid = look.get("look_id")
        if not lid:
            issues.append(f"looks[{i}] missing look_id")
        else:
            look_ids.append(lid)
        cond = look.get("condition_default", "worn")
        if cond not in CONDITION_VALUES:
            issues.append(f"looks[{i}] invalid condition_default: {cond}")
    aid = wardrobe.get("active_look_id")
    if aid and aid not in look_ids:
        issues.append(f"active_look_id not in looks: {aid}")
    return issues


def clothing_style_summary(wardrobe: dict[str, Any]) -> str:
    look = active_look(wardrobe)
    if not look:
        return ""
    parts: list[str] = []
    if look.get("label"):
        parts.append(str(look["label"]))
    if look.get("silhouette"):
        parts.append(str(look["silhouette"]))
    for g in look.get("garments") or []:
        name = g.get("name") or g.get("id") or ""
        colors = ", ".join(g.get("colors") or [])
        details = g.get("details") or ""
        chunk = name
        if colors:
            chunk = f"{colors} {chunk}".strip()
        if details:
            chunk = f"{chunk} ({details})" if chunk else details
        if chunk:
            parts.append(chunk)
    for a in look.get("accessories") or []:
        name = a.get("name") or a.get("id") or ""
        if name:
            parts.append(name)
    cond = look.get("condition_default")
    if cond and cond != "clean":
        parts.append(f"condition: {cond}")
    # de-dupe while preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for p in parts:
        key = p.strip().lower()
        if key and key not in seen:
            seen.add(key)
            ordered.append(p.strip())
    return "; ".join(ordered)


def sync_clothing_style(dna: dict[str, Any]) -> str:
    """When wardrobe_lock is locked, rewrite dna['clothing_style'] from active look."""
    wardrobe = dna.get("wardrobe_lock")
    if not isinstance(wardrobe, dict):
        return str(dna.get("clothing_style") or "")
    if wardrobe.get("status") != "locked":
        return str(dna.get("clothing_style") or "")
    summary = clothing_style_summary(wardrobe)
    if summary:
        dna["clothing_style"] = summary
    return summary


def build_wardrobe_inject(wardrobe: dict[str, Any], *, slug: str) -> dict[str, str]:
    look = active_look(wardrobe)
    if not look:
        return {"compact": "", "full": "", "video": ""}
    look_id = look.get("look_id") or "look_default"
    token = f"[WARDROBE_LOCK:{slug}:{look_id}]"
    summary = clothing_style_summary(wardrobe)
    layers = " > ".join(look.get("layer_order_bottom_to_top") or [])
    anchors = "; ".join(look.get("inject_anchors") or [])
    garments = look.get("garments") or []
    accessories = look.get("accessories") or []
    garment_lines = []
    for g in garments:
        garment_lines.append(
            f"- {g.get('name', g.get('id', 'garment'))}: "
            f"colors={', '.join(g.get('colors') or [])}; "
            f"materials={', '.join(g.get('materials') or [])}; "
            f"{g.get('details') or ''}".strip()
        )
    acc_lines = []
    for a in accessories:
        acc_lines.append(f"- {a.get('name', a.get('id', 'accessory'))}: {a.get('details') or ''}".strip())
    cond = look.get("condition_default", "worn")
    compact = f"{token} {summary}".strip()
    full_parts = [
        token,
        f"Look: {look.get('label') or look_id}",
        f"Silhouette: {look.get('silhouette') or 'n/a'}",
        f"Condition: {cond}",
    ]
    if layers:
        full_parts.append(f"Layers (bottom→top): {layers}")
    if garment_lines:
        full_parts.append("Garments:\n" + "\n".join(garment_lines))
    if acc_lines:
        full_parts.append("Accessories:\n" + "\n".join(acc_lines))
    if anchors:
        full_parts.append(f"Anchors: {anchors}")
    notes = wardrobe.get("secondary_notes") or ""
    if notes:
        full_parts.append(f"Secondary wardrobe notes: {notes}")
    full = "\n".join(full_parts)
    video = (
        f"{full}\n"
        f"Fabric/motion: preserve drape, layer separation, and accessory placement under camera move; "
        f"condition stays {cond} unless continuity delta says otherwise."
    )
    return {"compact": compact, "full": full, "video": video}


def build_clip_wardrobe_state(
    *,
    character_slug: str,
    look_id: str,
    condition: str,
    delta: str = "",
    layer_order: list[str] | None = None,
    updated_from_clip: str | None = None,
) -> dict[str, Any]:
    if condition not in CONDITION_VALUES:
        raise ValueError(f"Invalid condition: {condition}")
    state: dict[str, Any] = {
        "character_slug": character_slug,
        "look_id": look_id,
        "condition": condition,
        "delta": delta or "",
        "layer_order_bottom_to_top": list(layer_order or []),
    }
    if updated_from_clip is not None:
        state["updated_from_clip"] = updated_from_clip
    return state


def build_wardrobe_handoff_section(
    wardrobe: dict[str, Any],
    *,
    slug: str,
    condition: str | None = None,
) -> dict[str, Any] | None:
    if not wardrobe or wardrobe.get("status") != "locked":
        return None
    look = active_look(wardrobe)
    if not look:
        return None
    inject = build_wardrobe_inject(wardrobe, slug=slug)
    cond = condition or look.get("condition_default") or "worn"
    if cond not in CONDITION_VALUES:
        cond = "worn"
    return {
        "status": "locked",
        "active_look_id": wardrobe.get("active_look_id"),
        "inject": {"compact": inject["compact"], "full": inject["full"]},
        "condition": cond,
        "secondary_notes": wardrobe.get("secondary_notes") or "",
    }


def lock_wardrobe(wardrobe: dict[str, Any]) -> dict[str, Any]:
    issues = validate_wardrobe_lock(wardrobe)
    # allow lock even with empty garments; only hard-fail invalid enums / active look
    # status is pending before lock — strip status errors for pending→locked transition
    if any("active_look" in i for i in issues):
        raise ValueError("; ".join(issues))
    if any("condition" in i for i in issues):
        raise ValueError("; ".join(issues))
    if any("schema_version" in i for i in issues):
        raise ValueError("; ".join(issues))
    # Ignore Invalid status for allowed transition states; fail other status errors
    if wardrobe.get("status") not in (None, "pending", "drift_review", "locked"):
        status_issues = [i for i in issues if "Invalid status" in i]
        if status_issues:
            raise ValueError("; ".join(issues))
    wardrobe["status"] = "locked"
    wardrobe["locked_at"] = _now_iso()
    return wardrobe


def set_active_look(wardrobe: dict[str, Any], look_id: str) -> dict[str, Any]:
    ids = {look.get("look_id") for look in (wardrobe.get("looks") or [])}
    if look_id not in ids:
        raise ValueError(f"Unknown look_id: {look_id}")
    wardrobe["active_look_id"] = look_id
    return wardrobe
