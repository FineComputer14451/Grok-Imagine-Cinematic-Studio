"""Tests for Imagine API client and job queue."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from imagine_client import (  # noqa: E402
    ImagineAPIError,
    edit_image,
    extract_image_url,
    extract_video_url,
    generate_image,
    is_dry_run,
    submit_video_edit,
    submit_video_extension,
    submit_video_generation,
)
from imagine_jobs import create_job, job_summary, list_jobs, register_reference_asset  # noqa: E402


def test_dry_run_image_generation(monkeypatch=None) -> None:
    import imagine_client as ic

    if monkeypatch:
        monkeypatch.setattr(ic, "is_dry_run", lambda: True)
    elif not is_dry_run():
        return  # skip live API in bare __main__ runs

    resp = generate_image("Test cinematic still")
    assert resp.get("dry_run")
    url = extract_image_url(resp)
    assert url and "dry-run" in url


def test_dry_run_video_submit(monkeypatch=None) -> None:
    import imagine_client as ic

    if monkeypatch:
        monkeypatch.setattr(ic, "is_dry_run", lambda: True)
    elif not is_dry_run():
        return

    resp = submit_video_generation("Slow dolly in", duration=8)
    assert resp.get("dry_run")
    url = extract_video_url(resp)
    assert url and "dry-run" in url


def test_job_queue_crud(tmp_path, monkeypatch) -> None:
    state_file = tmp_path / "state.json"
    monkeypatch.setenv("CINEMATIC_STATE_FILE", str(state_file))
    # project_state uses PROJECT_STATE_FILE from studio_paths — patch via monkeypatch on module
    import project_state as ps
    import studio_paths as sp

    monkeypatch.setattr(sp, "PROJECT_STATE_FILE", state_file)
    monkeypatch.setattr(ps, "PROJECT_STATE_FILE", state_file)

    job = create_job("video", prompt="Test clip", model="grok-imagine-video-1.5", clip_id="clip_001")
    assert job["status"] == "queued"
    assert job["job_id"].startswith("job_")

    rows = list_jobs()
    assert any(r["job_id"] == job["job_id"] for r in rows)

    register_reference_asset("ref_001", url="https://example.com/plate.png", tier="hero")
    summary = job_summary()
    assert summary["reference_assets"] >= 1


def test_dry_run_image_2_0_quality_payload(monkeypatch) -> None:
    import imagine_client as ic

    monkeypatch.setattr(ic, "is_dry_run", lambda: True)
    resp = generate_image(
        "Hero plate",
        model="grok-imagine-image-2.0",
        resolution="2k",
        quality="medium",
        aspect_ratio="16:9",
        dry_run=True,
    )
    assert resp["model"] == "grok-imagine-image-2.0"
    assert resp["payload"]["resolution"] == "2k"
    assert resp["payload"]["quality"] == "medium"


def test_dry_run_reference_to_video(monkeypatch) -> None:
    import imagine_client as ic

    monkeypatch.setattr(ic, "is_dry_run", lambda: True)
    resp = submit_video_generation(
        "Walk the runway",
        reference_image_urls=["https://example.com/a.png"],
        reference_audios=["eve"],
        resolution="720p",
        dry_run=True,
    )
    assert resp["mode"] == "reference_to_video"
    assert resp["model"] == "grok-imagine-video-1.5"
    assert resp["payload"]["reference_images"]
    assert resp["payload"]["reference_audios"][0]["voice_id"] == "eve"


def test_r2v_exclusive_with_image() -> None:
    try:
        submit_video_generation(
            "Nope",
            image_url="https://example.com/still.png",
            reference_image_urls=["https://example.com/ref.png"],
            dry_run=True,
        )
        raise AssertionError("expected ImagineAPIError")
    except ImagineAPIError as exc:
        assert "cannot be combined" in str(exc)


def test_dry_run_video_edit_and_extend(monkeypatch) -> None:
    import imagine_client as ic

    monkeypatch.setattr(ic, "is_dry_run", lambda: True)
    edit = submit_video_edit("Add rain", video_url="https://example.com/clip.mp4", dry_run=True)
    assert edit["mode"] == "video_edit"
    assert edit["model"] == "grok-imagine-video"
    ext = submit_video_extension(
        "Continue",
        video_url="https://example.com/clip.mp4",
        model="grok-imagine-video-1.5",
        dry_run=True,
    )
    assert ext["mode"] == "video_extend"
    assert ext["model"] == "grok-imagine-video"  # 1.5 cannot extend


def test_edit_image_file_id(monkeypatch) -> None:
    import imagine_client as ic

    monkeypatch.setattr(ic, "is_dry_run", lambda: True)
    resp = edit_image("Add hat", image_file_id="file_abc", dry_run=True)
    assert resp["payload"]["image"]["file_id"] == "file_abc"


if __name__ == "__main__":
    test_dry_run_image_generation()
    test_dry_run_video_submit()
    print("Imagine client tests passed (job CRUD needs tmp_path — run via pytest)")