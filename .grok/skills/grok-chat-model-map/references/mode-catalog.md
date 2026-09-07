# Grok Chat mode catalog

Source: live grok.com Chat picker **2026-09-06** + https://docs.x.ai/developers/models + https://docs.x.ai/developers/grok-4-6

## Chat UI modes (canonical)

| Mode | Kind | Typical use | Notes |
|------|------|-------------|-------|
| `Auto` | Router | Default | Not an API model string |
| `Fast` | Latency | Short / simple | API id not exposed in UI |
| `Expert` | Deep reasoning | Hard tasks | Best Chat match for **Grok 4.6** generation |
| `Heavy` | Multi-agent | Max depth | Separate Heavy path |
| `Build` | Build Mode | Shareable apps in chat | Opens Build Mode → `*.grok.me` — **not** CLI `grok` |

### Aliases (spoken → mode)

```
default, router, automatic     → Auto
quick, speed, light, low-latency → Fast
deep, think, reasoning, smart  → Expert
max, multi-agent, team         → Heavy
prototype, website, app, game, grok.me → Build (Build Mode)
code, coding, agent, cli, tui, repo     → Terminal Grok Build (`grok`) — not Chat Build
```

Do **not** invent extra picker tiles (no “Grok 4.6” depth mode in verified snapshot).

## API / developer ids (not the Chat dropdown)

| API id | Role vs Chat |
|--------|----------------|
| `grok-4.6` | Recommended Chat + Code on API; Expert/Auto sit on this generation |
| `grok-4.5` | Prior flagship |
| `grok-4.3` | Long-context / alternate |
| `grok-4.20-0309-reasoning` | Reasoning variant |
| `grok-4.20-0309-non-reasoning` | Non-reasoning / faster analogue |
| `grok-4.20-multi-agent-0309` | Multi-agent analogue (Heavy-adjacent family) |
| `grok-build-0.1` | Build/coding agent model — not a Chat depth mode |

### Forbidden as API `model`

```
Auto, Fast, Expert, Heavy, Build
auto, fast, expert, heavy, build
```

## grok.com UI mapping

| Control | Meaning |
|---------|---------|
| Chat picker → Auto/Fast/Expert/Heavy | Chat reasoning / routing modes |
| Chat picker → Build | **Build Mode** (in-chat create/publish) — not Termux CLI |
| Sidebar → Imagine | Image/video models (see imagine-model-overrides) |

## Cross-skill

| Need | Skill |
|------|-------|
| Chat mode pick | **grok-chat-model-map** (this) |
| Imagine Quality/Fast · Video 1.0/1.5 | `imagine-model-overrides` |
| Studio ROLE_DEFAULTS | Cinematic Studio `tools/models.py` |


## Build Mode vs Grok Build CLI

| | Chat picker **Build** | Terminal **Grok Build** (`grok`) |
|--|----------------------|----------------------------------|
| Product | Build Mode ([news](https://x.ai/news/grok-build-mode)) | Coding agent CLI |
| Where | grok.com / iOS / Android | Local machine / Termux |
| Output | Preview + `*.grok.me` | Repo edits / shell / agents |

API id `grok-build-0.1` is a **model id**, not the Chat Build tile.
