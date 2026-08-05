# Studio Academy (web_academy)

Interactive educational companion for **Grok Imagine Cinematic Studio**.

Learn cinematography craft, studio agents, DNA/plates, editing, sound, packs, and delivery — with progress tracking and a graduate certificate path.

## Stack

| Layer | Library |
|-------|---------|
| UI | React 19 + Tailwind CSS v4 |
| Routing | TanStack Router / Start |
| State | Zustand (progress, quiz, graduate) |
| Icons | Lucide |

## Docs (markdown)

Static companion docs live in [`docs/academy/`](../docs/academy/):

- [Delivery checklist](../docs/academy/DELIVERY_CHECKLIST.md)
- [FAQ](../docs/academy/FAQ.md)

## Develop

```bash
cd web_academy
npm install
npm run dev
# → http://127.0.0.1:8080
```

```bash
npm run build
npm run typecheck
```

## Routes (highlights)

| Path | Topic |
|------|-------|
| `/` | Home dashboard + progress |
| `/learn` | Tiered curriculum |
| `/dna` · `/shots` · `/lab` | DNA, shot language, prompt lab |
| `/lenses` · `/movement` · `/color` · `/lighting` · `/composition` · `/aspect` | Cinematography track |
| `/editing` · `/sound` | Post craft |
| `/agents` · `/pack` · `/workflows` · `/pipeline` | Studio systems |
| `/quiz` · `/graduate` · `/recap` | Assessment + certificate |

## Notes

- Client-only progress (localStorage via Zustand persist).
- Independent community learning tool — not official xAI credentials.
- Sibling UIs: [`web_react/`](../web_react/) (cockpit SPA), [`web_nicegui/`](../web_nicegui/), [`web_ui/`](../web_ui/).

---

**Version**: 1.0.0 · Studio monorepo companion · August 2026
