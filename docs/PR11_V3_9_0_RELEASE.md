# PR11 — Studio v3.9.0 multi-surface release

## Summary

Bumps product version **3.8.9 → 3.9.0** for the multi-surface control plane:

- `studio_core` (dashboard · ActionSpec · execute)
- Streamlit · NiceGUI · TUI · FastAPI
- Compatibility / handoff protocol pin via `STUDIO_COMPATIBILITY_VERSION`

## Verify

```bash
cat VERSION   # 3.9.0
cinematic-studio status
pytest tests/test_control_plane_contract.py tests/test_tui_widgets.py tests/test_wave_a_packets.py -q
python scripts/smoke_studio_surfaces.py
```
