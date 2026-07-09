"""Guided Production Bible wizard: stage data and pure kwargs mapping.

No I/O, Typer, Streamlit, or project_state. Final assembly always goes through
``build_production_bible`` in ``cli.production``.
"""

from __future__ import annotations

from typing import Any, TypedDict

from models import DEFAULT_IMAGINE_VIDEO_MODEL, DEFAULT_XAI_CHAT_MODEL

# Kwargs accepted by build_production_bible (excluding agents_dir / locked_title).
ALLOWED_BIBLE_KWARGS = frozenset(
    {
        "title",
        "genre",
        "director_signature",
        "target_duration_seconds",
        "complexity",
        "chat_model",
        "video_model",
        "notes",
    }
)

DEFAULT_GENRE = "Cinematic"
DEFAULT_COMPLEXITY = "Medium"
DEFAULT_DURATION = 60


class StageField(TypedDict):
    key: str
    prompt: str
    example: str
    required: bool
    default: str | int | None


class Stage(TypedDict):
    id: str
    title: str
    fields: list[StageField]


STAGES: list[Stage] = [
    {
        "id": "story",
        "title": "Story Idea & Title",
        "fields": [
            {
                "key": "title",
                "prompt": "Project title",
                "example": "Rain Code",
                "required": True,
                "default": None,
            },
            {
                "key": "logline",
                "prompt": "Core story / logline (1–2 sentences, optional)",
                "example": "A detective hunts a rogue AI through neon rain.",
                "required": False,
                "default": None,
            },
        ],
    },
    {
        "id": "genre",
        "title": "Genre, Tone & Signature",
        "fields": [
            {
                "key": "genre",
                "prompt": "Primary genre",
                "example": "Neo-Noir / Sci-Fi",
                "required": True,
                "default": DEFAULT_GENRE,
            },
            {
                "key": "director_signature",
                "prompt": "Tone / director signature phrase (optional)",
                "example": "Wet neon, handheld urgency, moral grey",
                "required": False,
                "default": None,
            },
            {
                "key": "complexity",
                "prompt": "Complexity (low / medium / high)",
                "example": "Medium",
                "required": False,
                "default": DEFAULT_COMPLEXITY,
            },
        ],
    },
    {
        "id": "characters",
        "title": "Characters & World (light)",
        "fields": [
            {
                "key": "characters_text",
                "prompt": "1–3 key characters (one-liners; not DNA profiles)",
                "example": "Mara: exhausted detective. Kai: rogue AI in a human shell.",
                "required": False,
                "default": None,
            },
            {
                "key": "world_text",
                "prompt": "Key setting / world rule (short)",
                "example": "Tokyo 2091; rain never stops; cameras lie.",
                "required": False,
                "default": None,
            },
        ],
    },
    {
        "id": "technicals",
        "title": "Technical Specs",
        "fields": [
            {
                "key": "target_duration_seconds",
                "prompt": "Target duration in seconds",
                "example": "90",
                "required": True,
                "default": DEFAULT_DURATION,
            },
            {
                "key": "video_model",
                "prompt": "Imagine video model (1.0 default or 1.5 for native audio)",
                "example": "1.0 or 1.5",
                "required": False,
                "default": DEFAULT_IMAGINE_VIDEO_MODEL,
            },
            {
                "key": "chat_model",
                "prompt": "xAI chat model (optional)",
                "example": "grok-4.5 or grok-4.3 (1M)",
                "required": False,
                "default": DEFAULT_XAI_CHAT_MODEL,
            },
            {
                "key": "tech_notes",
                "prompt": "Audio / aspect / delivery notes (optional free text)",
                "example": "16:9; sparse score; native rain SFX if using 1.5",
                "required": False,
                "default": None,
            },
        ],
    },
    {
        "id": "review",
        "title": "Review & Generate",
        "fields": [],
    },
]

_STAGE_BY_ID: dict[str, Stage] = {s["id"]: s for s in STAGES}


def stage_by_id(stage_id: str) -> Stage:
    """Return a stage by id or raise KeyError."""
    try:
        return _STAGE_BY_ID[stage_id]
    except KeyError as exc:
        raise KeyError(f"Unknown stage id: {stage_id!r}") from exc


def _is_blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def validate_answers(stage_id: str, answers: dict[str, Any]) -> list[str]:
    """Return human-readable errors for missing required fields on a stage."""
    stage = stage_by_id(stage_id)
    errors: list[str] = []
    for field in stage["fields"]:
        if not field["required"]:
            continue
        key = field["key"]
        raw = answers.get(key)
        if _is_blank(raw):
            # Allow configured default to satisfy required (e.g. duration 60)
            if field["default"] is not None and not _is_blank(field["default"]):
                continue
            errors.append(f"{field['prompt']} is required ({key})")
            continue
        if key == "target_duration_seconds":
            try:
                n = int(raw)
                if n <= 0:
                    errors.append("Target duration must be a positive integer (seconds)")
            except (TypeError, ValueError):
                errors.append("Target duration must be a positive integer (seconds)")
    return errors


def build_notes(answers: dict[str, Any]) -> str:
    """Deterministic free-text rollup for the Bible notes field."""
    sections: list[tuple[str, str]] = [
        ("Logline", "logline"),
        ("Characters", "characters_text"),
        ("World", "world_text"),
        ("Technical notes", "tech_notes"),
    ]
    parts: list[str] = []
    for label, key in sections:
        val = answers.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(f"{label}: {val.strip()}")
    return "\n".join(parts)


def answers_to_kwargs(answers: dict[str, Any]) -> dict[str, Any]:
    """Map wizard answers to kwargs for ``build_production_bible``.

    Only returns keys in ALLOWED_BIBLE_KWARGS. Omits empty optional fields.
    """
    title = answers.get("title")
    if _is_blank(title):
        raise ValueError("title is required")
    title_s = str(title).strip()

    genre = answers.get("genre")
    genre_s = str(genre).strip() if not _is_blank(genre) else DEFAULT_GENRE

    complexity = answers.get("complexity")
    complexity_s = (
        str(complexity).strip() if not _is_blank(complexity) else DEFAULT_COMPLEXITY
    )

    duration_raw = answers.get("target_duration_seconds", DEFAULT_DURATION)
    if _is_blank(duration_raw):
        duration = DEFAULT_DURATION
    else:
        duration = int(duration_raw)
        if duration <= 0:
            raise ValueError("target_duration_seconds must be positive")

    kwargs: dict[str, Any] = {
        "title": title_s,
        "genre": genre_s,
        "target_duration_seconds": duration,
        "complexity": complexity_s,
    }

    director = answers.get("director_signature")
    if not _is_blank(director):
        kwargs["director_signature"] = str(director).strip()

    video_model = answers.get("video_model")
    if not _is_blank(video_model):
        kwargs["video_model"] = str(video_model).strip()

    chat_model = answers.get("chat_model")
    if not _is_blank(chat_model):
        kwargs["chat_model"] = str(chat_model).strip()

    notes = build_notes(answers)
    if notes:
        kwargs["notes"] = notes

    unknown = set(kwargs) - ALLOWED_BIBLE_KWARGS
    if unknown:
        raise RuntimeError(f"internal: unexpected bible kwargs {unknown}")
    return kwargs


def should_run_wizard(
    *,
    wizard_flag: bool,
    title: str | None,
    stdin_isatty: bool,
) -> bool:
    """Policy: wizard only via --wizard or missing title on a TTY."""
    if wizard_flag:
        return True
    if title is None or (isinstance(title, str) and not title.strip()):
        return stdin_isatty
    return False


def summary_and_next_steps(bible: dict[str, Any]) -> str:
    """Human-readable summary + text-only next CLI commands (not executed)."""
    title = bible.get("project_title", "Untitled")
    genre = bible.get("genre", DEFAULT_GENRE)
    duration = bible.get("target_duration_seconds", DEFAULT_DURATION)
    status = bible.get("status", "Ready for production")
    lines = [
        f"Production Bible ready: {title}",
        f"Genre: {genre} · Duration: {duration}s · Status: {status}",
        "",
        "Next steps (run manually as needed):",
        f'  python tools/cinematic_studio_cli.py dna init "Lead Character" \\',
        f'    --core "Core identity" --anchor "Distinctive visual anchor"',
        "  python tools/cinematic_studio_cli.py quota budget --tier supergrok_pro",
        f'  python tools/cinematic_studio_cli.py sequence init "Act 1" '
        f'--duration {duration} --genre "{genre}"',
        "  python tools/cinematic_studio_cli.py validate",
    ]
    return "\n".join(lines)
