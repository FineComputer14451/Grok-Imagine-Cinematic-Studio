#!/usr/bin/env python3
"""
Extend re-gen loop — fix prompts + attempt budget after chain QA No-Go (roadmap #5).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sequence_chain import build_extend_prompt
from sequence_memory import memory_bank_to_prompt_block
from stitch_artifact_lexicon import (
    build_negative_pack,
    suggest_entries_from_chain_qa,
    suggest_entries_from_seam,
)

DEFAULT_MAX_ATTEMPTS_PER_CLIP = 2
DEFAULT_MAX_SEQUENCE_ATTEMPTS = 20


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def ensure_regen_budget(seq: dict[str, Any]) -> dict[str, Any]:
    budget = seq.get("regen_budget")
    if not isinstance(budget, dict):
        budget = {}
    seq["regen_budget"] = {
        "max_attempts_per_clip": int(
            budget.get("max_attempts_per_clip", DEFAULT_MAX_ATTEMPTS_PER_CLIP)
        ),
        "max_sequence_attempts": budget.get(
            "max_sequence_attempts", DEFAULT_MAX_SEQUENCE_ATTEMPTS
        ),
        "sequence_attempts_used": int(budget.get("sequence_attempts_used", 0)),
    }
    return seq["regen_budget"]


def ensure_clip_regen(clip: dict[str, Any], seq: dict[str, Any] | None = None) -> dict[str, Any]:
    budget = ensure_regen_budget(seq) if seq is not None else {
        "max_attempts_per_clip": DEFAULT_MAX_ATTEMPTS_PER_CLIP
    }
    regen = clip.get("regen")
    if not isinstance(regen, dict):
        regen = {}
    clip["regen"] = {
        "attempts": int(regen.get("attempts", 0)),
        "max_attempts": int(
            regen.get(
                "max_attempts",
                budget.get("max_attempts_per_clip", DEFAULT_MAX_ATTEMPTS_PER_CLIP),
            )
        ),
        "last_plan_at": regen.get("last_plan_at"),
        "last_run_at": regen.get("last_run_at"),
        "history": list(regen.get("history") or []),
    }
    return clip["regen"]


def can_regen(seq: dict[str, Any], clip: dict[str, Any]) -> tuple[bool, str]:
    """Return (allowed, reason)."""
    ensure_regen_budget(seq)
    regen = ensure_clip_regen(clip, seq)
    max_a = regen["max_attempts"]
    if regen["attempts"] >= max_a:
        return False, f"Clip attempt budget exhausted ({regen['attempts']}/{max_a})"
    seq_budget = seq["regen_budget"]
    max_seq = seq_budget.get("max_sequence_attempts")
    if max_seq is not None and int(seq_budget.get("sequence_attempts_used", 0)) >= int(max_seq):
        return (
            False,
            f"Sequence attempt budget exhausted ({seq_budget['sequence_attempts_used']}/{max_seq})",
        )
    return True, "ok"


def _collect_fixes(clip: dict[str, Any]) -> list[str]:
    fixes: list[str] = []
    qa = clip.get("chain_qa") or {}
    for f in qa.get("fixes") or []:
        if f and f not in fixes:
            fixes.append(str(f))
    for key in ("identity_drift", "seam_report"):
        block = clip.get(key) or {}
        for f in block.get("fixes") or []:
            if f and f not in fixes:
                fixes.append(str(f))
        for fac in (block.get("factors") or [])[:3]:
            line = f"[{key}] {fac}"
            if line not in fixes:
                fixes.append(line)
    return fixes


def build_regen_fix_prompt(
    seq: dict[str, Any],
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    next_beat: str | None = None,
    character_injection: str = "",
) -> str:
    """Build a targeted re-gen prompt from QA + evidence + memory bank."""
    beat = (
        next_beat
        or clip.get("narrative_beat")
        or "Re-generate this clip fixing continuity failures; match previous end state exactly"
    )
    if previous_clip is not None:
        base = build_extend_prompt(
            seq, previous_clip, beat, character_injection=character_injection
        )
    else:
        # Opening clip re-gen: keep original intent + fixes
        parts = []
        if character_injection:
            parts.append(character_injection.strip())
        parts.append(clip.get("prompt") or beat)
        bank_block = memory_bank_to_prompt_block(seq.get("memory_bank"))
        if bank_block and not bank_block.rstrip().endswith("(empty)"):
            parts.append("")
            parts.append(bank_block)
        base = "\n".join(parts)

    fixes = _collect_fixes(clip)
    qa = clip.get("chain_qa") or {}
    critical = qa.get("critical_failures") or []
    drift = clip.get("identity_drift") or {}
    seam = clip.get("seam_report") or {}

    header = [
        "REGEN_FIX: Prior generation failed chain QA — apply ALL fixes below.",
        "Priority: invisible stitch continuity, identity lock, no morphing at boundary.",
        f"Prior decision: {qa.get('decision', 'unknown')} | weighted={qa.get('weighted_score')}",
    ]
    if critical:
        header.append(f"Critical failures: {', '.join(str(c) for c in critical)}")
    if drift.get("drift_score") is not None:
        header.append(f"identity_drift_score={drift.get('drift_score')} (pass={drift.get('pass')})")
    if seam.get("seam_risk") is not None:
        header.append(f"seam_risk={seam.get('seam_risk')} (pass={seam.get('pass')})")
    if fixes:
        header.append("FIXES:")
        for f in fixes:
            header.append(f"  - {f}")

    # Expand NEGATIVES from stitch artifact lexicon (seam + chain QA tags)
    tags = list(
        dict.fromkeys(
            suggest_entries_from_seam(seam)
            + suggest_entries_from_chain_qa(qa)
        )
    )
    pack = build_negative_pack(tags if tags else None, all_default=not tags)
    base_neg = (
        "face morph, wardrobe teleport, lighting pop, temporal flicker, "
        "identity drift, lost props, audio dialogue drop"
    )
    if pack:
        header.append(f"NEGATIVES: {base_neg}, {pack}")
    else:
        header.append(f"NEGATIVES: {base_neg}")
    header.append("---")
    return "\n".join(header) + "\n\n" + base


def plan_regen(
    seq: dict[str, Any],
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    next_beat: str | None = None,
    character_injection: str = "",
) -> dict[str, Any]:
    ensure_regen_budget(seq)
    ensure_clip_regen(clip, seq)
    allowed, reason = can_regen(seq, clip)
    fixes = _collect_fixes(clip)
    # Always build prompt for inspection even if not allowed
    fix_prompt = build_regen_fix_prompt(
        seq,
        clip,
        previous_clip=previous_clip,
        next_beat=next_beat,
        character_injection=character_injection,
    )
    return {
        "clip_id": clip.get("clip_id"),
        "allowed": allowed,
        "reason": reason,
        "fixes": fixes,
        "fix_prompt": fix_prompt,
        "attempts": clip["regen"]["attempts"],
        "max_attempts": clip["regen"]["max_attempts"],
        "sequence_attempts_used": seq["regen_budget"]["sequence_attempts_used"],
        "prior_decision": (clip.get("chain_qa") or {}).get("decision"),
    }


def _append_history(clip: dict[str, Any], entry: dict[str, Any]) -> None:
    regen = ensure_clip_regen(clip)
    hist = list(regen.get("history") or [])
    hist.append(entry)
    # keep last 10
    regen["history"] = hist[-10:]


def apply_regen_plan(
    seq: dict[str, Any],
    clip: dict[str, Any],
    plan: dict[str, Any] | None = None,
    *,
    previous_clip: dict[str, Any] | None = None,
    next_beat: str | None = None,
    character_injection: str = "",
) -> dict[str, Any]:
    """Write fix prompt onto clip; does not consume attempt budget."""
    if plan is None:
        plan = plan_regen(
            seq,
            clip,
            previous_clip=previous_clip,
            next_beat=next_beat,
            character_injection=character_injection,
        )
    ensure_clip_regen(clip, seq)
    prompt = plan["fix_prompt"]
    clip["prompt"] = prompt
    clip["regen_fix_prompt"] = prompt
    clip["status"] = "regen_ready"
    clip["regen"]["last_plan_at"] = _now_iso()
    _append_history(
        clip,
        {
            "at": _now_iso(),
            "action": "apply",
            "decision": plan.get("prior_decision"),
            "fixes": list(plan.get("fixes") or []),
            "prompt_excerpt": prompt[:200],
            "reason": plan.get("reason"),
        },
    )
    return plan


def consume_regen_attempt(seq: dict[str, Any], clip: dict[str, Any]) -> None:
    """Increment counters at start of a re-gen run."""
    ensure_regen_budget(seq)
    regen = ensure_clip_regen(clip, seq)
    regen["attempts"] = int(regen["attempts"]) + 1
    regen["last_run_at"] = _now_iso()
    seq["regen_budget"]["sequence_attempts_used"] = int(
        seq["regen_budget"].get("sequence_attempts_used", 0)
    ) + 1
    _append_history(
        clip,
        {
            "at": _now_iso(),
            "action": "run",
            "decision": (clip.get("chain_qa") or {}).get("decision"),
            "fixes": _collect_fixes(clip),
            "prompt_excerpt": (clip.get("prompt") or "")[:200],
            "reason": None,
        },
    )


def prepare_regen_run(
    seq: dict[str, Any],
    clip: dict[str, Any],
    *,
    previous_clip: dict[str, Any] | None = None,
    next_beat: str | None = None,
    character_injection: str = "",
    auto_apply: bool = True,
) -> dict[str, Any]:
    """
    Validate budget, optionally apply plan, consume attempt.
    Returns plan dict with allowed flag. Raises ValueError if not allowed.
    """
    plan = plan_regen(
        seq,
        clip,
        previous_clip=previous_clip,
        next_beat=next_beat,
        character_injection=character_injection,
    )
    if not plan["allowed"]:
        ensure_clip_regen(clip, seq)
        _append_history(
            clip,
            {
                "at": _now_iso(),
                "action": "blocked",
                "decision": plan.get("prior_decision"),
                "fixes": plan.get("fixes") or [],
                "prompt_excerpt": "",
                "reason": plan["reason"],
            },
        )
        raise ValueError(plan["reason"])
    if auto_apply:
        apply_regen_plan(seq, clip, plan)
    consume_regen_attempt(seq, clip)
    return plan
