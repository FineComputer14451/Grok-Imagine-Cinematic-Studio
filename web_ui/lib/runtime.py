"""Path setup, tool imports, availability flags, and subprocess helpers."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import streamlit as st
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))

STUDIO_VERSION = "3.6.5"
ACTIVATION_PHRASE = f"Activate Grok Imagine Cinematic Studio v{STUDIO_VERSION}"
AGENTS_DIR = ROOT / "references" / "agents"
ROLE_CARD_PREVIEW_CHARS = 4000

try:
    from cli.production import build_activation_prompt, build_production_bible, production_context
    from cli.shared import AGENTS, STUDIO_VERSION as _CLI_VERSION, core_agent_count as _core_agent_count

    STUDIO_VERSION = _CLI_VERSION
    ACTIVATION_PHRASE = f"Activate Grok Imagine Cinematic Studio v{STUDIO_VERSION}"
    PRODUCTION_AVAILABLE = True
except ImportError:
    AGENTS = {}
    PRODUCTION_AVAILABLE = False

    def _core_agent_count() -> int:
        return 23

try:
    from character_dna import (
        build_prompt_blocks,
        create_dna_scaffold,
        find_character_dna,
        inject_into_prompt,
        list_characters,
        load_character_dna,
        lock_to_identity_bank,
        save_character_dna,
    )
    from project_state import load_project_state, save_project_state
    from sequence_chain import (
        build_extend_prompt,
        create_sequence_scaffold,
        find_sequence,
        list_sequences,
        load_sequence,
        save_sequence,
    )
    from quota_optimizer import (
        assess_budget_risk,
        estimate_production,
        estimate_sequence_cost,
        get_optimization_recommendations,
        quota_dashboard,
        set_budget,
    )
    from models import (
        DEFAULT_IMAGINE_VIDEO_MODEL,
        DEFAULT_XAI_CHAT_MODEL,
        IMAGINE_VIDEO_MODELS,
        XAI_CHAT_MODELS,
        verify_model_compatibility,
    )
    from nsfw_orchestrator import plan_batch
    from nsfw_sequence_extender import plan_nsfw_extension

    DNA_AVAILABLE = True
    SEQ_AVAILABLE = True
    QUOTA_AVAILABLE = True
    MODELS_AVAILABLE = True
    NSFW_AVAILABLE = True
except ImportError:
    DNA_AVAILABLE = False
    SEQ_AVAILABLE = False
    QUOTA_AVAILABLE = False
    MODELS_AVAILABLE = False
    NSFW_AVAILABLE = False
    DEFAULT_IMAGINE_VIDEO_MODEL = "grok-imagine-video-1.5"
    DEFAULT_XAI_CHAT_MODEL = "grok-4.3"
    IMAGINE_VIDEO_MODELS = {}
    XAI_CHAT_MODELS = {}


def core_agent_count() -> int:
    if not AGENTS:
        return 23
    return _core_agent_count()


def list_role_card_options() -> list[tuple[str, Path]]:
    if not AGENTS_DIR.exists():
        return []
    options: list[tuple[str, Path]] = []
    for path in sorted(AGENTS_DIR.glob("*.md")):
        if path.stem == "AGENT_INDEX":
            continue
        label = path.stem.replace("_", " ")
        options.append((label, path))
    return options


def read_role_card_preview(path: Path, limit: int = ROLE_CARD_PREVIEW_CHARS) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n\n…"


def get_grok_client() -> OpenAI | None:
    api_key = os.getenv("XAI_API_KEY") or st.session_state.get("xai_api_key", "")
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")


def run_cli(args: list[str], timeout: int = 120) -> tuple[int, str]:
    cmd = [sys.executable, str(ROOT / "tools" / "cinematic_studio_cli.py"), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output.strip()


@st.cache_data(ttl=300, show_spinner=False)
def cached_plugin_details() -> str:
    try:
        result = subprocess.run(
            ["grok", "plugin", "details", "grok-imagine-cinematic-studio"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=ROOT,
        )
        return (result.stdout or result.stderr or "Plugin details unavailable.").strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return "Grok CLI not available in this environment."


def render_footer() -> None:
    st.divider()
    st.caption(
        f"Grok Imagine Cinematic Studio v{STUDIO_VERSION} · "
        f"Grok 4.3 + Imagine 1.5 + Grok Build · "
        f"Install: `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust`"
    )