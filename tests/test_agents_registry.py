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
    core_agent_count,
    get_role_card_path,
    list_role_card_files,
    total_agent_count,
)
from studio_paths import AGENTS_DIR


def test_core_agent_count() -> None:
    assert core_agent_count() == 23


def test_total_roster() -> None:
    assert total_agent_count() == 32


def test_production_pipeline_agents() -> None:
    pipeline = AGENTS.get("Production Pipeline", [])
    assert len(pipeline) == 4
    assert "Reference & Asset Curator v3.6.5" in pipeline
    assert "Image-to-Video Specialist v3.6.5" in pipeline


def test_role_cards_on_disk() -> None:
    cards = list_role_card_files()
    assert len(cards) == EXPECTED_ROLE_CARD_COUNT
    for name, rel in AGENT_ROLE_CARDS.items():
        path = AGENTS_DIR / rel
        assert path.is_file(), f"Missing role card for {name}: {rel}"


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