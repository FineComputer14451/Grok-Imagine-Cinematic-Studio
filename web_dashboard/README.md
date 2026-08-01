# Grok Imagine Cinematic Studio — React Dashboard

Modern React control plane for **Grok Imagine Cinematic Studio v3.8.9**.

Parity with Streamlit `web_ui/` and TUI Home:

| View | Purpose |
|------|---------|
| Dashboard | Compact / Ops / Full density (TUI 1/2/3) |
| Production | Guided Production Bible |
| DNA & Memory | Identity lock + drift |
| Sequences | Chain QA · polish · delivery |
| Imagine | Prompt compose + handoff slate |
| Gallery / Queue | Plates & render farm |
| Quota | Soft caps, cascade, spend |
| Tools | Activation, specialists, health actions |

## Run

```bash
cd web_dashboard
npm install
npm run dev   # 0.0.0.0:8080
```

```bash
npm run build
npm run typecheck
```

Stack: React 19 · TanStack Start · Tailwind v4 · Recharts · Zustand.

> Independent community UI surface — not affiliated with xAI.
