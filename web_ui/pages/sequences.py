"""Long-form sequence chain — extend/stitch planning."""

from __future__ import annotations

import streamlit as st

from lib import runtime as rt


def render() -> None:
    st.header("🎬 Sequences")
    st.caption(
        f"Long-form extend/stitch · studio v{rt.STUDIO_VERSION} · "
        f"video `{st.session_state.get('video_model', rt.DEFAULT_IMAGINE_VIDEO_MODEL)}` · "
        "Chain QA before every extend"
    )
    if not rt.SEQ_AVAILABLE:
        st.error("Sequence module unavailable")
        return

    with st.form("new_sequence"):
        seq_name = st.text_input("Sequence Name")
        seq_dur = st.number_input("Target Duration (s)", 30, 180, 60)
        if st.form_submit_button("➕ Create Sequence"):
            if seq_name:
                seq = rt.create_sequence_scaffold(seq_name, target_duration=seq_dur)
                rt.save_sequence(seq)
                st.success(f"Created: sequences/{seq['slug']}/")
                st.rerun()

    seqs = rt.list_sequences()
    if not seqs:
        st.caption("No sequences yet.")
        return

    sel = st.selectbox("Active sequence", [s["name"] for s in seqs])
    seq_path = rt.find_sequence(sel)
    if not seq_path:
        return
    seq_data = rt.load_sequence(seq_path)
    clips = seq_data.get("clips", [])

    st.caption(
        f"Health: {seq_data.get('sequence_health_score', '—')} · "
        f"Chain QA: {seq_data.get('chain_qa_status', 'pending')} · "
        f"Clips: {len(clips)}"
    )

    if rt.QUOTA_AVAILABLE:
        cost = rt.estimate_sequence_cost(
            seq_data.get("clips", []),
            video_model=st.session_state.video_model,
        )
        st.metric(
            "Sequence cost estimate",
            f"{cost.get('credits_low', 0):.0f}–{cost.get('credits_high', 0):.0f} credits",
        )

    if clips:
        last = clips[-1]
        next_beat = st.text_input("Next beat", placeholder="She turns into the alley...")
        if st.button("Generate extend prompt") and next_beat:
            st.code(rt.build_extend_prompt(seq_data, last, next_beat), language="markdown")