# Cinematic Studio — Plugin Marketplace (web)

Browser catalog for **Grok Imagine Cinematic Studio** plugins: full suite + modular packs
(Core, Camera & Image, Sequence & Narrative, Delivery & Post, NSFW).

Built with Grok Build · independent community project · not affiliated with xAI.

## What this is

| Surface | Behavior |
|---------|----------|
| **Packs** | Browse installable marketplace plugins with CLI copy |
| **Skills** | Exclusive skill browser (64 skills) with pack + text filters |
| **Graph** | Full suite vs modular dependency map (`full_suite_wins`) |
| **Sync** | Live merge from `.grok-plugin/marketplace.json` on GitHub `main` |

**Real installs** use the Grok CLI on your machine. Buttons in this UI only store
local demo library state in the browser (localStorage).

```bash
grok plugin update grok-imagine-cinematic-studio
# or fresh:
grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust
```

## Stack

| Layer | Library |
|-------|---------|
| UI | React 19 + Tailwind CSS v4 |
| App | TanStack Start / Router |
| State | Zustand (library + live catalog) |
| Icons | Lucide |

## Develop

```bash
cd web_marketplace
npm install
npm run dev
# → http://127.0.0.1:8080
```

```bash
npm run typecheck
npm run build
```

Catalog source of truth for skill lists / pins remains the monorepo:

- [`.grok-plugin/marketplace.json`](../.grok-plugin/marketplace.json)
- [`.grok-plugin/plugin.json`](../.grok-plugin/plugin.json)
- [`config/plugin_packs.yaml`](../config/plugin_packs.yaml)

Bundled fallback: [`src/data/catalog.json`](./src/data/catalog.json) (v3.11.2 · 64 skills).

## Deploy notes

- Production build uses Vercel/Nitro when `vite build` runs.
- Do not commit `node_modules/`, `.vercel/`, or local `.env*`.
- Optional auth (better-auth + PGLite) is included for sign-in demos; marketplace
  browsing works without it.

## Relationship to standalone repo

Previously developed as [cinematic-studio-plugin-marketplace](https://github.com/FineComputer14451/cinematic-studio-plugin-marketplace).
This monorepo path is the canonical home going forward.
