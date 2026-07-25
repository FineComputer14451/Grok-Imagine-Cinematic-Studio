#!/usr/bin/env python3
"""
Wave A packet fields & schemas (P1).

Standalone packet types for the eight Wave A specialists, plus helpers to
validate optional Wave A sections nested on other handoffs.

Consumed by:
  - .grok/skills/handoff-packet-validator/scripts/validate_handoff.py
  - agents (declarative builders)
"""

from __future__ import annotations

from typing import Any

from plate_readiness import PLATE_STATUSES, normalize_plate_status
from motion_readiness import MOTION_TRIPLE_KEYS, is_complete_motion_triple

# --- Packet type ids ---
PACKET_PLATE_MOTION = "plate_motion_readiness"
PACKET_CONTACT = "contact_micro_physics_brief"
PACKET_HMU = "hmu_lock_handoff"
PACKET_DIALOGUE = "dialogue_adr_block"
PACKET_SCORE = "score_temp_music_block"
PACKET_TITLE = "title_mograph_brief"
PACKET_CROP = "distribution_crop_plan"
PACKET_BRIEF_LOG = "parallel_brief_dispatch_log"

WAVE_A_PACKET_TYPE_IDS: frozenset[str] = frozenset(
    {
        PACKET_PLATE_MOTION,
        PACKET_CONTACT,
        PACKET_HMU,
        PACKET_DIALOGUE,
        PACKET_SCORE,
        PACKET_TITLE,
        PACKET_CROP,
        PACKET_BRIEF_LOG,
    }
)

HMU_CONDITION = frozenset(
    {"clean", "sweat", "smudge", "wet", "damaged", "styled", "reset", "custom"}
)
CROP_ASPECTS = frozenset({"16:9", "9:16", "1:1", "4:5", "2.39:1"})
BRIEF_PRIORITIES = frozenset({"high", "normal", "low"})


def _nonempty(value: Any) -> bool:
    return bool(str(value).strip()) if value is not None else False


# --- Declarative schemas (validator PACKET_TYPES format) ---

def plate_motion_schema() -> dict[str, Any]:
    return {
        "required": (
            "packet_type",
            "subject_id",
            "plate_status",
            "motion_vector",
            "i2v_motion_block_ready",
        ),
        "nonempty": ("subject_id",),
        "enums": {
            "plate_status": PLATE_STATUSES,
        },
        "typed": {
            "motion_vector": {"object_keys": MOTION_TRIPLE_KEYS},
        },
    }


def contact_schema() -> dict[str, Any]:
    return {
        "required": (
            "packet_type",
            "subject_id",
            "contact_brief",
            "micro_physics_notes",
        ),
        "nonempty": ("subject_id", "contact_brief"),
        "typed": {
            "micro_physics_notes": "dict",
        },
    }


def hmu_schema() -> dict[str, Any]:
    return {
        "required": (
            "packet_type",
            "character_slug",
            "hmu_lock",
            "active_look_id",
        ),
        "nonempty": ("character_slug", "active_look_id"),
        "typed": {
            "hmu_lock": "dict",
        },
    }


def dialogue_schema() -> dict[str, Any]:
    return {
        "required": (
            "packet_type",
            "subject_id",
            "dialogue_block",
        ),
        "nonempty": ("subject_id",),
        "typed": {
            "dialogue_block": "dict",
        },
    }


def score_schema() -> dict[str, Any]:
    return {
        "required": (
            "packet_type",
            "subject_id",
            "music_cues",
        ),
        "nonempty": ("subject_id",),
        "typed": {
            "music_cues": "list",
        },
    }


def title_schema() -> dict[str, Any]:
    return {
        "required": (
            "packet_type",
            "deliverable_id",
            "title_cards",
        ),
        "nonempty": ("deliverable_id",),
        "typed": {
            "title_cards": {"list_min": 1},
        },
    }


def crop_schema() -> dict[str, Any]:
    return {
        "required": (
            "packet_type",
            "subject_id",
            "crop_plan",
        ),
        "nonempty": ("subject_id",),
        "typed": {
            "crop_plan": {"list_min": 1},
        },
    }


def brief_log_schema() -> dict[str, Any]:
    return {
        "required": (
            "packet_type",
            "session_id",
            "briefs",
        ),
        "nonempty": ("session_id",),
        "typed": {
            "briefs": {"list_min": 1},
        },
    }


def wave_a_packet_schemas() -> dict[str, dict[str, Any]]:
    """Map packet_type → schema for validator registration."""
    return {
        PACKET_PLATE_MOTION: plate_motion_schema(),
        PACKET_CONTACT: contact_schema(),
        PACKET_HMU: hmu_schema(),
        PACKET_DIALOGUE: dialogue_schema(),
        PACKET_SCORE: score_schema(),
        PACKET_TITLE: title_schema(),
        PACKET_CROP: crop_schema(),
        PACKET_BRIEF_LOG: brief_log_schema(),
    }


# --- Builders ---

def build_plate_motion_readiness(
    *,
    subject_id: str,
    plate_status: str,
    action: str,
    camera: str,
    emotion: str,
    i2v_motion_block_ready: bool = True,
    plate_path: str | None = None,
    plate_asset_id: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    status = normalize_plate_status(plate_status) or str(plate_status).strip().lower()
    pkt: dict[str, Any] = {
        "packet_type": PACKET_PLATE_MOTION,
        "subject_id": subject_id,
        "plate_status": status,
        "motion_vector": {
            "action": (action or "").strip(),
            "camera": (camera or "").strip(),
            "emotion": (emotion or "").strip(),
        },
        "i2v_motion_block_ready": bool(i2v_motion_block_ready),
    }
    if plate_path:
        pkt["plate_path"] = plate_path
    if plate_asset_id:
        pkt["plate_asset_id"] = plate_asset_id
    if notes:
        pkt["notes"] = notes
    return pkt


def build_contact_brief(
    *,
    subject_id: str,
    contact_brief: str,
    hands: str = "",
    cloth: str = "",
    weight_transfer: str = "",
    liquids: str = "",
    risks: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "packet_type": PACKET_CONTACT,
        "subject_id": subject_id,
        "contact_brief": (contact_brief or "").strip(),
        "micro_physics_notes": {
            "hands": hands,
            "cloth": cloth,
            "weight_transfer": weight_transfer,
            "liquids": liquids,
        },
        "risks": list(risks or []),
    }


def build_hmu_lock(
    *,
    character_slug: str,
    active_look_id: str,
    hair: str,
    makeup: str,
    condition: str = "clean",
    inject_compact: str = "",
    delta: str = "",
) -> dict[str, Any]:
    cond = str(condition).strip().lower() or "clean"
    return {
        "packet_type": PACKET_HMU,
        "character_slug": character_slug,
        "active_look_id": active_look_id,
        "hmu_lock": {
            "hair": hair,
            "makeup": makeup,
            "condition": cond,
            "inject_compact": inject_compact,
            "delta": delta,
        },
    }


def build_dialogue_block(
    *,
    subject_id: str,
    lines: list[str] | None = None,
    vo: str = "",
    adr_notes: str = "",
    lip_sync_cues: str = "",
    native_dialogue_seed: str = "",
) -> dict[str, Any]:
    return {
        "packet_type": PACKET_DIALOGUE,
        "subject_id": subject_id,
        "dialogue_block": {
            "lines": list(lines or []),
            "vo": vo,
            "adr_notes": adr_notes,
            "lip_sync_cues": lip_sync_cues,
            "native_dialogue_seed": native_dialogue_seed,
        },
    }


def build_score_block(
    *,
    subject_id: str,
    music_cues: list[str] | None = None,
    temp_score_notes: str = "",
    emotional_tone_audio: str = "",
) -> dict[str, Any]:
    return {
        "packet_type": PACKET_SCORE,
        "subject_id": subject_id,
        "music_cues": list(music_cues or []),
        "temp_score_notes": temp_score_notes,
        "emotional_tone_audio": emotional_tone_audio,
    }


def build_title_brief(
    *,
    deliverable_id: str,
    title_cards: list[dict[str, Any]] | None = None,
    lower_thirds: list[str] | None = None,
    end_cards: list[str] | None = None,
    brand_lock_notes: str = "",
) -> dict[str, Any]:
    cards = list(title_cards or [{"text": "TITLE", "placement": "center"}])
    return {
        "packet_type": PACKET_TITLE,
        "deliverable_id": deliverable_id,
        "title_cards": cards,
        "lower_thirds": list(lower_thirds or []),
        "end_cards": list(end_cards or []),
        "brand_lock_notes": brand_lock_notes,
    }


def build_crop_plan(
    *,
    subject_id: str,
    variants: list[dict[str, Any]] | None = None,
    safe_action: str = "protect hero face/torso",
) -> dict[str, Any]:
    plan = list(
        variants
        or [
            {"aspect": "16:9", "priority": "primary", "notes": "theatrical"},
            {"aspect": "9:16", "priority": "social", "notes": "vertical safe-action"},
            {"aspect": "1:1", "priority": "secondary", "notes": "feed"},
        ]
    )
    return {
        "packet_type": PACKET_CROP,
        "subject_id": subject_id,
        "crop_plan": plan,
        "safe_action": safe_action,
    }


def build_brief_dispatch_log(
    *,
    session_id: str,
    briefs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    items = list(
        briefs
        or [
            {
                "brief_id": "pb-001",
                "to": "plate-motion-readiness-lead",
                "priority": "high",
                "scope": "lock hero plate + motion triple",
            }
        ]
    )
    return {
        "packet_type": PACKET_BRIEF_LOG,
        "session_id": session_id,
        "briefs": items,
        "non_blocking": True,
    }


# --- Semantic checks for optional nested Wave A fields on other packets ---

def validate_optional_wave_a_fields(
    data: dict[str, Any],
    *,
    strict_wave_a: bool = False,
) -> tuple[list[str], list[str]]:
    """
    Validate optional Wave A fields when present on any packet.

    Returns (hard_issues, warnings).
    strict_wave_a: for video still→video modes, require plate_status OK + full
    motion_vector if either field family is partially present.
    """
    issues: list[str] = []
    warnings: list[str] = []

    # plate_status
    if "plate_status" in data:
        st = normalize_plate_status(data.get("plate_status"))
        if st is None:
            issues.append(
                f"plate_status: invalid value {data.get('plate_status')!r} "
                f"(expected draft|approved|locked)"
            )
        elif st not in ("approved", "locked"):
            warnings.append(
                f"plate_status={st!r} not approved/locked — still→video may block"
            )

    # motion_vector
    if "motion_vector" in data:
        mv = data.get("motion_vector")
        if not isinstance(mv, dict):
            issues.append("motion_vector: must be an object")
        elif not is_complete_motion_triple(
            {k: str(mv.get(k) or "") for k in MOTION_TRIPLE_KEYS}
        ):
            msg = "motion_vector: incomplete triple (need action, camera, emotion)"
            if strict_wave_a:
                issues.append(msg)
            else:
                warnings.append(msg)

    # hmu_lock nested
    if "hmu_lock" in data:
        hmu = data.get("hmu_lock")
        if not isinstance(hmu, dict):
            issues.append("hmu_lock: must be an object")
        else:
            if not _nonempty(hmu.get("hair")) and not _nonempty(hmu.get("makeup")):
                warnings.append("hmu_lock: hair and makeup both empty")
            cond = hmu.get("condition")
            if cond is not None and str(cond).strip().lower() not in HMU_CONDITION:
                issues.append(f"hmu_lock.condition: invalid {cond!r}")

    # dialogue_block
    if "dialogue_block" in data:
        db = data.get("dialogue_block")
        if not isinstance(db, dict):
            issues.append("dialogue_block: must be an object")
        elif not (
            db.get("lines")
            or _nonempty(db.get("vo"))
            or _nonempty(db.get("native_dialogue_seed"))
        ):
            warnings.append(
                "dialogue_block: no lines/vo/native_dialogue_seed content"
            )

    # music_cues
    if "music_cues" in data and not isinstance(data.get("music_cues"), list):
        issues.append("music_cues: must be an array")

    # crop_plan
    if "crop_plan" in data:
        plan = data.get("crop_plan")
        if not isinstance(plan, list) or not plan:
            issues.append("crop_plan: must be a non-empty array")
        else:
            for i, row in enumerate(plan):
                if not isinstance(row, dict):
                    issues.append(f"crop_plan[{i}]: must be an object")
                    continue
                aspect = row.get("aspect")
                if aspect is not None and str(aspect) not in CROP_ASPECTS:
                    warnings.append(
                        f"crop_plan[{i}].aspect={aspect!r} not in common set "
                        f"{sorted(CROP_ASPECTS)}"
                    )

    # parallel brief log nested
    if "briefs" in data and data.get("packet_type") == PACKET_BRIEF_LOG:
        briefs = data.get("briefs")
        if isinstance(briefs, list):
            for i, b in enumerate(briefs):
                if not isinstance(b, dict):
                    issues.append(f"briefs[{i}]: must be an object")
                    continue
                if not _nonempty(b.get("brief_id")):
                    issues.append(f"briefs[{i}]: missing brief_id")
                pri = b.get("priority")
                if pri is not None and str(pri).lower() not in BRIEF_PRIORITIES:
                    issues.append(f"briefs[{i}].priority: invalid {pri!r}")

    mode = str(data.get("execution_mode") or "")
    if strict_wave_a and mode in ("image_to_video", "reference_to_video"):
        st = normalize_plate_status(data.get("plate_status"))
        if st not in ("approved", "locked"):
            issues.append(
                "strict-wave-a: still→video requires plate_status approved|locked"
            )
        mv = data.get("motion_vector")
        if not isinstance(mv, dict) or not is_complete_motion_triple(
            {k: str(mv.get(k) or "") for k in MOTION_TRIPLE_KEYS}
        ):
            issues.append(
                "strict-wave-a: still→video requires complete motion_vector triple"
            )

    return issues, warnings


def attach_wave_a_to_imagine(
    packet: dict[str, Any],
    *,
    plate_motion: dict[str, Any] | None = None,
    contact: dict[str, Any] | None = None,
    hmu: dict[str, Any] | None = None,
    dialogue: dict[str, Any] | None = None,
    score: dict[str, Any] | None = None,
    crop: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Merge selected Wave A fields onto an imagine_agent_mode_handoff packet.

    Copies plate_status / motion_vector to top-level for plate/motion readiness
    evaluators; nests department packets under wave_a.
    """
    out = dict(packet)
    wave: dict[str, Any] = dict(out.get("wave_a") or {}) if isinstance(out.get("wave_a"), dict) else {}

    if plate_motion:
        wave["plate_motion"] = plate_motion
        if plate_motion.get("plate_status") is not None:
            out["plate_status"] = plate_motion["plate_status"]
        if isinstance(plate_motion.get("motion_vector"), dict):
            out["motion_vector"] = plate_motion["motion_vector"]
        for k in ("plate_path", "plate_asset_id"):
            if plate_motion.get(k):
                out[k] = plate_motion[k]

    if contact:
        wave["contact"] = contact
    if hmu:
        wave["hmu"] = hmu
        if isinstance(hmu.get("hmu_lock"), dict):
            out["hmu_lock"] = hmu["hmu_lock"]
    if dialogue:
        wave["dialogue"] = dialogue
        if isinstance(dialogue.get("dialogue_block"), dict):
            out["dialogue_block"] = dialogue["dialogue_block"]
    if score:
        wave["score"] = score
        if isinstance(score.get("music_cues"), list):
            out["music_cues"] = score["music_cues"]
        if score.get("emotional_tone_audio"):
            out.setdefault("sound_layer", "")
            # keep AMV tone discoverable
            out["emotional_tone_audio"] = score["emotional_tone_audio"]
    if crop:
        wave["crop"] = crop
        if isinstance(crop.get("crop_plan"), list):
            out["crop_plan"] = crop["crop_plan"]

    if wave:
        out["wave_a"] = wave
    return out
