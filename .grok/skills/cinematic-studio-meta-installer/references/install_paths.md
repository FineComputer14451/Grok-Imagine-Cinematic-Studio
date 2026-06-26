# Cinematic Studio Meta Installer — Paths Reference v3.6.5

## Canonical URLs

| Resource | URL |
|----------|-----|
| Meta installer script | `https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/cinematic_studio.sh` |
| Shared library | `https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/lib/cinematic_studio_common.sh` |
| Skill manifest | `https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/required_skills.manifest` |
| Meta-installer zip (bootstrap) | `grok-imagine-cinematic-studio-meta-installer-v3.6.5.zip` — skill + scripts only; run `./bootstrap.sh` or `scripts/cinematic_studio.sh install` |
| Full skills zip (latest) | `https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/latest/download/grok-imagine-cinematic-studio-skills-install-v3.6.5.zip` |
| Full skills zip (versioned) | `https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/download/v3.6.5/grok-imagine-cinematic-studio-skills-install-v3.6.5.zip` |
| Build meta-installer | `bash scripts/build_meta_installer.sh` |
| Build full suite | `bash scripts/build_release_bundle.sh` |

## Default Install Paths

| Variable | Default | Purpose |
|----------|---------|---------|
| `SKILLS_DIR` | `~/.grok/skills` | Grok skill discovery |
| `PROJECT_DIR` | `~/Grok-Cinematic-Projects` | References, CLI tools, config, installer scripts |
| `CINEMATIC_RAW_BASE` | GitHub `main` raw | Fallback downloads |
| `CINEMATIC_RELEASE_BASE` | GitHub `releases/latest/download` | Release zip primary URL |

## PROJECT_DIR Layout After Install

```
~/Grok-Cinematic-Projects/
├── references/          # Role Cards, MODELS_v3.6.md, protocols
├── tools/               # cinematic_studio_cli.py + pipeline modules
├── tools/cli/           # models, bible, studio command modules
├── config/              # grok-build.example.toml
├── scripts/             # cinematic_studio.sh + lib (for local verify)
├── requirements.txt     # CLI dependencies
├── AGENTS.md
└── MASTER_PROMPT_v3.6.md
```

## Grok Build Config (Optional)

```bash
cp ~/Grok-Cinematic-Projects/config/grok-build.example.toml ~/.grok/config.toml
```

Sets `fork_secondary_model = "grok-build"` for code and skills work alongside `grok-composer-2.5-fast`.

## Verify Tiers

- **core** — 7 manifest skills marked `# core` plus `models verify`
- **all** — full 30 skills from `required_skills.manifest`