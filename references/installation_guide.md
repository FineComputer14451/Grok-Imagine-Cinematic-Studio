# Grok Imagine Cinematic Studio v3.6.4 — Installation Guide

This guide covers all methods to install the **Grok Imagine Cinematic Studio v3.6.4 "Odyssey Native"**.

## Recommended Method: Meta-Skill Installer (Easiest)

1. Go to **grok.com/skills**
2. Click **New Skill** → **Upload skill file**
3. Upload the meta-skill (when available in releases) or use the one-command script below.

### One-Command Installation (Recommended)

```bash
bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/install_cinematic_studio.sh)
```

This script will:
- Download the latest bundle
- Install all skills into `~/.grok/skills/`
- Set up references and prompts in `~/Grok-Cinematic-Projects/`

After running the script:
1. Refresh the Skills page in Grok
2. Start a **new chat**
3. Type: `Activate Grok Imagine Cinematic Studio v3.6.4`

---

## Manual Installation (Advanced Users)

If you prefer manual control:

### Step 1: Download the Bundle
Download the latest release:
`grok-imagine-cinematic-studio-skills-install-v3.6.4.zip`

### Step 2: Extract the Zip

### Step 3: Install Skills
Copy all folders from the extracted `.grok/skills/` directory into:
```bash
~/.grok/skills/
```

### Step 4: Install Supporting Files (Recommended)
Copy these into your project folder (e.g. `~/Grok-Cinematic-Projects/`):
- `references/agents/` → `~/Grok-Cinematic-Projects/references/agents/`
- `AGENTS.md`
- `MASTER_PROMPT_v3.6.md`

### Step 5: Activate
In a new Grok chat, type:
```
Activate Grok Imagine Cinematic Studio v3.6.4
```

---

## Verification

After installation, you can verify everything is working by typing:

```
VERIFY INSTALLATION
```

Or manually check that these skills appear in your Skills list:
- `grok-imagine-cinematic-studio`
- `ai-video-upscaler`
- `cinematic-sequence-extender`
- `studio-director`
- `quality-assurance-guardian`
- And others from the bundle

---

## Updating

To update to a newer version, simply re-run the installation script:

```bash
bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/install_cinematic_studio.sh)
```

It will overwrite existing files with the latest versions.

---

## Troubleshooting

### "Archive must contain SKILL.md at the root" error
→ You tried to upload the big bundle zip directly.  
**Solution:** Use the meta-skill or the one-command script instead.

### Skills not appearing after installation
1. Make sure you copied the folders **into** `~/.grok/skills/`, not as a subfolder.
2. Refresh the Skills page (or restart the Grok web app).
3. Try activating with the full name: `Activate Grok Imagine Cinematic Studio v3.6.4`

### Permission errors on Linux/macOS
Run the installer with `sudo` only if necessary, or manually set permissions:
```bash
chmod -R u+rw ~/.grok/skills/
```

### Want to start fresh?
Delete the cinematic skills and re-run the installer:
```bash
rm -rf ~/.grok/skills/ai-video-upscaler
rm -rf ~/.grok/skills/cinematic-sequence-extender
# ... remove others as needed
```

---

## File Locations

| Item                        | Default Location                              |
|----------------------------|-----------------------------------------------|
| All Skills                 | `~/.grok/skills/`                             |
| Role Cards                 | `~/Grok-Cinematic-Projects/references/agents/`|
| MASTER_PROMPT              | `~/Grok-Cinematic-Projects/MASTER_PROMPT_v3.6.md` |
| AGENTS.md                  | `~/Grok-Cinematic-Projects/AGENTS.md`         |
| Installation Script        | `scripts/install_cinematic_studio.sh`         |

---

For questions or issues, open an issue on the GitHub repository or reply in the r/grok announcement post.

**Maintained by u/Fine_Computer_4451** — June 2026

