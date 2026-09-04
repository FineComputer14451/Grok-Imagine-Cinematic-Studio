"""Studio Academy copy must pin v3.11.4 and not recommend stale live defaults."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ACADEMY_DIRS = (ROOT / "web_academy", ROOT / "docs" / "academy")
SCAN_SUFFIXES = {".ts", ".tsx", ".md"}

ACTIVATION_STALE = "Activate Grok Imagine Cinematic Studio v3.9"
ACTIVATION_LIVE = "Activate Grok Imagine Cinematic Studio v3.11.4"
SLUG_45 = "grok-4.5"
QUALITY_SLUG = "grok-imagine-image-quality"
STALE_39_STAMPS = ("v3.9.1", "v3.9.2", "v3.9.3")
REQUIRED_CORE_IDS = (
    "dna-extractor",
    "color",
    "narrative",
    "sequence-extender",
    "continuity-guardian",
)
ABSENT_ROSTER_IDS = ("sound-bed", "set-deco")
MODULE_VERSION_FILES = (
    ROOT / "web_academy" / "src" / "data" / "erosforge.ts",
    ROOT / "web_academy" / "src" / "data" / "delivery-pack.ts",
    ROOT / "web_academy" / "src" / "data" / "continuity.ts",
)
MODULE_BADGE_ROUTES = (
    ROOT / "web_academy" / "src" / "routes" / "erosforge.tsx",
    ROOT / "web_academy" / "src" / "routes" / "delivery-pack.tsx",
    ROOT / "web_academy" / "src" / "routes" / "continuity.tsx",
)

ALLOWED_45_HINTS = (
    "wrap",
    "alias",
    "legacy",
    "normaliz",
    "resolve",
    "old packet",
    "also pass",
    "also PASS",
)

ALLOWED_QUALITY_HINTS = (
    "retir",
    "legacy",
    "deprecat",
    "rewrit",
    "redirect",
    "do not",
    "don't",
    "billed as",
    "was $0.05",
    "aliases still",
)

VIDEO_20_DENIAL_HINTS = (
    "no ",
    "not ",
    "isn't",
    "is not",
    "there is no",
    "image only",
    "2.0 is image",
)

SKIP_DIR_NAMES = {"node_modules", ".git", "dist", ".output"}


def _iter_academy_files() -> list[Path]:
    paths: list[Path] = []
    for base in ACADEMY_DIRS:
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            if path.suffix.lower() not in SCAN_SUFFIXES:
                continue
            paths.append(path)
    return paths


def test_activation_v3114_present_in_studio() -> None:
    studio = ROOT / "web_academy" / "src" / "data" / "studio.ts"
    text = studio.read_text(encoding="utf-8")
    assert ACTIVATION_LIVE in text, (
        f"{studio.relative_to(ROOT)} must export/use {ACTIVATION_LIVE!r}"
    )


def test_no_stale_v39_activation() -> None:
    offenders: list[str] = []
    for path in _iter_academy_files():
        text = path.read_text(encoding="utf-8")
        if ACTIVATION_STALE not in text:
            continue
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(text.splitlines(), 1):
            if ACTIVATION_STALE in line:
                offenders.append(f"{rel}:{lineno}:{line.strip()}")
    assert offenders == [], (
        "Academy activations must pin v3.11.4, not v3.9.x:\n" + "\n".join(offenders)
    )


def test_no_live_suite_count_62() -> None:
    offenders: list[str] = []
    for path in _iter_academy_files():
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            if "62-skill" in low or "62 skill" in low:
                offenders.append(f"{rel}:{lineno}:{line.strip()}")
    assert offenders == [], (
        "Live suite count is 64 skills, not 62:\n" + "\n".join(offenders)
    )


def _allowed_45(line: str) -> bool:
    low = line.lower()
    return any(hint.lower() in low for hint in ALLOWED_45_HINTS)


def _is_quiz_option_string(path: Path, line: str) -> bool:
    """Quoted quiz options may name stale slugs as distractors."""
    return path.name == "quiz.ts" and line.strip().startswith('"')


def test_grok_45_not_live_default() -> None:
    offenders: list[str] = []
    for path in _iter_academy_files():
        text = path.read_text(encoding="utf-8")
        if SLUG_45 not in text:
            continue
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(text.splitlines(), 1):
            if SLUG_45 not in line:
                continue
            if _is_quiz_option_string(path, line):
                continue
            if _allowed_45(line):
                continue
            offenders.append(f"{rel}:{lineno}:{line.strip()}")
    assert offenders == [], (
        "Recommend grok-4.6 as the live chat default; grok-4.5 is a resolve alias only:\n"
        + "\n".join(offenders)
    )


def _allowed_quality(line: str) -> bool:
    low = line.lower()
    return any(hint in low for hint in ALLOWED_QUALITY_HINTS)


def test_quality_slug_not_live_hero() -> None:
    offenders: list[str] = []
    for path in _iter_academy_files():
        text = path.read_text(encoding="utf-8")
        if QUALITY_SLUG not in text:
            continue
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(text.splitlines(), 1):
            if QUALITY_SLUG not in line:
                continue
            if _is_quiz_option_string(path, line):
                continue
            if _allowed_quality(line):
                continue
            offenders.append(f"{rel}:{lineno}:{line.strip()}")
    assert offenders == [], (
        "Recommend grok-imagine-image-2.0 (quality=medium for hero); "
        "do not send grok-imagine-image-quality as the live hero:\n"
        + "\n".join(offenders)
    )


def test_no_stale_v39_version_stamps() -> None:
    offenders: list[str] = []
    for path in _iter_academy_files():
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(text.splitlines(), 1):
            if any(stamp in line for stamp in STALE_39_STAMPS):
                offenders.append(f"{rel}:{lineno}:{line.strip()}")
    assert offenders == [], (
        "Academy copy must not pin leftover v3.9.1 / v3.9.2 / v3.9.3:\n"
        + "\n".join(offenders)
    )


def test_canonical_activations_and_tier3_core_pipeline() -> None:
    studio = ROOT / "web_academy" / "src" / "data" / "studio.ts"
    text = studio.read_text(encoding="utf-8")
    assert "ACTIVATE CHARACTER_DNA_EXTRACTOR" in text
    assert "ACTIVATE COLOR_GRADING" in text
    assert 'ACTIVATE CHARACTER_DNA"' not in text
    assert 'ACTIVATE COLOR_GRADE"' not in text
    start = text.find("export const TIERS")
    end = text.find("export const AGENTS")
    assert start != -1 and end != -1 and start < end
    tiers = text[start:end]
    pipeline = tiers[tiers.find("Full 25-Agent Pipeline") :]
    agents_start = pipeline.rfind("agents:")
    assert agents_start != -1
    agents_block = pipeline[agents_start:]
    assert "Character DNA Extractor" in agents_block
    assert "ErosForge" not in agents_block


def test_core_roster_ids_present() -> None:
    studio = ROOT / "web_academy" / "src" / "data" / "studio.ts"
    text = studio.read_text(encoding="utf-8")
    assert "CORE_AGENT_COUNT = 25" in text, "CORE_AGENT_COUNT must stay 25"
    start = text.find("export const AGENTS")
    end = text.find("export const ALL_SKILLS")
    assert start != -1 and end != -1 and start < end
    chunk = text[start:end]
    missing = [aid for aid in REQUIRED_CORE_IDS if f'id: "{aid}"' not in chunk]
    assert missing == [], f"25-core roster missing ids: {missing}"
    for name in (
        "Character DNA Extractor",
        "Color Grading Supervisor",
        "Narrative Arc Pacing Strategist",
        "Cinematic Sequence Extender",
        "Continuity Guardian",
    ):
        assert f'name: "{name}"' in chunk, f"25-core roster missing name: {name}"
    eros = chunk[chunk.find('id: "erosforge"') : chunk.find('id: "erosforge"') + 450]
    assert 'category: "special"' in eros, "ErosForge must stay category special (opt-in)"


def test_removed_roster_ids_absent() -> None:
    offenders: list[str] = []
    needles = [f'id: "{aid}"' for aid in ABSENT_ROSTER_IDS]
    for path in _iter_academy_files():
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(text.splitlines(), 1):
            if any(needle in line for needle in needles):
                offenders.append(f"{rel}:{lineno}:{line.strip()}")
    assert offenders == [], (
        "sound-bed and set-deco were removed from the Academy roster:\n"
        + "\n".join(offenders)
    )


def test_academy_module_footer_badge_3114() -> None:
    studio = ROOT / "web_academy" / "src" / "data" / "studio.ts"
    studio_text = studio.read_text(encoding="utf-8")
    assert 'STUDIO_VERSION = "3.11.4"' in studio_text
    assert 'ACADEMY_VERSION = "3.11.4"' in studio_text
    for path in MODULE_VERSION_FILES:
        text = path.read_text(encoding="utf-8")
        assert 'ACADEMY_MODULE_VERSION = "3.11.4"' in text, (
            f"{path.relative_to(ROOT)} must pin ACADEMY_MODULE_VERSION 3.11.4"
        )
    shell = (ROOT / "web_academy" / "src" / "components" / "shell.tsx").read_text(
        encoding="utf-8"
    )
    assert "v{ACADEMY_VERSION}" in shell
    assert "v{STUDIO_VERSION}" in shell
    index = (ROOT / "web_academy" / "src" / "routes" / "index.tsx").read_text(
        encoding="utf-8"
    )
    assert "v{STUDIO_VERSION}" in index
    for path in MODULE_BADGE_ROUTES:
        text = path.read_text(encoding="utf-8")
        assert "Academy v{ACADEMY_MODULE_VERSION}" in text, (
            f"{path.relative_to(ROOT)} must badge Academy v{{ACADEMY_MODULE_VERSION}}"
        )


def test_graduate_quiz_pass_keeps_seventy_percent() -> None:
    graduate = (ROOT / "web_academy" / "src" / "routes" / "graduate.tsx").read_text(
        encoding="utf-8"
    )
    quiz = (ROOT / "web_academy" / "src" / "data" / "quiz.ts").read_text(encoding="utf-8")
    assert "const QUIZ_PASS = 9" in graduate
    assert quiz.count('id: "q') == 13


def test_quiz_wrong_options_do_not_leak_answer() -> None:
    quiz = ROOT / "web_academy" / "src" / "data" / "quiz.ts"
    text = quiz.read_text(encoding="utf-8")
    assert "wrong — it is only a resolve alias" not in text
    assert "as the live hero (retired; rewrites" not in text
    assert "grok-4.6 (grok-4.5 is a resolve alias that wraps 4.6)" in text
    assert "grok-imagine-image-2.0 with quality=medium" in text
    assert "No — 2.0 is Image only; video is 1.0 / 1.5" in text


def test_video_20_not_a_live_product() -> None:
    offenders: list[str] = []
    for path in _iter_academy_files():
        if path.name == "quiz.ts":
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(text.splitlines(), 1):
            low = line.lower()
            if "video 2.0" not in low and "grok-imagine-video-2" not in low:
                continue
            if any(hint in low for hint in VIDEO_20_DENIAL_HINTS):
                continue
            offenders.append(f"{rel}:{lineno}:{line.strip()}")
    assert offenders == [], (
        "Video 2.0 is not a product; mentions must deny it:\n" + "\n".join(offenders)
    )


def test_academy_api_docs_official_files_imagine_surface() -> None:
    """Academy /docs must pin the public Files + Imagine REST paths from docs.x.ai."""
    path = ROOT / "web_academy" / "src" / "data" / "api-docs.ts"
    text = path.read_text(encoding="utf-8")
    required = (
        'path: "/v1/files"',
        'path: "/v1/files/{id}"',
        'path: "/v1/images/generations"',
        'path: "/v1/images/edits"',
        'path: "/v1/videos/generations"',
        'path: "/v1/videos/{request_id}"',
        'method: "DELETE"',
        "expires_after MUST appear before the file part",
        '"status": "done"',
        '"file_id": "file_…"',
    )
    missing = [needle for needle in required if needle not in text]
    assert missing == [], f"{path.relative_to(ROOT)} missing official surface: {missing}"
    assert "/v1/videos (async start)" not in text
    assert "api.x.ai/v1/…/{request_id}" not in text
    assert '"status": "completed"' not in text
    assert "multipart or JSON per docs.x.ai Imagine API" not in text
    # Image edits are JSON; OpenAI multipart is unsupported.
    assert "images.edit() multipart is NOT supported" in text
    docs_route = ROOT / "web_academy" / "src" / "routes" / "docs.tsx"
    route = docs_route.read_text(encoding="utf-8")
    assert "DELETE:" in route, f"{docs_route.relative_to(ROOT)} must style DELETE"
