#!/usr/bin/env python3
"""
Grok Imagine Cinematic Studio — Streamlit Web UI v3.6.1
Aligned with 23-Agent System + DNA / Sequence / Quota Pipelines
"""

import streamlit as st
from datetime import datetime
import json
import os
import sys
from pathlib import Path
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
try:
    from character_dna import (
        build_prompt_blocks,
        create_dna_scaffold,
        list_characters,
        lock_to_identity_bank,
        save_character_dna,
    )
    from sequence_chain import (
        add_clip_to_sequence,
        build_extend_prompt,
        create_clip,
        create_sequence_scaffold,
        find_sequence,
        get_clip,
        list_sequences,
        load_sequence,
        save_sequence,
        update_sequence_health,
    )
    from quota_optimizer import (
        assess_budget_risk,
        estimate_production,
        estimate_sequence_cost,
        get_optimization_recommendations,
        quota_dashboard,
        record_spend,
        set_budget,
    )
    from models import (
        DEFAULT_IMAGINE_VIDEO_MODEL,
        DEFAULT_XAI_CHAT_MODEL,
        IMAGINE_VIDEO_MODELS,
        XAI_CHAT_MODELS,
        resolve_chat_model,
    )
    DNA_AVAILABLE = True
    SEQ_AVAILABLE = True
    QUOTA_AVAILABLE = True
    MODELS_AVAILABLE = True
except ImportError:
    DNA_AVAILABLE = False
    SEQ_AVAILABLE = False
    QUOTA_AVAILABLE = False
    MODELS_AVAILABLE = False
    DEFAULT_IMAGINE_VIDEO_MODEL = "grok-imagine-video-1.5"
    DEFAULT_XAI_CHAT_MODEL = "grok-4.3"

# ===================== CONFIG =====================
AGENTS_DIR = Path("../references/agents")

def get_grok_client():
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        api_key = st.session_state.get("xai_api_key", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")

# ===================== PAGE SETUP =====================
st.set_page_config(
    page_title="Grok Imagine Cinematic Studio v3.6",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cinematic Styling
st.markdown("""
<style>
    .main { background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%); }
    .stApp { color: #e0e0ff; }
    .stButton>button {
        background: linear-gradient(90deg, #6a00ff, #00d4ff);
        color: white; border: none; border-radius: 12px;
        padding: 12px 28px; font-weight: 600; transition: all 0.3s ease;
    }
    .stButton>button:hover { transform: scale(1.05); box-shadow: 0 0 20px #00d4ff; }
    .section-header { color: #00d4ff; margin-top: 1rem; }
</style>
""", unsafe_allow_html=True)

# ===================== HEADER =====================
st.title("🎥 Grok Imagine Cinematic Studio v3.6")
st.markdown("**23-Agent Professional Cinematic Production System** • DNA + Sequence + Quota Pipelines")

# ===================== SIDEBAR =====================
with st.sidebar:
    st.header("🎬 Production Crew")
    st.success("✅ 23 Agents + Role Cards Active")

    # Full Agent List
    with st.expander("View All 23 Agents", expanded=True):
        agents = [
            "Studio Director", "Mega Production Architect", "Character DNA Extractor",
            "Director of Photography", "Post-Production Color Grading Supervisor", "Production Designer / Set Decorator",
            "Performance & Emotion Director", "Identity Lock Specialist", "Narrative Arc & Pacing Strategist",
            "Sequence Director", "Cinematic Sequence Extender",
            "Continuity & Consistency Guardian", "Quality Assurance Guardian",
            "Imagine Prompt Master", "Workflow & Quota Optimizer",
            "Sonic Architect Native Audio Virtuoso", "Foley Sound Design Specialist",
            "Stunt & Action Choreographer", "VFX & SFX Supervisor",
            "Key Art & Poster Designer", "Trailer & Teaser Director",
            "Localization & Subtitle Specialist",
            "AI Polish Director", "ErosForge NSFW Director (opt-in)"
        ]
        for agent in agents:
            st.markdown(f"• {agent}")

    # Role Card Browser
    st.subheader("📋 Role Cards")
    if AGENTS_DIR.exists():
        role_cards = sorted([f.stem.replace("_", " ") for f in AGENTS_DIR.glob("*.md") if "AGENT_INDEX" not in f.stem])
        selected = st.selectbox("Browse Role Card", ["Select..."] + role_cards)
        if selected != "Select...":
            card_file = AGENTS_DIR / (selected.replace(" ", "_") + ".md")
            if card_file.exists():
                with st.expander(f"📖 {selected}", expanded=True):
                    st.markdown(card_file.read_text()[:2000] + "...")
    else:
        st.warning("references/agents/ not found")

    # Character DNA Section
    st.subheader("🧬 Character DNA")
    if DNA_AVAILABLE:
        with st.expander("Create DNA Profile", expanded=False):
            dna_name = st.text_input("Character Name", placeholder="Elena Voss", key="dna_name")
            dna_core = st.text_area("Core Identity", placeholder="Late 30s, silver-gray hair, quiet confidence...", height=60, key="dna_core")
            dna_facial = st.text_area("Facial DNA", placeholder="Hazel eyes, subtle crow's feet, defined cheekbones...", height=60, key="dna_facial")
            dna_hair = st.text_input("Hair & Grooming", placeholder="Silver-gray bob, side-parted", key="dna_hair")
            if st.button("💾 Save DNA Profile", use_container_width=True, key="dna_save"):
                if dna_name and dna_core and dna_facial:
                    dna = create_dna_scaffold(dna_name, core_identity=dna_core, facial_dna=dna_facial, hair_grooming=dna_hair, source="web-ui")
                    save_character_dna(dna)
                    st.success(f"✅ DNA saved: characters/{dna['slug']}/")
                    st.rerun()
                else:
                    st.warning("Name, Core Identity, and Facial DNA are required")

        chars = list_characters()
        if chars:
            with st.expander(f"Locked Characters ({len(chars)})", expanded=True):
                for c in chars:
                    col_a, col_b = st.columns([3, 1])
                    col_a.markdown(f"**{c['name']}** `{c['status']}`")
                    if col_b.button("🔒", key=f"lock_{c['slug']}", help="Lock to Identity Bank"):
                        from character_dna import find_character_dna, load_character_dna
                        path = find_character_dna(c["name"])
                        if path:
                            lock_to_identity_bank(load_character_dna(path))
                            st.success(f"Locked {c['name']}")
                            st.rerun()
        else:
            st.caption("No DNA profiles yet.")
    else:
        st.caption("Character DNA module unavailable.")

    # Legacy memory
    st.subheader("🧠 Quick Memory")
    if "memory" not in st.session_state:
        st.session_state.memory = {}
    with st.expander("Add Memory Entry", expanded=False):
        mem_name = st.text_input("Name", placeholder="PROJECT_THEME", key="mem_name")
        mem_value = st.text_area("Value", height=60, key="mem_value")
        if st.button("💾 Save", use_container_width=True, key="mem_save"):
            if mem_name and mem_value:
                st.session_state.memory[mem_name] = mem_value
                st.rerun()

    st.divider()

    # Production Settings
    st.subheader("⚙️ Settings")
    genre = st.selectbox("Genre", ["Sci-Fi", "Psychological Horror", "Action", "Drama", "Cyberpunk", "Intimate Drama", "Thriller"])
    director = st.selectbox("Director Signature", 
        ["Denis Villeneuve", "Christopher Nolan", "David Fincher", "Roger Deakins", "Zack Snyder", "Default"])
    if MODELS_AVAILABLE:
        video_model = st.selectbox(
            "Imagine Video Model",
            list(IMAGINE_VIDEO_MODELS.keys()),
            format_func=lambda s: f"{IMAGINE_VIDEO_MODELS[s]['label']} (${IMAGINE_VIDEO_MODELS[s]['usd_per_second']}/sec)",
            key="video_model",
        )
    else:
        video_model = DEFAULT_IMAGINE_VIDEO_MODEL
    duration = st.slider("Duration (seconds)", 15, 180, 60, step=5)
    complexity = st.select_slider("Complexity", ["Low", "Medium", "High", "Extreme"])
    fast_mode = st.checkbox("Fast Mode", value=False, key="fast_mode")
    tier = st.selectbox("Subscription", ["supergrok_pro", "supergrok_heavy", "custom"], key="quota_tier")

    # Live Quota Estimator (xAI per-second pricing)
    st.subheader("💰 Quota Estimate")
    if QUOTA_AVAILABLE:
        est = estimate_production(
            duration,
            complexity=complexity.lower(),
            fast_mode=fast_mode,
            video_model=video_model,
        )
        dash = quota_dashboard()
        risk = assess_budget_risk(est, tier=tier, budget_remaining=dash.get("budget_remaining"))
        col1, col2, col3 = st.columns(3)
        col1.metric("Credits", f"{est['credits_low']:.0f}–{est['credits_high']:.0f}")
        col2.metric("USD", f"${est['usd_low']}–${est['usd_high']}")
        col3.metric("Risk", risk["risk_level"].title())
        st.caption(f"Clips: ~{est['clip_count']} | Tokens: ~{est['estimated_tokens']:,}")
        if st.button("Set Budget Tier", key="set_tier"):
            set_budget(tier=tier)
            st.success(f"Tier set: {tier}")
    else:
        st.caption("Quota module unavailable.")

# ===================== SEQUENCE CHAIN =====================
if SEQ_AVAILABLE:
    seqs = list_sequences()
    with st.expander("🎬 Long-Form Sequence (1.5 Extend/Stitch)", expanded=False):
        if st.button("➕ New Sequence", key="seq_new_btn"):
            st.session_state.show_seq_form = True
        if st.session_state.get("show_seq_form"):
            seq_name = st.text_input("Sequence Name", key="seq_name")
            seq_dur = st.number_input("Target Duration (s)", 30, 180, 60, key="seq_dur")
            if st.button("Create Sequence", key="seq_create"):
                if seq_name:
                    seq = create_sequence_scaffold(seq_name, target_duration=seq_dur)
                    save_sequence(seq)
                    st.session_state.show_seq_form = False
                    st.success(f"Created: sequences/{seq['slug']}/")
                    st.rerun()
        if seqs:
            sel_seq = st.selectbox("Sequence", [s["name"] for s in seqs], key="sel_seq")
            seq_path = find_sequence(sel_seq)
            if seq_path:
                seq_data = load_sequence(seq_path)
                clips = seq_data.get("clips", [])
                st.caption(f"Health: {seq_data.get('sequence_health_score', '—')} | Chain QA: {seq_data.get('chain_qa_status', 'pending')} | Clips: {len(clips)}")
                if clips:
                    last = clips[-1]
                    next_beat = st.text_input("Next Beat", key="seq_beat", placeholder="She turns into the alley...")
                    if st.button("Generate Extend Prompt", key="seq_extend") and next_beat:
                        st.code(build_extend_prompt(seq_data, last, next_beat), language="markdown")

# ===================== CHARACTER DNA INJECTION =====================
if DNA_AVAILABLE:
    chars = list_characters()
    if chars:
        with st.expander("🧬 Character DNA Prompt Injection", expanded=False):
            inj_char = st.selectbox("Character", [c["name"] for c in chars], key="inj_char")
            inj_mode = st.selectbox("Mode", ["cinematic", "compact", "close_up", "sequence_starter", "video_1.5"], key="inj_mode")
            inj_base = st.text_area("Base Prompt (optional)", height=80, key="inj_base")
            if st.button("Generate Injection Block", key="inj_gen"):
                from character_dna import find_character_dna, inject_into_prompt, load_character_dna
                try:
                    result = inject_into_prompt(inj_base, inj_char, inj_mode)
                    st.code(result, language="markdown")
                except FileNotFoundError:
                    dna = load_character_dna(find_character_dna(inj_char))
                    st.code(build_prompt_blocks(dna)[inj_mode], language="markdown")

# ===================== MAIN AREA =====================
st.header("📝 Project Brief")

story = st.text_area(
    "Describe your cinematic vision",
    placeholder="A cyberpunk detective chases a rogue AI through neon-drenched Tokyo rooftops at midnight...",
    height=140
)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🚀 Generate Master Prompt", use_container_width=True):
        if story:
            prompt = f"""# Grok Imagine Cinematic Studio v3.6.1 — ACTIVATED

**Project:** {story[:120]}...
**Genre:** {genre}
**Director Signature:** {director}
**Duration:** {duration}s | **Complexity:** {complexity}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

You are now running the full **23-agent** Grok Imagine Cinematic Studio v3.6 with Role Cards loaded from `references/agents/`.

Please begin by confirming activation and building a detailed Production Bible.
"""
            st.code(prompt, language="markdown")
            st.success("✅ Prompt ready to copy")
        else:
            st.warning("Please enter a description first.")

with col2:
    if st.button("🎬 Simulate Full Production", use_container_width=True):
        if story:
            with st.spinner("Engaging all 23 agents..."):
                import time
                progress = st.progress(0)
                for i in range(100):
                    time.sleep(0.012)
                    progress.progress(i + 1)

            st.balloons()
            st.success("✅ Simulation Complete")

            st.subheader("📊 Structured Production Summary")

            # Generate structured simulation output
            st.markdown(f"""
**Project:** {story[:80]}...

**Genre:** {genre}  
**Director Signature:** {director}  
**Target Duration:** {duration}s  
**Complexity:** {complexity}

---

### Production Phases (Simulated)

**Phase 1: Pre-Production**
- **Mega Production Architect** → Production Bible generated
- **Identity Lock Specialist** → Character DNA locked
- **Production Designer** → World & set references created

**Phase 2: Core Production**
- **Director of Photography** + **Performance & Emotion Director** → Key sequences directed
- **Cinematic Sequence Extender** → Long-form expansion applied
- **Continuity Guardian** + **QA Guardian** → Consistency & quality checks passed

**Phase 3: Polish & Delivery**
- **Sonic Architect** + **Foley Specialist** → Audio design completed
- **Key Art Designer** + **Trailer Director** → Marketing assets generated
- **Quality Assurance Guardian** → Final 16-point QA: **PASSED**

---

### Quality Metrics
""")

            col_a, col_b, col_c, col_d = st.columns(4)
            col_a.metric("Character Consistency", "96%")
            col_b.metric("Emotional Impact", "94%")
            col_c.metric("Visual Coherence", "97%")
            col_d.metric("Overall QA Score", "✅ GO")

            st.info("This is an enhanced simulation. For real multi-agent generation, use the Grok API button below or the CLI.")
        else:
            st.warning("Enter a project description first.")

with col3:
    if st.button("📄 Export Production Bible", use_container_width=True):
        if story:
            bible = {
                "project_title": story[:80],
                "genre": genre,
                "director_signature": director,
                "target_duration_seconds": duration,
                "complexity": complexity,
                "total_agents": 23,
                "version": "3.6.1",
                "role_cards_source": "references/agents/",
                "locked_variables": {
                    "PROJECT_TITLE": story[:60],
                    "GENRE": genre,
                    "DIRECTOR_SIGNATURE": director,
                    "DURATION": f"{duration}s"
                },
                "key_agents_involved": [
                    "Mega Production Architect",
                    "Identity Lock Specialist",
                    "Director of Photography",
                    "Performance & Emotion Director",
                    "Cinematic Sequence Extender",
                    "Quality Assurance Guardian"
                ],
                "recommended_phases": [
                    "Pre-Production (Bible + Character DNA)",
                    "Core Production (Direction + Extension)",
                    "Polish & Delivery (Audio + Marketing + QA)"
                ],
                "created": datetime.now().isoformat(),
                "status": "Ready for production",
                "notes": "Generated via Grok Imagine Cinematic Studio Web UI. Use CLI for advanced memory & PDF reports."
            }
            st.download_button(
                "⬇️ Download production_bible.json",
                data=json.dumps(bible, indent=2),
                file_name="production_bible.json",
                mime="application/json"
            )
            st.success("✅ Rich Production Bible exported")
        else:
            st.warning("Describe your project first.")

# ===================== GROK API SECTION =====================
st.divider()
st.header("🔌 Live xAI API Integration")

chat_model_options = list(XAI_CHAT_MODELS.keys()) if MODELS_AVAILABLE else [DEFAULT_XAI_CHAT_MODEL]
chat_model = st.selectbox(
    "Chat Model",
    chat_model_options,
    format_func=lambda s: f"{XAI_CHAT_MODELS[s]['label']} — {XAI_CHAT_MODELS[s]['use_case']}" if MODELS_AVAILABLE else s,
    key="chat_model",
)

with st.expander("API Settings", expanded=False):
    st.text_input("XAI API Key", type="password", key="xai_api_key")
    st.caption("Grok Build CLI: `grok-composer-2.5-fast` (default), `grok-build` (fork). See `references/MODELS_v3.6.md`.")

if st.button("✨ Generate Prompt with xAI API", use_container_width=True):
    if not story:
        st.warning("Please enter a project description first.")
    else:
        client = get_grok_client()
        if not client:
            st.error("Please provide your XAI API key in the sidebar settings.")
        else:
            api_model = resolve_chat_model(chat_model) if MODELS_AVAILABLE else chat_model
            model_label = XAI_CHAT_MODELS.get(api_model, {}).get("label", api_model) if MODELS_AVAILABLE else api_model
            with st.spinner(f"{model_label} is crafting your cinematic prompt..."):
                try:
                    response = client.chat.completions.create(
                        model=api_model,
                        messages=[
                            {"role": "system", "content": "You are an expert cinematic prompt engineer for the 23-agent Grok Imagine Cinematic Studio v3.6."},
                            {"role": "user", "content": f"Create a detailed cinematic prompt for: {story}. Video pipeline: {video_model}. Include lighting, camera work, mood, and visual style."}
                        ],
                        max_tokens=850,
                        temperature=0.7
                    )
                    st.success(f"✅ Prompt generated by {model_label}")
                    st.text_area("Generated Prompt", response.choices[0].message.content, height=200)
                except Exception as e:
                    st.error(f"API Error: {e}")

# Footer
st.divider()
st.caption("Grok Imagine Cinematic Studio v3.6.1 • 23 Agents • DNA/Sequence/Quota • June 2026")