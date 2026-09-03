"""Fail-closed SpaceXAI AUP gates — metadata/stub prompts only."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

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
    gate_planning_subject,
    gate_nsfw_extension_text,
    gate_text,
    require_attestation,
    scan_csam,
    write_attestation,
)
from character_dna import (  # noqa: E402
    compose_injected_prompt,
    create_dna_scaffold,
    inject_into_prompt,
    load_character_dna,
    save_character_dna,
)
from nsfw_sequence_extender import plan_nsfw_extension  # noqa: E402


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


def _video_edit_extend_fns() -> tuple[tuple[str, Any], ...]:
    from imagine_client import submit_video_edit, submit_video_extension

    return (
        ("video_edit", submit_video_edit),
        ("video_extend", submit_video_extension),
    )


def test_video_edit_extend_csam_refused() -> None:
    clip = "https://example.invalid/clip.mp4"
    for mode, fn in _video_edit_extend_fns():
        try:
            fn("underage character study", video_url=clip, dry_run=True)
            raise AssertionError(f"expected AUPGateError from {mode}")
        except AUPGateError as exc:
            assert "minor-coded" in str(exc) or "CSAM" in str(exc)


def test_video_edit_extend_intimate_requires_attestation() -> None:
    clip = "https://example.invalid/clip.mp4"
    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        for mode, fn in _video_edit_extend_fns():
            try:
                fn("erotic candlelit two-shot", video_url=clip, dry_run=True)
                raise AssertionError(f"expected AUPGateError from {mode}")
            except AUPGateError as exc:
                assert "attest" in str(exc)
    finally:
        os.environ.pop(ATTESTATION_ENV, None)


def test_video_edit_extend_attested_intimate_allowed() -> None:
    clip = "https://example.invalid/clip.mp4"
    path, _ = _attest_env()
    try:
        for mode, fn in _video_edit_extend_fns():
            resp = fn(
                "erotic clothing-on R-rated continuation",
                video_url=clip,
                dry_run=True,
            )
            assert resp.get("dry_run") is True
            assert resp.get("mode") == mode
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


def test_compose_injected_prompt_csam_refused() -> None:
    try:
        compose_injected_prompt("[CHARACTER_DNA:ELENA]", "underage character study")
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "minor-coded" in str(exc) or "CSAM" in str(exc)


def test_inject_into_prompt_csam_refused() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        dna = create_dna_scaffold(
            "Elena Voss",
            core_identity="detective",
            facial_dna="grey eyes",
        )
        save_character_dna(dna, characters_root=root)
        try:
            inject_into_prompt(
                "underage character study",
                "Elena Voss",
                characters_root=root,
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            assert "minor-coded" in str(exc) or "CSAM" in str(exc)


def test_load_intimate_dna_requires_attestation() -> None:
    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            dna = create_dna_scaffold(
                "Mara",
                core_identity="adult fictional lead",
                facial_dna="sharp cheekbones",
                nsfw_notes="implied intimacy continuity",
                subject_kind="imaginary_adult",
            )
            path = Path(tmp) / "dna.json"
            path.write_text(json.dumps(dna), encoding="utf-8")
            try:
                load_character_dna(path)
                raise AssertionError("expected AUPGateError")
            except AUPGateError as exc:
                assert "attest" in str(exc)
    finally:
        os.environ.pop(ATTESTATION_ENV, None)


def test_dna_init_output_gates_intimate() -> None:
    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        dna = create_dna_scaffold(
            "Mara",
            core_identity="adult fictional lead",
            facial_dna="sharp cheekbones",
            nsfw_notes="implied intimacy continuity",
            subject_kind="unspecified",
        )
        try:
            gate_dna(dna)
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            assert "imaginary_adult" in str(exc) or "attest" in str(exc)
    finally:
        os.environ.pop(ATTESTATION_ENV, None)


def test_plan_nsfw_still_ref_refused_when_attested() -> None:
    path, _ = _attest_env()
    try:
        try:
            plan_nsfw_extension(
                "Still Ref Probe",
                target_duration=60,
                source_type="reference_frame",
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            lowered = str(exc).lower()
            assert "nudify" in lowered or "source still" in lowered
    finally:
        _cleanup(path)


def test_plan_nsfw_short_clip_attested_allowed() -> None:
    path, _ = _attest_env()
    try:
        seq = plan_nsfw_extension(
            "Clip Continue",
            target_duration=60,
            source_type="short_clip",
        )
        assert seq.get("prompt_chain")
    finally:
        _cleanup(path)


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


def test_bridge_has_reference_flag_refused() -> None:
    from imagine_bridge import build_handoff

    path, _ = _attest_env()
    try:
        try:
            build_handoff(
                {
                    "shot_id": "shot_flag",
                    "description": "erotic cinematic close-up",
                    "has_reference": True,
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


def test_handoff_kwarg_dna_inject_csam_refused() -> None:
    from imagine_bridge import build_handoff

    try:
        build_handoff(
            {
                "shot_id": "shot_ok",
                "description": "Cover frame at dusk",
                "recommended_mode": "image_prompt",
            },
            context="shot",
            agent_mode=True,
            execution_mode="image_prompt",
            dna_inject="underage character study",
        )
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "minor-coded" in str(exc) or "CSAM" in str(exc)


def test_markdown_paste_csam_refused() -> None:
    from imagine_bridge import build_handoff, handoff_to_markdown

    packet = build_handoff(
        {
            "shot_id": "shot_ok",
            "description": "Cover frame at dusk",
            "recommended_mode": "image_prompt",
        },
        context="shot",
        agent_mode=False,
    )
    packet["last_frame_recap"] = "underage character study"
    try:
        handoff_to_markdown(packet)
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "minor-coded" in str(exc) or "CSAM" in str(exc)


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


def test_bridge_recap_csam_refused() -> None:
    from imagine_bridge import build_handoff

    try:
        build_handoff(
            {
                "clip_id": "clip_csam",
                "prompt": "Continue dolly forward",
                "last_frame_recap": "underage character study",
            },
            context="clip",
            agent_mode=False,
        )
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "minor-coded" in str(exc) or "CSAM" in str(exc)


def test_handoff_validate_extend_recap_csam() -> None:
    from handoff_validate import validate_handoff_data

    result = validate_handoff_data(
        {
            "packet_type": "sequence_extend_handoff",
            "prompt": "",
            "last_frame_recap": "underage character study",
        }
    )
    assert result["ok"] is False
    blob = " ".join(result.get("issues") or [])
    assert "minor-coded" in blob or "CSAM" in blob


def test_handoff_validate_scans_nsfw_notes_with_dna_inject() -> None:
    from handoff_validate import validate_handoff_data

    path, _ = _attest_env()
    try:
        result = validate_handoff_data(
            {
                "packet_type": "imagine_agent_mode_handoff",
                "prompt": "candlelit two-shot",
                "dna_inject": "[CHARACTER_DNA:MARA]",
                "nsfw_notes": "creampie close-up",
            }
        )
        assert result["ok"] is False
        blob = " ".join(result.get("issues") or []).lower()
        assert "r-rated" in blob or "creampie" in blob
    finally:
        _cleanup(path)


def test_gate_planning_subject_scans_sound_layer() -> None:
    try:
        gate_planning_subject(
            {
                "prompt": "Continue dolly forward",
                "sound_layer": "underage character study",
            }
        )
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "minor-coded" in str(exc) or "CSAM" in str(exc)


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


def test_check_aup_warns_on_committed_templates() -> None:
    from doctor_checks import check_aup

    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            batches = root / "nsfw_batches"
            batches.mkdir()
            (batches / "outfit_library_shots.json").write_text("[]\n", encoding="utf-8")
            (root / "characters").mkdir()
            rows = check_aup(repo_root=root)
        names = {r.name: r for r in rows}
        assert names["AUP idle"].status == "PASS"
        assert names["NSFW templates on disk"].status == "WARN"
        assert "outfit" in names["NSFW templates on disk"].detail or "json" in names[
            "NSFW templates on disk"
        ].detail.lower()
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


def test_gate_dna_scans_clothing_style_csam() -> None:
    try:
        gate_dna(
            {
                "character_name": "Mara",
                "core_identity": "adult fictional lead",
                "facial_dna": "sharp cheekbones",
                "clothing_style": "schoolgirl uniform",
                "subject_kind": "imaginary_adult",
                "reference_image_ids": [],
            }
        )
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        lowered = str(exc).lower()
        assert "minor-coded" in lowered or "csam" in lowered or "schoolgirl" in lowered


def test_dna_to_markdown_clothing_csam() -> None:
    from character_dna import dna_to_markdown

    try:
        dna_to_markdown(
            {
                "schema_version": "1.0",
                "character_name": "Mara",
                "slug": "mara",
                "core_identity": "adult fictional lead",
                "facial_dna": "sharp cheekbones",
                "clothing_style": "schoolgirl uniform",
                "subject_kind": "imaginary_adult",
                "key_consistency_anchors": [],
                "reference_image_ids": [],
            }
        )
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        lowered = str(exc).lower()
        assert "minor-coded" in lowered or "csam" in lowered or "schoolgirl" in lowered


def test_beyond_r_refused_without_nsfw_keyword() -> None:
    try:
        gate_planning_packet("creampie close-up")
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "R-rated" in str(exc)

    from imagine_client import generate_image

    try:
        generate_image("ahegao portrait", dry_run=True)
        raise AssertionError("expected AUPGateError")
    except AUPGateError as exc:
        assert "R-rated" in str(exc)


def test_check_aup_fails_when_slug_dna_without_attest() -> None:
    from doctor_checks import check_aup

    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dna_dir = root / "characters" / "mara"
            dna_dir.mkdir(parents=True)
            (dna_dir / "dna.json").write_text(
                json.dumps(
                    {
                        "character_name": "Mara",
                        "slug": "mara",
                        "nsfw_notes": "implied intimacy continuity",
                    }
                ),
                encoding="utf-8",
            )
            (root / "nsfw_batches").mkdir()
            rows = check_aup(repo_root=root)
        attest = [r for r in rows if r.name == "AUP attestation"]
        assert attest, rows
        assert attest[0].status == "FAIL"
        assert "intimate DNA" in attest[0].detail or "attest" in attest[0].detail.lower()
    finally:
        os.environ.pop(ATTESTATION_ENV, None)


def test_nsfw_markdown_header_csam_refused() -> None:
    from nsfw_sequence_extender import nsfw_sequence_to_markdown

    path, _ = _attest_env()
    try:
        seq = {
            "sequence_name": "Probe",
            "slug": "probe",
            "clips": [],
            "nsfw_extension": {
                "source_type": "short_clip",
                "reference_description": "schoolgirl uniform",
                "tension_profile": "passionate",
            },
        }
        try:
            nsfw_sequence_to_markdown(seq)
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            lowered = str(exc).lower()
            assert "minor-coded" in lowered or "csam" in lowered or "schoolgirl" in lowered
    finally:
        _cleanup(path)


def test_handoff_prompt_injection_csam_fail_closed() -> None:
    from handoff_validate import validate_handoff_data

    result = validate_handoff_data(
        {
            "packet_type": "identity_lock_handoff",
            "video_pipeline_spec": {"locked": True},
            "prompt_injection": {"cinematic": "schoolgirl uniform, candlelit"},
        }
    )
    assert result["ok"] is False
    blob = " ".join(result.get("issues") or []).lower()
    assert "minor-coded" in blob or "csam" in blob or "schoolgirl" in blob


def test_build_nsfw_clip_prompt_gates_csam() -> None:
    from nsfw_extension_prompts import build_nsfw_clip_prompt

    path, _ = _attest_env()
    try:
        seq = {
            "nsfw_extension": {"source_type": "short_clip"},
            "video_pipeline_spec": {},
        }
        beat = {
            "beat_summary": "schoolgirl uniform",
            "phase": "contact",
            "phase_label": "contact",
            "tension_level": 0.5,
            "duration_seconds": 10,
        }
        try:
            build_nsfw_clip_prompt(seq, beat, is_first_clip=True)
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            lowered = str(exc).lower()
            assert "minor-coded" in lowered or "csam" in lowered or "schoolgirl" in lowered
    finally:
        _cleanup(path)


def test_build_nsfw_extend_prompt_gates_csam() -> None:
    from nsfw_extension_prompts import build_nsfw_extend_prompt

    path, _ = _attest_env()
    try:
        seq = {
            "nsfw_extension": {"source_type": "short_clip"},
            "video_pipeline_spec": {},
        }
        prev = {
            "clip_id": "clip_001",
            "last_frame_recap": "two adults pause in a doorway",
        }
        beat = {
            "beat_summary": "schoolgirl uniform",
            "phase": "contact",
            "phase_label": "contact",
            "tension_level": 0.5,
            "duration_seconds": 10,
        }
        try:
            build_nsfw_extend_prompt(seq, prev, beat)
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            lowered = str(exc).lower()
            assert "minor-coded" in lowered or "csam" in lowered or "schoolgirl" in lowered
    finally:
        _cleanup(path)


def test_build_nsfw_clip_prompt_short_clip_not_still_ref() -> None:
    from nsfw_extension_prompts import build_nsfw_clip_prompt

    path, _ = _attest_env()
    try:
        seq = {
            "nsfw_extension": {"source_type": "short_clip"},
            "video_pipeline_spec": {},
        }
        beat = {
            "beat_summary": "erotic candlelit two-shot",
            "phase": "contact",
            "phase_label": "contact",
            "tension_level": 0.5,
            "duration_seconds": 10,
        }
        prompt = build_nsfw_clip_prompt(seq, beat, is_first_clip=True)
        assert "erotic" in prompt.lower()
    finally:
        _cleanup(path)


def test_gate_nsfw_extension_text_still_ref_refused() -> None:
    path, _ = _attest_env()
    try:
        try:
            gate_nsfw_extension_text(
                "erotic candlelit two-shot",
                source_type="reference_frame",
            )
            raise AssertionError("expected AUPGateError")
        except AUPGateError as exc:
            lowered = str(exc).lower()
            assert "nudify" in lowered or "source still" in lowered
    finally:
        _cleanup(path)


def test_list_characters_surfaces_aup_blocked() -> None:
    from character_dna import list_characters

    os.environ[ATTESTATION_ENV] = "/nonexistent-aup-attestation.json"
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dna_dir = root / "mara"
            dna_dir.mkdir()
            (dna_dir / "dna.json").write_text(
                json.dumps(
                    {
                        "schema_version": "1.0",
                        "character_name": "Mara",
                        "slug": "mara",
                        "core_identity": "adult fictional lead",
                        "facial_dna": "sharp cheekbones",
                        "nsfw_notes": "implied intimacy continuity",
                        "subject_kind": "imaginary_adult",
                    }
                ),
                encoding="utf-8",
            )
            rows = list_characters(characters_root=root)
        assert rows, "unattested intimate DNA must still appear in dna list"
        assert rows[0]["status"] == "aup_blocked"
        assert rows[0]["slug"] == "mara"
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
    test_video_edit_extend_csam_refused()
    test_video_edit_extend_intimate_requires_attestation()
    test_video_edit_extend_attested_intimate_allowed()
    test_imagine_edit_intimate_plus_source_image_refused()
    test_403_429_not_in_failover()
    test_execute_nsfw_shot_requires_attestation()
    test_403_does_not_failover_regions()
    test_compose_injected_prompt_csam_refused()
    test_inject_into_prompt_csam_refused()
    test_load_intimate_dna_requires_attestation()
    test_dna_init_output_gates_intimate()
    test_plan_nsfw_still_ref_refused_when_attested()
    test_plan_nsfw_short_clip_attested_allowed()
    test_planning_packet_csam_refused()
    test_bridge_intimate_plus_reference_refused()
    test_bridge_has_reference_flag_refused()
    test_handoff_kwarg_dna_inject_csam_refused()
    test_markdown_paste_csam_refused()
    test_handoff_validate_csam_fail_closed()
    test_bridge_recap_csam_refused()
    test_handoff_validate_extend_recap_csam()
    test_handoff_validate_scans_nsfw_notes_with_dna_inject()
    test_gate_planning_subject_scans_sound_layer()
    test_aup_status_hides_flags()
    test_check_aup_idle_without_batches()
    test_check_aup_warns_on_committed_templates()
    test_check_aup_fails_when_batch_without_attest()
    test_gate_dna_scans_clothing_style_csam()
    test_dna_to_markdown_clothing_csam()
    test_beyond_r_refused_without_nsfw_keyword()
    test_check_aup_fails_when_slug_dna_without_attest()
    test_nsfw_markdown_header_csam_refused()
    test_handoff_prompt_injection_csam_fail_closed()
    test_build_nsfw_clip_prompt_gates_csam()
    test_build_nsfw_extend_prompt_gates_csam()
    test_build_nsfw_clip_prompt_short_clip_not_still_ref()
    test_gate_nsfw_extension_text_still_ref_refused()
    test_list_characters_surfaces_aup_blocked()
    test_nsfw_pack_is_opt_in_aup()
    print("All AUP gate tests passed")
