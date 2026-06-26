"""NSFW chain QA scaffold and evaluation for intimate sequence clips."""

from __future__ import annotations

from typing import Any

from nsfw_extension_config import NSFW_CHAIN_QA_CHECKS, NSFW_QA_CRITICAL
from nsfw_util import now_iso


def run_nsfw_chain_qa_scaffold(clip: dict[str, Any]) -> dict[str, Any]:
    """Return NSFW-specific chain QA scaffold (standard + intimate checks)."""
    result: dict[str, Any] = {
        "clip_id": clip["clip_id"],
        "evaluated_at": now_iso(),
        "nsfw_checks": {},
        "decision": "awaiting_scores",
        "critical_failures": [],
        "artifact_fixes": [],
    }
    for key, label, weight in NSFW_CHAIN_QA_CHECKS:
        result["nsfw_checks"][key] = {
            "label": label,
            "score": None,
            "pass": None,
            "weight": weight,
            "critical": key in NSFW_QA_CRITICAL,
        }
    result["artifact_fixes"] = [
        "If hand_finger_integrity < 7: regenerate with hands out of frame or single-hand pose",
        "If explicit_area_artifact_risk < 7: pull back framing, reduce simultaneous body focus",
        "If skin_texture_consistency < 7: tighten Character DNA inject, match color grade",
        "If fabric_cloth_physics < 7: specify one fabric tension point in prompt",
    ]
    return result


def evaluate_nsfw_chain_qa(clip: dict[str, Any], scores: dict[str, float]) -> dict[str, Any]:
    """Evaluate NSFW chain QA scores."""
    result = run_nsfw_chain_qa_scaffold(clip)
    total_weight = 0.0
    weighted_sum = 0.0
    critical_failures: list[str] = []

    for key, label, weight in NSFW_CHAIN_QA_CHECKS:
        score = scores.get(key)
        if score is None:
            continue
        passed = score >= 7.0
        result["nsfw_checks"][key] = {
            "label": label,
            "score": score,
            "pass": passed,
            "weight": weight,
            "critical": key in NSFW_QA_CRITICAL,
        }
        weighted_sum += score * weight
        total_weight += weight
        if not passed and key in NSFW_QA_CRITICAL:
            critical_failures.append(key)

    result["weighted_score"] = round(weighted_sum / total_weight, 2) if total_weight else None
    result["critical_failures"] = critical_failures

    if critical_failures:
        result["decision"] = "no_go"
    elif result["weighted_score"] is not None and result["weighted_score"] >= 7.0:
        result["decision"] = "go"
    elif result["weighted_score"] is not None and result["weighted_score"] >= 5.5:
        result["decision"] = "conditional_go"
    else:
        result["decision"] = "no_go"

    return result