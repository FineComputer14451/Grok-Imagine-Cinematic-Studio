# Repository Layout — v3.7.1 · Grok 4.5

Canonical map of the Grok Imagine Cinematic Studio monorepo. Runtime paths used by the CLI are fixed in `tools/studio_paths.py`.

## Root (keep lean)

| Entry | Role |
|-------|------|
| `README.md` | Project overview |
| `AGENTS.md` | AI agent instructions (canonical) |
| `CHANGELOG.md` | Version history |
| `MASTER_PROMPT.md` | Chat activation prompt (Grok 4.5) |
| `VERSION` · `LICENSE` | Release identity |
| `CONTRIBUTING.md` · `CODE_OF_CONDUCT.md` · `CONTRIBUTORS.md` | Community |
| `requirements*.txt` | Python deps |
| `MASTER_PROMPT.md` etc. | **Stubs** → new paths (back-compat) |

## First-class packages

```
.grok/skills/          # 48 studio skills (agent-only SKILL.md)
.grok-plugin/          # marketplace.json, plugin.json, plugin-index.json
commands/              # Slash commands for Grok Build plugin
tools/                 # CLI + libraries (models.py is stack registry)
tools/cli/             # Click command modules
web_ui/                # Streamlit dashboard
scripts/               # install / verify / catalog pin shims
tests/                 # pytest
config/                # grok-build.example.toml
assets/                # banner, logos
examples/              # sample bibles / pitch docs
references/            # MODELS, Role Cards, shared lexicon
docs/                  # human documentation (this tree)
```

## Runtime / project state (CLI)

Do **not** move these without updating `tools/studio_paths.py`:

| Path | Purpose |
|------|---------|
| `characters/` | DNA profiles (gitignored contents) |
| `sequences/` | Sequence blueprints |
| `sfw_batches/` · `nsfw_batches/` | Batch plans |
| `artifacts/` | Generated media & delivery (gitignored) |
| `.cinematic_project_state.json` | Local studio state (gitignored) |

## Documentation tree

```
docs/
├── README.md
├── REPOSITORY_LAYOUT.md
├── guides/           # Quick Start, Upgrade, Installation
├── templates/        # Bible, kink library
├── releases/         # RELEASE_NOTES_v3.7.1.md
├── archive/          # superseded (e.g. MODEL_LAYER_v3.6.7)
└── development/      # internal plans/specs
```

## Models & agents

| File | Notes |
|------|--------|
| `tools/models.py` | Code registry |
| `references/MODELS.md` | Human model guide (alias) |
| `references/MODELS_v3.6.md` | Same guide (historical filename; still valid) |
| `references/agents/MODEL_LAYER_v3.7.1.md` | Embeddable stack for skills/Role Cards |
| `references/agents/*.md` | Role Cards |
| `references/SKILLS_TAXONOMY.md` | Skill groups + dual-install declutter rules |

## What not to put in root

- Long guides / templates / release notes → `docs/`
- Role Cards → `references/agents/`
- Skill bodies → `.grok/skills/`
- Session DNA / sequences / batches → runtime dirs above
- Build zips → regenerate via `scripts/build_*.sh` (gitignored)

*Updated for Grok 4.5 · studio v3.7.1 — July 2026*
