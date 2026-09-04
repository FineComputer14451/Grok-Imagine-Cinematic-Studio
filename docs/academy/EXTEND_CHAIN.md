# Extend chain playbook

Plan multi-clip **Extend-from-Frame** sequences before spending video seconds.

Interactive tool: Studio Academy **`/extend`** (Extend Lab).

## When to use

- You already have a locked Character DNA and DoP card
- At least one **plate is locked** (or you accept a stills-only montage)
- You want 2–6 short clips (typically 4–8s) with continuity

## Rules (blockers)

1. **Plate lock** before hero i2v / 6s spend on clip_01  
2. **One primary move** per clip (push **or** track **or** static)  
3. **LAST_FRAME_RECAP + motion_out** at every clip boundary  
4. **DNA inject** on every still/video packet  
5. **Chain QA Go** before stitch — identity No-Go = repair only  

## Recommended spine

| Step | Tool | Output |
|------|------|--------|
| 1 | Shot list / Extend Lab | Ordered clips + durations |
| 2 | Prompt lab + DNA | Locked plates |
| 3 | Recap builder | Per-boundary handoffs |
| 4 | Sequence / Continuity agents | Clip N+1 packets |
| 5 | Consistency / QA | Chain Go |
| 6 | Editing + Sound | Teaser spine |
| 7 | Delivery checklist | Ship gate |

## Packet shape

Copy from Extend Lab:

- Project + character_id  
- Clip table (framing, action, move, motion_in/out, plate_status)  
- Activation block (Sequence Director · Multi-Clip Continuity · Handoff · QA · Identity Lock)  

## Budget tips

- Prefer **stills montage + one hero 6s** before long motion chains  
- Count total seconds before generate  
- Short chains (2–4 clips) for first teasers  

## Related Academy pages

- `/extend` — chain planner  
- `/recap` — last-frame recap  
- `/consistency` — algorithms  
- `/delivery` — final checklist  
- `/movement` — one-move grammar  

Stills-first · SFW educational path · Studio v3.11.4 · independent of xAI credentials (not affiliated with xAI/SpaceXAI).
