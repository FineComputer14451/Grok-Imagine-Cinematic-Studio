"""Tests for agent roster and role card registry consistency."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from cli.shared import (  # noqa: E402
    AGENT_ROLE_CARDS,
    AGENTS,
    EXPECTED_ROLE_CARD_COUNT,
    ROLE_CARD_ALIAS_FILES,
    ROLE_CARD_SHARED_DOCS,
    core_agent_count,
    get_role_card_path,
    list_role_card_files,
    total_agent_count,
)
from studio_paths import AGENTS_DIR


def test_core_agent_count() -> None:
    # Core Leadership … Post-Production + Grok Doctor + Multi-Clip Continuity
    assert core_agent_count() == 25


def _md_core_slugs(text: str, start: str, end: str) -> list[str]:
    i = text.index(start)
    j = text.index(end, i)
    block = text[i:j]
    slugs = []
    for line in block.splitlines():
        if line.startswith("|") and "`" in line:
            parts = [p.strip().strip("`") for p in line.split("|") if p.strip()]
            for p in parts:
                if p.startswith(("studio-", "mega-", "director-", "production-",
                                 "post-production-", "character-", "performance-",
                                 "identity-", "narrative-", "sequence-",
                                 "cinematic-sequence-", "continuity-", "multi-clip-",
                                 "imagine-prompt-", "quality-", "grok-doctor",
                                 "workflow-", "sonic-", "foley-", "stunt-",
                                 "vfx-", "key-art-", "trailer-", "localization-",
                                 "ai-polish-", "erosforge-")):
                    slugs.append(p)
                    break
    return slugs


def test_docs_core_25_matches_cli() -> None:
    """Published 25-core lists: DNA in, ErosForge opt-in (CLI CORE_AGENT_CATEGORIES)."""
    agents_md = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    slugs = _md_core_slugs(
        agents_md,
        "## Core Agent Skill Slugs",
        "**High-traffic specialists",
    )
    assert "character-dna-extractor" in slugs
    assert "erosforge-nsfw-director" not in slugs
    assert "grok-doctor" in slugs
    assert "multi-clip-continuity-orchestrator" in slugs
    assert len(slugs) == 25

    cheat = (ROOT / "docs" / "guides" / "OPERATOR_CHEAT_SHEET.md").read_text(
        encoding="utf-8"
    )
    cheat_slugs = _md_core_slugs(
        cheat,
        "## 25 Role-Card core agents",
        "Matches `tools/cli/shared.py`",
    )
    assert cheat_slugs[5] == "character-dna-extractor"
    assert "erosforge-nsfw-director" not in cheat_slugs
    assert len(cheat_slugs) == 25

    prompt = (ROOT / "MASTER_PROMPT.md").read_text(encoding="utf-8")
    crew = prompt.split("## 🧠 25-Agent Professional Film Crew")[1].split(
        "## 🏗️ Core Protocols"
    )[0]
    core_part, opt_in = crew.split("### Specialist (Opt-in)")
    assert "Character DNA Extractor" in core_part
    assert "Grok Doctor" in core_part
    assert "Multi-Clip Continuity Orchestrator" in core_part
    assert "ErosForge" not in core_part
    assert "ErosForge" in opt_in


def test_docs_studio_pin_matches_version() -> None:
    """Agent Index, Wave A cards, and skill manifest pin the current VERSION."""
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    idx = (ROOT / "references" / "agents" / "AGENT_INDEX.md").read_text(
        encoding="utf-8"
    )
    assert f"**Studio:** v{version}" in idx
    assert f"Activate Grok Imagine Cinematic Studio v{version}" in idx
    assert "Activate Grok Imagine Cinematic Studio v3.9.0" not in idx
    stale = (
        "Cinematic Studio v3.9.0+ (Wave A scaffold)",
        "Cinematic Studio v3.8.7+ (Wave A scaffold)",
    )
    agents_dir = ROOT / "references" / "agents"
    for path in sorted(agents_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for needle in stale:
            assert needle not in text, f"{path.name} still has {needle}"
    header = (ROOT / "scripts" / "required_skills.manifest").read_text(
        encoding="utf-8"
    ).splitlines()[0]
    assert f"v{version}" in header


def test_grok_doctor_explicit_path_not_a_fake_agent() -> None:
    card = (AGENTS_DIR / "Grok_Doctor.md").read_text(encoding="utf-8")
    assert "There is no separate NSFW Prompt Optimizer agent" in card
    assert "MODEL_LAYER_v4.5.md" in card


def test_agent_index_buckets_match_cli() -> None:
    idx = (ROOT / "references" / "agents" / "AGENT_INDEX.md").read_text(
        encoding="utf-8"
    )
    tech = idx.split("## Technical & Continuity")[1].split("## Audio")[0]
    pipeline = idx.split("## Production Pipeline")[1].split("## Wave A")[0]
    wave = idx.split("## Wave A Specialists")[1].split("## Refinement")[0]
    assert "Costume_Wardrobe_Continuity.md" in pipeline
    assert "Costume_Wardrobe_Continuity.md" not in tech
    assert "Plate_Motion_Readiness_Lead.md" in wave
    assert "Plate_Motion_Readiness_Lead.md" not in pipeline
    assert "Contact_Micro_Physics_Specialist.md" in wave
    assert "Contact_Micro_Physics_Specialist.md" not in pipeline


def test_skills_declare_model_compatibility() -> None:
    from studio_health import skills_missing_model_compatibility

    assert skills_missing_model_compatibility() == []


def test_role_card_template_is_v45() -> None:
    tpl = (
        ROOT
        / ".grok"
        / "skills"
        / "skill-agent-architect"
        / "references"
        / "role-card-template.md"
    ).read_text(encoding="utf-8")
    assert tpl.startswith("# Role Card Template v4.5")
    assert "MODEL_LAYER_v4.5.md" in tpl
    assert "studio v3.10.0" in tpl
    assert "MODEL_LAYER_v3.7.1.md" not in tpl


def test_narrative_arc_activation_aligned() -> None:
    """Index, cheat sheet, Role Card, and skill share ACTIVATE NARRATIVE_ARC."""
    card = (AGENTS_DIR / "Narrative_Arc_Pacing_Strategist_v3.5.md").read_text(
        encoding="utf-8"
    )
    idx = (ROOT / "references" / "agents" / "AGENT_INDEX.md").read_text(
        encoding="utf-8"
    )
    skill = (
        ROOT / ".grok" / "skills" / "narrative-arc-pacing-strategist" / "SKILL.md"
    ).read_text(encoding="utf-8")
    cheat = (ROOT / "docs" / "guides" / "OPERATOR_CHEAT_SHEET.md").read_text(
        encoding="utf-8"
    )
    for text, label in (
        (card, "Role Card"),
        (idx, "AGENT_INDEX"),
        (skill, "SKILL.md"),
        (cheat, "OPERATOR_CHEAT_SHEET"),
    ):
        assert "ACTIVATE NARRATIVE_ARC" in text, f"{label} missing ACTIVATE NARRATIVE_ARC"
    assert "ACTIVATE NARRATIVE_STRATEGIST" in card


STILLS_IMAGE_20_CARDS = (
    "Character_DNA_Extractor_v3.5.md",
    "Identity_Lock_Specialist.md",
    "Imagine_Prompt_Master.md",
    "Key_Art_Poster_Designer_v3.5.md",
    "I2I_Cinematic_Refiner.md",
    "I2I_Refiner.md",
    "Production_Designer_Set_Decorator_v3.5.md",
    "Reference_Asset_Curator.md",
)


def test_mapped_role_cards_have_preferred_model_yaml() -> None:
    missing = [
        rel
        for rel in AGENT_ROLE_CARDS.values()
        if "preferred_model:" not in (AGENTS_DIR / rel).read_text(encoding="utf-8")
    ]
    assert missing == [], f"Role Cards missing preferred_model YAML: {missing}"


def test_stills_role_cards_route_image_2_0() -> None:
    """Hero-plate agents declare Image 2.0; no Video 2.0 product."""
    agents_dir = ROOT / "references" / "agents"
    for name in STILLS_IMAGE_20_CARDS:
        text = (agents_dir / name).read_text(encoding="utf-8")
        assert "grok-imagine-image-2.0" in text, f"{name} missing Image 2.0 slug"
        if name != "Reference_Asset_Curator.md":
            assert "no** Imagine Video 2.0" in text or "no Imagine Video 2.0" in text, (
                f"{name} missing no-Video-2.0 rule"
            )


def test_total_roster() -> None:
    # core 25 + i2i 2 + pipeline 6 + Wave A 8 + NSFW opt-in 3 + meta 3
    assert total_agent_count() == 47


def test_meta_tools_agents() -> None:
    meta = AGENTS.get("Meta & Tools", [])
    assert len(meta) == 3
    assert "GitHub Repo Manager v4.5" in meta
    assert "Quota Dashboard v4.5" in meta
    assert "Extend Frame to Video v4.5" in meta
    assert "GitHub Repo Manager v4.5" not in AGENTS["Core Leadership"]


def test_production_pipeline_agents() -> None:
    pipeline = AGENTS.get("Production Pipeline", [])
    assert len(pipeline) == 6
    assert "Reference & Asset Curator v3.6.5" in pipeline
    assert "Image-to-Video Specialist v3.6.5" in pipeline
    assert "Multi-Character Identity Arbiter v3.6.5" in pipeline
    assert "Costume & Wardrobe Continuity v4.5" in pipeline
    # Wave A plate/contact must not pollute the production pipeline bucket
    assert "Plate & Motion Readiness Lead v4.5" not in pipeline
    assert "Contact & Micro-Physics Specialist v4.5" not in pipeline


def test_wave_a_specialists_bucket() -> None:
    wave = AGENTS.get("Wave A Specialists", [])
    assert len(wave) == 8
    assert "Plate & Motion Readiness Lead v4.5" in wave
    assert "Parallel Brief Dispatcher v4.5" in wave
    # Non–Wave-A core agents must not live here
    assert "Grok Doctor v4.5" not in wave
    assert "Multi-Clip Continuity Orchestrator v4.5" not in wave
    tech = AGENTS.get("Technical & Continuity", [])
    assert "Grok Doctor v4.5" in tech
    assert "Multi-Clip Continuity Orchestrator v4.5" in tech


def test_role_cards_on_disk() -> None:
    cards = list_role_card_files()
    assert len(cards) == EXPECTED_ROLE_CARD_COUNT
    listed_names = {p.name for p in cards}
    expected_names = set(AGENT_ROLE_CARDS.values())
    assert listed_names == expected_names, (
        f"extras={sorted(listed_names - expected_names)}; "
        f"missing={sorted(expected_names - listed_names)}"
    )
    for name, rel in AGENT_ROLE_CARDS.items():
        path = AGENTS_DIR / rel
        assert path.is_file(), f"Missing role card for {name}: {rel}"


def test_shared_agent_docs_excluded_from_role_cards() -> None:
    """Non-role protocol/model docs must stay in ROLE_CARD_SHARED_DOCS."""
    card_names = {p.name for p in list_role_card_files()}
    for shared in ROLE_CARD_SHARED_DOCS:
        path = AGENTS_DIR / shared
        if path.is_file():
            assert shared not in card_names, f"{shared} incorrectly listed as a Role Card"
    # Protocol + model layer docs that ship with the suite
    for required_shared in (
        "MODEL_LAYER_v3.7.1.md",
        "IMAGINE_AGENT_MODE_HANDOFF_v3.7.1.md",
        "IMAGINE_SURFACES.md",
    ):
        assert required_shared in ROLE_CARD_SHARED_DOCS
        assert (AGENTS_DIR / required_shared).is_file()
    listed = {p.name for p in list_role_card_files()}
    for alias in ROLE_CARD_ALIAS_FILES:
        assert (AGENTS_DIR / alias).is_file(), f"missing alias {alias}"
        assert alias not in listed, f"{alias} should not count as a mapped Role Card"


def test_role_card_lookup() -> None:
    assert get_role_card_path("Studio Director v3.6.5") is not None
    assert get_role_card_path("ErosForge NSFW Director v3.6.5") is not None
    assert get_role_card_path("NSFW Quota Orchestrator v1.0") is not None


def test_agents_dict_matches_role_cards() -> None:
    listed = [name for names in AGENTS.values() for name in names]
    assert len(listed) == len(AGENT_ROLE_CARDS)
    assert set(listed) == set(AGENT_ROLE_CARDS)


if __name__ == "__main__":
    test_core_agent_count()
    test_docs_core_25_matches_cli()
    test_docs_studio_pin_matches_version()
    test_narrative_arc_activation_aligned()
    test_grok_doctor_explicit_path_not_a_fake_agent()
    test_agent_index_buckets_match_cli()
    test_skills_declare_model_compatibility()
    test_role_card_template_is_v45()
    test_mapped_role_cards_have_preferred_model_yaml()
    test_stills_role_cards_route_image_2_0()
    test_total_roster()
    test_production_pipeline_agents()
    test_role_cards_on_disk()
    test_role_card_lookup()
    test_agents_dict_matches_role_cards()
    test_meta_tools_agents()
    print("All agent registry tests passed")