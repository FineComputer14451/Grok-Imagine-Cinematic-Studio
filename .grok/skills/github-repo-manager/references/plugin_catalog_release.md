# Plugin Catalog Release Protocol (v3.7.1)

For **Grok Imagine Cinematic Studio** marketplace installs.

## Why two commits

The marketplace `sha` is the **content revision** users install. A pin commit cannot contain its own hash, so the tip after pin is often catalog-only. That is expected.

## Steps

1. **Finish content** — skills, tools, docs, `required_skills.manifest`, VERSION as needed  
2. **Commit content** (everything except unfinished pin):
   ```bash
   git add <content paths>
   git commit -m "feat(…): …"
   ```
3. **Generate if needed** (usually part of pin tooling):
   ```bash
   python3 scripts/generate_plugin_index.py
   ```
4. **Pin** HEAD as install SHA:
   ```bash
   bash scripts/release_plugin_catalog.sh
   # or: python tools/cinematic_studio_cli.py plugin catalog pin
   ```
5. **Commit only catalog**:
   ```bash
   git add .grok-plugin/marketplace.json .grok-plugin/plugin-index.json .grok-plugin/plugin.json
   git commit -m "chore(plugins): pin marketplace catalog to content SHA"
   ```
6. **Release gate**:
   ```bash
   bash scripts/verify_plugins.sh --release
   # or: python tools/cinematic_studio_cli.py plugin catalog check --release
   ```

## Allowed paths after pin (no re-pin)

Only:

- `.grok-plugin/marketplace.json`
- `.grok-plugin/plugin-index.json`
- `.grok-plugin/plugin.json`

Any skill/code/doc change after pin → **re-pin**.

## Parity checklist

| Source | Must match |
|--------|------------|
| `.grok/skills/*/SKILL.md` dirs | Count & names |
| `scripts/required_skills.manifest` | Same names |
| `.grok-plugin/plugin.json` `skills[]` | Same paths |
| `.grok-plugin/plugin-index.json` | Same skill names |
| Marketplace description skill count | Human docs (AGENTS, README, install guide) |

## User install

```bash
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust
grok plugin update grok-imagine-cinematic-studio
```

Orchestration default remains **`grok-4.6`** (not `grok-4.3`; `grok-4.5` aliases wrap 4.6).
