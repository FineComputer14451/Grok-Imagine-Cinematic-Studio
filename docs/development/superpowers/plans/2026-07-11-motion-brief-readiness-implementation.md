# Motion Brief Readiness Implementation Plan

**Goal:** Structured `motion_vector` {action, camera, emotion} before video spend; free-text soft fallback; `--strict-motion` / `--strict-handoff` require triple.

**Design:** [../specs/2026-07-11-motion-brief-readiness-design.md](../specs/2026-07-11-motion-brief-readiness-design.md)

## Status: implemented 2026-07-11

- [x] `tools/motion_readiness.py` + tests  
- [x] Handoff GHR-03 via helper; `strict_motion` on evaluate + CLI  
- [x] Stamp motion fields from shot → packet  
- [x] `sfw motion set/show`; `--strict-motion` SFW/NSFW run/session  
- [x] Agent/skill notes + CHANGELOG  

---

*Motion brief readiness plan — 2026-07-11*
