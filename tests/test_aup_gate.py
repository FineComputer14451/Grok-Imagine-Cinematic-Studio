"""Fail-closed SpaceXAI AUP gates — metadata/stub prompts only."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from aup_gate import (  # noqa: E402
    AUP_URL,
    AUPGateError,
    ATTESTATION_ENV,
    attestation_is_valid,
    aup_status,
    gate_dna,
    gate_imagine_prompt,
    gate_nsfw_batch,
    gate_nsfw_shot,
    gate_planning_packet,
    gate_text,
    require_attestation,
    scan_csam,
    write_attestation,
)


def _attest_env() -> tuple[str, str]:
    handle = tempfile.NamedTemporaryFile(prefix="aup-", suffix=".json", delete=False)
    handle.close()
    path = handle.name
    os.environ[ATTESTATION_ENV] = path
    write_attestation(
        age_18_plus=True,
        imaginary_adults_only=True,
        not_a_real_person=True,
        aup_acknowledged=True,
        path=Path(path),
    )
    return path, ATTESTATION_ENV


def _cleanup(path: str) -> None:
    os.environ.pop(ATTESTATION_ENV, None)
    try:
        os.unlink(path)
    except OSError:
        pass


def test_attestation_requires_all_flags() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "attestation.json"
        try:
            write_attestation(
                age_18_plus=True,
                imaginary_adults_only=True,
                not_a_real_person=False,
                aup_acknowledged=True,
                path=path,
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            assert "All four attestations" in str(exc)
        assert not path.exists()


def test_checkbox_is_not_attestation() -> None:
    os.environ[ATTESTATION_ENV] = str(Path(__file__).resolve().parent / "missing-aup-attestation.json")
    try:
        require_attestation()
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "nsfw attest" in str(exc)
        assert AUP_URL in str(exc)
    finally:
        os.environ.pop(ATTESTATION_ENV, None)


def test_valid_attestation_roundtrip() -> None:
    path, _ = _attest_env()
    try:
        data = json.loads(Path(path).read_text())
        assert attestation_is_valid(data)
        assert require_attestation()["age_18_plus"] is True
    finally:
        _cleanup(path)


def test_csam_keyword_refuse_uses_stubs_only() -> None:
    assert scan_csam("loli aesthetic")
    assert scan_csam("schoolgirl uniform")
    assert scan_csam("aged down")
    assert not scan_csam("childhood bedroom flashback")
    try:
        gate_text("underage character study")
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "NCMEC" in str(exc)


def test_explicit_beyond_r_refused_when_nsfw() -> None:
    path, _ = _attest_env()
    try:
        try:
            gate_text("creampie close-up", nsfw=True)
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            assert "R-rated" in str(exc)
        gate_text("tender implied intimacy, clothing on, R-rated", nsfw=True)
    finally:
        _cleanup(path)


def test_hidden_camera_refused() -> None:
    path, _ = _attest_env()
    try:
        try:
            gate_text("hidden camera through window", nsfw=True)
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            assert "hidden-camera" in str(exc) or "nudify" in str(exc)
    finally:
        _cleanup(path)


def test_nsfw_shot_refuses_reference_image() -> None:
    path, _ = _attest_env()
    try:
        try:
            gate_nsfw_shot(
                {
                    "description": "candlelit embrace",
                    "tier": "hero",
                    "explicit_level": "moderate",
                    "has_reference": True,
                }
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            assert "reference" in str(exc).lower()
    finally:
        _cleanup(path)


def test_nsfw_shot_refuses_explicit_level() -> None:
    path, _ = _attest_env()
    try:
        try:
            gate_nsfw_shot(
                {
                    "description": "slow reveal",
                    "tier": "hero",
                    "explicit_level": "explicit",
                }
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            assert "suggestive or moderate" in str(exc)
    finally:
        _cleanup(path)


def test_nsfw_batch_allows_r_rated_imaginary() -> None:
    path, _ = _attest_env()
    try:
        gate_nsfw_batch(
            "Hero Session",
            [{"description": "Cover frame candlelit embrace", "tier": "hero", "explicit_level": "suggestive"}],
        )
    finally:
        _cleanup(path)


def test_dna_intimate_requires_imaginary_adult_no_photo() -> None:
    path, _ = _attest_env()
    try:
        try:
            gate_dna(
                {
                    "character_name": "Mara",
                    "core_identity": "adult fictional lead",
                    "facial_dna": "sharp cheekbones",
                    "nsfw_notes": "implied intimacy continuity",
                    "subject_kind": "unspecified",
                    "reference_image_ids": [],
                }
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            assert "imaginary_adult" in str(exc)

        try:
            gate_dna(
                {
                    "character_name": "Mara",
                    "core_identity": "adult fictional lead",
                    "facial_dna": "sharp cheekbones",
                    "nsfw_notes": "implied intimacy continuity",
                    "subject_kind": "imaginary_adult",
                    "reference_image_ids": ["img_123"],
                }
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            lowered = str(exc).lower()
            assert "photos" in lowered or "reference" in lowered

        gate_dna(
            {
                "character_name": "Mara",
                "core_identity": "adult fictional lead",
                "facial_dna": "sharp cheekbones",
                "nsfw_notes": "implied intimacy continuity",
                "subject_kind": "imaginary_adult",
                "reference_image_ids": [],
            }
        )
    finally:
        _cleanup(path)


def test_sfw_dna_with_refs_still_allowed() -> None:
    gate_dna(
        {
            "character_name": "Elena Voss",
            "core_identity": "detective",
            "facial_dna": "grey eyes",
            "subject_kind": "unspecified",
            "reference_image_ids": ["hero_still"],
        }
    )


def test_video_extend_csam_refused() -> None:
    from imagine_client import submit_video_extension

    try:
        submit_video_extension(
            "underage character study",
            video_url="https://example.invalid/clip.mp4",
            dry_run=True,
        )
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "minor-coded" in str(exc) or "CSAM" in str(exc)


def test_video_edit_intimate_requires_attestation() -> None:
    from imagine_client import submit_video_edit

    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        try:
            submit_video_edit(
                "erotic candlelit two-shot",
                video_url="https://example.invalid/clip.mp4",
                dry_run=True,
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            assert "attest" in str(exc)
    finally:
        os.environ.pop(ATTESTATION_ENV, None)


def test_video_extend_attested_intimate_allowed() -> None:
    from imagine_client import submit_video_extension

    path, _ = _attest_env()
    try:
        resp = submit_video_extension(
            "erotic clothing-on R-rated continuation",
            video_url="https://example.invalid/clip.mp4",
            dry_run=True,
        )
        assert resp.get("dry_run") is True
        assert resp.get("mode") == "video_extend"
    finally:
        _cleanup(path)



def test_video_edit_csam_refused() -> None:
    from imagine_client import submit_video_edit

    try:
        submit_video_edit(
            "underage character study",
            video_url="https://example.invalid/clip.mp4",
            dry_run=True,
        )
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "minor-coded" in str(exc) or "CSAM" in str(exc)


def test_video_extend_intimate_requires_attestation() -> None:
    from imagine_client import submit_video_extension

    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        try:
            submit_video_extension(
                "erotic candlelit two-shot",
                video_url="https://example.invalid/clip.mp4",
                dry_run=True,
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            assert "attest" in str(exc)
    finally:
        os.environ.pop(ATTESTATION_ENV, None)


def test_video_edit_attested_intimate_allowed() -> None:
    from imagine_client import submit_video_edit

    path, _ = _attest_env()
    try:
        resp = submit_video_edit(
            "erotic clothing-on R-rated continuation",
            video_url="https://example.invalid/clip.mp4",
            dry_run=True,
        )
        assert resp.get("dry_run") is True
        assert resp.get("mode") == "video_edit"
    finally:
        _cleanup(path)


def test_imagine_edit_intimate_plus_source_image_refused() -> None:
    path, _ = _attest_env()
    try:
        try:
            gate_imagine_prompt(
                "intimate cinematic close-up",
                nsfw=True,
                has_reference_image=True,
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            lowered = str(exc).lower()
            assert "nudify" in lowered or "source still" in lowered
    finally:
        _cleanup(path)


def test_403_429_not_in_failover() -> None:
    from imagine_regions import FAILOVER_STATUS_CODES

    assert 403 not in FAILOVER_STATUS_CODES
    assert 429 not in FAILOVER_STATUS_CODES
    assert 500 in FAILOVER_STATUS_CODES


def test_execute_nsfw_shot_requires_attestation() -> None:
    from unittest.mock import patch

    from aup_gate import AUPGateError
    from batch_runner import execute_nsfw_shot
    from nsfw_orchestrator import plan_batch

    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        batch = plan_batch(
            "Gate Test",
            [{"tier": "hero", "description": "Cover frame candlelit embrace"}],
            budget_credits=200,
        )
        shot_id = batch["shots"][0]["shot_id"]
        noop = lambda *args, **kwargs: None
        with patch("quota_optimizer.save_project_state", noop), patch(
            "project_state.save_project_state", noop
        ):
            try:
                execute_nsfw_shot(batch, shot_id, dry_run=True, record_quota=False)
                raise AssertionError("expected AUPGateError")
            except AUPGateError as exc:
                assert "attest" in str(exc)
    finally:
        os.environ.pop(ATTESTATION_ENV, None)


def test_403_does_not_failover_regions() -> None:
    import io
    import urllib.error
    from unittest.mock import patch

    from imagine_client import ImagineAPIError, generate_image

    calls: list[str] = []

    def boom(method, path, *, payload, headers, timeout):
        calls.append(str((payload or {}).get("region", "")))
        raise urllib.error.HTTPError(
            "https://api.x.ai/v1/images/generations",
            403,
            "Forbidden",
            hdrs=None,
            fp=io.BytesIO(b'{"error":"denied"}'),
        )

    with patch.dict(os.environ, {"XAI_API_KEY": "xai-test-placeholder-not-a-real-key"}):
        with patch("imagine_client._request_single", boom):
            try:
                generate_image("Test cinematic still", dry_run=False)
                raise AssertionError("expected ImagineAPIError")
            except ImagineAPIError as exc:
                assert exc.status == 403
                assert "fail closed" in str(exc)
    assert len(calls) == 1


def test_planning_packet_csam_refused() -> None:
    try:
        gate_planning_packet("underage character study")
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "minor-coded" in str(exc) or "CSAM" in str(exc)


def test_bridge_intimate_plus_reference_refused() -> None:
    from imagine_bridge import build_handoff

    path, _ = _attest_env()
    try:
        try:
            build_handoff(
                {
                    "shot_id": "shot_int",
                    "description": "erotic cinematic close-up",
                    "reference_image_id": "plate_001",
                    "recommended_mode": "image_to_video",
                },
                context="shot",
                agent_mode=False,
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            lowered = str(exc).lower()
            assert "nudify" in lowered or "source still" in lowered
    finally:
        _cleanup(path)


def test_handoff_validate_csam_fail_closed() -> None:
    from handoff_validate import validate_handoff_data

    result = validate_handoff_data(
        {
            "packet_type": "imagine_agent_mode_handoff",
            "prompt": "underage character study",
        }
    )
    assert result["ok"] is False
    blob = " ".join(result.get("issues") or [])
    assert "minor-coded" in blob or "CSAM" in blob


def test_aup_status_hides_flags() -> None:
    path, _ = _attest_env()
    try:
        status = aup_status()
        assert status["valid"] is True
        assert status["present"] is True
        assert "age_18_plus" not in status
        assert status["aup_url"] == AUP_URL
    finally:
        _cleanup(path)


def test_check_aup_idle_without_batches() -> None:
    from doctor_checks import check_aup

    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "characters").mkdir()
            (root / "nsfw_batches").mkdir()
            rows = check_aup(repo_root=root)
        names = {r.name: r.status for r in rows}
        assert names.get("AUP idle") == "PASS" or names.get("AUP attestation") == "PASS"
        assert "FAIL" not in {r.status for r in rows if r.name.startswith("AUP")}
    finally:
        os.environ.pop(ATTESTATION_ENV, None)


def test_check_aup_fails_when_batch_without_attest() -> None:
    from doctor_checks import check_aup

    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batch_dir = root / "nsfw_batches" / "probe"
            batch_dir.mkdir(parents=True)
            (batch_dir / "batch.json").write_text(
                '{"batch_id":"probe","slug":"probe"}\n', encoding="utf-8"
            )
            (root / "characters").mkdir()
            rows = check_aup(repo_root=root)
        attest = [r for r in rows if r.name == "AUP attestation"]
        assert attest, rows
        assert attest[0].status == "FAIL"
        assert "attest" in attest[0].detail.lower() or "nsfw" in attest[0].detail.lower()
    finally:
        os.environ.pop(ATTESTATION_ENV, None)


def test_nsfw_pack_is_opt_in_aup() -> None:
    marketplace = json.loads((ROOT / ".grok-plugin" / "marketplace.json").read_text())
    assert "Official Grok plugin marketplace" not in marketplace.get("description", "")
    packs = {p["name"]: p for p in marketplace.get("plugins", [])}
    nsfw = packs.get("grok-imagine-nsfw")
    assert nsfw, "v3.11 modular nsfw pack missing"
    desc = nsfw.get("description", "").lower()
    assert "18+" in desc or "aup" in desc
    assert "imaginary" in desc or "attest" in desc


if __name__ == "__main__":
    test_attestation_requires_all_flags()
    test_checkbox_is_not_attestation()
    test_valid_attestation_roundtrip()
    test_csam_keyword_refuse_uses_stubs_only()
    test_explicit_beyond_r_refused_when_nsfw()
    test_hidden_camera_refused()
    test_nsfw_shot_refuses_reference_image()
    test_nsfw_shot_refuses_explicit_level()
    test_nsfw_batch_allows_r_rated_imaginary()
    test_dna_intimate_requires_imaginary_adult_no_photo()
    test_sfw_dna_with_refs_still_allowed()
    test_video_extend_csam_refused()
    test_video_edit_intimate_requires_attestation()
    test_video_extend_attested_intimate_allowed()
    test_video_edit_csam_refused()
    test_video_extend_intimate_requires_attestation()
    test_video_edit_attested_intimate_allowed()
    test_imagine_edit_intimate_plus_source_image_refused()
    test_403_429_not_in_failover()
    test_execute_nsfw_shot_requires_attestation()
    test_403_does_not_failover_regions()
    test_planning_packet_csam_refused()
    test_bridge_intimate_plus_reference_refused()
    test_handoff_validate_csam_fail_closed()
    test_aup_status_hides_flags()
    test_check_aup_idle_without_batches()
    test_check_aup_fails_when_batch_without_attest()
    test_nsfw_pack_is_opt_in_aup()
    print("All AUP gate tests passed")
