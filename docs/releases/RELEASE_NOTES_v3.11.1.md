# Release Notes — v3.11.1

**Date:** 2026-09-02  
**Codename:** SpaceXAI AUP gates

## Highlights

Grok Imagine Cinematic Studio **v3.11.1** ships fail-closed **SpaceXAI Acceptable Use Policy** gates on Imagine spend, plus the CLI help information architecture that landed after 3.11.0.

| Area | Pin |
|------|-----|
| Studio / packaging | **3.11.1** |
| Cinematic / Build / CLI agent | `grok-4.6` (unchanged from 3.11.0) |
| Grok Build binary min | **1.0.5** |
| Imagine | Image 2.0 + Video 1.0 / 1.5 (no Video 2.0) |
| AUP | https://x.ai/legal/acceptable-use-policy |

Intimate work remains **18+**, **imaginary adults only**, **R-rated**, and requires `nsfw attest`.

## AUP fail-closed gates

- `tools/aup_gate.py` — attestation, CSAM stub refusals, R-rated cap, no real-person undress, hidden-camera NCII patterns
- `cinematic-studio nsfw attest` writes `.aup_attestation.json` (or `GROK_STUDIO_AUP_ATTESTATION`)
- Wired on Imagine client, DNA intimate path, NSFW batch/shot, Streamlit settings
- HTTP **403 / 429** do **not** hop Imagine regions

## Operator CLI

- Journey-grouped `--help` (Orient / Health / Produce / Spend / Gate / Deliver / Surfaces / Meta)
- `cinematic-studio commands [query]`
- SFW / NSFW / Wave A help panels
- Hidden ghost aliases print the real verbs and exit 2

## Installer

Curl/one-liner fallback without a local `VERSION` file is **3.11.1** (was incorrectly **3.10.0**).

## Upgrade

```bash
grok plugin update grok-imagine-cinematic-studio
# or
bash scripts/cinematic_studio.sh update

cinematic-studio doctor --quick
cinematic-studio nsfw attest   # required before NSFW spend
```

Activation: **`Activate Grok Imagine Cinematic Studio v3.11.1`**

## Compatibility

- `VERSION` / `STUDIO_COMPATIBILITY_VERSION`: **3.11.1**
- Handoff `PROTOCOL_OK` includes **3.11.1** (prior 3.7.1–3.11.0 packets still accepted)
- Builds on **v3.11.0** Grok 4.6 stack lock

## Assets

- `grok-imagine-cinematic-studio-skills-install-v3.11.1.zip`
- `grok-imagine-cinematic-studio-meta-installer-v3.11.1.zip`
