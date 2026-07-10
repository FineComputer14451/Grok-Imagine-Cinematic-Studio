#!/usr/bin/env python3
"""
Stitch artifact lexicon — shared vocabulary + negative/positive packs (roadmap #11).

Data-first catalog for flicker, morph, halo, identity melt, wardrobe teleport,
lighting pop, and related stitch artifacts. Consumed by Imagine Prompt Master,
Sequence Extender / re-gen, and CLI `sequence artifact-lexicon`.
"""

from __future__ import annotations

from typing import Any

# Core default pack for extend / re-gen when no specific tags requested
DEFAULT_PACK_IDS: tuple[str, ...] = (
    "flicker",
    "morph",
    "halo",
    "identity_melt",
    "wardrobe_teleport",
    "lighting_pop",
    "motion_hitch",
)

# High seam_risk (>= this) suggests the full default pack
_HIGH_SEAM_RISK = 6.0

# Keyword (substring) → entry ids for seam factor / free-text mapping
_SEAM_KEYWORD_MAP: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("flicker", ("flicker",)),
    ("strobe", ("flicker",)),
    ("temporal flash", ("flicker",)),
    ("morph", ("morph",)),
    ("face melt", ("morph", "identity_melt")),
    ("body melt", ("morph",)),
    ("halo", ("halo",)),
    ("edge glow", ("halo",)),
    ("double contour", ("halo",)),
    ("identity melt", ("identity_melt",)),
    ("identity_melt", ("identity_melt",)),
    ("feature blend", ("identity_melt",)),
    ("character drift", ("identity_melt", "morph")),
    ("wardrobe", ("wardrobe_teleport",)),
    ("clothing", ("wardrobe_teleport",)),
    ("costume", ("wardrobe_teleport",)),
    ("lighting pop", ("lighting_pop",)),
    ("light pop", ("lighting_pop",)),
    ("color shift", ("lighting_pop",)),
    ("key shift", ("lighting_pop",)),
    ("prop pop", ("prop_pop",)),
    ("prop appear", ("prop_pop",)),
    ("prop disappear", ("prop_pop",)),
    ("lip desync", ("lip_desync",)),
    ("lip_sync", ("lip_desync",)),
    ("mouth out", ("lip_desync",)),
    ("motion hitch", ("motion_hitch",)),
    ("velocity", ("motion_hitch",)),
    ("motion discontinuity", ("motion_hitch",)),
    ("resolution swim", ("resolution_swim",)),
    ("soft/sharp", ("resolution_swim",)),
    ("sharpness pump", ("resolution_swim",)),
)

# chain QA critical key → suggested entry ids
_CHAIN_QA_KEY_MAP: dict[str, tuple[str, ...]] = {
    "character_drift_boundary": ("identity_melt", "morph"),
    "stitch_artifact_risk": ("flicker", "halo", "motion_hitch"),
    "last_frame_continuity": ("flicker", "motion_hitch", "morph"),
    "lighting_color_match": ("lighting_pop",),
    "physics_realism": ("motion_hitch", "prop_pop"),
    "wardrobe_consistency": ("wardrobe_teleport",),
    "identity_lock": ("identity_melt", "morph"),
    "lip_sync": ("lip_desync",),
    "audio_sync": ("lip_desync",),
    "resolution_stability": ("resolution_swim",),
}

_ENTRIES: list[dict[str, Any]] = [
    {
        "id": "flicker",
        "name": "Temporal flicker",
        "aliases": ["strobe", "frame flicker", "temporal flash"],
        "category": "temporal",
        "description": (
            "Frame flashing or strobing at the stitch boundary where temporal "
            "sampling or blend modes fight between adjacent clips."
        ),
        "symptoms": [
            "brief strobe or flash at cut/extend join",
            "alternating brightness across 1–3 frames",
            "unstable exposure at seam",
        ],
        "negative_phrases": [
            "temporal flicker",
            "frame flicker",
            "strobe flash at stitch",
            "flashing frames",
            "exposure strobing",
        ],
        "positive_guards": [
            "stable temporal sampling across the stitch",
            "smooth exposure continuity at the join",
            "no frame flash or strobe at the boundary",
        ],
        "qa_hooks": ["stitch_artifact_risk", "last_frame_continuity"],
    },
    {
        "id": "morph",
        "name": "Face/body morph",
        "aliases": ["face morph", "body melt", "geometry morph"],
        "category": "identity",
        "description": (
            "Face or body geometry melts or warps between clips at the "
            "extend/stitch boundary instead of holding identity lock."
        ),
        "symptoms": [
            "facial landmarks slide or warp at join",
            "body proportions briefly intermediate",
            "mesh-like melt between two identities or poses",
        ],
        "negative_phrases": [
            "face morph",
            "body morph",
            "geometry melt at stitch",
            "warping face at boundary",
            "melting features between clips",
        ],
        "positive_guards": [
            "locked facial geometry across the stitch",
            "stable body proportions at the join",
            "hard identity continuity, no morph between frames",
        ],
        "qa_hooks": ["character_drift_boundary", "identity_lock", "stitch_artifact_risk"],
    },
    {
        "id": "halo",
        "name": "Edge halo / double contour",
        "aliases": ["edge glow", "double contour", "outline halo"],
        "category": "geometry",
        "description": (
            "Edge glow, fringing, or double contour around subjects at the "
            "stitch from mismatched mattes, sharpening, or blend residuals."
        ),
        "symptoms": [
            "bright or dark rim around subject edges",
            "ghosted double outline",
            "chromatic fringe at silhouette",
        ],
        "negative_phrases": [
            "edge halo",
            "double contour",
            "outline glow",
            "fringing around subject",
            "ghost edges at stitch",
        ],
        "positive_guards": [
            "clean single silhouette edge",
            "no halo or double contour at the boundary",
            "matched edge treatment across the join",
        ],
        "qa_hooks": ["stitch_artifact_risk"],
    },
    {
        "id": "identity_melt",
        "name": "Identity melt",
        "aliases": ["feature blend", "identity blend", "co-star melt"],
        "category": "identity",
        "description": (
            "Character features blend toward a co-star or prior frame identity, "
            "breaking DNA / identity lock across the seam."
        ),
        "symptoms": [
            "eyes, nose, or jaw shift toward another face",
            "skin tone or age drifts mid-join",
            "DNA lock fields no longer match hero reference",
        ],
        "negative_phrases": [
            "identity melt",
            "feature blend toward another face",
            "character identity drift at stitch",
            "face blending with co-star",
            "DNA lock break",
        ],
        "positive_guards": [
            "strict identity lock to hero DNA across the stitch",
            "unchanged facial landmarks and skin tone at the join",
            "no feature blend toward other characters or prior frames",
        ],
        "qa_hooks": ["character_drift_boundary", "identity_lock"],
    },
    {
        "id": "wardrobe_teleport",
        "name": "Wardrobe teleport",
        "aliases": ["costume jump", "clothing change", "outfit pop"],
        "category": "wardrobe",
        "description": (
            "Clothing or accessories change without story motivation at the "
            "stitch boundary (teleport outfit, missing layers, color swap)."
        ),
        "symptoms": [
            "jacket/shirt color or cut changes at join",
            "accessories appear or vanish",
            "fabric state (wet/dry, torn) resets",
        ],
        "negative_phrases": [
            "wardrobe teleport",
            "sudden costume change",
            "clothing pop at stitch",
            "outfit discontinuity",
            "accessories appearing or disappearing",
        ],
        "positive_guards": [
            "identical wardrobe continuity across the stitch",
            "same layers, colors, and accessories at the join",
            "no unmotivated costume change",
        ],
        "qa_hooks": ["wardrobe_consistency", "stitch_artifact_risk"],
    },
    {
        "id": "lighting_pop",
        "name": "Lighting pop",
        "aliases": ["key shift", "color pop", "exposure jump"],
        "category": "lighting",
        "description": (
            "Sudden key, fill, or color temperature shift at the seam without "
            "motivated lighting change."
        ),
        "symptoms": [
            "key light direction or intensity jumps",
            "white balance / color grade snaps",
            "shadow density resets at boundary",
        ],
        "negative_phrases": [
            "lighting pop",
            "sudden key shift",
            "color temperature jump",
            "exposure pop at stitch",
            "ungraded lighting discontinuity",
        ],
        "positive_guards": [
            "matched key and fill continuity across the stitch",
            "stable color temperature and exposure at the join",
            "no unmotivated lighting pop",
        ],
        "qa_hooks": ["lighting_color_match", "stitch_artifact_risk"],
    },
    {
        "id": "prop_pop",
        "name": "Prop pop",
        "aliases": ["prop teleport", "object appear", "object disappear"],
        "category": "geometry",
        "description": (
            "Props or set dressing appear, disappear, or jump position at the "
            "stitch without narrative cause."
        ),
        "symptoms": [
            "handheld object vanishes mid-action",
            "background prop swaps position",
            "set dressing density changes abruptly",
        ],
        "negative_phrases": [
            "prop pop",
            "props appearing or disappearing",
            "object teleport at stitch",
            "set dressing jump",
            "background object discontinuity",
        ],
        "positive_guards": [
            "stable prop placement across the stitch",
            "same handheld objects and set dressing at the join",
            "no unmotivated prop appear or disappear",
        ],
        "qa_hooks": ["physics_realism", "stitch_artifact_risk"],
    },
    {
        "id": "lip_desync",
        "name": "Lip desync",
        "aliases": ["mouth desync", "lip sync fail", "dialogue mouth lag"],
        "category": "audio",
        "description": (
            "Mouth motion out of phase with dialogue or audio momentum at the "
            "extend boundary (especially native-audio 1.5 pipelines)."
        ),
        "symptoms": [
            "mouth still moving after line ends",
            "phoneme shapes lag dialogue",
            "silent mouth flap or frozen lips under speech",
        ],
        "negative_phrases": [
            "lip desync",
            "mouth out of phase with dialogue",
            "bad lip sync at stitch",
            "dialogue mouth lag",
            "unsynced mouth motion",
        ],
        "positive_guards": [
            "mouth motion locked to dialogue timing across the stitch",
            "clean lip sync continuity at the join",
            "audio and mouth performance in phase",
        ],
        "qa_hooks": ["lip_sync", "audio_sync"],
    },
    {
        "id": "motion_hitch",
        "name": "Motion hitch",
        "aliases": ["velocity hitch", "motion discontinuity", "speed pop"],
        "category": "temporal",
        "description": (
            "Velocity or easing discontinuity at the stitch — motion stalls, "
            "snaps, or changes speed without physics motivation."
        ),
        "symptoms": [
            "subject freezes then resumes",
            "camera speed pops at join",
            "action energy resets abruptly",
        ],
        "negative_phrases": [
            "motion hitch",
            "velocity discontinuity",
            "speed pop at stitch",
            "motion stall then snap",
            "physics hitch at boundary",
        ],
        "positive_guards": [
            "continuous motion velocity across the stitch",
            "matched easing and momentum at the join",
            "no hitch, stall, or speed pop at the boundary",
        ],
        "qa_hooks": ["physics_realism", "stitch_artifact_risk", "last_frame_continuity"],
    },
    {
        "id": "resolution_swim",
        "name": "Resolution swim",
        "aliases": ["sharpness swim", "detail pump", "soft sharp pump"],
        "category": "temporal",
        "description": (
            "Soft/sharp pumping or detail level swimming across frames at the "
            "seam from inconsistent denoise, upscale, or generation quality."
        ),
        "symptoms": [
            "alternating soft and crisp frames",
            "facial detail pumps in and out",
            "texture clarity unstable at join",
        ],
        "negative_phrases": [
            "resolution swim",
            "sharpness pumping",
            "soft sharp oscillation",
            "detail swim at stitch",
            "inconsistent sharpness across frames",
        ],
        "positive_guards": [
            "stable resolution and sharpness across the stitch",
            "matched detail level at the join",
            "no soft/sharp pumping or resolution swim",
        ],
        "qa_hooks": ["resolution_stability", "stitch_artifact_risk"],
    },
]

LEXICON: dict[str, dict[str, Any]] = {e["id"]: e for e in _ENTRIES}


def list_entries(*, category: str | None = None) -> list[dict[str, Any]]:
    """Return lexicon entries, optionally filtered by category."""
    entries = list(_ENTRIES)
    if category is not None:
        cat = category.strip().lower()
        entries = [e for e in entries if str(e.get("category", "")).lower() == cat]
    # Return shallow copies so callers cannot mutate the catalog
    return [dict(e) for e in entries]


def get_entry(entry_id: str) -> dict[str, Any] | None:
    """Return a single entry by id, or None if unknown."""
    if not entry_id:
        return None
    entry = LEXICON.get(str(entry_id).strip().lower())
    return dict(entry) if entry else None


def _resolve_ids(entry_ids: list[str] | None, *, all_default: bool = False) -> list[str]:
    """Resolve requested ids to known catalog ids (stable order, de-duped).

    all_default=True or entry_ids is None → DEFAULT_PACK_IDS.
    Explicit empty list → no entries.
    """
    if all_default or entry_ids is None:
        wanted: list[str] = list(DEFAULT_PACK_IDS)
    else:
        wanted = list(entry_ids)

    seen: set[str] = set()
    resolved: list[str] = []
    for raw in wanted:
        eid = str(raw).strip().lower()
        if not eid or eid in seen:
            continue
        if eid in LEXICON:
            seen.add(eid)
            resolved.append(eid)
    return resolved


def build_negative_pack(
    entry_ids: list[str] | None = None,
    *,
    all_default: bool = False,
) -> str:
    """
    Join negative_phrases for the given entry ids into a comma-separated pack.

    When all_default=True, or entry_ids is None, uses DEFAULT_PACK_IDS.
    Unknown ids are skipped. Returns empty string if nothing resolves.
    """
    ids = _resolve_ids(entry_ids, all_default=all_default)
    phrases: list[str] = []
    seen: set[str] = set()
    for eid in ids:
        entry = LEXICON.get(eid)
        if not entry:
            continue
        for phrase in entry.get("negative_phrases") or []:
            p = str(phrase).strip()
            if not p:
                continue
            key = p.lower()
            if key in seen:
                continue
            seen.add(key)
            phrases.append(p)
    return ", ".join(phrases)


def build_positive_guards(entry_ids: list[str] | None = None) -> str:
    """
    Join positive_guards for the given entry ids into a semicolon-separated string.

    When entry_ids is None, uses DEFAULT_PACK_IDS.
    """
    ids = _resolve_ids(entry_ids)
    phrases: list[str] = []
    seen: set[str] = set()
    for eid in ids:
        entry = LEXICON.get(eid)
        if not entry:
            continue
        for phrase in entry.get("positive_guards") or []:
            p = str(phrase).strip()
            if not p:
                continue
            key = p.lower()
            if key in seen:
                continue
            seen.add(key)
            phrases.append(p)
    return "; ".join(phrases)


def _collect_text_blobs(seam_report: dict[str, Any]) -> str:
    """Flatten factors/fixes/notes from a seam report into one lowercased blob."""
    parts: list[str] = []
    for key in ("factors", "fixes", "notes", "tags"):
        val = seam_report.get(key)
        if isinstance(val, (list, tuple)):
            parts.extend(str(x) for x in val)
        elif val is not None:
            parts.append(str(val))
    for key in ("summary", "mode", "detail"):
        if seam_report.get(key):
            parts.append(str(seam_report[key]))
    return " ".join(parts).lower()


def suggest_entries_from_seam(seam_report: dict | None) -> list[str]:
    """
    Map seam_report factors / risk to suggested lexicon entry ids.

    - Keyword matches in factors/fixes text → corresponding ids
    - High seam_risk (>= 6) → full DEFAULT_PACK_IDS
    """
    if not seam_report or not isinstance(seam_report, dict):
        return []

    suggested: list[str] = []
    seen: set[str] = set()

    def _add(ids: tuple[str, ...] | list[str]) -> None:
        for eid in ids:
            if eid in LEXICON and eid not in seen:
                seen.add(eid)
                suggested.append(eid)

    blob = _collect_text_blobs(seam_report)
    for keyword, ids in _SEAM_KEYWORD_MAP:
        if keyword in blob:
            _add(ids)

    # High seam risk → ensure default pack is covered
    risk = seam_report.get("seam_risk")
    try:
        risk_f = float(risk) if risk is not None else None
    except (TypeError, ValueError):
        risk_f = None
    if risk_f is not None and risk_f >= _HIGH_SEAM_RISK:
        _add(DEFAULT_PACK_IDS)

    return suggested


def suggest_entries_from_chain_qa(chain_qa: dict | None) -> list[str]:
    """
    Map chain QA critical keys / failed gates to suggested lexicon entry ids.

    Looks at critical, failed, flags, scores, and suggested_scores structures.
    """
    if not chain_qa or not isinstance(chain_qa, dict):
        return []

    suggested: list[str] = []
    seen: set[str] = set()

    def _add(ids: tuple[str, ...] | list[str]) -> None:
        for eid in ids:
            if eid in LEXICON and eid not in seen:
                seen.add(eid)
                suggested.append(eid)

    keys_to_check: list[str] = []

    for list_key in (
        "critical",
        "critical_failures",
        "failed",
        "flags",
        "failures",
        "gate_fails",
    ):
        val = chain_qa.get(list_key)
        if isinstance(val, (list, tuple)):
            for item in val:
                if isinstance(item, dict):
                    k = item.get("key") or item.get("name") or item.get("id")
                    if k:
                        keys_to_check.append(str(k))
                else:
                    keys_to_check.append(str(item))

    # Low scores in scores / suggested_scores (threshold < 7)
    for score_key in ("scores", "suggested_scores", "gates"):
        scores = chain_qa.get(score_key)
        if not isinstance(scores, dict):
            continue
        for k, v in scores.items():
            try:
                fv = float(v)
            except (TypeError, ValueError):
                # Non-numeric may still be a flag string
                if str(v).lower() in ("fail", "failed", "critical", "low"):
                    keys_to_check.append(str(k))
                continue
            if fv < 7.0:
                keys_to_check.append(str(k))

    # Direct boolean/critical flags on root
    for k, mapped in _CHAIN_QA_KEY_MAP.items():
        if k in chain_qa:
            val = chain_qa[k]
            if val is True or (isinstance(val, (int, float)) and not isinstance(val, bool) and float(val) < 7.0):
                _add(mapped)
            elif isinstance(val, str) and val.lower() in ("fail", "failed", "critical", "low"):
                _add(mapped)

    for k in keys_to_check:
        kn = k.strip().lower().replace(" ", "_").replace("-", "_")
        if kn in _CHAIN_QA_KEY_MAP:
            _add(_CHAIN_QA_KEY_MAP[kn])
        else:
            # Fuzzy: substring match against known keys
            for known, mapped in _CHAIN_QA_KEY_MAP.items():
                if known in kn or kn in known:
                    _add(mapped)
                    break

    return suggested


def format_lexicon_markdown(entry_ids: list[str] | None = None) -> str:
    """
    Format lexicon entries as markdown for agent/human reference.

    When entry_ids is None, formats the full catalog.
    """
    if entry_ids is None:
        ids = [e["id"] for e in _ENTRIES]
    elif not entry_ids:
        ids = []
    else:
        ids = _resolve_ids(entry_ids)

    lines: list[str] = [
        "# Stitch Artifact Lexicon",
        "",
        "Shared vocabulary and prompt packs for extend/stitch continuity (roadmap #11).",
        "",
    ]
    for eid in ids:
        entry = LEXICON.get(eid)
        if not entry:
            continue
        lines.append(f"## `{entry['id']}` — {entry['name']}")
        lines.append("")
        lines.append(f"- **Category:** {entry['category']}")
        aliases = entry.get("aliases") or []
        if aliases:
            lines.append(f"- **Aliases:** {', '.join(aliases)}")
        lines.append(f"- **Description:** {entry['description']}")
        symptoms = entry.get("symptoms") or []
        if symptoms:
            lines.append("- **Symptoms:**")
            for s in symptoms:
                lines.append(f"  - {s}")
        negs = entry.get("negative_phrases") or []
        if negs:
            lines.append(f"- **Negative pack:** {', '.join(negs)}")
        guards = entry.get("positive_guards") or []
        if guards:
            lines.append(f"- **Positive guards:** {'; '.join(guards)}")
        hooks = entry.get("qa_hooks") or []
        if hooks:
            lines.append(f"- **QA hooks:** {', '.join(hooks)}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
