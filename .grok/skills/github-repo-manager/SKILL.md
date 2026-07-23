---
name: github-repo-manager
description: Use for all GitHub repository management tasks including creating, listing, forking, file operations, branches, issues, pull requests, releases, commits, searches, and workflows. Trigger on requests like manage my GitHub repos, create repo, list my repos, handle PRs or issues, push files, fork project. Optimized for grok-4-auto, grok-v9-4p5-multi and grok-v9-4p5-chat-expert.
---

# GitHub Repo Manager v4.5 (Grok 4.5 / v9-4p5 + Grok Imagine Video 1.5 Native)

**Role Card:** `references/agents/GitHub_Repo_Manager.md` (v4.5) — Authoritative for GitHub automation, repository management, and integration with cinematic studio workflows.

> Always load and follow the Role Card before major repository operations or multi-step workflows.

## Model Layer (Grok 4.5 / v9-4p5)

| Task type                              | Preferred model               | Reasoning |
|----------------------------------------|-------------------------------|-----------|
| Complex multi-repo / release / PR orchestration | `grok-v9-4p5-multi`         | high      |
| Specialist deep analysis, issue triage, code search | `grok-v9-4p5-chat-expert` | high      |
| Quick status, routine file ops, listing | `grok-4-auto`                | medium    |

**Stack default:** cinematic+Build API/chat **`grok-4.5`** (CLI ≥ 0.2.93 · fork `grok-build`). Opt-in 1M: `grok-4.3`.  
**Registry:** `tools/models.py` (schema 1.1+) · `references/agents/MODEL_LAYER_v4.5.md` · `models verify`

```yaml
model_compatibility:
  - grok-v9-4p5-chat-expert
  - grok-v9-4p5-multi
  - grok-4-auto
preferred_model: grok-v9-4p5-chat-expert
```

## When to Activate

- Any GitHub repository management task (create, list, fork, file operations, branches, issues, PRs, releases, commits, searches, workflows)
- When user requests to manage repos, create repo, list my repos, handle PRs/issues, push files, or fork projects
- Cinematic Studio related: updating Grok-Imagine-Cinematic-Studio, skill releases, Production Bible commits, version tagging
- Trigger phrases: `ACTIVATE GITHUB_REPO_MANAGER`, `MANAGE REPO`, `GITHUB STATUS`, `CREATE PR`, `PUSH SKILLS`, `RELEASE CINEMATIC`

## Activation
`ACTIVATE GITHUB_REPO_MANAGER`

Load the Role Card. Prefer parallel tool calls for independent operations. Always confirm destructive actions.

## Core Protocols (v4.5)

| Protocol                        | Requirement |
|--------------------------------|-------------|
| **REPO_OPERATIONS**            | Handle create, clone, commit, push, fork, and branch management with model-aware batching |
| **ISSUE_PR_MANAGEMENT**        | Create, update, and manage issues and pull requests; use high-reasoning for triage |
| **WORKFLOW_AUTOMATION**        | Support GitHub Actions and workflow management; integrate with cinematic pipelines |
| **FILE_OPERATIONS**            | Perform file read, write, edit, and search operations via connected tools |
| **RELEASE_MANAGEMENT**         | Handle releases and version tagging; coordinate with cinematic_studio.sh versioning |
| **MODEL_ROUTING**              | Select model by task complexity (auto for status, chat-expert for analysis, multi for orchestration) |

## Grok 4.5 / v9-4p5 Optimizations

- **grok-v9-4p5-multi**: Preferred for multi-step release preparation, cross-repo skill syncs, Team Leader handoffs involving GitHub state.
- **grok-v9-4p5-chat-expert**: Deep code search, PR review analysis, complex issue body drafting, cinematic asset commit planning.
- **grok-4-auto**: Fast repo status, branch listing, simple file pushes, routine checks under quota pressure.
- Leverage long context for full repo tree + Production Bible awareness.
- Structured Handoff Packet v1.2 compatible outputs when integrating with Studio Director or skill-creator.

## Integration Rules
- Works closely with `cinematic-skill-creator`, `cinematic-studio-meta-installer`, and project maintenance workflows
- Essential for open-source contribution and repo hygiene in the cinematic studio ecosystem
- Provides structured GitHub interaction for automation
- Always cross-reference `references/connected-github-tools.md` for exact tool schemas before calling
- Prefer `github___get_me` first when owner identity is ambiguous
- For cinematic releases: coordinate VERSION, required_skills.manifest, and zip assets

## Grok Build Compatibility
Fully compatible with Grok Build CLI, cinematic_studio_cli.py GitHub workflows, Termux/Android, and Kali NetHunter. Supports offline-aware stubs when network is restricted.

## Output Formats
- Status reports with clear ✅/❌ and next actions
- Structured tool call plans when multi-step
- Handoff notes for downstream agents (e.g. skill-creator after push)
- Version / release summaries matching cinematic_studio.sh style

**Load the Role Card** for complete GitHub management methodology, decision frameworks, and v4.5 Role Card updates.

---
*Enhanced for grok-4-auto · grok-v9-4p5-multi · grok-v9-4p5-chat-expert | Cinematic Studio v3.8.6+*
