# Image-to-Video Decision Tree

Run before every NSFW generation to avoid wasted video credits.

---

## Decision Flow

```
START
  │
  ├─ Quota risk HIGH/CRITICAL and tier ∉ {hero, consistency_anchor}?
  │    YES → image_prompt (explore cheaply)
  │
  ├─ tier == consistency_anchor AND no reference?
  │    YES → image_prompt (lock identity first)
  │
  ├─ has_reference AND motion ∈ {medium, high}?
  │    YES → image_to_video
  │
  ├─ tier ∈ {hero, key_explicit} AND has_reference?
  │    YES → image_to_video
  │
  ├─ motion == low AND explicit ∈ {suggestive, moderate}?
  │    YES → image_prompt (still is sufficient)
  │
  ├─ motion == high AND no reference?
  │    YES → image_prompt → then i2v on QA pass
  │
  ├─ duration ≥ 10s AND consistency_required AND has_reference?
  │    YES → image_to_video (extend from still)
  │
  ├─ tier == filler?
  │    YES → image_prompt (unless budget surplus)
  │
  └─ DEFAULT → video_prompt (atmospheric, no identity lock needed)
```

---

## Mode Definitions

| Mode | Cost Profile | When |
|------|--------------|------|
| `image_prompt` | ~2–5 credits | Exploration, anchors, quota pressure |
| `image_to_video` | ~82–92 credits (10s) | Locked identity + motion |
| `video_prompt` | ~80–92 credits (10s) | No ref needed, atmospheric motion |

---

## Follow-Up Actions

- **image_prompt + motion medium/high** → On QA ≥7, promote to i2v using still as ref
- **video_prompt + consistency_required** → Generate anchor first if drift detected
- **image_to_video fail** → Retry with simplified motion, not new video_prompt

---

## CLI

```bash
python tools/cinematic_studio_cli.py nsfw decide SHOT_ID --tier hero --motion high --has-ref
```