"""Production defaults, models, and API configuration."""

from __future__ import annotations

import streamlit as st

from lib import runtime as rt
from lib import session as sess


def render() -> None:
    st.header("⚙️ Settings")

    opts = sess.PRODUCTION_OPTIONS

    st.subheader("Production defaults")
    st.session_state.genre = st.selectbox(
        "Genre",
        opts["genres"],
        index=sess.select_index(opts["genres"], st.session_state.genre),
    )
    st.session_state.director = st.selectbox(
        "Director Signature",
        opts["directors"],
        index=sess.select_index(opts["directors"], st.session_state.director),
    )
    if rt.MODELS_AVAILABLE:
        video_models = list(rt.IMAGINE_VIDEO_MODELS.keys())
        chat_models = list(rt.XAI_CHAT_MODELS.keys())
        st.session_state.video_model = st.selectbox(
            "Imagine Video Model",
            video_models,
            index=sess.select_index(video_models, st.session_state.video_model),
            format_func=lambda s: (
                f"{rt.IMAGINE_VIDEO_MODELS[s]['label']} "
                f"(${rt.IMAGINE_VIDEO_MODELS[s]['usd_per_second']}/sec)"
            ),
        )
        st.session_state.chat_model = st.selectbox(
            "xAI Chat Model",
            chat_models,
            index=sess.select_index(chat_models, st.session_state.chat_model),
            format_func=lambda s: (
                f"{rt.XAI_CHAT_MODELS[s]['label']} — {rt.XAI_CHAT_MODELS[s]['use_case']}"
            ),
        )
    st.session_state.duration = st.slider(
        "Duration (seconds)", 15, 180, st.session_state.duration, step=5
    )
    st.session_state.complexity = st.select_slider(
        "Complexity",
        opts["complexities"],
        value=st.session_state.complexity,
    )
    st.session_state.fast_mode = st.checkbox("Fast Mode", value=st.session_state.fast_mode)
    st.session_state.quota_tier = st.selectbox(
        "Subscription",
        opts["tiers"],
        index=sess.select_index(opts["tiers"], st.session_state.quota_tier),
    )

    st.divider()
    st.subheader("🔑 xAI API")
    st.text_input(
        "XAI API Key",
        type="password",
        key="xai_api_key",
        help="Or set XAI_API_KEY in the environment.",
    )
    st.caption("Grok Build CLI models: `grok-composer-2.5-fast`, `grok-build` — see `references/MODELS_v3.6.md`")

    st.divider()
    st.subheader("🔞 NSFW pipelines")
    st.session_state.nsfw_opt_in = st.checkbox(
        "Enable NSFW planning tools",
        value=st.session_state.nsfw_opt_in,
        help="Unlocks the NSFW page. Explicit activation still required in Grok.",
    )
    if st.session_state.nsfw_opt_in:
        st.caption("Open the **NSFW** page to plan batches and extensions.")