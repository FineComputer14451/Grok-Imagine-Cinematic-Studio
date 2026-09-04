"""Production defaults, Grok 4.6 Model Layer, and API configuration."""

from __future__ import annotations

import streamlit as st

from lib import runtime as rt
from lib import session as sess


def render() -> None:
    st.header("⚙️ Settings")
    st.caption("Session defaults for Production, Quota, and Imagine. Orchestration defaults to **Grok 4.6**.")

    opts = sess.PRODUCTION_OPTIONS

    st.subheader("Model Layer (Grok 4.6 · studio v3.11.0)")
    st.markdown(rt.stack_banner_markdown())

    if rt.MODELS_AVAILABLE:
        video_models = rt.ordered_video_model_slugs()
        image_models = rt.ordered_image_model_slugs()
        chat_models = rt.ordered_chat_model_slugs()
        st.session_state.chat_model = st.selectbox(
            "xAI Chat / orchestration model",
            chat_models,
            index=sess.select_index(chat_models, st.session_state.chat_model),
            format_func=rt.format_chat_model_label,
            help="Default: grok-4.6 (cinematic + Build). Use grok-4.3 only for 1M-context Bibles. grok-4.5 aliases wrap 4.6.",
        )
        st.session_state.image_model = st.selectbox(
            "Imagine Image model",
            image_models,
            index=sess.select_index(image_models, st.session_state.get("image_model", rt.DEFAULT_IMAGINE_IMAGE_MODEL)),
            format_func=rt.format_image_model_label,
            help="Draft default is Image 1.0. Hero plates and Quality Mode use Image 2.0. There is no Video 2.0.",
        )
        st.session_state.video_model = st.selectbox(
            "Imagine Video model",
            video_models,
            index=sess.select_index(video_models, st.session_state.video_model),
            format_func=rt.format_video_model_label,
            help="Cost default is 1.0 (grok-imagine-video). Use 1.5 when native audio is required. Edit/extend is 1.0 only.",
        )
        st.session_state.reasoning_level = st.select_slider(
            "Preferred reasoning (Grok 4.6)",
            options=opts["reasoning_levels"],
            value=st.session_state.get("reasoning_level", "high"),
            help="High for Bibles, QA, Identity Lock, Sequence Director. Medium for routine prompts.",
        )
        st.session_state.prompt_cache_key = st.text_input(
            "prompt_cache_key (project slug)",
            value=st.session_state.get("prompt_cache_key", ""),
            placeholder="my-film-slug",
            help="Stable key for multi-turn grok-4.6 agent loops — reduces cost on repeated context.",
        )
        with st.expander("VIDEO_PIPELINE_SPEC (from registry)", expanded=False):
            st.code(
                rt.build_video_pipeline_spec(st.session_state.video_model),
                language=None,
            )
        with st.expander("Model stack JSON", expanded=False):
            st.json(rt.session_model_stack())
        col_v, col_c = st.columns(2)
        with col_v:
            if st.button("Run models verify", width="stretch"):
                rt.cached_models_verify.clear()
                result = rt.cached_models_verify()
                if result.get("ok"):
                    st.success("Model compatibility OK")
                else:
                    st.error("Compatibility issues")
                for issue in result.get("issues") or []:
                    st.markdown(f"- {issue}")
                for warn in result.get("warnings") or []:
                    st.caption(f"⚠️ {warn}")
        with col_c:
            st.caption(
                f"Registry: `{rt.DOCS_MODELS}` · Layer: `{rt.DOCS_MODEL_LAYER}` · "
                f"CLI ≥ {rt.MIN_GROK_BUILD_CLI}"
            )
    else:
        st.warning("Model registry unavailable — tools/models.py failed to import.")

    st.divider()
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

    if rt.REGIONS_AVAILABLE:
        region_keys = list(rt.IMAGINE_REGIONS.keys())
        current = rt.get_active_region()
        st.session_state.imagine_region = st.selectbox(
            "Imagine API Region",
            region_keys,
            index=sess.select_index(region_keys, st.session_state.get("imagine_region", current)),
            format_func=lambda r: f"{r} — {rt.IMAGINE_REGIONS[r]['label']}",
            help="Routes Imagine API requests; failover chain used on 403/429/5xx.",
        )
        if st.session_state.imagine_region != current:
            rt.set_imagine_region(st.session_state.imagine_region)
            st.caption(f"Active region: {rt.get_active_region()}")

    st.divider()
    st.subheader("🔑 xAI API")
    st.text_input(
        "XAI API Key",
        type="password",
        key="xai_api_key",
        help=(
            "Session override. Resolution order: this field → XAI_API_KEY env → "
            "Streamlit secrets (Community Cloud App settings → Secrets)."
        ),
    )
    resolved = bool(rt.resolve_xai_api_key())
    if resolved and not str(st.session_state.get("xai_api_key") or "").strip():
        st.success("API key loaded from environment or Streamlit secrets (not shown).")
    elif not resolved:
        st.info(
            "No key yet — Imagine stays in dry-run. On Streamlit Community Cloud, add "
            "`XAI_API_KEY = \"…\"` under **App settings → Secrets** "
            "(see `.streamlit/secrets.toml.example`)."
        )
    st.caption(
        "Never treat Imagine image/video slugs as chat models. "
        "Orchestration = `grok-4.6` · video/image spend = `grok-imagine-*` only. "
        "Do not commit secrets; `.streamlit/secrets.toml` is gitignored."
    )

    st.divider()
    st.subheader("🔞 NSFW pipelines (18+ / SpaceXAI AUP)")
    st.markdown(
        "Limited **R-rated fictional adult** material of **imaginary adults** only. "
        "Not affiliated with xAI / SpaceXAI. Policy: "
        "[Acceptable Use Policy](https://x.ai/legal/acceptable-use-policy)"
    )
    age_ok = st.checkbox("I am 18 or older", value=False, key="aup_age")
    imag_ok = st.checkbox("Subjects are fictional imaginary adults", value=False, key="aup_imaginary")
    real_ok = st.checkbox("I will not use real-person photos or likenesses", value=False, key="aup_not_real")
    aup_ok = st.checkbox("I acknowledge the SpaceXAI Acceptable Use Policy", value=False, key="aup_ack")
    can_enable = age_ok and imag_ok and real_ok and aup_ok
    if not can_enable:
        st.session_state.nsfw_opt_in = False
        st.caption("All four attestations are required. A Settings checkbox alone is not enough.")
    else:
        from aup_gate import write_attestation

        try:
            write_attestation(
                age_18_plus=True,
                imaginary_adults_only=True,
                not_a_real_person=True,
                aup_acknowledged=True,
            )
        except Exception as exc:
            st.error(str(exc))
            st.session_state.nsfw_opt_in = False
        else:
            st.session_state.nsfw_opt_in = st.checkbox(
                "Enable NSFW planning tools",
                value=st.session_state.nsfw_opt_in,
                help="Unlocks the NSFW page after AUP attestation.",
            )
            if st.session_state.nsfw_opt_in:
                st.caption("Open the **NSFW** page. Live Imagine calls still default to dry-run.")
