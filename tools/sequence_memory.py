#!/usr/bin/env python3
"""
Sequence memory bank — running cast/prop/lighting/emotion/audio state (roadmap #4).

Pure functions only. sequence_chain and CLI call into this module.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

MEMORY_BANK_VERSION = "1.0"


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def empty_memory_bank() -> dict[str, Any]:
    return {
        "version": MEMORY_BANK_VERSION,
        "updated_at": None,
        "updated_from_clip_id": None,
        "cast": {},
        "environment": {
            "location": "",
            "time_of_day": "",
            "weather": "",
            "props": [],
        },
        "lighting": {
            "state": "",
            "motifs": [],
        },
        "emotion": {
            "sequence_temperature": "",
            "last_emotional_state": "",
        },
        "audio": {
            "dialogue_state": "",
            "sfx_timing": "",
            "emotional_tone_audio": "",
            "music_cue_points": [],
            "lip_sync_state": "",
        },
        "notes": [],
    }


def ensure_memory_bank(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Return a full bank; fill missing keys from empty template. Never mutates input."""
    base = empty_memory_bank()
    if not raw:
        return base
    out = deepcopy(base)
    for key in ("version", "updated_at", "updated_from_clip_id", "notes"):
        if key in raw and raw[key] is not None:
            out[key] = deepcopy(raw[key])
    if isinstance(raw.get("cast"), dict):
        out["cast"] = deepcopy(raw["cast"])
    for section in ("environment", "lighting", "emotion", "audio"):
        if isinstance(raw.get(section), dict):
            out[section] = {**out[section], **deepcopy(raw[section])}
    if not isinstance(out["environment"].get("props"), list):
        out["environment"]["props"] = []
    if not isinstance(out["audio"].get("music_cue_points"), list):
        out["audio"]["music_cue_points"] = []
    if not isinstance(out["lighting"].get("motifs"), list):
        out["lighting"]["motifs"] = []
    if not isinstance(out["notes"], list):
        out["notes"] = []
    out["version"] = MEMORY_BANK_VERSION
    return out


def _merge_props(existing: list[str], incoming: Any) -> list[str]:
    items: list[str] = list(existing)
    if incoming is None:
        return items
    if isinstance(incoming, str):
        parts = [p.strip() for p in incoming.split(",") if p.strip()]
    elif isinstance(incoming, list):
        parts = [str(p).strip() for p in incoming if str(p).strip()]
    else:
        parts = [str(incoming).strip()] if str(incoming).strip() else []
    for p in parts:
        if p not in items:
            items.append(p)
    return items


def apply_clip_to_memory_bank(
    bank: dict[str, Any],
    clip: dict[str, Any],
    *,
    character_slug: str | None = None,
    character_name: str | None = None,
) -> dict[str, Any]:
    """Return new bank with clip state merged in (does not mutate inputs)."""
    out = ensure_memory_bank(bank)
    mv = clip.get("momentum_vector") or {}
    amv = clip.get("audio_momentum_vector") or {}
    cont = clip.get("continuity_state") or {}

    lighting = str(mv.get("lighting_state") or "").strip()
    if lighting:
        out["lighting"]["state"] = lighting

    emotion = str(mv.get("emotional_state") or "").strip()
    if emotion:
        out["emotion"]["last_emotional_state"] = emotion

    for key in (
        "dialogue_state",
        "sfx_timing",
        "emotional_tone_audio",
        "lip_sync_state",
    ):
        val = str(amv.get(key) or "").strip()
        if val:
            out["audio"][key] = val
    cues = amv.get("music_cue_points")
    if isinstance(cues, list) and cues:
        existing = list(out["audio"].get("music_cue_points") or [])
        for c in cues:
            s = str(c).strip()
            if s and s not in existing:
                existing.append(s)
        out["audio"]["music_cue_points"] = existing

    for env_key in ("location", "time_of_day", "weather"):
        val = str(cont.get(env_key) or "").strip()
        if val:
            out["environment"][env_key] = val
    if "props" in cont:
        out["environment"]["props"] = _merge_props(
            list(out["environment"].get("props") or []), cont.get("props")
        )

    slug = (character_slug or "").strip()
    if slug:
        entry = dict(out["cast"].get(slug) or {})
        entry["name"] = character_name or entry.get("name") or slug
        ref = str(clip.get("reference_image_id") or "").strip()
        if ref:
            entry["reference_image_id"] = ref
        wardrobe = str(cont.get("wardrobe") or entry.get("wardrobe") or "").strip()
        if wardrobe:
            entry["wardrobe"] = wardrobe
        if emotion:
            entry["emotional_state"] = emotion
        entry["last_seen_clip_id"] = clip.get("clip_id") or entry.get("last_seen_clip_id")
        out["cast"][slug] = entry

    out["updated_from_clip_id"] = clip.get("clip_id")
    out["updated_at"] = _now_iso()
    return out


def mirror_bank_to_continuity_state(bank: dict[str, Any]) -> dict[str, Any]:
    """Project bank into a clip-shaped continuity_state dict."""
    b = ensure_memory_bank(bank)
    env = b["environment"]
    cont: dict[str, Any] = {}
    if env.get("location"):
        cont["location"] = env["location"]
    if env.get("time_of_day"):
        cont["time_of_day"] = env["time_of_day"]
    if env.get("weather"):
        cont["weather"] = env["weather"]
    if env.get("props"):
        cont["props"] = list(env["props"])
    if b["lighting"].get("state"):
        cont["lighting_state"] = b["lighting"]["state"]
    if b["emotion"].get("last_emotional_state"):
        cont["emotional_state"] = b["emotion"]["last_emotional_state"]
    return cont


def memory_bank_to_prompt_block(bank: dict[str, Any]) -> str:
    b = ensure_memory_bank(bank)
    lines = ["SEQUENCE_MEMORY_BANK:"]
    env = b["environment"]
    if env.get("location"):
        lines.append(f"  location: {env['location']}")
    if env.get("time_of_day"):
        lines.append(f"  time_of_day: {env['time_of_day']}")
    if env.get("weather"):
        lines.append(f"  weather: {env['weather']}")
    if env.get("props"):
        lines.append(f"  props: {', '.join(env['props'])}")
    if b["lighting"].get("state"):
        lines.append(f"  lighting: {b['lighting']['state']}")
    if b["emotion"].get("last_emotional_state"):
        lines.append(f"  emotion: {b['emotion']['last_emotional_state']}")
    audio = b["audio"]
    if audio.get("dialogue_state"):
        lines.append(f"  audio.dialogue_state: {audio['dialogue_state']}")
    if audio.get("sfx_timing"):
        lines.append(f"  audio.sfx_timing: {audio['sfx_timing']}")
    if audio.get("emotional_tone_audio"):
        lines.append(f"  audio.emotional_tone: {audio['emotional_tone_audio']}")
    cast = b.get("cast") or {}
    if cast:
        lines.append("  cast:")
        for slug, entry in cast.items():
            name = (entry or {}).get("name") or slug
            wardrobe = (entry or {}).get("wardrobe") or ""
            emo = (entry or {}).get("emotional_state") or ""
            ref = (entry or {}).get("reference_image_id") or ""
            lines.append(
                f"    - {name}: wardrobe={wardrobe}; emotion={emo}; ref={ref}"
            )
    if len(lines) == 1:
        lines.append("  (empty)")
    return "\n".join(lines)


def memory_bank_summary(bank: dict[str, Any]) -> str:
    """One-line human summary for CLI."""
    b = ensure_memory_bank(bank)
    loc = b["environment"].get("location") or "?"
    cast_n = len(b.get("cast") or {})
    props_n = len(b["environment"].get("props") or [])
    return (
        f"location={loc} | cast={cast_n} | props={props_n} | "
        f"lighting={b['lighting'].get('state') or '—'} | "
        f"from={b.get('updated_from_clip_id') or '—'}"
    )
