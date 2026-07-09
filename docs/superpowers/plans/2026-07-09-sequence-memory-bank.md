# Sequence Memory Bank (#4) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a first-class **sequence memory bank** — running cast, prop, lighting, emotion, and audio state across the whole sequence — so handoffs and extend prompts read/write one bank instead of only ad-hoc per-clip fields.

**Architecture:** Pure module `tools/sequence_memory.py` owns empty bank shape, ensure/migrate, apply clip → bank updates, bank → continuity_state mirror, and bank → prompt block. `sequence_chain` scaffolds include `memory_bank`, accept schema `1.0` and `1.1`, load migrates missing banks, handoff/extend-prompt embed bank snapshot. CLI adds `sequence memory show|update|sync`. No re-gen loop (#5) in this epic — only stable bank APIs #5 will call later.

**Tech Stack:** Python 3.11+, existing `tools/sequence_chain.py`, Typer/Rich CLI, pytest (`sys.path` → `tools/`).

**Design:** [docs/superpowers/specs/2026-07-09-long-form-continuity-roadmap-design.md](../specs/2026-07-09-long-form-continuity-roadmap-design.md) — backlog item **#4**

**Depends on:** Evidence loop shipped (`identity_drift`, `seam_report`, assist v2) — not required for bank pure logic.

---

## Principles

1. **Additive schema** — old `sequence.json` without `memory_bank` must load; never hard-break `schema_version: "1.0"`.
2. **Single bank owner** — all mutate/read of bank shape goes through `sequence_memory.py` (not ad-hoc dicts in CLI).
3. **Mirror, don’t replace** — keep clip `continuity_state`, momentum, AMV; bank is sequence-level running state that *updates from* clips and *feeds* handoffs.
4. **YAGNI** — no Continuity Diff CLI (#9), no re-gen (#5), no Web UI, no new Role Card.
5. **TDD** per task; frequent commits.

## Out of scope

- Extend Re-Gen Loop (#5)
- Audio Momentum Integrity (#6) as separate scorer
- Emotional Temperature Gate (#7)
- Multi-character arbiter (#8)
- Vision / frame paths
- Plugin catalog pin (unless skill one-liner committed with release process later)

---

## Memory bank contract (locked)

```python
MEMORY_BANK_VERSION = "1.0"

# Empty bank shape (all keys always present after ensure_memory_bank)
{
  "version": "1.0",
  "updated_at": str | None,          # ISO or None
  "updated_from_clip_id": str | None,
  "cast": {
    # character_slug -> {
    #   "name": str,
    #   "reference_image_id": str,
    #   "wardrobe": str,
    #   "emotional_state": str,
    #   "last_seen_clip_id": str,
    # }
  },
  "environment": {
    "location": str,
    "time_of_day": str,
    "weather": str,
    "props": list[str],           # ordered unique-ish list
  },
  "lighting": {
    "state": str,                 # from momentum lighting_state
    "motifs": list[str],
  },
  "emotion": {
    "sequence_temperature": str,  # free text / short tag
    "last_emotional_state": str,
  },
  "audio": {
    "dialogue_state": str,
    "sfx_timing": str,
    "emotional_tone_audio": str,
    "music_cue_points": list[str],
    "lip_sync_state": str,
  },
  "notes": list[str],             # optional free-form continuity notes
}
```

**Update rules (`apply_clip_to_memory_bank(bank, clip, *, character_slug=None, character_name=None)`):**

- Copy non-empty `momentum_vector.lighting_state` → `lighting.state`
- Copy non-empty `momentum_vector.emotional_state` → `emotion.last_emotional_state` and cast entry if character known
- Copy non-empty AMV fields → `audio.*` (overwrite with latest non-empty)
- Merge `continuity_state` keys if present:
  - `location`, `time_of_day`, `weather` → environment
  - `props` (list or comma string) → append unique to `environment.props`
  - `wardrobe` / `character` → cast if slug/name provided
- `reference_image_id` on clip → cast entry when character_slug set
- Set `updated_from_clip_id`, `updated_at`
- Never delete prior props/cast entries unless explicitly cleared (no clear API in v1)

**Handoff:** `build_handoff_from_clip(clip, *, memory_bank=None)` adds `"memory_bank": snapshot` when provided (full bank dict copy).

**Extend prompt:** After AMV block, if bank present, append:

```
SEQUENCE_MEMORY_BANK:
  location: ...
  lighting: ...
  cast: ...
  audio.dialogue_state: ...
  props: ...
```

---

## File map

| Path | Role |
|------|------|
| `tools/sequence_memory.py` | Bank CRUD pure functions |
| `tools/sequence_chain.py` | Scaffold, load migrate, handoff, extend prompt, schema accept 1.0+1.1 |
| `tools/cli/sequence_commands.py` | `memory show`, `memory update`, wire handoff/extend |
| `tests/test_sequence_memory.py` | Unit tests for bank |
| `tests/test_sequence_chain_memory.py` or extend existing sequence tests | Integration with scaffold/handoff |
| `CHANGELOG.md` | Unreleased note |

---

### Task 1: Pure memory bank module + unit tests

**Files:**
- Create: `tools/sequence_memory.py`
- Create: `tests/test_sequence_memory.py`

- [ ] **Step 1: Write failing tests**

```python
"""Tests for sequence memory bank (roadmap #4)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from sequence_memory import (  # noqa: E402
    MEMORY_BANK_VERSION,
    apply_clip_to_memory_bank,
    empty_memory_bank,
    ensure_memory_bank,
    memory_bank_to_prompt_block,
    mirror_bank_to_continuity_state,
)
from sequence_chain import create_clip  # noqa: E402


def test_empty_bank_has_required_keys() -> None:
    bank = empty_memory_bank()
    assert bank["version"] == MEMORY_BANK_VERSION
    for key in ("cast", "environment", "lighting", "emotion", "audio", "notes"):
        assert key in bank
    assert bank["environment"]["props"] == []
    assert bank["cast"] == {}


def test_ensure_fills_missing_on_legacy_dict() -> None:
    partial = {"cast": {"liora": {"name": "Liora"}}}
    bank = ensure_memory_bank(partial)
    assert "environment" in bank
    assert bank["cast"]["liora"]["name"] == "Liora"
    assert bank["version"] == MEMORY_BANK_VERSION


def test_ensure_none_returns_empty() -> None:
    bank = ensure_memory_bank(None)
    assert bank["cast"] == {}


def test_apply_clip_updates_lighting_emotion_audio() -> None:
    bank = empty_memory_bank()
    clip = create_clip(
        prompt="Walk",
        last_frame_recap="Neon alley",
        reference_image_id="ref_a1",
    )
    clip["clip_id"] = "clip_001"
    clip["momentum_vector"]["lighting_state"] = "neon rain"
    clip["momentum_vector"]["emotional_state"] = "tense"
    clip["audio_momentum_vector"]["dialogue_state"] = "whisper mid-line"
    clip["continuity_state"] = {
        "location": "Neon alley",
        "props": ["umbrella", "briefcase"],
        "wardrobe": "charcoal coat",
    }
    out = apply_clip_to_memory_bank(
        bank, clip, character_slug="liora", character_name="Liora"
    )
    assert out["lighting"]["state"] == "neon rain"
    assert out["emotion"]["last_emotional_state"] == "tense"
    assert out["audio"]["dialogue_state"] == "whisper mid-line"
    assert out["environment"]["location"] == "Neon alley"
    assert "umbrella" in out["environment"]["props"]
    assert out["cast"]["liora"]["reference_image_id"] == "ref_a1"
    assert out["cast"]["liora"]["wardrobe"] == "charcoal coat"
    assert out["updated_from_clip_id"] == "clip_001"


def test_apply_does_not_wipe_prior_props() -> None:
    bank = empty_memory_bank()
    bank["environment"]["props"] = ["key"]
    clip = create_clip()
    clip["clip_id"] = "clip_002"
    clip["continuity_state"] = {"props": ["key", "phone"]}
    out = apply_clip_to_memory_bank(bank, clip)
    assert out["environment"]["props"] == ["key", "phone"] or set(out["environment"]["props"]) >= {
        "key",
        "phone",
    }


def test_prompt_block_includes_location_and_cast() -> None:
    bank = empty_memory_bank()
    bank["environment"]["location"] = "Rooftop"
    bank["lighting"]["state"] = "golden hour"
    bank["cast"]["liora"] = {
        "name": "Liora",
        "wardrobe": "coat",
        "emotional_state": "calm",
        "reference_image_id": "ref_1",
        "last_seen_clip_id": "clip_001",
    }
    block = memory_bank_to_prompt_block(bank)
    assert "SEQUENCE_MEMORY_BANK" in block
    assert "Rooftop" in block
    assert "Liora" in block or "liora" in block.lower()


def test_mirror_to_continuity_state() -> None:
    bank = empty_memory_bank()
    bank["environment"]["location"] = "Dock"
    bank["environment"]["props"] = ["crate"]
    bank["lighting"]["state"] = "fog"
    cont = mirror_bank_to_continuity_state(bank)
    assert cont.get("location") == "Dock"
    assert "crate" in (cont.get("props") or [])
```

- [ ] **Step 2: Run — expect fail**

```bash
pytest tests/test_sequence_memory.py -v
```

Expected: `ModuleNotFoundError: sequence_memory`

- [ ] **Step 3: Implement `tools/sequence_memory.py`**

```python
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
        # merge unique
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
```

- [ ] **Step 4: pytest pass**

```bash
pytest tests/test_sequence_memory.py -v
```

- [ ] **Step 5: Commit**

```bash
git add tools/sequence_memory.py tests/test_sequence_memory.py
git commit -m "feat(continuity): sequence memory bank pure module"
```

---

### Task 2: Wire memory bank into sequence_chain

**Files:**
- Modify: `tools/sequence_chain.py`
- Create: `tests/test_sequence_chain_memory.py`

- [ ] **Step 1: Failing integration tests**

```python
"""sequence_chain integration with memory bank."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from sequence_chain import (  # noqa: E402
    SCHEMA_VERSION,
    build_extend_prompt,
    build_handoff_from_clip,
    create_clip,
    create_sequence_scaffold,
    load_sequence,
    save_sequence,
    validate_sequence,
)


def test_scaffold_includes_memory_bank() -> None:
    seq = create_sequence_scaffold("Memory Test")
    assert "memory_bank" in seq
    assert "cast" in seq["memory_bank"]
    # New scaffolds may be 1.1; 1.0 still valid for legacy
    assert seq["schema_version"] in ("1.0", "1.1")


def test_validate_accepts_1_0_and_1_1() -> None:
    seq = create_sequence_scaffold("V")
    seq["schema_version"] = "1.0"
    assert validate_sequence(seq) == [] or all(
        "schema" not in i.lower() for i in validate_sequence(seq)
    )
    seq["schema_version"] = "1.1"
    issues = validate_sequence(seq)
    assert not any("schema_version" in i for i in issues)


def test_load_migrates_missing_memory_bank(tmp_path: Path) -> None:
    legacy = create_sequence_scaffold("Legacy")
    legacy.pop("memory_bank", None)
    legacy["schema_version"] = "1.0"
    path = tmp_path / "sequence.json"
    # save without going through ensure if needed — write raw
    path.write_text(json.dumps(legacy))
    loaded = load_sequence(path)
    assert "memory_bank" in loaded
    assert "environment" in loaded["memory_bank"]


def test_handoff_includes_memory_bank_when_provided() -> None:
    clip = create_clip(prompt="x", last_frame_recap="end")
    bank = {"cast": {}, "environment": {"location": "Pier", "props": [], "time_of_day": "", "weather": ""},
            "lighting": {"state": "dusk", "motifs": []},
            "emotion": {"sequence_temperature": "", "last_emotional_state": ""},
            "audio": {"dialogue_state": "", "sfx_timing": "", "emotional_tone_audio": "",
                      "music_cue_points": [], "lip_sync_state": ""},
            "notes": [], "version": "1.0"}
    # Prefer API: build_handoff_from_clip(clip, memory_bank=bank) OR build_handoff_from_clip(clip, seq=seq)
    handoff = build_handoff_from_clip(clip, memory_bank=bank)
    assert handoff.get("memory_bank") is not None
    assert handoff["memory_bank"]["environment"]["location"] == "Pier"


def test_extend_prompt_includes_memory_block() -> None:
    seq = create_sequence_scaffold("Ext")
    seq["memory_bank"]["environment"]["location"] = "Train car"
    seq["memory_bank"]["lighting"]["state"] = "flicker fluorescent"
    prev = create_clip(last_frame_recap="Door opens", prompt="Open")
    text = build_extend_prompt(seq, prev, "She steps inside")
    assert "SEQUENCE_MEMORY_BANK" in text
    assert "Train car" in text
```

- [ ] **Step 2: Implement sequence_chain changes**

1. Import from `sequence_memory`:
   `ensure_memory_bank`, `empty_memory_bank`, `memory_bank_to_prompt_block`, `apply_clip_to_memory_bank` (apply optional helper on add later).

2. Constants:

```python
SCHEMA_VERSION = "1.1"  # new scaffolds
SUPPORTED_SCHEMA_VERSIONS = frozenset({"1.0", "1.1"})
```

3. `create_sequence_scaffold` — add `"memory_bank": empty_memory_bank()`, schema_version uses SCHEMA_VERSION (`1.1`).

4. `validate_sequence`:

```python
if seq.get("schema_version") not in SUPPORTED_SCHEMA_VERSIONS:
    issues.append(f"Unsupported schema_version: {seq.get('schema_version')}")
```

5. `load_sequence` — after json load:

```python
data["memory_bank"] = ensure_memory_bank(data.get("memory_bank"))
# do not force rewrite schema_version; leave 1.0 as 1.0 until save optionally
```

6. `build_handoff_from_clip`:

```python
def build_handoff_from_clip(
    clip: dict[str, Any],
    *,
    memory_bank: dict[str, Any] | None = None,
) -> dict[str, Any]:
    packet = { ... existing ... }
    if memory_bank is not None:
        packet["memory_bank"] = ensure_memory_bank(memory_bank)
    return packet
```

7. `build_extend_prompt` — after existing lines, if seq has memory_bank:

```python
bank = ensure_memory_bank(seq.get("memory_bank"))
block = memory_bank_to_prompt_block(bank)
if block:
    lines.append("")
    lines.append(block)
```

Also pass bank into handoff if you build handoff from seq inside extend (optional consistency).

8. Optional helper for callers:

```python
def sync_memory_from_clip(
    seq: dict[str, Any],
    clip: dict[str, Any],
    *,
    character_slug: str | None = None,
    character_name: str | None = None,
) -> dict[str, Any]:
    seq["memory_bank"] = apply_clip_to_memory_bank(
        seq.get("memory_bank"),
        clip,
        character_slug=character_slug,
        character_name=character_name,
    )
    return seq
```

- [ ] **Step 3: pytest**

```bash
pytest tests/test_sequence_memory.py tests/test_sequence_chain_memory.py -v
# also any tests that assume schema_version == "1.0" only
pytest tests/ -q --tb=no -k sequence 2>/dev/null | tail -20
```

Fix any breakage from SCHEMA_VERSION change (validators, fixtures).

- [ ] **Step 4: Commit**

```bash
git add tools/sequence_chain.py tests/test_sequence_chain_memory.py
git commit -m "feat(continuity): wire memory bank into sequence scaffold and handoffs"
```

---

### Task 3: CLI — memory show / update / sync + handoff wiring

**Files:**
- Modify: `tools/cli/sequence_commands.py`
- Modify: `tests/test_cli_smoke.py`

- [ ] **Step 1: Smoke test**

```python
def test_sequence_memory_commands_registered() -> None:
    result = run_cli("sequence", "--help")
    assert result.returncode == 0
    # Typer may show "memory" as sub-app or commands memory-show — pick one design
    assert "memory" in result.stdout.lower()
```

**CLI design (prefer nested typer if pattern exists; else flat commands):**

Flat (simpler, matches drift-score style):

- `sequence memory-show NAME`
- `sequence memory-sync NAME --clip CLIP [--character SLUG]`
- `sequence memory-set NAME --location ... --prop ...` (optional minimal)

Or nested:

```python
memory_app = typer.Typer(help="Sequence memory bank")
app.add_typer(memory_app, name="memory")

@memory_app.command("show")
...
@memory_app.command("sync")
...
```

Use nested if `nsfw extend` pattern is familiar — check `cinematic_studio_cli.py` for typer nesting. Prefer **nested** `sequence memory show|sync` for cleanliness.

- [ ] **Step 2: Implement**

**show:** load seq, print `memory_bank_summary` + pretty JSON panel (truncated).

**sync:** require clip; call `sync_memory_from_clip` or `apply_clip_to_memory_bank`; save_sequence; print summary.

**handoff command:** pass `memory_bank=seq.get("memory_bank")` into `build_handoff_from_clip`.

**extend-prompt:** already uses seq → should pick up bank from Task 2 automatically; verify manually.

**add-clip (optional):** add `--sync-memory` flag default False to avoid surprise; or auto-sync on add when continuity fields set. **YAGNI:** do not auto-sync on add unless trivial — user runs `memory sync`.

- [ ] **Step 3: Tests + manual help**

```bash
pytest tests/test_cli_smoke.py tests/test_sequence_memory.py tests/test_sequence_chain_memory.py -v
python tools/cinematic_studio_cli.py sequence memory --help
```

- [ ] **Step 4: Commit**

```bash
git add tools/cli/sequence_commands.py tests/test_cli_smoke.py
git commit -m "feat(cli): sequence memory show and sync commands"
```

---

### Task 4: Docs + regression

**Files:**
- Modify: `CHANGELOG.md` under Unreleased Added
- Optional: one line in continuity-consistency-guardian or sequence-director skill

- [ ] **Step 1: CHANGELOG**

```markdown
- **Sequence memory bank (roadmap #4)** — `tools/sequence_memory.py`; `sequence.json` `memory_bank` (schema 1.0+1.1); handoff/extend-prompt embed running cast/prop/lighting/audio state; CLI `sequence memory show|sync`
```

- [ ] **Step 2: Full related tests**

```bash
pytest tests/test_sequence_memory.py tests/test_sequence_chain_memory.py tests/test_identity_drift.py tests/test_seam_report.py tests/test_chain_qa_assist.py tests/test_cli_smoke.py tests/test_handoff_validator.py -v
```

If handoff validator rejects new `memory_bank` key on packets, **update validator to allow optional `memory_bank`** (additive) — do not strip bank.

Check `tools/handoff` or `handoff-packet-validator` / `tests/test_handoff_validator.py`.

- [ ] **Step 3: Commit**

```bash
git add CHANGELOG.md  # + validator if touched
git commit -m "docs: changelog for sequence memory bank"
```

---

## Spec coverage checklist

| Spec #4 outcome | Task |
|-----------------|------|
| Running cast/prop/lighting/emotion/audio state | Task 1 |
| sequence schema fields | Task 2 |
| Handoffs read/write bank | Task 2–3 |
| Not only ad-hoc clip fields | apply_clip + sync CLI |
| Additive / dual-read 1.0 | Task 2 validate + load migrate |
| No #5 re-gen | Out of scope |

## Hooks for #5 (do not implement)

- `seq["memory_bank"]` after failed QA → re-gen prompt includes `memory_bank_to_prompt_block` + `chain_qa.fixes`
- Attempt budget counter can live on `seq["regen_budget"]` later

---

## Execution handoff

Plan complete when saved to `docs/superpowers/plans/2026-07-09-sequence-memory-bank.md`.

**Two execution options:**

1. **Subagent-Driven (recommended)** — fresh subagent per task  
2. **Inline Execution** — this session with checkpoints  

Which approach?
