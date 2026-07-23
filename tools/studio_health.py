"""Shared studio workspace health metrics."""

from __future__ import annotations

from pathlib import Path

from studio_paths import SKILLS_DIR, STUDIO_ROOT

SKILLS_ROOT = SKILLS_DIR
MIN_EXPECTED_SKILLS = 40


def count_skills(skills_root: Path | None = None) -> int:
    """Count skill directories with a SKILL.md manifest."""
    root = skills_root if skills_root is not None else SKILLS_ROOT
    if not root.is_dir():
        return 0
    return sum(1 for d in root.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())


def skill_names(skills_root: Path | None = None) -> set[str]:
    """Return skill directory names that contain SKILL.md."""
    root = skills_root if skills_root is not None else SKILLS_ROOT
    if not root.is_dir():
        return set()
    return {d.name for d in root.iterdir() if d.is_dir() and (d / "SKILL.md").is_file()}


def skills_missing_model_compatibility(skills_root: Path | None = None) -> list[str]:
    """Return skill names whose SKILL.md lacks a model_compatibility marker."""
    root = skills_root if skills_root is not None else SKILLS_ROOT
    missing: list[str] = []
    if not root.is_dir():
        return missing
    for d in sorted(root.iterdir(), key=lambda p: p.name):
        skill_md = d / "SKILL.md"
        if not d.is_dir() or not skill_md.is_file():
            continue
        try:
            text = skill_md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            missing.append(d.name)
            continue
        if "model_compatibility" not in text:
            missing.append(d.name)
    return missing


def user_skill_names(home: Path | None = None) -> set[str]:
    """Skill dir names under ~/.grok/skills (or home/.grok/skills)."""
    base = (home if home is not None else Path.home()) / ".grok" / "skills"
    if not base.is_dir():
        return set()
    return {d.name for d in base.iterdir() if d.is_dir()}


def user_studio_skill_dupes(
    home: Path | None = None,
    skills_root: Path | None = None,
) -> list[str]:
    """Studio skill names also present under the user skills directory (declutter debt)."""
    return sorted(skill_names(skills_root) & user_skill_names(home))


def read_version_file(path: Path) -> str | None:
    """Read a VERSION file; return stripped text or None."""
    if not path.is_file():
        return None
    try:
        text = path.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    return text or None


def studio_version(studio_root: Path | None = None) -> str | None:
    """VERSION at the studio/repo root."""
    root = studio_root if studio_root is not None else STUDIO_ROOT
    return read_version_file(root / "VERSION")
