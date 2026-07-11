#!/usr/bin/env python3
"""
Identity drift scorer for long-form extend/stitch (roadmap #1).

Returns a structured report. Higher drift_score = more drift (0–10).
Pass when drift_score < threshold (default 2.5, Identity Lock convention).
v1: metadata heuristics; optional still paths for hybrid mode via soft PIL import.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

DEFAULT_DRIFT_THRESHOLD = 2.5

DRIFT_EVIDENCE_SCHEMA_VERSION = "1.0"
DRIFT_EVIDENCE_PROTOCOL = "IDENTITY_CONTINUITY_PROTOCOL"
DRIFT_EVIDENCE_PROTOCOL_VERSION = "1.0"
DRIFT_EVIDENCE_TOOL = "sequence drift-score"
DRIFT_EVIDENCE_STATUSES = frozenset({"pass", "risk", "incomplete", "skipped"})
DRIFT_EVIDENCE_REQUIRED_FIELDS = (
    "schema_version",
    "protocol",
    "protocol_version",
    "clip_id",
    "character_slug",
    "scored_at",
    "tool",
    "score",
    "threshold",
    "status",
    "attempt",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def status_from_report(report: dict[str, Any]) -> str:
    if report.get("pass") is True:
        return "pass"
    return "risk"


def report_to_drift_evidence(
    report: dict[str, Any],
    *,
    character_slug: str,
    dna_version: int = 1,
    attempt: int = 1,
    reference_hint: str = "",
    notes: str = "",
    scored_at: str | None = None,
    tool: str = DRIFT_EVIDENCE_TOOL,
) -> dict[str, Any]:
    factors = [str(f) for f in (report.get("factors") or []) if f]
    fixes = [str(f) for f in (report.get("fixes") or []) if f]
    summary_parts = factors[:3] if factors else []
    if fixes:
        summary_parts.append("fixes: " + "; ".join(fixes[:2]))
    score = float(report.get("drift_score", report.get("score", 0.0)) or 0.0)
    threshold = float(report.get("threshold", DEFAULT_DRIFT_THRESHOLD) or DEFAULT_DRIFT_THRESHOLD)
    status = status_from_report(report)
    return {
        "schema_version": DRIFT_EVIDENCE_SCHEMA_VERSION,
        "protocol": DRIFT_EVIDENCE_PROTOCOL,
        "protocol_version": DRIFT_EVIDENCE_PROTOCOL_VERSION,
        "clip_id": str(report.get("clip_id") or ""),
        "character_slug": character_slug,
        "scored_at": scored_at or _now_iso(),
        "tool": tool,
        "score": score,
        "threshold": threshold,
        "status": status,
        "baseline": {
            "dna_slug": character_slug,
            "dna_version": int(dna_version),
            "reference_hint": reference_hint or "",
        },
        "signals": {
            "summary": "; ".join(summary_parts) if summary_parts else f"drift_score={score}",
            "flags": factors[:8],
        },
        "attempt": int(attempt),
        "notes": notes or "",
    }


def incomplete_drift_evidence(
    *,
    clip_id: str,
    character_slug: str,
    attempt: int = 1,
    notes: str = "Drift score not run",
) -> dict[str, Any]:
    return {
        "schema_version": DRIFT_EVIDENCE_SCHEMA_VERSION,
        "protocol": DRIFT_EVIDENCE_PROTOCOL,
        "protocol_version": DRIFT_EVIDENCE_PROTOCOL_VERSION,
        "clip_id": clip_id,
        "character_slug": character_slug,
        "scored_at": _now_iso(),
        "tool": DRIFT_EVIDENCE_TOOL,
        "score": 0.0,
        "threshold": DEFAULT_DRIFT_THRESHOLD,
        "status": "incomplete",
        "baseline": {
            "dna_slug": character_slug,
            "dna_version": 1,
            "reference_hint": "",
        },
        "signals": {"summary": notes, "flags": ["incomplete"]},
        "attempt": int(attempt),
        "notes": notes,
    }


def normalize_drift_evidence(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    return []


_DEFAULT_STRICT_FIXES = (
    "Run: python tools/cinematic_studio_cli.py sequence drift-score "
    '"<Seq>" --clip <clip_id> --dna characters/{slug}/dna.json',
    "Attach drift_evidence (ICP-02/03); see "
    "references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md",
)


def _evaluate_one_evidence(
    item: dict[str, Any],
    *,
    threshold: float,
) -> dict[str, Any]:
    """Evaluate a single drift_evidence object under strict rules."""
    status = str(item.get("status") or "").strip() or "incomplete"
    score_raw = item.get("score", item.get("drift_score"))
    try:
        score = float(score_raw) if score_raw is not None else None
    except (TypeError, ValueError):
        score = None

    fixes = list(_DEFAULT_STRICT_FIXES)

    if status == "incomplete":
        return {
            "pass": False,
            "status": "incomplete",
            "score": score,
            "reasons": ["drift_evidence status=incomplete"],
            "fixes": fixes,
        }
    if status == "skipped":
        return {
            "pass": False,
            "status": "skipped",
            "score": score,
            "reasons": [
                "drift_evidence status=skipped — strict mode does not allow skip"
            ],
            "fixes": fixes + ["Remove --strict-identity or run drift-score"],
        }
    if status == "risk":
        reasons = [f"identity risk (status=risk, score={score})"]
        summary = (item.get("signals") or {}).get("summary") or ""
        if summary:
            reasons.append(str(summary))
        risk_fixes = list(fixes)
        risk_fixes.append("Reinforce DNA anchors / re-lock identity before extend")
        return {
            "pass": False,
            "status": "risk",
            "score": score,
            "reasons": reasons,
            "fixes": risk_fixes,
        }
    if status != "pass":
        return {
            "pass": False,
            "status": status or "incomplete",
            "score": score,
            "reasons": [f"unknown or non-pass status={status!r}"],
            "fixes": fixes,
        }
    if score is not None and score >= threshold:
        return {
            "pass": False,
            "status": "risk",
            "score": score,
            "reasons": [f"score {score} >= threshold {threshold} despite status=pass"],
            "fixes": fixes + ["Re-run sequence drift-score and refresh evidence"],
        }
    return {
        "pass": True,
        "status": "pass",
        "score": score,
        "reasons": [],
        "fixes": [],
    }


def evaluate_identity_strict_gate(
    *,
    clip: dict[str, Any],
    drift_evidence: dict | list | None = None,
    threshold: float = DEFAULT_DRIFT_THRESHOLD,
) -> dict[str, Any]:
    """
    Opt-in strict identity gate for extend-path CLI.

    Fail on missing/incomplete/skipped evidence or risk (score >= threshold).
    """
    thr = float(threshold)
    items = normalize_drift_evidence(drift_evidence)

    if not items:
        report = clip.get("identity_drift")
        if isinstance(report, dict) and report.get("drift_score") is not None:
            slug = (
                str(clip.get("character_slug") or "")
                or str(report.get("character_slug") or "")
                or "unknown"
            )
            item = report_to_drift_evidence(
                report,
                character_slug=slug,
                reference_hint=str(clip.get("reference_image_id") or ""),
            )
            if report.get("pass") is False:
                item["status"] = "risk"
            scorer_fixes = [str(f) for f in (report.get("fixes") or []) if f]
            if scorer_fixes:
                item["notes"] = "; ".join(scorer_fixes)
            items = [item]

    if not items:
        return {
            "pass": False,
            "strict": True,
            "status": "missing",
            "reasons": [
                "No drift_evidence and no clip identity_drift score — "
                "run sequence drift-score"
            ],
            "fixes": list(_DEFAULT_STRICT_FIXES),
            "score": None,
            "threshold": thr,
        }

    order = {
        "missing": 4,
        "skipped": 3,
        "incomplete": 2,
        "risk": 1,
        "pass": 0,
    }
    worst_status = "pass"
    all_reasons: list[str] = []
    all_fixes: list[str] = []
    scores: list[float] = []
    overall_pass = True

    for item in items:
        one = _evaluate_one_evidence(item, threshold=thr)
        if item.get("notes") and not one["pass"]:
            for part in str(item["notes"]).split(";"):
                part = part.strip()
                if part and part not in one["fixes"]:
                    one["fixes"].append(part)
        if not one["pass"]:
            overall_pass = False
        if order.get(one["status"], 0) >= order.get(worst_status, 0):
            worst_status = one["status"]
        all_reasons.extend(one.get("reasons") or [])
        for f in one.get("fixes") or []:
            if f not in all_fixes:
                all_fixes.append(f)
        if one.get("score") is not None:
            scores.append(float(one["score"]))

    return {
        "pass": overall_pass,
        "strict": True,
        "status": "pass" if overall_pass else worst_status,
        "reasons": all_reasons,
        "fixes": all_fixes,
        "score": max(scores) if scores else None,
        "threshold": thr,
    }


_TOKEN_RE = re.compile(r"[a-z0-9']+")


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if len(t) > 2}


def _clamp(score: float, lo: float = 0.0, hi: float = 10.0) -> float:
    return round(max(lo, min(hi, score)), 2)


def _dna_corpus(dna: dict[str, Any]) -> str:
    parts = [
        dna.get("character_name", ""),
        dna.get("core_identity", ""),
        dna.get("facial_dna", ""),
        dna.get("hair_grooming", ""),
        dna.get("clothing_style", ""),
        dna.get("movement_posture", ""),
        " ".join(dna.get("key_consistency_anchors") or []),
    ]
    return " ".join(str(p) for p in parts if p)


def _anchor_hit(anchor: str, clip_text_lower: str, clip_toks: set[str]) -> bool:
    """True if full phrase appears or any distinctive token from the anchor is present."""
    a = anchor.strip().lower()
    if not a:
        return False
    if a in clip_text_lower:
        return True
    a_toks = _tokens(a)
    return bool(a_toks) and any(t in clip_toks for t in a_toks)


def score_identity_drift(
    clip: dict[str, Any],
    *,
    dna: dict[str, Any] | None = None,
    previous_clip: dict[str, Any] | None = None,
    threshold: float = DEFAULT_DRIFT_THRESHOLD,
    reference_still_path: str | None = None,
    clip_still_path: str | None = None,
) -> dict[str, Any]:
    """
    Score identity drift for a clip against Character DNA and chain context.

    Optional still paths enable hybrid mode when PIL can load both images.
    """
    factors: list[str] = []
    penalties: list[float] = []

    prompt = (clip.get("prompt") or "").strip()
    recap = (clip.get("last_frame_recap") or "").strip()
    ref_id = (clip.get("reference_image_id") or "").strip()
    clip_text = f"{prompt} {recap}"
    clip_text_lower = clip_text.lower()
    clip_toks = _tokens(clip_text)

    if not dna:
        # No DNA: still allow dry-run / early plates when a reference + prompt exist.
        # Penalty maps via _drift_to_qa_score (QA = 10 - drift); critical floor is 7.0.
        word_n = len(prompt.split())
        if ref_id and word_n >= 6:
            penalties.append(2.5)  # QA ≈ 7.5 — pass critical with monitoring
            factors.append(
                "No DNA profile — reference_image_id + solid prompt (lock DNA before long-form)"
            )
        elif ref_id and word_n >= 4:
            penalties.append(3.0)  # QA ≈ 7.0 — critical floor
            factors.append(
                "No DNA profile — reference_image_id + prompt (recommend DNA lock)"
            )
        else:
            penalties.append(4.0)  # QA ≈ 6.0 — no_go critical
            factors.append("No DNA profile — high identity risk")
            if word_n < 4:
                penalties.append(0.5)
                factors.append("Thin prompt without DNA")
    else:
        if dna.get("identity_lock_status") != "locked":
            penalties.append(1.0)
            factors.append(
                f"identity_lock_status={dna.get('identity_lock_status', 'pending')}"
            )

        corpus = _dna_corpus(dna)
        dna_toks = _tokens(corpus)
        anchors = [
            str(a) for a in (dna.get("key_consistency_anchors") or []) if str(a).strip()
        ]

        if not dna_toks:
            penalties.append(2.5)
            factors.append("DNA fields empty")
        elif not clip_toks:
            penalties.append(3.0)
            factors.append("Clip prompt/recap empty — cannot verify identity")
        else:
            # Coverage: fraction of DNA tokens found in clip text (identity recall)
            overlap = len(dna_toks & clip_toks) / max(1, len(dna_toks))
            # Soft lexical penalty so strong anchor locks stay under threshold
            lex_penalty = _clamp((1.0 - overlap) * 2.5, 0.0, 4.0)
            penalties.append(lex_penalty)
            factors.append(f"DNA token overlap={overlap:.0%} (lex_penalty={lex_penalty})")

            if anchors:
                hit = sum(
                    1 for a in anchors if _anchor_hit(a, clip_text_lower, clip_toks)
                )
                miss = len(anchors) - hit
                if miss:
                    ap = min(3.0, float(miss))
                    penalties.append(ap)
                    factors.append(f"Anchors missed={miss}/{len(anchors)}")
                else:
                    # Credit full anchor lock — counters residual lexical gap
                    penalties.append(-0.75)
                    factors.append(f"All {len(anchors)} anchors present in prompt/recap")

        dna_refs = [str(r) for r in (dna.get("reference_image_ids") or []) if r]
        if dna_refs:
            if not ref_id:
                penalties.append(1.5)
                factors.append(
                    "DNA has reference_image_ids but clip has no reference_image_id"
                )
            elif ref_id not in dna_refs:
                penalties.append(2.0)
                factors.append(f"reference_image_id={ref_id} not in DNA refs {dna_refs}")
            else:
                factors.append(f"reference_image_id matches DNA ({ref_id})")
        elif ref_id:
            factors.append(f"reference_image_id={ref_id} (no DNA ref list)")

    if previous_clip is not None:
        prev_ref = (previous_clip.get("reference_image_id") or "").strip()
        if prev_ref and ref_id and prev_ref == ref_id:
            penalties.append(-0.5)
            factors.append("reference_image_id propagated from previous clip")
        elif prev_ref and ref_id and prev_ref != ref_id:
            penalties.append(1.5)
            factors.append(
                f"reference_image_id changed {prev_ref} → {ref_id} (ok if scene change)"
            )
        elif prev_ref and not ref_id:
            penalties.append(1.0)
            factors.append("Previous clip had reference_image_id; current missing")

    mode = "metadata"
    if reference_still_path and clip_still_path:
        frame_score = _optional_still_drift(reference_still_path, clip_still_path)
        if frame_score is not None:
            mode = "hybrid"
            penalties.append(frame_score)
            factors.append(f"still_compare_penalty={frame_score}")

    raw = sum(penalties)
    drift_score = _clamp(raw if raw > 0 else 0.0)
    if not prompt and not recap and not dna:
        drift_score = max(drift_score, 6.0)

    passed = drift_score < threshold
    return {
        "clip_id": clip.get("clip_id"),
        "drift_score": drift_score,
        "threshold": threshold,
        "pass": passed,
        "mode": mode,
        "factors": factors,
        "suggested_character_drift_boundary": _drift_to_qa_score(drift_score),
        "fixes": []
        if passed
        else [
            "Reinforce DNA anchors in prompt",
            "Restore reference_image_id from DNA / previous clip",
            "Re-lock identity before extend",
        ],
    }


def _drift_to_qa_score(drift_score: float) -> float:
    """Map drift 0–10 to chain QA character_drift_boundary 1–10 (higher=better)."""
    return round(max(1.0, min(10.0, 10.0 - drift_score)), 1)


def _optional_still_drift(ref_path: str, clip_path: str) -> float | None:
    """Return extra drift penalty 0–3 from mean abs pixel diff, or None if unavailable."""
    try:
        from PIL import Image
    except ImportError:
        return None
    try:
        a = Image.open(ref_path).convert("RGB").resize((64, 64))
        b = Image.open(clip_path).convert("RGB").resize((64, 64))
    except OSError:
        return None

    px_a = list(a.getdata())
    px_b = list(b.getdata())
    if not px_a or len(px_a) != len(px_b):
        return None

    mad = sum(abs(pa[i] - pb[i]) for pa, pb in zip(px_a, px_b) for i in range(3)) / (
        len(px_a) * 3 * 255.0
    )
    return round(min(3.0, mad * 6.0), 2)
