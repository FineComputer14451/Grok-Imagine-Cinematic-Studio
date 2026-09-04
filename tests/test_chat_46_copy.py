"""Agent-facing copy must not recommend sending grok-4.5 as the live default."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLUG = "grok-4.5"
# Mentions are fine when they document alias / wrap / old-packet normalize.
ALLOWED_HINTS = (
    "wrap",
    "alias",
    "legacy",
    "normaliz",
    "resolve",
    "old packet",
    "also pass",
    "also PASS",
)
# Specialist picker ids that happen to contain grok-4.5 as a prefix.
ALLOWED_SPECIALIST = (
    "grok-4.5-expert",
    "grok-4.5-multi",
    "grok-4.5-latest",
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
    if any(hint.lower() in low for hint in ALLOWED_HINTS):
        return True
    # Line only mentions 4.5 as a specialist/latest picker alias prefix.
    remainder = line
    for token in ALLOWED_SPECIALIST:
        remainder = remainder.replace(token, "")
    return SLUG not in remainder


def test_agent_facing_copy_does_not_recommend_grok_45() -> None:
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
        "Recommend grok-4.6 as the live chat default; grok-4.5 is a resolve alias only:\n"
        + "\n".join(offenders)
    )
