"""Doctor AUP inventory: attestation + on-disk NSFW/DNA fail-closed checks."""

from __future__ import annotations

import json
from pathlib import Path

from doctor_types import CheckResult
from studio_paths import STUDIO_ROOT


def check_aup(*, repo_root: Path | None = None) -> list[CheckResult]:
    """Attestation + 403/429 fail-closed. Never prints attestation JSON."""
    section = "14. SpaceXAI AUP"
    from aup_gate import AUP_URL, aup_status
    from imagine_regions import FAILOVER_STATUS_CODES, POLICY_FAIL_CLOSED_CODES

    results: list[CheckResult] = []
    if 403 in FAILOVER_STATUS_CODES or 429 in FAILOVER_STATUS_CODES:
        results.append(
            CheckResult(
                "FAIL",
                "403/429 failover",
                "policy or rate-limit codes hop Imagine regions",
                section,
            )
        )
    elif 403 not in POLICY_FAIL_CLOSED_CODES or 429 not in POLICY_FAIL_CLOSED_CODES:
        results.append(
            CheckResult(
                "FAIL",
                "403/429 fail-closed",
                "POLICY_FAIL_CLOSED_CODES missing 403/429",
                section,
            )
        )
    else:
        results.append(
            CheckResult("PASS", "403/429 fail-closed", "no region hop", section)
        )

    root = repo_root or STUDIO_ROOT
    batch_count = 0
    template_json = 0
    batches_dir = root / "nsfw_batches"
    if batches_dir.is_dir():
        batch_count = len(list(batches_dir.glob("*/batch.json")))
        for path in batches_dir.glob("*.json"):
            if path.name.startswith("."):
                continue
            template_json += 1
    dna_intimate = 0
    chars = root / "characters"
    if chars.is_dir():
        for path in chars.glob("*/dna.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(payload, dict) and str(payload.get("nsfw_notes") or "").strip():
                dna_intimate += 1

    status = aup_status()
    if status["present"] and not status["valid"]:
        results.append(
            CheckResult(
                "FAIL",
                "AUP attestation",
                "checkbox is not attestation; run nsfw attest",
                section,
            )
        )
    elif status["valid"]:
        when = status.get("attested_at") or "ok"
        results.append(
            CheckResult(
                "PASS",
                "AUP attestation",
                f"valid · {when} · {AUP_URL}",
                section,
            )
        )
    elif batch_count or dna_intimate:
        results.append(
            CheckResult(
                "FAIL",
                "AUP attestation",
                f"NSFW work on disk ({batch_count} batches, {dna_intimate} intimate DNA) "
                f"without nsfw attest ({AUP_URL})",
                section,
            )
        )
    else:
        results.append(
            CheckResult(
                "PASS",
                "AUP idle",
                f"attest before NSFW · {AUP_URL}",
                section,
            )
        )
    if template_json and not status["valid"]:
        results.append(
            CheckResult(
                "WARN",
                "NSFW templates on disk",
                f"{template_json} committed nsfw_batches/*.json (not operator batch.json); "
                f"attest before generating from them ({AUP_URL})",
                section,
            )
        )
    return results
