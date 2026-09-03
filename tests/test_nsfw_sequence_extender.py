"""Tests for NSFW sequence extender module split."""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from aup_gate import ATTESTATION_ENV, AUPGateError, write_attestation  # noqa: E402
from nsfw_chain_qa import evaluate_nsfw_chain_qa  # noqa: E402
from nsfw_extension_config import TENSION_PROFILES  # noqa: E402
from nsfw_sequence_extender import (  # noqa: E402
    build_erotic_beat_sheet,
    plan_nsfw_extension,
    run_nsfw_chain_qa_scaffold,
)


def _attest_env() -> str:
    handle = tempfile.NamedTemporaryFile(prefix="aup-", suffix=".json", delete=False)
    handle.close()
    os.environ[ATTESTATION_ENV] = handle.name
    write_attestation(
        age_18_plus=True,
        imaginary_adults_only=True,
        not_a_real_person=True,
        aup_acknowledged=True,
        path=Path(handle.name),
    )
    return handle.name


def _cleanup(path: str) -> None:
    os.environ.pop(ATTESTATION_ENV, None)
    try:
        os.unlink(path)
    except OSError:
        pass


def test_tension_profiles_available() -> None:
    assert "passionate" in TENSION_PROFILES
    assert "slow_burn" in TENSION_PROFILES


def test_plan_nsfw_extension_builds_clips() -> None:
    path = _attest_env()
    try:
        seq = plan_nsfw_extension("Module Split Test", target_duration=60)
        assert len(seq["clips"]) >= 3
        assert seq["prompt_chain"]
        assert seq["cost_estimate"]
    finally:
        _cleanup(path)


def test_plan_nsfw_extension_requires_attestation() -> None:
    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        try:
            plan_nsfw_extension("No Attest", target_duration=60)
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            assert "attest" in str(exc)
    finally:
        os.environ.pop(ATTESTATION_ENV, None)


def test_beat_sheet_timing() -> None:
    beats = build_erotic_beat_sheet(target_duration=90, tension_profile="intense")
    assert beats[-1]["t_end"] > beats[0]["t_start"]


def test_chain_qa_go_decision() -> None:
    clip = {"clip_id": "clip_001"}
    scaffold = run_nsfw_chain_qa_scaffold(clip)
    assert scaffold["decision"] == "awaiting_scores"
    from nsfw_extension_config import NSFW_CHAIN_QA_CHECKS

    scores = {key: 8.0 for key, _, _ in NSFW_CHAIN_QA_CHECKS}
    result = evaluate_nsfw_chain_qa(clip, scores)
    assert result["decision"] == "go"


if __name__ == "__main__":
    test_tension_profiles_available()
    test_plan_nsfw_extension_requires_attestation()
    test_plan_nsfw_extension_builds_clips()
    test_beat_sheet_timing()
    test_chain_qa_go_decision()
    print("All NSFW sequence extender tests passed")