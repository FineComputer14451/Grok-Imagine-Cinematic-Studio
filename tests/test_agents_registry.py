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
    ROLE_CARD_SHARED_DOCS,
    core_agent_count,
    get_role_card_path,
    list_role_card_files,
    total_agent_count,
)
from studio_paths import AGENTS_DIR


def test_core_agent_count() -> None:
    assert core_agent_count() == 23


def test_total_roster() -> None:
    assert total_agent_count() == 33


def test_production_pipeline_agents() -> None:
    pipeline = AGENTS.get("Production Pipeline", [])
    assert len(pipeline) == 5
    assert "Reference & Asset Curator v3.6.5" in pipeline
    assert "Image-to-Video Specialist v3.6.5" in pipeline
    assert "Multi-Character Identity Arbiter v3.6.5" in pipeline


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
    ):
        assert required_shared in ROLE_CARD_SHARED_DOCS
        assert (AGENTS_DIR / required_shared).is_file()


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
    test_total_roster()
    test_production_pipeline_agents()
    test_role_cards_on_disk()
    test_role_card_lookup()
    test_agents_dict_matches_role_cards()
    print("All agent registry tests passed")