# Naming — reference plates

## Folders

```
<project>/
  characters/
  props/
  locations/
  board/          # optional contact sheet exports
```

## Files

| Kind | Pattern | Example |
|------|---------|---------|
| Character hero | `char_<slug>_hero_<view>` | `char_mara_hero_front` |
| Character variant | `char_<slug>_var_<tag>` | `char_mara_var_rain_coat` |
| Prop hero | `prop_<slug>_hero` | `prop_pulse_rifle_hero` |
| Prop detail | `prop_<slug>_detail_<tag>` | `prop_pulse_rifle_detail_grip` |
| Location establish | `loc_<slug>_establish` | `loc_neon_pier_establish` |
| Location coverage | `loc_<slug>_<angle>` | `loc_neon_pier_reverse` |

Use lowercase `snake_case` slugs. Keep a one-line `DNA.txt` or sidecar note next to each hero.
