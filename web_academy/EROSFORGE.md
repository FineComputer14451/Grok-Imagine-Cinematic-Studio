# ErosForge module (Academy v3.11.4)

Opt-in educational module for the NSFW production pack.

## Status

Core integration is landing on `main` via sequential commits:

- Progress store + README + shell nav
- Search index Packs group
- Data module `src/data/erosforge.ts`
- Route page `src/routes/erosforge.tsx`
- Craft / home / glossary / studio / routeTree updates

## Local path

```bash
cd web_academy
npm install
npm run dev
# open /erosforge
```

Policy: fictional adults only · strict opt-in · workflow education only (no media generation in Academy).

## AUP / SFW default (v3.11+)

Studio stays **SFW by default**. Intimate / NSFW Academy paths require:

1. Optional NSFW add-on (`.grok-plugin/nsfw-plugin.json` / marketplace NSFW pack)
2. Local four-flag attestation: `nsfw attest --i-am-18 --imaginary-adults --not-a-real-person --acknowledge-aup`
3. Fail-closed gates (no silent routing; Imagine 403/429 do not hop regions)

Policy: https://x.ai/legal/acceptable-use-policy

This Academy module is educational only — not affiliated with xAI or SpaceXAI.
