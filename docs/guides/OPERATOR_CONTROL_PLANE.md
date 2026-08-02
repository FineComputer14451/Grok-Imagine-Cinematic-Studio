# Operator Control Plane
## Grok Imagine Cinematic Studio v3.9.0

How to run the studio like an ops board: **Orient → Health → Produce → Gate → Converge & Deliver**.

> [!NOTE]
> Independent community project — **not affiliated with or endorsed by xAI**. Full notice: [DISCLAIMER.md](../../DISCLAIMER.md).

**Version:** 3.9.0 · **Introduced:** v3.8.8 (Phases 1–3) · **Density UX:** v3.9.0  
**North-star design:** `docs/development/superpowers/specs/2026-07-26-operator-ux-north-star-design.md`

---

## Why this exists

Creative pipelines fail most often from **silent drift**: identity breaks, unlocked plates, incomplete handoffs, or spend without health checks. The control plane makes the same readiness signals visible on:

| Surface | Entry |
|---------|--------|
| **Terminal TUI** | `cinematic-studio ui` |
| **Streamlit Dashboard** | `streamlit run web_ui/app.py` → Dashboard |
| **CLI** | `doctor` · `validate` · `quota sync` · `models verify` · `handoff validate` |

---

## The five-step loop

```text
┌─────────┐   ┌────────┐   ┌─────────┐   ┌──────┐   ┌──────────────────┐
│ Orient  │ → │ Health │ → │ Produce │ → │ Gate │ → │ Converge & Deliver│
└─────────┘   └────────┘   └─────────┘   └──────┘   └──────────────────┘
```

### 1. Orient

Open the live dashboard and **read severity before you create**.

| Signal | Meaning |
|--------|---------|
| **OK** | Safe to proceed with normal gates |
| **WARN** | Soft blockers — fix or accept risk consciously |
| **CRITICAL** | Do not spend until doctor / validate / identity issues clear |

Also check the **Attention** list (shared helpers on TUI + Streamlit).

**TUI Home (v3.9.0 density)**

| Key | Action |
|-----|--------|
| `1` | Compact view |
| `2` | Ops view |
| `3` | Full view |
| `Tab` | Cycle density modes |
| `p` | Pause / resume auto-refresh |
| Type | Filter Launcher / Cockpit action lists |

Dual-column panels: **READINESS** | **CONVERGENCE** on Home.

### 2. Health

Safe actions only — **no Imagine spend**.

| Intent | TUI | Streamlit | CLI |
|--------|-----|-----------|-----|
| Doctor | `d` | Health → Doctor | `cinematic-studio doctor` / `doctor --quick` |
| Validate | `v` | Health → Validate | `cinematic-studio validate` |
| Quota sync | `s` | Health → Quota sync | `cinematic-studio quota sync` |
| Models | `m` | Health → Models | `cinematic-studio models verify` |
| Stack | `k` | — | `cinematic-studio models stack` |

Refresh the snapshot and re-check Attention until clear or risks are accepted.

### 3. Produce

Build creative state **after** health is acceptable:

- Production Bible (wizard / Guided Creator / chat)
- Character DNA init → extract → lock → inject
- Sequence init / add-clip / handoff scaffold
- Imagine packets (CLI or Web Imagine pages)

**Important:** TUI Launcher and Cockpit deliberately **do not** fire spend commands (`run` / `submit` / `record` / live wizard spend). Use CLI or Streamlit Imagine for generation.

### 4. Gate

Hard-quality checks before and after generation:

| Gate | Soft default | Strict enforcement |
|------|--------------|--------------------|
| Handoff packet | warn | `--strict-handoff` · `handoff validate` |
| Plate lock | warn | `--strict-plate` |
| Motion brief | warn | `--strict-motion` |
| Identity | warn | `--strict-identity` |
| Wave A packets | optional | `--strict-wave-a` |
| Chain QA | No-Go blocks extend | Re-QA after fix |

```bash
cinematic-studio handoff validate path/to/packet.json
cinematic-studio handoff validate path/to/packet.json --strict-handoff --strict-wave-a
cinematic-studio sequence qa
```

On **No-Go**: fix evidence (identity drift, seam, AMV, temperature) → re-run QA → only then extend.

### 5. Converge & Deliver

| Checklist | Purpose |
|-----------|---------|
| **Convergence** | Agent-mode handoff readiness (specialists aligned) |
| **Parallel Briefs** | `cinematic-studio wave-a briefs` / dispatcher logs |
| **Delivery** | Polish + deliver readiness rollup |
| **Bridge preview** | `cinematic-studio imagine bridge` or Web Tools → paste to grok.com/imagine |

TUI Cockpit polish / deliver actions are **dry-run only** — safe scaffolding before real post commands.

---

## Wave A in the control plane

Wave A specialists feed **produce + gate** packets:

| Packet builder | Craft |
|----------------|-------|
| `wave-a plate-motion` | Plate / motion readiness |
| `wave-a contact` | Contact / micro-physics |
| `wave-a hmu` | Hair & makeup continuity |
| `wave-a dialogue` | Dialogue / ADR |
| `wave-a score` | Score / temp music |
| `wave-a title` | Titles / motion graphics |
| `wave-a crop` | Distribution / crop strategy |
| `wave-a briefs` | Parallel brief discovery |
| `wave-a validate` | Completeness check |
| `wave-a attach` | Attach packets to Imagine handoff |

Use `--strict-wave-a` on `sfw run`, `nsfw run`, and `imagine agent-handoff` when completeness is required for delivery.

---

## Unreleased (next) — TUI palette

Documented in [CHANGELOG.md](../../CHANGELOG.md) under **[Unreleased]**; not yet part of a numbered studio release:

| Feature | Behavior |
|---------|----------|
| **Command palette** | `/` or **Ctrl+P** — allowlisted action search |
| **KPI bar** | Under status strip |
| **Save orient brief** | `y` → `artifacts/tui_orient_brief.txt` |
| **Non-TTY fallback** | `cinematic-studio ui --print` (and bare `ui` without a TTY) prints orient dashboard |

When these ship in a version bump, activation phrase and `VERSION` will move together.

---

## Suggested daily ritual

1. `cinematic-studio ui` (or Dashboard) — Orient  
2. `d` / `v` / `s` / `m` — Health  
3. Produce Bible/DNA/sequence only when Attention is clear  
4. `handoff validate` + plate/motion before video  
5. Generate → Chain QA → Color → Polish → Deliver  
6. Log spend: `cinematic-studio generation summary`

---

## Related docs

| Document | Role |
|----------|------|
| [USER_GUIDE.md](USER_GUIDE.md) | Full creator workflow |
| [Quick_Start_Guide.md](Quick_Start_Guide.md) | Fast onboarding + operator loop summary |
| [OFFICIAL_DOCUMENTATION.md](../OFFICIAL_DOCUMENTATION.md) | Canonical product manual |
| [CLI_REFERENCE.md](../CLI_REFERENCE.md) | Commands + TUI keys |
| [ARCHITECTURE.md](../ARCHITECTURE.md) | Layered system design |

---

*Grok Imagine Cinematic Studio v3.9.0 — Operator Control Plane · Independent community project · Not affiliated with xAI*
