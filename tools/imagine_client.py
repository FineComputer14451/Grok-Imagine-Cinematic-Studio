#!/usr/bin/env python3
"""
Thin xAI Imagine API client for image, video, and extension workflows.

Uses REST endpoints at https://api.x.ai/v1. Falls back to dry-run mock
responses when XAI_API_KEY is unset (planner → generator bridge for local dev).
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
import uuid
from typing import Any

from aup_gate import gate_imagine_prompt
from imagine_regions import (
    FAILOVER_STATUS_CODES,
    POLICY_FAIL_CLOSED_CODES,
    get_failover_chain,
    record_region_used,
    region_payload_fields,
    region_request_headers,
)
from models import (
    DEFAULT_IMAGINE_IMAGE_MODEL,
    DEFAULT_IMAGINE_VIDEO_MODEL,
    resolve_image_model,
    resolve_video_model,
)
from project_state import load_project_state

DEFAULT_BASE_URL = "https://api.x.ai/v1"
DEFAULT_POLL_INTERVAL = 5.0
DEFAULT_POLL_TIMEOUT = 600.0

VIDEO_TERMINAL_STATUSES = frozenset({"done", "failed", "expired"})


class ImagineAPIError(RuntimeError):
    """Raised when the Imagine API returns an error or times out."""

    def __init__(self, message: str, *, status: int | None = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


def get_api_key() -> str | None:
    key = os.getenv("XAI_API_KEY", "").strip()
    return key or None


def is_dry_run() -> bool:
    return get_api_key() is None


def _base_url() -> str:
    return os.getenv("XAI_API_BASE", DEFAULT_BASE_URL).rstrip("/")


def _request_single(
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None,
    headers: dict[str, str],
    timeout: float,
) -> dict[str, Any]:
    url = f"{_base_url()}{path}"
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _request(
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: float = 120.0,
    region: str | None = None,
) -> dict[str, Any]:
    api_key = get_api_key()
    if not api_key:
        raise ImagineAPIError("XAI_API_KEY not set — use dry_run helpers or export the key")

    state = load_project_state()
    regions = get_failover_chain(region, state)
    last_error: ImagineAPIError | None = None

    for idx, reg in enumerate(regions):
        body_payload = dict(payload or {})
        body_payload.update(region_payload_fields(reg))
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            **region_request_headers(reg),
        }
        try:
            result = _request_single(method, path, payload=body_payload, headers=headers, timeout=timeout)
            record_region_used(reg, failed=idx > 0)
            result["region"] = reg
            return result
        except urllib.error.HTTPError as exc:
            body: Any = None
            try:
                body = json.loads(exc.read().decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                body = exc.read().decode("utf-8", errors="replace")
            last_error = ImagineAPIError(
                f"Imagine API {method.upper()} {path} failed ({exc.code}) region={reg}",
                status=exc.code,
                body=body,
            )
            if exc.code in POLICY_FAIL_CLOSED_CODES:
                last_error = ImagineAPIError(
                    f"Imagine API {method.upper()} {path} failed ({exc.code}) region={reg} "
                    "— fail closed (no region hop on 403/429 policy or rate-limit)",
                    status=exc.code,
                    body=body,
                )
                raise last_error from exc
            if exc.code in FAILOVER_STATUS_CODES and idx < len(regions) - 1:
                record_region_used(reg, failed=True)
                continue
            raise last_error from exc

    if last_error:
        raise last_error
    raise ImagineAPIError(f"Imagine API {method.upper()} {path} failed — no regions available")


def _mock_request_id(prefix: str = "dry") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def _use_dry_run(dry_run: bool | None) -> bool:
    return is_dry_run() if dry_run is None else dry_run


def generate_image(
    prompt: str,
    *,
    model: str | None = None,
    n: int = 1,
    aspect_ratio: str | None = None,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    """Generate image(s) from a text prompt."""
    gate_imagine_prompt(prompt, nsfw=False, has_reference_image=False)
    slug = resolve_image_model(model or DEFAULT_IMAGINE_IMAGE_MODEL)
    if _use_dry_run(dry_run):
        images = [
            {
                "url": f"https://dry-run.x.ai/images/{_mock_request_id('img')}.png",
                "revised_prompt": prompt,
            }
            for _ in range(max(1, n))
        ]
        return {"dry_run": True, "model": slug, "data": images}

    payload: dict[str, Any] = {"model": slug, "prompt": prompt, "n": n}
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    result = _request("POST", "/images/generations", payload=payload)
    result["model"] = slug
    return result


def edit_image(
    prompt: str,
    *,
    image_url: str,
    model: str | None = None,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    """Edit a source image with a natural-language prompt."""
    gate_imagine_prompt(prompt, nsfw=False, has_reference_image=True)
    slug = resolve_image_model(model or DEFAULT_IMAGINE_IMAGE_MODEL)
    if _use_dry_run(dry_run):
        return {
            "dry_run": True,
            "model": slug,
            "data": [{"url": f"https://dry-run.x.ai/edits/{_mock_request_id('edit')}.png"}],
        }

    payload = {
        "model": slug,
        "prompt": prompt,
        "image": {"url": image_url, "type": "image_url"},
    }
    result = _request("POST", "/images/edits", payload=payload)
    result["model"] = slug
    return result


def submit_video_generation(
    prompt: str,
    *,
    model: str | None = None,
    duration: int = 10,
    image_url: str | None = None,
    aspect_ratio: str | None = None,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    """Start async text-to-video or image-to-video generation."""
    gate_imagine_prompt(prompt, nsfw=False, has_reference_image=bool(image_url))
    slug = resolve_video_model(model or DEFAULT_IMAGINE_VIDEO_MODEL)
    if _use_dry_run(dry_run):
        rid = _mock_request_id("vid")
        return {
            "dry_run": True,
            "request_id": rid,
            "model": slug,
            "status": "done",
            "video": {"url": f"https://dry-run.x.ai/videos/{rid}.mp4"},
        }

    payload: dict[str, Any] = {
        "model": slug,
        "prompt": prompt,
        "duration": duration,
    }
    if image_url:
        payload["image"] = {"url": image_url}
    if aspect_ratio:
        payload["aspect_ratio"] = aspect_ratio
    result = _request("POST", "/videos/generations", payload=payload)
    result["model"] = slug
    return result


def submit_video_extension(
    prompt: str,
    *,
    video_url: str,
    model: str | None = None,
    duration: int = 10,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    """Start async video extension from an existing clip."""
    gate_imagine_prompt(prompt, nsfw=False, has_reference_image=False)
    slug = resolve_video_model(model or "grok-imagine-video")
    if _use_dry_run(dry_run):
        rid = _mock_request_id("ext")
        return {
            "dry_run": True,
            "request_id": rid,
            "model": slug,
            "status": "done",
            "video": {"url": f"https://dry-run.x.ai/videos/{rid}_extended.mp4"},
        }

    payload = {
        "model": slug,
        "prompt": prompt,
        "duration": duration,
        "video": {"url": video_url},
    }
    result = _request("POST", "/videos/extensions", payload=payload)
    result["model"] = slug
    return result


def get_video_job(request_id: str) -> dict[str, Any]:
    """Poll video job status by request ID."""
    if request_id.startswith("dry_") or request_id.startswith("vid_") or request_id.startswith("ext_"):
        return {
            "dry_run": True,
            "request_id": request_id,
            "status": "done",
            "video": {"url": f"https://dry-run.x.ai/videos/{request_id}.mp4"},
        }
    return _request("GET", f"/videos/{request_id}")


def poll_video_job(
    request_id: str,
    *,
    interval: float = DEFAULT_POLL_INTERVAL,
    timeout: float = DEFAULT_POLL_TIMEOUT,
) -> dict[str, Any]:
    """Poll until video job reaches a terminal state."""
    if is_dry_run() or request_id.startswith(("dry_", "vid_", "ext_")):
        return get_video_job(request_id)

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        result = get_video_job(request_id)
        status = result.get("status", "")
        if status in VIDEO_TERMINAL_STATUSES:
            if status == "done":
                return result
            raise ImagineAPIError(
                f"Video job {request_id} ended with status={status}",
                body=result,
            )
        time.sleep(interval)
    raise ImagineAPIError(f"Video job {request_id} timed out after {timeout}s")


def extract_image_url(response: dict[str, Any]) -> str | None:
    data = response.get("data") or []
    if data and isinstance(data[0], dict):
        return data[0].get("url")
    return response.get("url")


def extract_video_url(response: dict[str, Any]) -> str | None:
    video = response.get("video")
    if isinstance(video, dict):
        return video.get("url")
    return response.get("url")