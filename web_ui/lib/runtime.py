"""Path setup, tool imports, availability flags, and subprocess helpers."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import streamlit as st
from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "tools"))
# studio_core (UI-agnostic services) lives at repo root
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STUDIO_VERSION = "3.7.1"
ACTIVATION_PHRASE = f"Activate Grok Imagine Cinematic Studio v{STUDIO_VERSION}"
AGENTS_DIR = ROOT / "references" / "agents"
ROLE_CARD_PREVIEW_CHARS = 4000
MIN_GROK_BUILD_CLI = "0.2.93"
DOCS_MODELS = "references/MODELS.md"
DOCS_MODEL_LAYER = "references/agents/MODEL_LAYER_v4.5.md"

try:
    from cli.production import build_activation_prompt, build_production_bible, production_context
    from cli.shared import (
        AGENTS,
        STUDIO_VERSION as _CLI_VERSION,
        core_agent_count as _core_agent_count,
        list_role_card_files,
    )

    STUDIO_VERSION = _CLI_VERSION
    ACTIVATION_PHRASE = f"Activate Grok Imagine Cinematic Studio v{STUDIO_VERSION}"
    PRODUCTION_AVAILABLE = True
except ImportError:
    AGENTS = {}
    PRODUCTION_AVAILABLE = False

    def _core_agent_count() -> int:
        return 23

try:
    from cli.bible_stages import (
        STAGES,
        answers_to_kwargs,
        build_notes,
        summary_and_next_steps,
        validate_answers,
    )

    BIBLE_STAGES_AVAILABLE = True
except ImportError:
    BIBLE_STAGES_AVAILABLE = False
    STAGES = []

    def answers_to_kwargs(answers):  # type: ignore[misc]
        raise RuntimeError("bible stages unavailable")

    def build_notes(answers):  # type: ignore[misc]
        return ""

    def summary_and_next_steps(bible):  # type: ignore[misc]
        return ""

    def validate_answers(stage_id, answers):  # type: ignore[misc]
        return ["bible stages unavailable"]

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
    try:
        from studio_core.services.dashboard import build_studio_dashboard
    except ImportError:  # pragma: no cover — shim path
        from cli.dashboard import build_studio_dashboard
    from imagine_jobs import job_summary, list_jobs
    from imagine_regions import IMAGINE_REGIONS, get_active_region, set_imagine_region
    from models import (
        DEFAULT_IMAGINE_IMAGE_MODEL,
        DEFAULT_IMAGINE_VIDEO_MODEL,
        DEFAULT_XAI_BUILD_MODEL,
        DEFAULT_XAI_CHAT_MODEL,
        IMAGINE_VIDEO_MODELS,
        MIN_GROK_BUILD_CLI_VERSION,
        ROLE_DEFAULTS,
        STACK_CONTRACT,
        XAI_CHAT_MODELS,
        build_video_pipeline_spec,
        model_stack_summary,
        verify_model_compatibility,
    )

    DNA_AVAILABLE = True
    SEQ_AVAILABLE = True
    QUOTA_AVAILABLE = True
    MODELS_AVAILABLE = True
    NSFW_AVAILABLE = True
    DASHBOARD_AVAILABLE = True
    IMAGINE_AVAILABLE = True
    REGIONS_AVAILABLE = True
    MIN_GROK_BUILD_CLI = MIN_GROK_BUILD_CLI_VERSION
except ImportError:
    DNA_AVAILABLE = False
    SEQ_AVAILABLE = False
    QUOTA_AVAILABLE = False
    MODELS_AVAILABLE = False
    NSFW_AVAILABLE = False
    DASHBOARD_AVAILABLE = False
    IMAGINE_AVAILABLE = False
    REGIONS_AVAILABLE = False
    IMAGINE_REGIONS = {}
    DEFAULT_IMAGINE_VIDEO_MODEL = "grok-imagine-video"
    DEFAULT_IMAGINE_IMAGE_MODEL = "grok-imagine-image"
    DEFAULT_XAI_CHAT_MODEL = "grok-4.5"
    DEFAULT_XAI_BUILD_MODEL = "grok-4.5"
    IMAGINE_VIDEO_MODELS = {}
    XAI_CHAT_MODELS = {}
    STACK_CONTRACT = {"cinematic": "grok-4.5", "build": "grok-4.5", "cli": "grok-4.5"}
    ROLE_DEFAULTS = dict(STACK_CONTRACT)
    MIN_GROK_BUILD_CLI = "0.2.93"

    def model_stack_summary(**kwargs):  # type: ignore[misc]
        return {
            "cinematic": DEFAULT_XAI_CHAT_MODEL,
            "build": DEFAULT_XAI_BUILD_MODEL,
            "cli": DEFAULT_XAI_CHAT_MODEL,
            "imagine_video": DEFAULT_IMAGINE_VIDEO_MODEL,
            "imagine_image": DEFAULT_IMAGINE_IMAGE_MODEL,
        }

    def build_video_pipeline_spec(model=None):  # type: ignore[misc]
        m = model or DEFAULT_IMAGINE_VIDEO_MODEL
        native = "1.5" in str(m)
        return (
            f'[VIDEO_PIPELINE_SPEC: model="{m}", resolution="720p", '
            f'clip_length="8-12s preferred", native_audio={str(native).lower()}, '
            f'reference_image_fidelity=high, '
            f'extend_protocol="LAST_FRAME + MOTION_VECTOR + AUDIO_CUE", '
            f"stitch_priority=high]"
        )

    def verify_model_compatibility():  # type: ignore[misc]
        return {"ok": False, "issues": ["models registry unavailable"], "warnings": []}


def core_agent_count() -> int:
    if not AGENTS:
        return 23
    return _core_agent_count()


def ordered_chat_model_slugs() -> list[str]:
    """Prefer grok-4.5 first (cinematic default); 4.3 is opt-in 1M."""
    if not XAI_CHAT_MODELS:
        return [DEFAULT_XAI_CHAT_MODEL]
    keys = list(XAI_CHAT_MODELS.keys())
    preferred = DEFAULT_XAI_CHAT_MODEL
    if preferred in keys:
        return [preferred] + [k for k in keys if k != preferred]
    return keys


def ordered_video_model_slugs() -> list[str]:
    """Prefer cost-default 1.0 (`grok-imagine-video`) before 1.5 native audio."""
    if not IMAGINE_VIDEO_MODELS:
        return [DEFAULT_IMAGINE_VIDEO_MODEL]
    keys = list(IMAGINE_VIDEO_MODELS.keys())
    preferred = DEFAULT_IMAGINE_VIDEO_MODEL
    if preferred in keys:
        return [preferred] + [k for k in keys if k != preferred]
    return keys


def format_chat_model_label(slug: str) -> str:
    meta = XAI_CHAT_MODELS.get(slug, {})
    label = meta.get("label", slug)
    use = meta.get("use_case", "")
    role = meta.get("role", "")
    badge = ""
    if slug == DEFAULT_XAI_CHAT_MODEL or role == "default":
        badge = " ★ default"
    elif role == "long_context":
        badge = " · 1M opt-in"
    ctx = meta.get("context_tokens")
    ctx_s = f" · {ctx // 1000}k ctx" if isinstance(ctx, int) else ""
    return f"{label}{badge}{ctx_s}" + (f" — {use}" if use else "")


def format_video_model_label(slug: str) -> str:
    meta = IMAGINE_VIDEO_MODELS.get(slug, {})
    label = meta.get("label", slug)
    price = meta.get("usd_per_second")
    native = meta.get("native_audio")
    bits = [label]
    if price is not None:
        bits.append(f"${price}/sec")
    if native:
        bits.append("native audio")
    elif slug == DEFAULT_IMAGINE_VIDEO_MODEL:
        bits.append("cost default")
    return " · ".join(bits)


def session_model_stack() -> dict[str, Any]:
    """Stack reflecting current Streamlit session + registry defaults."""
    chat = st.session_state.get("chat_model", DEFAULT_XAI_CHAT_MODEL)
    video = st.session_state.get("video_model", DEFAULT_IMAGINE_VIDEO_MODEL)
    base = model_stack_summary() if MODELS_AVAILABLE else model_stack_summary()
    if isinstance(base, dict):
        out = dict(base)
    else:
        out = {}
    out["cinematic"] = chat
    out["build"] = DEFAULT_XAI_BUILD_MODEL
    out["imagine_video"] = video
    out["session_reasoning"] = st.session_state.get("reasoning_level", "high")
    out["prompt_cache_key"] = st.session_state.get("prompt_cache_key") or None
    return out


def stack_banner_markdown() -> str:
    chat = st.session_state.get("chat_model", DEFAULT_XAI_CHAT_MODEL)
    video = st.session_state.get("video_model", DEFAULT_IMAGINE_VIDEO_MODEL)
    reason = st.session_state.get("reasoning_level", "high")
    cache = st.session_state.get("prompt_cache_key") or "—"
    return (
        f"**Grok 4.5 stack** · studio **v{STUDIO_VERSION}**  \n"
        f"Chat: `{chat}` · Video: `{video}` · Reasoning: **{reason}** · "
        f"`prompt_cache_key`: `{cache}`  \n"
        f"Build/coding: `{DEFAULT_XAI_BUILD_MODEL}` · CLI ≥ **{MIN_GROK_BUILD_CLI}** · "
        f"4.3 = 1M **opt-in only**"
    )


@st.cache_data(ttl=120, show_spinner=False)
def cached_models_verify() -> dict[str, Any]:
    try:
        return verify_model_compatibility()
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "issues": [str(exc)], "warnings": []}


def list_role_card_options() -> list[tuple[str, Path]]:
    if not AGENTS_DIR.exists():
        return []
    try:
        return [(p.stem.replace("_", " "), p) for p in list_role_card_files()]
    except NameError:
        return [
            (p.stem.replace("_", " "), p)
            for p in sorted(AGENTS_DIR.glob("*.md"))
            if p.stem not in {"AGENT_INDEX", "MODEL_LAYER_v3.7.1", "MODEL_LAYER_v3.6.7"}
            and not p.stem.startswith("IMAGINE_AGENT")
            and not p.stem.startswith("MODEL_LAYER")
        ]


def read_role_card_preview(path: Path, limit: int = ROLE_CARD_PREVIEW_CHARS) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + "\n\n…"


def is_streamlit_cloud() -> bool:
    """Detect Streamlit Community Cloud (or compatible hosted runtime)."""
    if os.getenv("STREAMLIT_SHARING_MODE"):
        return True
    if os.getenv("STREAMLIT_RUNTIME_ENV", "").lower() == "cloud":
        return True
    if os.getenv("IS_STREAMLIT_CLOUD", "").lower() in {"1", "true", "yes"}:
        return True
    # Community Cloud mounts the repo under /mount/src/<app>
    try:
        return Path("/mount/src").is_dir() and str(ROOT).startswith("/mount/src")
    except OSError:
        return False


def resolve_xai_api_key() -> str:
    """Resolve xAI API key: session override → env → Streamlit secrets (Cloud)."""
    session_key = str(st.session_state.get("xai_api_key") or "").strip()
    if session_key:
        return session_key
    env_key = (os.getenv("XAI_API_KEY") or "").strip()
    if env_key:
        return env_key
    try:
        secrets = st.secrets
        if "XAI_API_KEY" in secrets:
            return str(secrets["XAI_API_KEY"]).strip()
        if "xai" in secrets:
            nested = secrets["xai"]
            if "api_key" in nested:
                return str(nested["api_key"]).strip()
            if "XAI_API_KEY" in nested:
                return str(nested["XAI_API_KEY"]).strip()
    except Exception:  # noqa: BLE001 — secrets missing/unavailable is normal locally
        pass
    return ""


def sync_xai_api_key_to_environ() -> str:
    """Export resolved key to os.environ so tools/imagine_client dry-run checks work."""
    key = resolve_xai_api_key()
    if key:
        os.environ["XAI_API_KEY"] = key
    return key


def get_grok_client() -> OpenAI | None:
    api_key = sync_xai_api_key_to_environ()
    if not api_key:
        return None
    return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")


def run_cli(args: list[str], timeout: int = 120) -> tuple[int, str]:
    cmd = [sys.executable, str(ROOT / "tools" / "cinematic_studio_cli.py"), *args]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=ROOT)
    output = (result.stdout or "") + (result.stderr or "")
    return result.returncode, output.strip()


def execute_registered(
    action_id: str,
    answers: dict[str, str] | None = None,
    *,
    timeout: float = 90.0,
    mode: str = "inprocess",
) -> dict[str, Any]:
    """Run a registered ActionSpec via studio_core (Streamlit-safe dict result).

    Falls back to bare error dict if studio_core is unavailable.
    """
    try:
        from studio_core.services.execute import execute_action
    except ImportError:
        return {
            "ok": False,
            "returncode": 2,
            "stdout": "",
            "stderr": "studio_core.services.execute unavailable",
            "argv": [],
            "action_id": action_id,
            "errors": ["studio_core unavailable"],
            "mode": mode,
        }
    result = execute_action(
        action_id,
        answers or {},
        mode=mode,  # type: ignore[arg-type]
        timeout=timeout,
        cwd=ROOT,
    )
    return {
        "ok": bool(result.ok),
        "returncode": int(result.returncode),
        "stdout": result.stdout or "",
        "stderr": result.stderr or "",
        "argv": list(result.argv),
        "action_id": result.action_id or action_id,
        "errors": list(result.errors or []),
        "timed_out": bool(result.timed_out),
        "mode": result.mode,
        "output": result.output,
    }


def run_cli_or_action(
    action_id: str,
    answers: dict[str, str] | None = None,
    *,
    timeout: float = 90.0,
) -> tuple[int, str]:
    """Prefer ActionSpec execute; return (code, combined output) like :func:`run_cli`."""
    result = execute_registered(action_id, answers, timeout=timeout, mode="inprocess")
    out = (result.get("output") or "").strip()
    if not out:
        out = ((result.get("stdout") or "") + (result.get("stderr") or "")).strip()
    return int(result.get("returncode", 1)), out


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


def render_sidebar_stack() -> None:
    """Compact Model Layer strip for the sidebar."""
    st.markdown(
        f'<div class="stack-badge">Grok 4.5 · v{STUDIO_VERSION}</div>',
        unsafe_allow_html=True,
    )
    st.caption(
        f"Chat `{st.session_state.get('chat_model', DEFAULT_XAI_CHAT_MODEL)}` · "
        f"Video `{st.session_state.get('video_model', DEFAULT_IMAGINE_VIDEO_MODEL)}`"
    )
    if MODELS_AVAILABLE:
        vr = cached_models_verify()
        if vr.get("ok"):
            st.success("models verify ✅", icon="✅")
        else:
            st.warning("models verify ⚠️")
    with st.expander("Activation", expanded=False):
        st.code(ACTIVATION_PHRASE, language=None)
        st.caption("Paste MASTER_PROMPT.md in Grok Build, then use this phrase.")


def render_footer() -> None:
    st.divider()
    st.caption(
        f"Grok Imagine Cinematic Studio **v{STUDIO_VERSION}** · "
        f"**Grok 4.5** cinematic+Build · optional **4.3** (1M) · Imagine **1.0** cost / **1.5** audio · "
        f"CLI ≥ {MIN_GROK_BUILD_CLI} · "
        f"`{DOCS_MODEL_LAYER}` · `{DOCS_MODELS}` · "
        f"Install: `grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust`"
    )
    st.caption(
        "Independent community project — **not affiliated with or endorsed by xAI**. "
        "See repository `DISCLAIMER.md`."
    )
