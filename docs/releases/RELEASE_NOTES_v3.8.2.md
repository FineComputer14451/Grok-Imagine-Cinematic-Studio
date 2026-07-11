# Release Notes — v3.8.2

**Date:** 2026-07-11  
**Theme:** Pipeline readiness gates + Streamlit Community Cloud

## Highlights

1. **Generation handoff readiness** — semantic checks before Imagine spend (`evaluate_imagine_handoff_readiness`); soft validator warnings; hard-fail with `imagine agent-handoff --strict-handoff` or `validate_handoff.py --strict-handoff`.
2. **Post-delivery pipeline readiness** — `evaluate_delivery_pipeline_readiness`; soft notes on polish/deliver; hard-fail with `--strict-delivery`.
3. **Streamlit Community Cloud** — deploy `web_ui/app.py` from GitHub; secrets for `XAI_API_KEY`; ephemeral-FS guidance.

## Install / update

```bash
# Plugin (Method B)
grok plugin update grok-imagine-cinematic-studio

# Meta installer (Method A)
bash scripts/cinematic_studio.sh update
```

## Verify

```bash
python tools/cinematic_studio_cli.py version
python tools/cinematic_studio_cli.py validate
bash scripts/verify_plugins.sh --release
```

## Activation

`Activate Grok Imagine Cinematic Studio v3.8.2`

## Streamlit Cloud

Main file: `web_ui/app.py` · Guide: `docs/guides/streamlit_cloud_deploy.md`

## Related

- Handoff readiness: `tools/handoff_readiness.py`
- Delivery readiness: `tools/delivery_readiness.py`
- Prior identity work: v3.8.1 release notes
