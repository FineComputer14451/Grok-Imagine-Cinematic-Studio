# Identity Continuity Agent Wiring Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wire existing long-form agents so identity drift scoring and handoff evidence are **required protocol** (Role Cards + skills + additive `drift_evidence` schema), with **warn-only** validation — no new agents and no CLI hard-block on extend.

**Architecture:** Canonical protocol doc under `references/agents/`. Pure mapping helper in `tools/identity_drift.py` projects clip `identity_drift` reports into handoff `drift_evidence`. Validator gains a separate warnings channel (exit 0 when only warnings). Sequence handoff builder attaches evidence when present. Role Cards and skills cite ICP step IDs.

**Tech Stack:** Python 3.11+, existing `identity_drift` / `sequence_chain` / `handoff-packet-validator`, pytest, Markdown Role Cards + SKILL.md. No new packaging deps.

**Design:** [docs/development/superpowers/specs/2026-07-11-identity-continuity-agent-wiring-design.md](../specs/2026-07-11-identity-continuity-agent-wiring-design.md)

**Depends on:** Shipped long-form tools (`sequence drift-score`, DNA handoffs, chain QA).

---

## Principles

1. **Protocol over gates** — agents must call tools; CLI never refuses extend for missing evidence in this epic.
2. **Additive schema** — `drift_evidence` never required for hard packet validity; missing → warning on extend-type packets.
3. **One mapping helper** — do not rename clip field `identity_drift`.
4. **TDD** for Python; docs tasks still have verification steps.
5. **YAGNI** — no vision scorer, no multi-cast arbiter rewrite, no plugin pack changes unless releasing skills (pin is a separate release step; this plan edits skills in-repo).

## Out of scope

- CLI hard-block / `--strict-identity` exit codes on `sequence` run
- Vision / hybrid scorer quality upgrades
- New Role Cards or agents
- NSFW-only forks
- Full Studio Director rewrite

---

## File map

| Path | Action | Responsibility |
|------|--------|----------------|
| `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` | **Create** | Canonical ICP v1.0 steps + schema |
| `tools/identity_drift.py` | **Modify** | `report_to_drift_evidence`, status helpers, constants |
| `tools/sequence_chain.py` | **Modify** | `build_handoff_from_clip` attaches `drift_evidence` when clip has `identity_drift` |
| `tools/character_dna.py` | **Modify** | Soft-align identity_lock_instructions; optional evidence note |
| `.grok/skills/handoff-packet-validator/scripts/validate_handoff.py` | **Modify** | Warn channel for `drift_evidence` |
| `.grok/skills/handoff-packet-validator/SKILL.md` | **Modify** | Document warn-only ICP checks |
| `tests/test_identity_drift.py` | **Modify** | Mapping helper tests |
| `tests/test_handoff_validator.py` | **Modify** | Warning + schema tests |
| `tests/test_sequence_chain_memory.py` or new `tests/test_drift_evidence_handoff.py` | **Create/Modify** | Handoff builder includes evidence |
| `references/agents/Identity_Lock_Specialist.md` | **Modify** | ICP ownership + protocol link |
| `references/agents/Character_DNA_Extractor_v3.5.md` | **Modify** | ICP-01 |
| `references/agents/Cinematic_Sequence_Extender.md` | **Modify** | ICP-04 |
| `references/agents/Continuity_Consistency_Guardian.md` | **Modify** | ICP-05 |
| `references/agents/Quality_Assurance_Guardian_v3.5.md` | **Modify** | ICP-06 |
| `references/agents/Sequence_Director.md` | **Modify** | Light routing |
| `.grok/skills/identity-lock-specialist/SKILL.md` | **Modify** | Required ICP steps |
| `.grok/skills/character-dna-extractor/SKILL.md` | **Modify** | ICP-01 |
| `.grok/skills/cinematic-sequence-extender/SKILL.md` | **Modify** | ICP-04 |
| `.grok/skills/continuity-consistency-guardian/SKILL.md` | **Modify** | ICP-05 |
| `.grok/skills/quality-assurance-guardian/SKILL.md` | **Modify** | ICP-06 |
| `.grok/skills/chain-qa-protocol/SKILL.md` | **Modify** | Map identity criteria → evidence |
| `.grok/skills/sequence-director/SKILL.md` | **Modify** | Light pre-extend identity step |
| `references/agents/AGENT_INDEX.md` | **Modify** | Long-form preset one-liner |
| `CHANGELOG.md` | **Modify** | Unreleased entry |

---

## Contract: `drift_evidence`

```python
DRIFT_EVIDENCE_SCHEMA_VERSION = "1.0"
DRIFT_EVIDENCE_PROTOCOL = "IDENTITY_CONTINUITY_PROTOCOL"
DRIFT_EVIDENCE_PROTOCOL_VERSION = "1.0"
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
# baseline.dna_slug also required when baseline is present; always set by mapper
```

**Status mapping from scorer report:**

| Condition | `status` |
|-----------|----------|
| `report["pass"] is True` | `"pass"` |
| `report["pass"] is False` | `"risk"` |
| Manual incomplete (no report) | `"incomplete"` |
| User skip | `"skipped"` (+ `skipped_reason`) |

**Score field:** use `report["drift_score"]` as `score`.

**Multi-cast:** handoff may set `drift_evidence` to a **list** of objects; single cast uses one **object**.

---

### Task 1: Mapping helper (`report_to_drift_evidence`)

**Files:**
- Modify: `tools/identity_drift.py`
- Test: `tests/test_identity_drift.py`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_identity_drift.py`:

```python
from identity_drift import (  # noqa: E402
    DEFAULT_DRIFT_THRESHOLD,
    score_identity_drift,
    report_to_drift_evidence,
    normalize_drift_evidence,
    DRIFT_EVIDENCE_REQUIRED_FIELDS,
)


def test_report_to_drift_evidence_pass() -> None:
    dna = _dna()
    clip = create_clip(
        prompt="Liora charcoal coat black bob scar left brow",
        reference_image_id="ref_liora_a1",
        last_frame_recap="same face coat bob scar",
    )
    clip["clip_id"] = "clip_002"
    report = score_identity_drift(clip, dna=dna)
    evidence = report_to_drift_evidence(
        report,
        character_slug="liora",
        dna_version=1,
        attempt=1,
    )
    assert evidence["status"] == "pass"
    assert evidence["score"] == report["drift_score"]
    assert evidence["threshold"] == DEFAULT_DRIFT_THRESHOLD
    assert evidence["clip_id"] == "clip_002"
    assert evidence["character_slug"] == "liora"
    assert evidence["protocol"] == "IDENTITY_CONTINUITY_PROTOCOL"
    assert evidence["tool"] == "sequence drift-score"
    assert evidence["baseline"]["dna_slug"] == "liora"
    for key in DRIFT_EVIDENCE_REQUIRED_FIELDS:
        assert key in evidence, f"missing {key}"
    assert evidence["baseline"]["dna_slug"]


def test_report_to_drift_evidence_risk() -> None:
    report = {
        "clip_id": "clip_003",
        "drift_score": 4.0,
        "threshold": 2.5,
        "pass": False,
        "mode": "metadata",
        "factors": ["DNA token overlap=10%"],
        "fixes": ["Reinforce DNA anchors in prompt"],
    }
    evidence = report_to_drift_evidence(report, character_slug="liora")
    assert evidence["status"] == "risk"
    assert evidence["score"] == 4.0
    assert "DNA" in evidence["signals"]["summary"] or evidence["signals"]["flags"]


def test_normalize_drift_evidence_object_and_list() -> None:
    one = report_to_drift_evidence(
        {"clip_id": "c1", "drift_score": 1.0, "threshold": 2.5, "pass": True, "factors": []},
        character_slug="a",
    )
    assert len(normalize_drift_evidence(one)) == 1
    assert len(normalize_drift_evidence([one, one])) == 2
    assert normalize_drift_evidence(None) == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_identity_drift.py::test_report_to_drift_evidence_pass tests/test_identity_drift.py::test_report_to_drift_evidence_risk tests/test_identity_drift.py::test_normalize_drift_evidence_object_and_list -v`

Expected: FAIL with `ImportError` or `cannot import name report_to_drift_evidence`

- [ ] **Step 3: Implement mapping helpers in `tools/identity_drift.py`**

Add after `DEFAULT_DRIFT_THRESHOLD` (and keep existing scorer unchanged):

```python
from datetime import datetime, timezone

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
    """Map scorer report to protocol status (pass|risk)."""
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
    """
    Project sequence clip identity_drift report → handoff drift_evidence object.
    """
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
    """Build incomplete evidence when scoring was not performed."""
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
    """Accept object, list, or None → list of evidence dicts."""
    if value is None:
        return []
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list):
        return [x for x in value if isinstance(x, dict)]
    return []
```

If `_now_iso` already exists in this module, reuse it and do not duplicate.

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_identity_drift.py -v`

Expected: PASS (all existing + new)

- [ ] **Step 5: Commit**

```bash
git add tools/identity_drift.py tests/test_identity_drift.py
git commit -m "feat(identity): map identity_drift reports to drift_evidence"
```

---

### Task 2: Attach `drift_evidence` on sequence extend handoffs

**Files:**
- Modify: `tools/sequence_chain.py` (`build_handoff_from_clip`)
- Create: `tests/test_drift_evidence_handoff.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_drift_evidence_handoff.py`:

```python
"""drift_evidence on sequence_extend_handoff (identity continuity wiring)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from identity_drift import report_to_drift_evidence  # noqa: E402
from sequence_chain import build_handoff_from_clip, create_clip  # noqa: E402


def test_handoff_includes_drift_evidence_from_clip() -> None:
    clip = create_clip(prompt="hero locked face coat", last_frame_recap="same face")
    clip["clip_id"] = "clip_001"
    clip["identity_drift"] = {
        "clip_id": "clip_001",
        "drift_score": 1.2,
        "threshold": 2.5,
        "pass": True,
        "factors": ["All anchors present"],
        "fixes": [],
    }
    handoff = build_handoff_from_clip(
        clip,
        character_slug="liora",
    )
    assert handoff["packet_type"] == "sequence_extend_handoff"
    assert "drift_evidence" in handoff
    ev = handoff["drift_evidence"]
    assert isinstance(ev, dict)
    assert ev["status"] == "pass"
    assert ev["score"] == 1.2
    assert ev["character_slug"] == "liora"
    assert "ICP" in " ".join(handoff.get("extend_instructions") or []) or any(
        "drift" in str(x).lower() for x in (handoff.get("extend_instructions") or [])
    )


def test_handoff_omits_drift_evidence_when_not_scored() -> None:
    clip = create_clip(prompt="unscored", last_frame_recap="recap")
    clip["clip_id"] = "clip_002"
    handoff = build_handoff_from_clip(clip)
    # Additive: no synthetic incomplete unless explicitly requested
    assert "drift_evidence" not in handoff or handoff.get("drift_evidence") is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_drift_evidence_handoff.py -v`

Expected: FAIL (`character_slug` unexpected kwarg and/or missing `drift_evidence`)

- [ ] **Step 3: Update `build_handoff_from_clip` in `tools/sequence_chain.py`**

Change signature and body (preserve memory_bank behavior):

```python
def build_handoff_from_clip(
    clip: dict[str, Any],
    *,
    memory_bank: dict[str, Any] | None = None,
    character_slug: str | None = None,
    dna_version: int = 1,
    attempt: int = 1,
) -> dict[str, Any]:
    """Generate handoff packet for the next clip in the chain."""
    packet: dict[str, Any] = {
        "packet_type": "sequence_extend_handoff",
        "schema_version": SCHEMA_VERSION,
        "created_at": _now_iso(),
        "source_clip_id": clip["clip_id"],
        "last_frame_recap": clip.get("last_frame_recap", ""),
        "momentum_vector": clip.get("momentum_vector", _empty_momentum()),
        "audio_momentum_vector": clip.get("audio_momentum_vector", _empty_audio_momentum()),
        "continuity_state": clip.get("continuity_state", {}),
        "reference_image_id": clip.get("reference_image_id", ""),
        "transition_recommendation": clip.get("transition_to_next", "invisible_edit"),
        "extend_instructions": [
            "extend_from_last=true",
            "stitch_to_previous=true",
            "Use LAST_FRAME_RECAP as authoritative starting state",
            "Propagate AUDIO_MOMENTUM_VECTOR for native audio continuity",
            "Maintain reference_image_id unless deliberate scene change",
            "Run chain QA before approving next clip",
            "Identity Continuity: require drift_evidence (ICP-02/03) before claiming extend-ready; "
            "run: python tools/cinematic_studio_cli.py sequence drift-score",
        ],
    }
    if memory_bank is not None:
        packet["memory_bank"] = ensure_memory_bank(memory_bank)

    report = clip.get("identity_drift")
    if isinstance(report, dict) and report.get("drift_score") is not None:
        from identity_drift import report_to_drift_evidence

        slug = (
            character_slug
            or (clip.get("character_slug") or "")
            or (report.get("character_slug") or "")
            or "unknown"
        )
        packet["drift_evidence"] = report_to_drift_evidence(
            report,
            character_slug=str(slug),
            dna_version=dna_version,
            attempt=attempt,
            reference_hint=str(clip.get("reference_image_id") or ""),
        )
        # Mirror score into continuity_state for Continuity Guardian (ICP-05)
        cont = dict(packet.get("continuity_state") or {})
        cont["drift_evidence_status"] = packet["drift_evidence"]["status"]
        cont["drift_score"] = packet["drift_evidence"]["score"]
        packet["continuity_state"] = cont

    return packet
```

Prefer a top-of-file import of `report_to_drift_evidence` if `sequence_chain` already imports from sibling tools without cycles. If circular import appears, keep the local import inside the `if` block as shown.

- [ ] **Step 4: Run tests**

Run:

```bash
pytest tests/test_drift_evidence_handoff.py tests/test_sequence_chain_memory.py -v
```

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/sequence_chain.py tests/test_drift_evidence_handoff.py
git commit -m "feat(sequence): attach drift_evidence on extend handoffs"
```

---

### Task 3: Validator warn channel for `drift_evidence`

**Files:**
- Modify: `.grok/skills/handoff-packet-validator/scripts/validate_handoff.py`
- Modify: `tests/test_handoff_validator.py`
- Modify: `.grok/skills/handoff-packet-validator/SKILL.md` (brief)

**Design rules:**
- Hard `issues` still fail exit code 1.
- Warnings for: missing `drift_evidence` on `sequence_extend_handoff` / `identity_lock_handoff`; incomplete required fields when section present; `skipped` without `skipped_reason`; `status=risk` (informational warn).
- Invalid `status` enum when section present → **issue** (schema error), not warning.
- Exit code **0** when only warnings (print `⚠️` lines).

- [ ] **Step 1: Write failing tests**

Append to `tests/test_handoff_validator.py`:

```python
def _minimal_extend(**overrides):
    base = {
        "packet_type": "sequence_extend_handoff",
        "source_clip_id": "clip_001",
        "last_frame_recap": "Wide shot, hero mid-stride",
        "momentum_vector": {"action": "walking", "camera": "dolly in", "emotion": "tense"},
        "audio_momentum_vector": {"dialogue": "none", "sfx": "rain"},
    }
    base.update(overrides)
    return base


def test_extend_missing_drift_evidence_warns_but_exits_0() -> None:
    result = run_validator(_minimal_extend())
    assert result.returncode == 0, result.stdout + result.stderr
    out = result.stdout + result.stderr
    assert "drift_evidence" in out.lower() or "⚠️" in out


def test_extend_with_valid_drift_evidence_ok() -> None:
    result = run_validator(_minimal_extend(drift_evidence={
        "schema_version": "1.0",
        "protocol": "IDENTITY_CONTINUITY_PROTOCOL",
        "protocol_version": "1.0",
        "clip_id": "clip_001",
        "character_slug": "liora",
        "scored_at": "2026-07-11T00:00:00+00:00",
        "tool": "sequence drift-score",
        "score": 1.0,
        "threshold": 2.5,
        "status": "pass",
        "baseline": {"dna_slug": "liora", "dna_version": 1},
        "attempt": 1,
    }))
    assert result.returncode == 0, result.stdout + result.stderr


def test_drift_evidence_invalid_status_is_error() -> None:
    result = run_validator(_minimal_extend(drift_evidence={
        "schema_version": "1.0",
        "protocol": "IDENTITY_CONTINUITY_PROTOCOL",
        "protocol_version": "1.0",
        "clip_id": "clip_001",
        "character_slug": "liora",
        "scored_at": "2026-07-11T00:00:00+00:00",
        "tool": "sequence drift-score",
        "score": 1.0,
        "threshold": 2.5,
        "status": "banana",
        "baseline": {"dna_slug": "liora", "dna_version": 1},
        "attempt": 1,
    }))
    assert result.returncode == 1


def test_drift_evidence_skipped_without_reason_warns() -> None:
    result = run_validator(_minimal_extend(drift_evidence={
        "schema_version": "1.0",
        "protocol": "IDENTITY_CONTINUITY_PROTOCOL",
        "protocol_version": "1.0",
        "clip_id": "clip_001",
        "character_slug": "liora",
        "scored_at": "2026-07-11T00:00:00+00:00",
        "tool": "sequence drift-score",
        "score": 0.0,
        "threshold": 2.5,
        "status": "skipped",
        "baseline": {"dna_slug": "liora", "dna_version": 1},
        "attempt": 1,
    }))
    assert result.returncode == 0
    assert "skipped" in (result.stdout + result.stderr).lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_handoff_validator.py::test_extend_missing_drift_evidence_warns_but_exits_0 tests/test_handoff_validator.py::test_drift_evidence_invalid_status_is_error -v`

Expected: FAIL (no warning text / invalid status still exit 0)

- [ ] **Step 3: Implement validation helpers and update `main`**

In `validate_handoff.py`, add (imports as needed):

```python
EXTEND_PACKET_TYPES_WARN_IF_NO_DRIFT = frozenset({
    "sequence_extend_handoff",
    "identity_lock_handoff",
})

DRIFT_EVIDENCE_STATUSES = frozenset({"pass", "risk", "incomplete", "skipped"})
DRIFT_EVIDENCE_REQUIRED = (
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


def _iter_drift_evidence_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("drift_evidence")
    if raw is None:
        return []
    if isinstance(raw, dict):
        return [raw]
    if isinstance(raw, list):
        return [x for x in raw if isinstance(x, dict)]
    return []


def validate_drift_evidence_section(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    """
    Returns (issues, warnings) for drift_evidence.
    Missing section on extend packets → warning only.
    """
    issues: list[str] = []
    warnings: list[str] = []
    packet_type = data.get("packet_type")
    raw = data.get("drift_evidence", "__missing__")

    if raw == "__missing__" or raw is None:
        if packet_type in EXTEND_PACKET_TYPES_WARN_IF_NO_DRIFT:
            warnings.append(
                "drift_evidence missing — run sequence drift-score (ICP-02/03); "
                "see references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md"
            )
        return issues, warnings

    if not isinstance(raw, (dict, list)):
        issues.append("drift_evidence: must be an object or array of objects")
        return issues, warnings

    items = _iter_drift_evidence_items(data)
    if isinstance(raw, list) and not items:
        issues.append("drift_evidence: array must contain objects")
        return issues, warnings

    for i, item in enumerate(items):
        prefix = f"drift_evidence[{i}]" if len(items) > 1 or isinstance(raw, list) else "drift_evidence"
        for field in DRIFT_EVIDENCE_REQUIRED:
            if field not in item:
                warnings.append(f"{prefix}: missing field '{field}' (incomplete evidence)")
        status = item.get("status")
        if status is not None and status not in DRIFT_EVIDENCE_STATUSES:
            issues.append(f"{prefix}: invalid status: {status}")
        if status == "skipped" and not str(item.get("skipped_reason") or "").strip():
            warnings.append(f"{prefix}: status=skipped requires skipped_reason")
        if status == "risk":
            warnings.append(
                f"{prefix}: status=risk score={item.get('score')} "
                f"(threshold={item.get('threshold')}) — recommend ICP-07 fix"
            )
        if status == "incomplete":
            warnings.append(f"{prefix}: status=incomplete — run sequence drift-score")
        baseline = item.get("baseline")
        if isinstance(baseline, dict) and not str(baseline.get("dna_slug") or "").strip():
            warnings.append(f"{prefix}: baseline.dna_slug empty")
        elif baseline is None and "baseline" not in item:
            warnings.append(f"{prefix}: missing baseline.dna_slug")

    return issues, warnings


def validate_packet(data: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    packet_type = data.get("packet_type")
    if not packet_type:
        issues.append("missing packet_type")
        return issues

    schema = PACKET_TYPES.get(packet_type)
    if not schema:
        issues.append(f"unknown packet_type: {packet_type}")
        return issues

    issues.extend(apply_schema_rules(data, schema))
    drift_issues, _warnings = validate_drift_evidence_section(data)
    issues.extend(drift_issues)
    return issues


def validate_packet_with_warnings(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    issues = validate_packet(data)
    # Re-run warnings without double-counting issues: call section helper only for warnings
    _di, warnings = validate_drift_evidence_section(data)
    # validate_packet already included drift issues; warnings standalone
    return issues, warnings
```

**Bug to avoid:** calling `validate_drift_evidence_section` twice for issues. Cleaner pattern:

```python
def validate_packet_with_warnings(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    issues: list[str] = []
    packet_type = data.get("packet_type")
    if not packet_type:
        return ["missing packet_type"], []
    schema = PACKET_TYPES.get(packet_type)
    if not schema:
        return [f"unknown packet_type: {packet_type}"], []
    issues.extend(apply_schema_rules(data, schema))
    drift_issues, warnings = validate_drift_evidence_section(data)
    issues.extend(drift_issues)
    return issues, warnings


def validate_packet(data: dict[str, Any]) -> list[str]:
    issues, _warnings = validate_packet_with_warnings(data)
    return issues
```

Update `main()`:

```python
    issues, warnings = validate_packet_with_warnings(data)
    for w in warnings:
        print(f"⚠️  {w}")
    if issues:
        print(f"❌ Handoff validation failed ({path.name})")
        for issue in issues:
            print(f"  • {issue}")
        return 1

    if warnings:
        print(f"✅ Handoff valid with warnings: {data.get('packet_type')}")
    else:
        print(f"✅ Handoff valid: {data.get('packet_type')}")
    return 0
```

- [ ] **Step 4: Run full handoff validator tests**

Run: `pytest tests/test_handoff_validator.py -v`

Expected: PASS (including pre-existing tests — exit 0 still for valid packets; extend packets may now print warnings but return 0)

- [ ] **Step 5: Document in skill**

In `.grok/skills/handoff-packet-validator/SKILL.md`, add a short subsection:

```markdown
## Identity Continuity (`drift_evidence`)

For `sequence_extend_handoff` and `identity_lock_handoff`, missing or incomplete
`drift_evidence` produces **warnings** (exit 0). Invalid `status` enums are **errors**.
Protocol: `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`
CLI: `sequence drift-score`
```

- [ ] **Step 6: Commit**

```bash
git add .grok/skills/handoff-packet-validator/scripts/validate_handoff.py \
  .grok/skills/handoff-packet-validator/SKILL.md \
  tests/test_handoff_validator.py
git commit -m "feat(handoff): warn-only drift_evidence validation (ICP)"
```

---

### Task 4: Canonical Identity Continuity Protocol doc

**Files:**
- Create: `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`

- [ ] **Step 1: Write the protocol file**

Create `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` with this content (full file):

```markdown
# Identity Continuity Protocol v1.0 (studio v3.8)

**Cited as:** `[IDENTITY_CONTINUITY_PROTOCOL: v1.0]`  
**Path:** `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`  
**Enforcement:** Agent protocol only — CLI does **not** hard-block extend when evidence is missing.  
**Tooling:** `python tools/cinematic_studio_cli.py sequence drift-score`  
**Threshold:** drift score must stay **below 2.5** for `status=pass` (Identity Lock convention).

## Purpose

Make identity drift handling mandatory for long-form extend/stitch: score → record `drift_evidence` → consume in Extender / Continuity / QA — without new agents.

## Step IDs

| ID | When | Owner | Action |
|----|------|-------|--------|
| **ICP-01** | Character onboard / re-lock | DNA Extractor → Identity Lock | DNA complete; hero refs locked; inject blocks available |
| **ICP-02** | Before extend (N→N+1) or re-gen | Identity Lock (Extender verifies) | Run `sequence drift-score` vs DNA + prior end-state |
| **ICP-03** | Same moment as ICP-02 | Identity Lock | Fill `drift_evidence` on Lock + extend handoffs |
| **ICP-04** | Extend prompt build | Sequence Extender | Attach DNA inject; do not claim extend-ready if evidence missing or `skipped` without Director note |
| **ICP-05** | After clip / before next extend | Continuity Guardian | Mirror status/score into `continuity_state`; flag worsening trend |
| **ICP-06** | Chain QA / full QA | QA Guardian / Chain QA | Map identity criteria to evidence; missing → identity risk finding |
| **ICP-07** | No-Go on identity | Identity Lock + Extender | Fix → re-score → new evidence; increment `attempt` |

## Status language

| Condition | status | Agent behavior |
|-----------|--------|----------------|
| score &lt; 2.5 | `pass` | Proceed |
| score ≥ 2.5 | `risk` | Call out; recommend fix; user may continue (no CLI block) |
| Not scored | `incomplete` | Flag; run ICP-02 |
| User skip | `skipped` | Requires `skipped_reason` |

## Clip vs handoff fields

| Location | Field | Role |
|----------|-------|------|
| `sequence.json` clip | `identity_drift` | Raw scorer report from CLI |
| Handoff packet | `drift_evidence` | Agent contract (object or array) |
| Mapper | `identity_drift.report_to_drift_evidence` | Projection helper |

## `drift_evidence` shape

See design spec and `tools/identity_drift.py` (`report_to_drift_evidence`).  
Multi-cast: array of evidence objects (one per character).

## Validator

`handoff-packet-validator`: warns if missing/incomplete on extend-type packets; errors only on invalid schema (e.g. bad `status`). Exit 0 with warnings.

## Related agents

Identity Lock · Character DNA Extractor · Cinematic Sequence Extender · Continuity Guardian · QA Guardian · Sequence Director (routing) · Chain QA Protocol

---

*Identity Continuity Protocol v1.0 — Grok Imagine Cinematic Studio v3.8 · deepen existing agents*
```

- [ ] **Step 2: Verify file exists and is non-empty**

Run: `test -s references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md && wc -l references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`

Expected: line count > 40

- [ ] **Step 3: Commit**

```bash
git add references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md
git commit -m "docs(agents): Identity Continuity Protocol v1.0"
```

---

### Task 5: Role Card patches (core five + Sequence Director light)

**Files:**
- Modify: `references/agents/Identity_Lock_Specialist.md`
- Modify: `references/agents/Character_DNA_Extractor_v3.5.md`
- Modify: `references/agents/Cinematic_Sequence_Extender.md`
- Modify: `references/agents/Continuity_Consistency_Guardian.md`
- Modify: `references/agents/Quality_Assurance_Guardian_v3.5.md`
- Modify: `references/agents/Sequence_Director.md`

**Pattern for each card:** After Model Layer (or Key Responsibilities), insert an **Identity Continuity (required)** section. Soft-align any “block video / reject” CLI language to agent judgment + `status=risk` without promising CLI refuse.

- [ ] **Step 1: Patch Identity Lock**

Insert after Capabilities (or before Drift Score):

```markdown
## Identity Continuity (required)

**Protocol:** `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` · `[IDENTITY_CONTINUITY_PROTOCOL: v1.0]`

| Step | You own |
|------|---------|
| ICP-01 | Accept DNA handoff; lock status |
| ICP-02 | Run / request `sequence drift-score` before every extend or re-gen |
| ICP-03 | Fill `drift_evidence` on handoffs (map from clip `identity_drift`) |
| ICP-07 | After identity No-Go: fix → re-score → increment `attempt` |

**CLI (evidence):**
```bash
python tools/cinematic_studio_cli.py sequence drift-score "Sequence Name" --clip clip_002 --dna characters/{slug}/dna.json
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py path/to/handoff.json
```

**Soft gate language:** score ≥ 2.5 → `status=risk` — recommend correction and may refuse creatively; **studio CLI does not hard-block** extend in this protocol. Do not invent scores. Missing evidence → `incomplete` / do not claim Lock-approved for extend.
```

Update Drift Score section actions to match: `> 2.5 → risk + revise`; `> 3.0 → re-lock / new anchor; **agent** may withhold video approval` (not “CLI blocks”).

- [ ] **Step 2: Patch Character DNA Extractor**

Add:

```markdown
## Identity Continuity (required)

**Protocol:** `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`

| Step | You own |
|------|---------|
| ICP-01 | Complete DNA + hero refs + inject blocks; handoff to Identity Lock |

Do not mark DNA production-ready for long-form without anchors and `reference_image_ids` when available. Downstream Lock runs ICP-02/03.
```

- [ ] **Step 3: Patch Cinematic Sequence Extender**

Add:

```markdown
## Identity Continuity (required)

**Protocol:** `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`

| Step | You own |
|------|---------|
| ICP-04 | Consume `drift_evidence` + DNA inject + LAST_FRAME; verify Lock ran ICP-02/03 |
| ICP-07 | With Identity Lock after identity No-Go |

**Extend-ready rule (protocol):** Do **not** claim extend-ready if `drift_evidence` is missing, `status=incomplete`, or `status=skipped` without Director `skipped_reason` / notes. Ask for `sequence drift-score` first. CLI will not stop the user — you still must flag.
```

- [ ] **Step 4: Patch Continuity Guardian**

Add:

```markdown
## Identity Continuity (required)

**Protocol:** `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`

| Step | You own |
|------|---------|
| ICP-05 | Mirror `drift_evidence.status` / score into `continuity_state`; flag worsening trend across clips |

Prefer handoff `drift_evidence` as source of truth; clip `identity_drift` is the raw scorer log.
```

- [ ] **Step 5: Patch QA Guardian**

Add:

```markdown
## Identity Continuity (required)

**Protocol:** `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`

| Step | You own |
|------|---------|
| ICP-06 | Map Chain QA / identity criteria to `drift_evidence`; missing section = identity **risk** finding |

**Fix text when missing:** “Run ICP-02/03: `sequence drift-score` and attach `drift_evidence`.”  
`status=risk` supports No-Go on identity criteria; still not a CLI hard-block.
```

- [ ] **Step 6: Patch Sequence Director (light)**

Add under sequencing / dependencies:

```markdown
## Identity Continuity (routing)

Long-form clip graphs must include a pre-extend **identity continuity** dependency: Identity Lock completes ICP-02/03 (`drift_evidence`) before Extender ICP-04.  
Protocol: `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`
```

- [ ] **Step 7: Grep verification**

Run:

```bash
rg -n "IDENTITY_CONTINUITY_PROTOCOL" references/agents/Identity_Lock_Specialist.md \
  references/agents/Character_DNA_Extractor_v3.5.md \
  references/agents/Cinematic_Sequence_Extender.md \
  references/agents/Continuity_Consistency_Guardian.md \
  references/agents/Quality_Assurance_Guardian_v3.5.md \
  references/agents/Sequence_Director.md
```

Expected: each file has ≥1 match

- [ ] **Step 8: Commit**

```bash
git add references/agents/Identity_Lock_Specialist.md \
  references/agents/Character_DNA_Extractor_v3.5.md \
  references/agents/Cinematic_Sequence_Extender.md \
  references/agents/Continuity_Consistency_Guardian.md \
  references/agents/Quality_Assurance_Guardian_v3.5.md \
  references/agents/Sequence_Director.md
git commit -m "docs(agents): wire Identity Continuity Protocol into Role Cards"
```

---

### Task 6: Skill patches

**Files:**
- Modify: `.grok/skills/identity-lock-specialist/SKILL.md`
- Modify: `.grok/skills/character-dna-extractor/SKILL.md`
- Modify: `.grok/skills/cinematic-sequence-extender/SKILL.md`
- Modify: `.grok/skills/continuity-consistency-guardian/SKILL.md`
- Modify: `.grok/skills/quality-assurance-guardian/SKILL.md`
- Modify: `.grok/skills/chain-qa-protocol/SKILL.md`
- Modify: `.grok/skills/sequence-director/SKILL.md`

- [ ] **Step 1: Identity Lock skill**

After Core Mandate (or Key Protocols table), add:

```markdown
## Identity Continuity Protocol (required)

**Doc:** `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` · `[IDENTITY_CONTINUITY_PROTOCOL: v1.0]`

You own **ICP-02, ICP-03, ICP-07** (and ICP-01 with DNA Extractor).

Before every extend or re-gen:

1. `sequence drift-score "Seq" --clip <id> --dna characters/{slug}/dna.json`
2. Ensure handoff includes `drift_evidence` (from clip `identity_drift` via mapper / `build_handoff_from_clip`)
3. `status=risk` (≥ 2.5) → recommend fix; do not invent a pass
4. Validate: `python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py <handoff.json>` (warnings OK; fix errors)

Soft-align Hard Blocks: drift > 3.0 means **you** withhold video/extend approval until corrected — CLI does not hard-block generation in this protocol.
```

Update any “block video” table rows to the soft language above.

- [ ] **Step 2: DNA Extractor skill** — add ICP-01 subsection + protocol link (same pattern, shorter).

- [ ] **Step 3: Sequence Extender skill** — add ICP-04 / ICP-07 + extend-ready rule from Role Card.

- [ ] **Step 4: Continuity Guardian skill** — add ICP-05.

- [ ] **Step 5: QA Guardian skill** — add ICP-06.

- [ ] **Step 6: Chain QA Protocol skill** — add:

```markdown
## Identity Continuity (ICP-06)

When scoring `character_drift_boundary` / identity criteria, require handoff `drift_evidence` (or clip `identity_drift`).  
If missing → finding: run ICP-02/03 (`sequence drift-score`).  
Protocol: `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md`
```

- [ ] **Step 7: Sequence Director skill** — light routing note (pre-extend identity dependency).

- [ ] **Step 8: Grep verification**

```bash
rg -n "IDENTITY_CONTINUITY_PROTOCOL|ICP-0" \
  .grok/skills/identity-lock-specialist/SKILL.md \
  .grok/skills/character-dna-extractor/SKILL.md \
  .grok/skills/cinematic-sequence-extender/SKILL.md \
  .grok/skills/continuity-consistency-guardian/SKILL.md \
  .grok/skills/quality-assurance-guardian/SKILL.md \
  .grok/skills/chain-qa-protocol/SKILL.md \
  .grok/skills/sequence-director/SKILL.md
```

Expected: each path matches

- [ ] **Step 9: Commit**

```bash
git add .grok/skills/identity-lock-specialist/SKILL.md \
  .grok/skills/character-dna-extractor/SKILL.md \
  .grok/skills/cinematic-sequence-extender/SKILL.md \
  .grok/skills/continuity-consistency-guardian/SKILL.md \
  .grok/skills/quality-assurance-guardian/SKILL.md \
  .grok/skills/chain-qa-protocol/SKILL.md \
  .grok/skills/sequence-director/SKILL.md
git commit -m "docs(skills): require Identity Continuity Protocol steps"
```

---

### Task 7: DNA handoff instruction soft-align + AGENT_INDEX + CHANGELOG

**Files:**
- Modify: `tools/character_dna.py` (`build_handoff_packet` instructions)
- Modify: `references/agents/AGENT_INDEX.md`
- Modify: `CHANGELOG.md`
- Test: extend existing DNA/handoff tests if any assert instruction strings

- [ ] **Step 1: Find tests that lock instruction strings**

Run: `rg -n "reject if > 2.5|Calculate drift score" tests/ tools/`

If tests assert exact strings, update them in the same change.

- [ ] **Step 2: Soft-align `build_handoff_packet` instructions**

In `tools/character_dna.py`, change the identity_lock_instructions list item from hard reject to:

```python
"Run sequence drift-score before every extend; fill drift_evidence (ICP-02/03); "
"status=risk when score >= 2.5 — recommend correction; agent may withhold approval "
"(CLI does not hard-block). Protocol: IDENTITY_CONTINUITY_PROTOCOL v1.0",
```

Keep other instructions; add if missing:

```python
"Cite references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md on long-form handoffs",
```

- [ ] **Step 3: AGENT_INDEX long-form preset**

In `references/agents/AGENT_INDEX.md`, under Activation Presets row for Long-Form Sequence (preset 3), extend the command cell:

```markdown
| 3 | Long-Form Sequence | `ACTIVATE SEQUENCE_DIRECTOR` + `ACTIVATE SEQUENCE_EXTENDER` + Identity Continuity (`sequence drift-score` / ICP) |
```

Add under Supporting Skills or Technical section a one-liner:

```markdown
**Identity Continuity Protocol:** `references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md` (required wiring for Lock / Extender / Continuity / QA on long-form extends).
```

- [ ] **Step 4: CHANGELOG Unreleased**

Under `### Added` or `### Changed` in Unreleased:

```markdown
- **Identity Continuity Protocol v1.0** — deepen existing long-form agents: canonical ICP, `drift_evidence` handoff mapping, warn-only validator checks (no new agents; no CLI hard-block).
```

- [ ] **Step 5: Run targeted tests**

```bash
pytest tests/test_identity_drift.py tests/test_drift_evidence_handoff.py tests/test_handoff_validator.py tests/test_sequence_chain_memory.py -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add tools/character_dna.py references/agents/AGENT_INDEX.md CHANGELOG.md
git commit -m "docs: AGENT_INDEX + CHANGELOG for Identity Continuity wiring"
```

---

### Task 8: Full verification gate

- [ ] **Step 1: Run full related test suite**

```bash
pytest tests/test_identity_drift.py tests/test_drift_evidence_handoff.py \
  tests/test_handoff_validator.py tests/test_sequence_chain_memory.py \
  tests/test_chain_qa_assist.py tests/test_handoff_schema.py -v
```

Expected: PASS

- [ ] **Step 2: Protocol + wiring presence check**

```bash
test -s references/agents/IDENTITY_CONTINUITY_PROTOCOL_v3.8.md
rg -l "IDENTITY_CONTINUITY_PROTOCOL" references/agents/*.md .grok/skills/*/SKILL.md | sort
```

Expected: protocol file present; Role Cards + skills from Tasks 5–6 listed.

- [ ] **Step 3: Manual validator smoke**

```bash
python .grok/skills/handoff-packet-validator/scripts/validate_handoff.py - <<'EOF'
# use a temp file instead:
EOF
python - <<'PY'
import json, subprocess, sys, tempfile
from pathlib import Path
p = Path(tempfile.mkstemp(suffix=".json")[1])
p.write_text(json.dumps({
  "packet_type": "sequence_extend_handoff",
  "source_clip_id": "clip_001",
  "last_frame_recap": "recap",
  "momentum_vector": {"action": "a", "camera": "c", "emotion": "e"},
  "audio_momentum_vector": {},
}))
r = subprocess.run([sys.executable, ".grok/skills/handoff-packet-validator/scripts/validate_handoff.py", str(p)], capture_output=True, text=True)
print(r.returncode, r.stdout, r.stderr)
assert r.returncode == 0
assert "drift_evidence" in (r.stdout + r.stderr).lower() or "⚠️" in r.stdout
PY
```

Expected: exit 0 + warning about missing drift_evidence

- [ ] **Step 4: Optional studio verify (if env supports)**

```bash
bash scripts/verify_cinematic_studio.sh
```

Expected: pass or only pre-existing unrelated warnings

- [ ] **Step 5: Final commit only if Step 1–3 produced fixes; else done**

If only verification and no code changes: no empty commit.

---

## Spec coverage checklist (plan self-review)

| Spec requirement | Task |
|------------------|------|
| Canonical protocol doc | Task 4 |
| Role Cards ICP ownership | Task 5 |
| Skills ICP ownership | Task 6 |
| `drift_evidence` schema + mapper | Task 1 |
| Clip `identity_drift` → handoff | Tasks 1–2 |
| Validator warn-only | Task 3 |
| No new agents | (all tasks) |
| No CLI hard-block | Task 3 exit 0; docs language Tasks 5–7 |
| AGENT_INDEX preset | Task 7 |
| Soft-align DNA instructions | Task 7 |
| Continuity mirror | Task 2 (`continuity_state`) |
| Multi-cast array support | Task 1 `normalize`; Task 3 `_iter_drift_evidence_items` |
| Tests | Tasks 1–3, 8 |
| CHANGELOG | Task 7 |

**Placeholder scan:** none intentional.  
**Type consistency:** `status` ∈ pass|risk|incomplete|skipped; score from `drift_score`; protocol name `IDENTITY_CONTINUITY_PROTOCOL`.

---

## Execution handoff

Plan complete and saved to `docs/development/superpowers/plans/2026-07-11-identity-continuity-agent-wiring-implementation.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task, review between tasks  
2. **Inline Execution** — this session via executing-plans, batch with checkpoints  

Which approach?
