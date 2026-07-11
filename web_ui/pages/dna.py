"""Character DNA profiles, identity lock, and quick memory."""

from __future__ import annotations

import streamlit as st

from lib import runtime as rt


def render() -> None:
    st.header("🧬 Character DNA & Memory")
    if not rt.DNA_AVAILABLE:
        st.error("Character DNA module unavailable")
        return

    tab_dna, tab_mem, tab_inj = st.tabs(["DNA Profiles", "Quick Memory", "Prompt Injection"])

    with tab_dna:
        with st.form("dna_form"):
            dna_name = st.text_input("Character Name", placeholder="Elena Voss")
            dna_core = st.text_area("Core Identity", height=60)
            dna_facial = st.text_area("Facial DNA", height=60)
            dna_hair = st.text_input("Hair & Grooming")
            if st.form_submit_button("💾 Save DNA Profile", width="stretch"):
                if dna_name and dna_core and dna_facial:
                    dna = rt.create_dna_scaffold(
                        dna_name,
                        core_identity=dna_core,
                        facial_dna=dna_facial,
                        hair_grooming=dna_hair,
                        source="web-ui",
                    )
                    rt.save_character_dna(dna)
                    st.success(f"Saved: characters/{dna['slug']}/")
                    st.rerun()
                else:
                    st.warning("Name, core identity, and facial DNA are required")

        chars = rt.list_characters()
        if chars:
            for c in chars:
                col_a, col_b = st.columns([4, 1])
                col_a.markdown(f"**{c['name']}** `{c['status']}`")
                if col_b.button("🔒 Lock", key=f"lock_{c['slug']}"):
                    path = rt.find_character_dna(c["name"])
                    if path:
                        rt.lock_to_identity_bank(rt.load_character_dna(path))
                        st.rerun()
        else:
            st.caption("No DNA profiles yet.")

    with tab_mem:
        with st.form("memory_form"):
            mem_name = st.text_input("Name", placeholder="PROJECT_THEME")
            mem_value = st.text_area("Value", height=80)
            if st.form_submit_button("💾 Save Memory", width="stretch"):
                if mem_name and mem_value:
                    state = rt.load_project_state()
                    state["characters"][mem_name] = mem_value
                    rt.save_project_state(state)
                    st.success(f"Saved: {mem_name}")
                    st.rerun()
                else:
                    st.warning("Name and value required")

        entries = {
            k: v
            for k, v in rt.load_project_state().get("characters", {}).items()
            if isinstance(v, str)
        }
        for name, value in entries.items():
            preview = value[:120] + ("…" if len(value) > 120 else "")
            st.markdown(f"**{name}** — {preview}")

    with tab_inj:
        chars = rt.list_characters()
        if not chars:
            st.caption("Create a DNA profile first.")
            return
        inj_char = st.selectbox("Character", [c["name"] for c in chars])
        inj_mode = st.selectbox(
            "Mode",
            [
                "cinematic",
                "compact",
                "close_up",
                "sequence_starter",
                "video_1.0",
                "video_1.5",
            ],
            help="video_1.0 = cost-default video inject · video_1.5 = native-audio / micro-detail",
        )
        inj_base = st.text_area("Base Prompt (optional)", height=80)
        if st.button("Generate Injection Block"):
            try:
                result = rt.inject_into_prompt(inj_base, inj_char, inj_mode)
            except FileNotFoundError:
                dna = rt.load_character_dna(rt.find_character_dna(inj_char))
                result = rt.build_prompt_blocks(dna)[inj_mode]
            st.code(result, language="markdown")