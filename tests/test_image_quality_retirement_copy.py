"""Agent-facing copy must not recommend sending grok-imagine-image-quality."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLUG = "grok-imagine-image-quality"
# Mentions are fine when they document retirement / do-not-send.
ALLOWED_HINTS = (
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


def _iter_agent_facing() -> list[Path]:
    paths: list[Path] = []
    skills = ROOT / ".grok" / "skills"
    if skills.is_dir():
        paths.extend(skills.rglob("SKILL.md"))
        paths.extend(skills.rglob("references/*.md"))
    personas = ROOT / ".grok" / "personas"
    if personas.is_dir():
        paths.extend(personas.glob("*.toml"))
    commands = ROOT / "commands"
    if commands.is_dir():
        paths.extend(commands.glob("*.md"))
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def _allowed(line: str) -> bool:
    low = line.lower()
    return any(hint in low for hint in ALLOWED_HINTS)


def test_agent_facing_copy_does_not_recommend_quality_slug() -> None:
    offenders: list[str] = []
    for path in _iter_agent_facing():
        text = path.read_text(encoding="utf-8")
        if SLUG not in text:
            continue
        rel = path.relative_to(ROOT)
        for lineno, line in enumerate(text.splitlines(), 1):
            if SLUG not in line:
                continue
            if _allowed(line):
                continue
            offenders.append(f"{rel}:{lineno}:{line.strip()}")
    assert offenders == [], (
        "Recommend grok-imagine-image-2.0 (quality=medium for hero); "
        "do not send grok-imagine-image-quality (retired 2026-11-02 → 2.0 quality=low):\n"
        + "\n".join(offenders)
    )
