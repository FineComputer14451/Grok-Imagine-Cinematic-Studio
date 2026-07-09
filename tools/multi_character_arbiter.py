#!/usr/bin/env python3
"""
Multi-character identity arbiter (roadmap #8).

Elects a primary lock, assigns reference weights, detects cast conflicts,
and builds dual/multi DNA inject blocks with anti-merge language.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from character_dna import (
    build_prompt_blocks,
    find_character_dna,
    load_character_dna,
    slugify,
)

# Primary ref weight by cast size N
_PRIMARY_WEIGHT_BY_N: dict[int, float] = {
    2: 0.75,
    3: 0.70,
}
_PRIMARY_WEIGHT_DEFAULT = 0.65  # N >= 4 (and fallback)


def _conflict(code: str, severity: str, message: str) -> dict[str, str]:
    return {"code": code, "severity": severity, "message": message}


def _primary_weight_for_n(n: int) -> float:
    if n <= 1:
        return 1.0
    return _PRIMARY_WEIGHT_BY_N.get(n, _PRIMARY_WEIGHT_DEFAULT)


def _default_weights(slugs: list[str], primary_slug: str) -> dict[str, float]:
    """Assign primary + equal-split secondary weights; last secondary absorbs rounding."""
    n = len(slugs)
    if n == 0:
        return {}
    if n == 1:
        return {slugs[0]: 1.0}

    primary_w = _primary_weight_for_n(n)
    remainder = 1.0 - primary_w
    secondaries = [s for s in slugs if s != primary_slug]
    if not secondaries:
        return {primary_slug: 1.0}

    each = round(remainder / len(secondaries), 2)
    weights: dict[str, float] = {primary_slug: primary_w}
    assigned = 0.0
    for i, s in enumerate(secondaries):
        if i == len(secondaries) - 1:
            w = round(remainder - assigned, 2)
        else:
            w = each
            assigned = round(assigned + each, 2)
        weights[s] = w
    return weights


def _ref_id(dna: dict[str, Any]) -> str:
    refs = dna.get("reference_image_ids") or []
    if not refs:
        return ""
    return str(refs[0]).strip()


def _dna_locked(dna: dict[str, Any]) -> bool:
    return str(dna.get("identity_lock_status", "")).lower() == "locked"


def build_multi_inject(
    cast: list[dict[str, Any]],
    primary_slug: str,
    *,
    dnas_by_slug: dict[str, dict[str, Any]] | None = None,
) -> str:
    """
    Build full multi-character injection text.

    Prefer inject_compact / inject_cinematic on cast entries when present;
    otherwise use dnas_by_slug + build_prompt_blocks.
    """
    if not cast:
        return ""

    lines: list[str] = ["[MULTI_CHARACTER_LOCK]"]

    primary_entry = next((c for c in cast if c.get("slug") == primary_slug), cast[0])
    secondaries = [c for c in cast if c.get("slug") != primary_entry.get("slug")]

    p_name = primary_entry.get("name") or primary_entry.get("slug", "primary")
    p_w = primary_entry.get("ref_weight", 0.0)
    lines.append(
        f"Primary: {p_name} (weight={p_w}) — never blend facial DNA with co-stars."
    )
    for sec in secondaries:
        s_name = sec.get("name") or sec.get("slug", "secondary")
        s_w = sec.get("ref_weight", 0.0)
        lines.append(f"Secondary: {s_name} (weight={s_w}).")

    lines.append(
        "Anti-merge: Distinct faces, hairstyles, wardrobes; "
        "no face morph between characters; never blend facial DNA."
    )
    lines.append("---")

    def _block_for(entry: dict[str, Any], *, primary: bool) -> str:
        if primary and entry.get("inject_cinematic"):
            return str(entry["inject_cinematic"])
        if entry.get("inject_compact"):
            return str(entry["inject_compact"])
        slug = entry.get("slug", "")
        if dnas_by_slug and slug in dnas_by_slug:
            blocks = build_prompt_blocks(dnas_by_slug[slug])
            return blocks["cinematic"] if primary else blocks["compact"]
        return str(entry.get("inject_compact") or entry.get("name") or slug)

    lines.append(_block_for(primary_entry, primary=True))
    for sec in secondaries:
        lines.append("---")
        lines.append(
            "Secondary identity — lower ref weight; do not override primary face"
        )
        lines.append(_block_for(sec, primary=False))

    return "\n".join(lines)


def arbitrate_cast(
    dnas: list[dict[str, Any]],
    *,
    primary_slug: str | None = None,
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Arbitrate multi-character cast: primary lock, weights, conflicts, inject block.

    dnas: loaded DNA dicts (must include slug).
    primary_slug: defaults to first dna slug if omitted.
    weights: optional explicit slug->weight map (must include primary when provided).
    """
    conflicts: list[dict[str, str]] = []
    rules_applied: list[str] = []

    if not dnas:
        return {
            "mode": "multi_character",
            "primary_slug": primary_slug or "",
            "primary_name": "",
            "cast": [],
            "conflicts": [
                _conflict("empty_cast", "error", "No characters provided for arbitration")
            ],
            "inject_block": "",
            "rules_applied": ["empty_cast"],
            "pass": False,
        }

    # Normalize / index by slug
    by_slug: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for dna in dnas:
        slug = str(dna.get("slug") or slugify(str(dna.get("character_name", "character"))))
        if slug not in by_slug:
            order.append(slug)
        by_slug[slug] = dna

    # Resolve primary
    if primary_slug is None:
        primary_slug = order[0]
        rules_applied.append("default_primary_first_dna")
    else:
        primary_slug = slugify(primary_slug) if primary_slug else primary_slug
        # Allow exact slug match without re-slugifying if already present
        if primary_slug not in by_slug:
            # try raw then slugified variants already tried
            raw = str(primary_slug)
            if raw in by_slug:
                primary_slug = raw
            else:
                # keep as-is for no_primary detection
                pass

    if primary_slug not in by_slug:
        # Attempt match against original primary_slug before slugify issues
        conflicts.append(
            _conflict(
                "no_primary",
                "error",
                f"Primary slug '{primary_slug}' not in cast: {', '.join(order)}",
            )
        )
        rules_applied.append("no_primary")
        return {
            "mode": "multi_character",
            "primary_slug": primary_slug or "",
            "primary_name": "",
            "cast": [],
            "conflicts": conflicts,
            "inject_block": "",
            "rules_applied": rules_applied,
            "pass": False,
        }

    n = len(order)
    rules_applied.append("primary_first")

    if n == 1:
        conflicts.append(
            _conflict(
                "single_cast",
                "info",
                "Only one character — single inject pass-through",
            )
        )
        rules_applied.append("single_cast")

    # Weights
    if weights:
        weight_map = {slugify(k) if k not in by_slug else k: float(v) for k, v in weights.items()}
        # normalize keys to actual slugs
        normalized: dict[str, float] = {}
        for k, v in weight_map.items():
            if k in by_slug:
                normalized[k] = float(v)
            else:
                sk = slugify(k)
                if sk in by_slug:
                    normalized[sk] = float(v)
        # ensure all cast members have a weight
        for s in order:
            if s not in normalized:
                normalized[s] = 0.0
        weight_map = normalized
        total = sum(weight_map.values())
        if total < 0.95 or total > 1.05:
            conflicts.append(
                _conflict(
                    "weight_sum",
                    "warn",
                    f"Explicit weights sum to {total:.3f} (expected ~1.0 within 0.95–1.05)",
                )
            )
            rules_applied.append("weight_sum_check")
        rules_applied.append("explicit_weights")
    else:
        weight_map = _default_weights(order, primary_slug)
        rules_applied.append(f"default_weights_n{n}")

    # not_locked
    for slug in order:
        dna = by_slug[slug]
        if not _dna_locked(dna):
            conflicts.append(
                _conflict(
                    "not_locked",
                    "warn",
                    f"Character '{slug}' identity_lock_status="
                    f"{dna.get('identity_lock_status', 'pending')}",
                )
            )
    if any(c["code"] == "not_locked" for c in conflicts):
        rules_applied.append("not_locked_check")

    # shared_ref_id
    ref_owners: dict[str, list[str]] = {}
    for slug in order:
        rid = _ref_id(by_slug[slug])
        if rid:
            ref_owners.setdefault(rid, []).append(slug)
    for rid, owners in ref_owners.items():
        if len(owners) > 1:
            conflicts.append(
                _conflict(
                    "shared_ref_id",
                    "warn",
                    f"Shared reference_image_id '{rid}' among: {', '.join(owners)}",
                )
            )
            rules_applied.append("shared_ref_id_check")

    # Build cast list — primary first, then remaining in input order
    cast_order = [primary_slug] + [s for s in order if s != primary_slug]
    cast: list[dict[str, Any]] = []
    for slug in cast_order:
        dna = by_slug[slug]
        role = "primary" if slug == primary_slug else "secondary"
        blocks = build_prompt_blocks(dna)
        inject_text = blocks["cinematic"] if role == "primary" else blocks["compact"]
        cast.append(
            {
                "slug": slug,
                "name": dna.get("character_name") or slug,
                "role": role,
                "ref_weight": float(weight_map.get(slug, 0.0)),
                "reference_image_id": _ref_id(dna),
                "dna_path": dna.get("dna_path"),  # optional if loader attached
                "locked": _dna_locked(dna),
                "inject_compact": inject_text,
                "inject_cinematic": blocks["cinematic"],
            }
        )

    inject_block = build_multi_inject(cast, primary_slug, dnas_by_slug=by_slug)
    rules_applied.append("multi_inject")

    has_error = any(c["severity"] == "error" for c in conflicts)
    primary_name = by_slug[primary_slug].get("character_name") or primary_slug

    return {
        "mode": "multi_character",
        "primary_slug": primary_slug,
        "primary_name": primary_name,
        "cast": cast,
        "conflicts": conflicts,
        "inject_block": inject_block,
        "rules_applied": rules_applied,
        "pass": not has_error,
    }


def load_cast_dnas(
    slugs: list[str],
    *,
    characters_root: Path | None = None,
) -> list[dict[str, Any]]:
    """
    Load DNA profiles for cast slugs via character_dna find/load.

    Raises ValueError listing missing slugs if any cannot be resolved.
    """
    loaded: list[dict[str, Any]] = []
    missing: list[str] = []
    for raw in slugs:
        path = find_character_dna(raw, characters_root=characters_root)
        if path is None:
            missing.append(raw)
            continue
        dna = load_character_dna(path)
        dna = dict(dna)
        dna["dna_path"] = str(path)
        loaded.append(dna)
    if missing:
        raise ValueError(f"Missing DNA for slugs: {', '.join(missing)}")
    return loaded
