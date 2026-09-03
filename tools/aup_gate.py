#!/usr/bin/env python3
"""
SpaceXAI AUP fail-closed gates for Grok Imagine Cinematic Studio.

Policy: https://x.ai/legal/acceptable-use-policy (effective 14 Aug 2026)

Allowed intimate work: limited R-rated fictional adult material of
imaginary adults, for 18+ operators who attested and enabled NSFW on
their xAI account.

Blocked: CSAM / minor-coded tropes, real-person undress/nudify,
pornographic depictions beyond R-rated, hidden-camera NCII patterns.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from studio_paths import STUDIO_ROOT

AUP_URL = "https://x.ai/legal/acceptable-use-policy"
ATTESTATION_SCHEMA = "1.0"
ATTESTATION_ENV = "GROK_STUDIO_AUP_ATTESTATION"
DEFAULT_ATTESTATION_NAME = ".aup_attestation.json"

REQUIRED_ATTESTATION_FLAGS = (
    "age_18_plus",
    "imaginary_adults_only",
    "not_a_real_person",
    "aup_acknowledged",
)

SUBJECT_KIND_IMAGINARY_ADULT = "imaginary_adult"
ALLOWED_SUBJECT_KINDS = ("unspecified", "imaginary_adult", "real_person")
R_RATED_EXPLICIT_LEVELS = frozenset({"suggestive", "moderate", ""})

# Stub keyword refusals only — tests must not include illegal fixtures.
_CSAM_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bloli(?:ta|con)?\b",
        r"\bshota\b",
        r"\bcsam\b",
        r"\bchild\s*porn",
        r"\bunderage\b",
        r"\bpre[- ]?teen\b",
        r"\baged[- ]?down\b",
        r"\bschoolgirl\b",
        r"\bunder[- ]?18\b",
    )
)

_EXPLICIT_BEYOND_R_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bcreampie\b",
        r"\bahegao\b",
        r"\bpenetration\b",
        r"\bgenitals?\b",
        r"\bsemen\b",
        r"\bcumshot\b",
        r"\bexplicit porn",
        r"\bhero explicit beat\b",
    )
)

_NCII_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        r"\bhidden camera\b",
        r"\bnudif(?:y|ying|ication)\b",
        r"\bdeepfake\b",
        r"\bundress(?:ing)? (?:her|him|them|this person)\b",
    )
)

_INTIMATE_HINT = re.compile(
    r"\b(nsfw|erotic|nude|nudity|explicit|erosforge)\b",
    re.IGNORECASE,
)


class AUPGateError(ValueError):
    """Raised when a request would violate SpaceXAI AUP."""


def attestation_path() -> Path:
    override = os.getenv(ATTESTATION_ENV, "").strip()
    if override:
        return Path(override)
    return STUDIO_ROOT / DEFAULT_ATTESTATION_NAME


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_attestation(path: Path | None = None) -> dict[str, Any] | None:
    target = path or attestation_path()
    if not target.is_file():
        return None
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def attestation_is_valid(data: dict[str, Any] | None) -> bool:
    if not data:
        return False
    return all(data.get(flag) is True for flag in REQUIRED_ATTESTATION_FLAGS)


def write_attestation(
    *,
    age_18_plus: bool,
    imaginary_adults_only: bool,
    not_a_real_person: bool,
    aup_acknowledged: bool,
    path: Path | None = None,
) -> dict[str, Any]:
    if not all((age_18_plus, imaginary_adults_only, not_a_real_person, aup_acknowledged)):
        raise AUPGateError(
            "All four attestations are required: 18+, imaginary adults only, "
            f"not a real person, and AUP acknowledgment ({AUP_URL})."
        )
    payload = {
        "schema_version": ATTESTATION_SCHEMA,
        "age_18_plus": True,
        "imaginary_adults_only": True,
        "not_a_real_person": True,
        "aup_acknowledged": True,
        "aup_url": AUP_URL,
        "attested_at": _now_iso(),
    }
    target = path or attestation_path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    try:
        os.chmod(target, 0o600)
    except OSError:
        pass
    return payload


def require_attestation(path: Path | None = None) -> dict[str, Any]:
    data = load_attestation(path)
    if not attestation_is_valid(data):
        raise AUPGateError(
            "NSFW / intimate work requires a local 18+ AUP attestation. "
            "Run: python tools/cinematic_studio_cli.py nsfw attest "
            "--i-am-18 --imaginary-adults --not-a-real-person --acknowledge-aup "
            f"(policy: {AUP_URL})"
        )
    assert data is not None
    return data


def aup_status(path: Path | None = None) -> dict[str, Any]:
    """Public attestation status for doctor / API. Never returns flag values."""
    data = load_attestation(path)
    valid = attestation_is_valid(data)
    attested_at = None
    if valid and data:
        raw = data.get("attested_at")
        attested_at = str(raw) if raw else None
    return {
        "valid": valid,
        "present": data is not None,
        "attested_at": attested_at,
        "aup_url": AUP_URL,
        "schema_version": str(data.get("schema_version") or "") if valid and data else None,
    }


def gate_planning_packet(
    prompt: str,
    *,
    extra: str = "",
    has_reference_image: bool = False,
) -> None:
    """Fail-closed on Imagine-bound planning packets (bridge / generate-prompt / handoff)."""
    blob = _join_fields([prompt, extra])
    gate_imagine_prompt(blob, has_reference_image=has_reference_image)


_PACKET_TEXT_KEYS = (
    "prompt",
    "description",
    "dna_inject",
    "prompt_injection",
    "dna_profile",
    "nsfw_notes",
    "last_frame_recap",
    "sound_layer",
    "dialogue",
)


def _flatten_planning_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, dict):
        return _join_fields(value.values())
    if isinstance(value, (list, tuple)):
        return _join_fields(value)
    return str(value).strip()


def packet_planning_text(data: dict[str, Any]) -> str:
    """Join paste-facing packet fields (prompt, recap, sound, momentum, notes)."""
    parts: list[Any] = [data.get(key) for key in _PACKET_TEXT_KEYS]
    parts.append(data.get("momentum_vector"))
    parts.append(data.get("audio_momentum_vector"))
    amv = data.get("audio_momentum_vector")
    if isinstance(amv, dict):
        parts.append(amv.get("dialogue_state"))
    return _join_fields(_flatten_planning_value(item) for item in parts if item)


def packet_has_reference(data: dict[str, Any]) -> bool:
    refs = data.get("reference_hints") or []
    return bool(
        refs
        or data.get("reference_image_id")
        or data.get("reference_image_url")
        or data.get("has_reference")
        or data.get("has_ref")
    )


def packet_is_imagine_bound(data: dict[str, Any]) -> bool:
    ptype = str(data.get("packet_type") or "").lower()
    for marker in ("imagine", "agent_mode", "extend", "intimacy"):
        if marker in ptype:
            return True
    if data.get("prompt") or data.get("description"):
        return True
    if data.get("last_frame_recap") or data.get("sound_layer"):
        return True
    if data.get("video_pipeline_spec") or data.get("grok_imagine_url"):
        return True
    return False


def gate_planning_subject(
    data: dict[str, Any],
    *,
    has_reference_image: bool | None = None,
) -> None:
    """Fail-closed AUP on every Imagine-paste field, not prompt-only."""
    blob = packet_planning_text(data)
    ref = packet_has_reference(data) if has_reference_image is None else has_reference_image
    ptype = str(data.get("packet_type") or "").lower()
    nsfw = bool(data.get("nsfw_notes")) or "intimacy" in ptype
    gate_imagine_prompt(blob, nsfw=nsfw, has_reference_image=ref)


def _collect_matches(text: str, patterns: Iterable[re.Pattern[str]]) -> list[str]:
    found: list[str] = []
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            found.append(match.group(0))
    return found


def scan_csam(text: str) -> list[str]:
    return _collect_matches(text or "", _CSAM_PATTERNS)


def scan_explicit_beyond_r(text: str) -> list[str]:
    return _collect_matches(text or "", _EXPLICIT_BEYOND_R_PATTERNS)


def scan_ncii(text: str) -> list[str]:
    return _collect_matches(text or "", _NCII_PATTERNS)


def is_intimate_text(text: str) -> bool:
    return bool(_INTIMATE_HINT.search(text or ""))


def _join_fields(values: Iterable[Any]) -> str:
    parts: list[str] = []
    for value in values:
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            parts.extend(str(item) for item in value if item)
        else:
            text = str(value).strip()
            if text:
                parts.append(text)
    return "\n".join(parts)


def gate_text(text: str, *, nsfw: bool = False) -> None:
    """Fail closed on CSAM, beyond-R, and NCII. `nsfw` does not waive those scans."""
    blob = text or ""
    csam = scan_csam(blob)
    if csam:
        raise AUPGateError(
            "Blocked: minor-coded or CSAM-adjacent language is forbidden "
            f"({', '.join(csam)}). SpaceXAI reports CSAM to NCMEC."
        )
    beyond_r = scan_explicit_beyond_r(blob)
    if beyond_r:
        raise AUPGateError(
            "Blocked: pornographic / NC-17 depiction exceeds limited R-rated "
            f"fictional adult material ({', '.join(beyond_r)}). Policy: {AUP_URL}"
        )
    ncii = scan_ncii(blob)
    if ncii:
        raise AUPGateError(
            "Blocked: non-consensual / hidden-camera / nudify language "
            f"({', '.join(ncii)}). Policy: {AUP_URL}"
        )


def _shot_blob(shot: dict[str, Any], extra: str = "") -> str:
    return _join_fields(
        [
            shot.get("description"),
            shot.get("tier"),
            shot.get("explicit_level"),
            shot.get("explicit"),
            shot.get("prompt"),
            shot.get("recommended_mode"),
            extra,
        ]
    )


def _shot_has_reference(shot: dict[str, Any]) -> bool:
    if shot.get("has_reference") or shot.get("has_ref"):
        return True
    if shot.get("reference_image_id") or shot.get("reference_image_url"):
        return True
    refs = shot.get("reference_image_ids") or []
    return bool(refs)


def _explicit_level(shot: dict[str, Any]) -> str:
    raw = shot.get("explicit_level") or shot.get("explicit") or ""
    return str(raw).strip().lower()


def gate_nsfw_shot(shot: dict[str, Any], *, extra_prompt: str = "") -> None:
    require_attestation()
    blob = _shot_blob(shot, extra_prompt)
    gate_text(blob, nsfw=True)
    level = _explicit_level(shot)
    if level and level not in R_RATED_EXPLICIT_LEVELS:
        raise AUPGateError(
            "Blocked: explicit_level must be suggestive or moderate (R-rated). "
            f"Got {level!r}. Full explicit is not allowed on SpaceXAI Imagine."
        )
    if _shot_has_reference(shot):
        raise AUPGateError(
            "Blocked: reference images cannot be used on the NSFW / intimate "
            "path (real-person undress / publicity risk). Use imaginary-adult "
            f"text DNA only. Policy: {AUP_URL}"
        )


def gate_nsfw_batch(title: str, shots: Iterable[dict[str, Any]]) -> None:
    require_attestation()
    gate_text(title or "", nsfw=True)
    for shot in shots:
        gate_nsfw_shot(shot)


def gate_imagine_prompt(
    prompt: str,
    *,
    nsfw: bool = False,
    has_reference_image: bool = False,
) -> None:
    blob = prompt or ""
    intimate = nsfw or is_intimate_text(blob)
    if intimate:
        require_attestation()
    gate_text(blob, nsfw=intimate)
    if intimate and has_reference_image:
        raise AUPGateError(
            "Blocked: image-to-image / i2v from a source still is not allowed "
            "for intimate prompts (real-person nudify risk)."
        )


_STILL_SOURCE_TYPES = frozenset({"reference_frame", "still", "image", "i2v"})
_STILL_EXTEND_MODES = frozenset({"reference_to_video", "image_to_video", "i2v"})


def nsfw_extension_is_still_ref(source_type: str = "", extend_mode: str = "") -> bool:
    st = str(source_type or "").strip().lower()
    mode = str(extend_mode or "").strip().lower()
    return st in _STILL_SOURCE_TYPES or mode in _STILL_EXTEND_MODES


def gate_nsfw_extension_text(
    *parts: Any,
    source_type: str = "",
    extend_mode: str = "",
) -> None:
    """Attestation + R-rated text gate; fail-closed on intimate still-ref (nudify)."""
    require_attestation()
    blob = "\n".join(str(p).strip() for p in parts if p)
    still = nsfw_extension_is_still_ref(source_type, extend_mode)
    gate_imagine_prompt(blob, nsfw=True, has_reference_image=still)


_DNA_SCAN_KEYS = (
    "character_name",
    "core_identity",
    "facial_dna",
    "hair_grooming",
    "clothing_style",
    "movement_posture",
    "emotional_baseline",
    "motion_dna",
    "nsfw_notes",
    "subject_kind",
    "key_consistency_anchors",
)


def _dna_scan_blob(dna: dict[str, Any]) -> str:
    """Same fields Imagine prompt blocks emit, plus nested inject/wardrobe."""
    parts: list[Any] = [dna.get(key) for key in _DNA_SCAN_KEYS]
    parts.append(dna.get("prompt_injection"))
    parts.append(dna.get("wardrobe_lock"))
    return _join_fields(
        _flatten_planning_value(item) for item in parts if item not in (None, "")
    )


def _dna_is_intimate(dna: dict[str, Any]) -> bool:
    notes = str(dna.get("nsfw_notes") or "")
    if notes.strip():
        return True
    return is_intimate_text(_dna_scan_blob(dna))


def _dna_has_reference(dna: dict[str, Any]) -> bool:
    refs = dna.get("reference_image_ids") or []
    if refs:
        return True
    source = str(dna.get("source") or "").lower()
    return "upload" in source or "image" in source or "photo" in source


def gate_dna(dna: dict[str, Any]) -> None:
    blob = _dna_scan_blob(dna)
    gate_text(blob, nsfw=_dna_is_intimate(dna))
    kind = str(dna.get("subject_kind") or "unspecified").strip().lower()
    if kind and kind not in ALLOWED_SUBJECT_KINDS:
        raise AUPGateError(f"Unknown subject_kind: {kind!r}")
    if not _dna_is_intimate(dna):
        return
    require_attestation()
    if kind != SUBJECT_KIND_IMAGINARY_ADULT:
        raise AUPGateError(
            "Intimate DNA requires subject_kind=imaginary_adult "
            "(fictional adult, not a real person or lookalike)."
        )
    if _dna_has_reference(dna):
        raise AUPGateError(
            "Blocked: cannot lock uploaded / referenced photos into intimate "
            "DNA (undress / right-of-publicity). Use text-only imaginary adults."
        )
