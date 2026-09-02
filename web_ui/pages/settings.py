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
                f"(${rt.IMAGINE_VIDEO_MODELS[s]['usd_per_second']}/sec"
                f"{', native audio' if rt.IMAGINE_VIDEO_MODELS[s].get('native_audio') else ''})"
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
        help="Or set XAI_API_KEY in the environment.",
    )
    st.caption("Grok Build CLI models: `grok-composer-2.5-fast`, `grok-build` — see `references/MODELS_v3.6.md`")

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