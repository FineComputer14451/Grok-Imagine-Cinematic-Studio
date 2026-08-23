"""Production brief, prompts, bible export, and live xAI API."""

from __future__ import annotations

import json

import streamlit as st

from lib import bible_wizard_ui
from lib import runtime as rt
from lib import session as sess


def _fallback_prompt(story: str) -> str:
    brief = sess.clip_story(story, 120)
    return (
        f"# Grok Imagine Cinematic Studio — ACTIVATED\n\n"
        f"**Project:** {brief}\n"
        f"**Genre:** {st.session_state.genre}\n"
        f"**Director:** {st.session_state.director}"
    )


def _fallback_bible(story: str) -> dict:
    return {
        "project_title": sess.clip_story(story, 80),
        "genre": st.session_state.genre,
        "director_signature": st.session_state.director,
        "target_duration_seconds": st.session_state.duration,
        "complexity": st.session_state.complexity,
        "status": "Ready for production",
    }


def _render_phase_outline(story: str) -> None:
    st.subheader("Production Phase Outline")
    st.caption("Planned agent workflow — not a live generation or QA run.")
    st.markdown(
        f"""
**Project:** {sess.clip_story(story, 80)}

**Genre:** {st.session_state.genre}  
**Director Signature:** {st.session_state.director}  
**Target Duration:** {st.session_state.duration}s  
**Complexity:** {st.session_state.complexity}
"""
    )
    st.markdown(
        """
**Phase 1 — Pre-Production (Grok 4.6)**
- Mega Production Architect → Production Bible + `model_stack` + `VIDEO_PIPELINE_SPEC`
- Character DNA → Identity Lock · Reference Curator (tiers)
- Optional Animatic Director (≤20% budget)

**Phase 2 — Core Production**
- Prompt Master + DoP + Performance → stills first, then I2V
- Sequence Director + Extender → long-form (1.0 cost default; 1.5 for native audio)
- Continuity + Chain QA / QA Guardian → go/no-go gates

**Phase 3 — Polish & Delivery**
- Assembly Editor → Color Grade → AI Polish Director (local upscale)
- Sonic/Foley when 1.5 or post mix · cinematic-ffmpeg for delivery crops
"""
    )

    dna_count = len(rt.list_characters()) if rt.DNA_AVAILABLE else 0
    seq_count = len(rt.list_sequences()) if rt.SEQ_AVAILABLE else 0
    locked_count = (
        len(rt.load_project_state().get("identity_lock", {})) if rt.DNA_AVAILABLE else 0
    )
    st.markdown("**Current project state**")
    state_col1, state_col2, state_col3 = st.columns(3)
    state_col1.metric("DNA Profiles", dna_count)
    state_col2.metric("Identity Locked", locked_count)
    state_col3.metric("Sequences", seq_count)

    snapshot = sess.session_quota_snapshot()
    if snapshot:
        est = snapshot["estimate"]
        risk = snapshot["risk"]
        st.caption(
            f"Est. cost: {est['credits_low']:.0f}–{est['credits_high']:.0f} credits "
            f"(${est['usd_low']}–${est['usd_high']}) · Risk: {risk['risk_level']}"
        )

    st.info("Run real generation via the xAI API button below or `tools/cinematic_studio_cli.py`.")


def render() -> None:
    st.header("📝 Production")
    st.caption(f"Activation phrase: `{rt.ACTIVATION_PHRASE}`")
    st.markdown(rt.stack_banner_markdown())

    story = st.text_area(
        "Describe your cinematic vision",
        placeholder="A cyberpunk detective chases a rogue AI through neon-drenched Tokyo rooftops...",
        height=140,
        key="production_story",
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🚀 Generate Master Prompt", width="stretch"):
            if not story:
                st.warning("Enter a description first")
            elif rt.PRODUCTION_AVAILABLE:
                prompt = rt.build_activation_prompt(
                    sess.clip_story(story, 120),
                    director=st.session_state.director,
                    genre=st.session_state.genre,
                    duration=st.session_state.duration,
                    complexity=st.session_state.complexity,
                    chat_model=st.session_state.chat_model,
                    video_model=st.session_state.video_model,
                )
                st.session_state.last_prompt = prompt
                st.success("Prompt ready")
            else:
                st.session_state.last_prompt = _fallback_prompt(story)
                st.success("Fallback prompt ready (production module unavailable)")

    with c2:
        if st.button("📋 Preview Phases", width="stretch"):
            if story:
                st.session_state.show_phases = True
            else:
                st.warning("Enter a description first")

    with c3:
        if st.button("📄 Export Bible", width="stretch"):
            if not story:
                st.warning("Describe your project first")
            elif rt.PRODUCTION_AVAILABLE:
                bible = rt.build_production_bible(
                    sess.clip_story(story, 80),
                    genre=st.session_state.genre,
                    director_signature=st.session_state.director,
                    target_duration_seconds=st.session_state.duration,
                    complexity=st.session_state.complexity,
                    locked_title=sess.clip_story(story, 60),
                    chat_model=st.session_state.chat_model,
                    video_model=st.session_state.video_model,
                    notes="Generated via Grok Imagine Cinematic Studio Web UI.",
                )
                st.session_state.last_bible = bible
                st.success("Bible ready for download")
            else:
                st.session_state.last_bible = _fallback_bible(story)
                st.success("Fallback bible ready for download")

    if prompt := st.session_state.get("last_prompt"):
        st.code(prompt, language="markdown")

    if st.session_state.get("show_phases") and story:
        _render_phase_outline(story)

    if bible := st.session_state.get("last_bible"):
        with st.expander("Production Bible preview", expanded=True):
            st.json(bible)
        st.download_button(
            "⬇️ Download production_bible.json",
            data=json.dumps(bible, indent=2),
            file_name="production_bible.json",
            mime="application/json",
        )

    st.divider()
    bible_wizard_ui.render_bible_wizard()

    st.divider()
    st.subheader("🔌 Live xAI API")
    if st.button("✨ Generate with xAI API", width="stretch"):
        if not story:
            st.warning("Enter a project description first")
        else:
            client = rt.get_grok_client()
            if not client:
                st.error("Set your XAI API key in Settings")
            elif rt.PRODUCTION_AVAILABLE:
                ctx = rt.production_context(
                    chat_model=st.session_state.chat_model,
                    video_model=st.session_state.video_model,
                )
                with st.spinner(f"{ctx['chat_label']} crafting prompt..."):
                    try:
                        response = client.chat.completions.create(
                            model=ctx["chat_slug"],
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        f"You are the Grok Imagine Cinematic Studio v{rt.STUDIO_VERSION} "
                                        "prompt engineer. Use Imagine Video 1.5 native audio rules."
                                    ),
                                },
                                {
                                    "role": "user",
                                    "content": (
                                        f"Create a cinematic prompt for: {story}\n"
                                        f"Pipeline: {ctx['pipeline_spec']}"
                                    ),
                                },
                            ],
                            max_tokens=850,
                            temperature=0.7,
                        )
                        st.text_area(
                            "Generated Prompt",
                            response.choices[0].message.content,
                            height=220,
                        )
                    except Exception as exc:
                        err = str(exc).lower()
                        if "401" in err or "auth" in err or "api key" in err:
                            st.error("Authentication failed — check your XAI API key in Settings.")
                        elif "429" in err or "rate" in err:
                            st.error("Rate limit exceeded — wait and retry.")
                        else:
                            st.error(f"API error: {exc}")
            else:
                st.warning("Production module unavailable — use Generate Master Prompt for a local fallback.")