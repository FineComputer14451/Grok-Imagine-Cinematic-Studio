# Grok Imagine Cinematic Studio - Repository Structure

**Draft v1.0** | Proposed structure for v3.5 maturity and v4.0 scalability  
**Date**: June 02, 2026  
**Author**: Grok (drafted for FineComputer14451 / u/Fine_Computer_4451)

---

## Purpose of This Document

This document provides a **clean, professional, and scalable folder structure** for the Grok Imagine Cinematic Studio repository.

The current repository (as of early June 2026) has grown organically with 124+ commits and now includes a full 22-agent cinematic production system, CLI toolkit, Streamlit Web UI, multiple master prompts, production bible examples, kink/NSFW template library, and active development of v3.5 features.

While the project is already impressive and functional, the flat layout in `agents/` and the accumulation of many versioned Markdown files at the root are starting to create maintenance friction. This draft proposes an improved layout that:
- Separates concerns clearly (prompts vs. agents vs. tools vs. documentation)
- Scales gracefully to 30+ agents and multiple personality versions (v3.x / v4.0+)
- Follows modern open-source best practices
- Makes it easier to maintain character consistency, add new agents, and support both SFW and NSFW/ErosForge workflows
- Prepares the project for potential PyPI packaging or deeper CLI/SDK integration

---

## Current Structure Snapshot (June 2026)

```
grok-imagine-cinematic-studio/
├── .github/workflows/
├── .grok/skills/
├── agents/                          # ~20+ flat *.txt files (mixed v3.3–v3.5, some filename issues)
├── assets/
├── examples/
├── tools/                           # cinematic_studio_cli.py
├── web_ui/                          # Streamlit app
├── AGENTS.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── CONTRIBUTORS.md
├── Example_Production_Bible_Example.md
├── Kink_Specific_Cinematic_Template_Library_v3.3.md
├── LICENSE
├── MASTER_PROMPT_v3.4.md
├── MASTER_PROMPT_v3.5.md
├── Project_Bible_Template.md
├── Quick_Start_Guide.md
├── README.md
├── RELEASE_NOTES_v3.5.md
├── UPGRADE_GUIDE.md
├── requirements-streamlit.txt
├── requirements.txt
└── (other root files)
```

**Observed pain points**:
- `agents/` is becoming unwieldy (flat list of 20+ files, inconsistent naming/versions, some typos like "v3..")
- Too many important `.md` files polluting the repository root
- No dedicated `prompts/` or `templates/` separation
- Lacks `tests/`, `docs/`, `scripts/`, and modern Python packaging (`pyproject.toml`)
- Documentation and production artifacts are not first-class citizens

---

## Proposed Improved Structure

``` 
grok-imagine-cinematic-studio/
├── .github/
│   ├── workflows/                   # CI/CD, automated releases, docs publishing
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
├── .grok/
│   └── skills/                      # Local Grok skill mirrors or activation references (optional)
├── agents/                          # Reorganized by real film production departments
│   ├── core/
│   ├── visual_camera/
│   ├── story_performance/
│   ├── technical_continuity/
│   ├── audio/
│   ├── action_vfx/
│   ├── marketing/
│   └── nsfw/
├── prompts/
│   ├── master/
│   ├── templates/
│   └── system/
├── production_bibles/
│   ├── examples/
│   └── templates/
├── examples/
│   ├── stories/
│   └── productions/
├── tools/
│   ├── cli/
│   └── utils/
├── web_ui/
│   ├── app.py
│   ├── components/
│   ├── pages/
│   └── static/
├── docs/
│   ├── guides/
│   ├── architecture/
│   └── reference/
├── tests/
│   ├── test_agents/
│   ├── test_prompts/
│   ├── test_cli/
├── scripts/
├── assets/
├── data/
├── notebooks/
├── .github/
├── .grok/
├── .gitignore
├── .gitattributes
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── requirements-streamlit.txt
├── Makefile
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── CHANGELOG.md
├── RELEASE_NOTES_v3.5.md
├── SECURITY.md
└── CITATION.cff
```

---

## Detailed Rationale & Benefits

### 1. `agents/` — Reorganized by Production Department
**Problem**: Flat list of 20+ files is already difficult to navigate and will become unsustainable with v4.0 personalities and new agents.

**Solution**: Mirror real film crew hierarchy.
- Each agent gets its own folder containing:
  - `system_prompt.txt`
  - Versioned personality files (`personality_v3.5.md`, `personality_v4.0.md`)
  - `activation_commands.md`
  - `examples/` (few-shot prompts or test cases)
  - `CHANGELOG.md` (per-agent evolution history)

This makes personality updates, diffs, and selective loading by the orchestrator trivial.

### 2. `prompts/` — New First-Class Citizen
Centralizes everything prompt-related:
- `master/` → Canonical `MASTER_PROMPT_vX.Y.md` files + activation tables
- `templates/` → Small, composable, reusable blocks (lighting, continuity, NSFW rails, etc.)
- `system/` → Foundational rules that change infrequently

This dramatically reduces root clutter and improves prompt maintainability and reuse.

### 3. `production_bibles/` & `docs/`
Gives production artifacts and documentation proper homes.
- `docs/` keeps the growing body of guides, architecture, and reference material out of the root so `README.md` stays clean and welcoming.
- Future: Can publish `docs/` via GitHub Pages or MkDocs with minimal effort.

### 4. NSFW / ErosForge Isolation
Keeping `nsfw/erosforge_nsfw_director/` under `agents/` makes it easy to maintain, version, and (if desired) toggle or license separately while still fully integrating with the rest of the studio.

### 5. Professional Open-Source Hygiene
- `tests/`, `scripts/`, `pyproject.toml`, improved `.github/` templates, `SECURITY.md`
- Prepares the project for packaging (`pip install ...`) and broader adoption
- `scripts/generate_agent_index.py` can auto-generate the agent table in `docs/guides/AGENTS.md` from the folder structure — huge maintenance win

### 6. Future-Proofing
Adding Agent #23, a new v4.1 personality variant, or a new marketing specialist becomes a simple, predictable folder creation + file population task.

---

## Suggested High-Priority New Files

1. `docs/REPOSITORY_STRUCTURE.md` — This document (self-hosting the plan)
2. `docs/architecture/SYSTEM_ARCHITECTURE.md` — Detailed 22-agent orchestration, memory passing between agents, Studio Director + Mega Production Architect flow, and continuity mechanisms
3. `pyproject.toml` — Modern packaging metadata, dependencies, and CLI entrypoint (`cinematic-studio` command)
4. `.github/ISSUE_TEMPLATE/agent_contribution.md` — Standardized template for community contributions of new agents or personality updates
5. `scripts/generate_agent_index.py` — Script that walks the `agents/` tree and auto-updates documentation tables
6. `SECURITY.md` — Responsible disclosure and notes on moderation/NSFW handling (even if primarily prompt-based)

---

## Migration Strategy (Non-Breaking)

**Phase 1** (Immediate): Add new folders in parallel + this structure document. No deletions.

**Phase 2**: Move long documentation files into `docs/guides/`. Update internal links.

**Phase 3**: Refactor `agents/` into category + per-agent folders using `git mv`. Existing CLI/UI paths preserved via thin compatibility shims or deprecation warnings.

**Phase 4**: Extract modular prompt blocks into `prompts/templates/`.

**Phase 5** (Optional): Add `pyproject.toml` and optional packaging support.

This approach ensures zero breaking changes for existing users of the CLI, Web UI, or direct prompt usage.

---

## Alignment with Local Cinematic Studio Skill

This structure directly supports the local `/home/workdir/.grok/skills/grok-imagine-cinematic-studio` activation system (22 agents, v3.5 / v4.0 personalities, ErosForge NSFW Director, full production bible workflows). The folder organization makes it trivial to keep the GitHub repo and the local skill activation prompt in sync.

---

## Next Steps & Call for Feedback

1. Review this draft (open a GitHub issue or comment directly on the file once added).
2. Decide whether to land this in `main` for v3.5 finalization or create a `v4-restructure` branch.
3. Prioritize Phase 1 (add `docs/` + this file + a couple of high-value new documents).
4. Iterate on categories, file naming conventions, or packaging approach based on maintainer + community input.

---

**This structure draft is ready for discussion, refinement, and implementation.** It is designed to keep the Grok Imagine Cinematic Studio the most advanced, consistent, and enjoyable multi-agent cinematic production system available for Grok.

*Maintained with care for the continued excellence of the project and the broader Grok Imagine ecosystem.*

---

**End of Draft v1.0**