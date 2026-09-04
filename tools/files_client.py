#!/usr/bin/env python3
"""Thin xAI Files API client (list / get / upload / delete).

Upload is multipart/form-data. ``expires_after`` must be encoded *before*
the ``file`` part or the API returns 400. JSON Imagine calls live in
``imagine_client`` — do not send Files uploads through that JSON path.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any

from imagine_client import ImagineAPIError, get_api_key, is_dry_run
from studio_paths import ARTIFACTS_DIR

FILES_INBOX_DIR = ARTIFACTS_DIR / "files_inbox"

DEFAULT_BASE_URL = "https://api.x.ai/v1"
MAX_FILE_BYTES = 50 * 1024 * 1024
EXPIRES_AFTER_MIN = 3600
EXPIRES_AFTER_MAX = 2_592_000
DEFAULT_PURPOSE = "assistants"

_MIME_BY_SUFFIX = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".gif": "image/gif",
    ".mp4": "video/mp4",
    ".jsonl": "application/jsonl",
    ".json": "application/json",
    ".pdf": "application/pdf",
    ".txt": "text/plain",
}


class FilesAPIError(ImagineAPIError):
    """Raised when the Files API rejects a request or local preflight fails."""


def _base_url() -> str:
    return os.getenv("XAI_API_BASE", DEFAULT_BASE_URL).rstrip("/")


def _use_dry_run(dry_run: bool | None) -> bool:
    return is_dry_run() if dry_run is None else dry_run


def _file_size(path: Path) -> int:
    return path.stat().st_size


def _mime_for(path: Path) -> str:
    return _MIME_BY_SUFFIX.get(path.suffix.lower(), "application/octet-stream")


def _safe_filename(name: str) -> str:
    return name.replace('"', "_").replace("\r", "_").replace("\n", "_")


def validate_expires_after(expires_after: int | None) -> int | None:
    if expires_after is None:
        return None
    value = int(expires_after)
    if value < EXPIRES_AFTER_MIN or value > EXPIRES_AFTER_MAX:
        raise FilesAPIError(
            f"expires_after must be {EXPIRES_AFTER_MIN}–{EXPIRES_AFTER_MAX} seconds "
            f"(1 hour–30 days); got {value}"
        )
    return value


def save_inbox_file(filename: str, data: bytes) -> Path:
    """Write a browser/TUI drop to artifacts/files_inbox (local path for upload)."""
    if not data:
        raise FilesAPIError("Refusing to save an empty inbox file")
    if len(data) > MAX_FILE_BYTES:
        raise FilesAPIError(
            f"File exceeds Files API maximum of {MAX_FILE_BYTES // (1024 * 1024)} MB "
            f"({len(data)} bytes)"
        )
    safe = _safe_filename(Path(filename or "upload.bin").name)
    if not safe or safe in {".", ".."}:
        safe = f"upload_{uuid.uuid4().hex[:8]}.bin"
    FILES_INBOX_DIR.mkdir(parents=True, exist_ok=True)
    dest = FILES_INBOX_DIR / safe
    dest.write_bytes(data)
    return dest


def validate_upload_path(path: Path) -> Path:
    resolved = path.expanduser()
    if not resolved.is_file():
        raise FilesAPIError(f"File not found: {path}")
    size = _file_size(resolved)
    if size > MAX_FILE_BYTES:
        raise FilesAPIError(
            f"File exceeds Files API maximum of {MAX_FILE_BYTES // (1024 * 1024)} MB "
            f"({size} bytes)"
        )
    if size < 1:
        raise FilesAPIError("Refusing to upload an empty file")
    return resolved


def encode_multipart(
    *,
    file_path: Path,
    file_bytes: bytes,
    expires_after: int | None = None,
    purpose: str | None = None,
    boundary: str | None = None,
) -> tuple[bytes, str, tuple[str, ...]]:
    """Build a multipart body with ``expires_after`` (if set) before ``file``."""
    token = (boundary or uuid.uuid4().hex).replace("-", "")
    marker = f"----StudioFiles{token}"
    filename = _safe_filename(file_path.name)
    mime = _mime_for(file_path)
    parts: list[bytes] = []
    names: list[str] = []

    def add_field(name: str, value: str) -> None:
        names.append(name)
        parts.append(
            (
                f"--{marker}\r\n"
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
                f"{value}\r\n"
            ).encode("utf-8")
        )

    if expires_after is not None:
        add_field("expires_after", str(int(expires_after)))
    if purpose:
        add_field("purpose", str(purpose))

    names.append("file")
    header = (
        f"--{marker}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {mime}\r\n\r\n"
    ).encode("utf-8")
    parts.append(header)
    parts.append(file_bytes)
    parts.append(b"\r\n")
    parts.append(f"--{marker}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    content_type = f"multipart/form-data; boundary={marker}"
    return body, content_type, tuple(names)


def _http(
    method: str,
    path: str,
    *,
    query: dict[str, Any] | None = None,
    data: bytes | None = None,
    content_type: str | None = None,
    timeout: float = 120.0,
) -> dict[str, Any]:
    api_key = get_api_key()
    if not api_key:
        raise FilesAPIError("XAI_API_KEY not set — use dry_run helpers or export the key")

    params = {k: v for k, v in (query or {}).items() if v is not None and v != ""}
    url = f"{_base_url()}{path}"
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"

    headers = {"Authorization": f"Bearer {api_key}"}
    if content_type:
        headers["Content-Type"] = content_type
    elif data is not None:
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        body: Any = None
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError, OSError):
            body = None
        raise FilesAPIError(
            f"Files API {method.upper()} {path} failed ({exc.code})",
            status=exc.code,
            body=body,
        ) from exc


def _mock_file_id() -> str:
    return f"file_dry_{uuid.uuid4().hex[:12]}"


def list_files(
    *,
    limit: int = 20,
    order: str | None = None,
    sort_by: str | None = None,
    pagination_token: str | None = None,
    filter_expr: str | None = None,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    """GET /v1/files — paginated metadata list."""
    query = {
        "limit": int(limit),
        "order": order,
        "sort_by": sort_by,
        "pagination_token": pagination_token,
        "filter": filter_expr,
    }
    if _use_dry_run(dry_run):
        return {
            "dry_run": True,
            "data": [],
            "pagination_token": None,
            "query": {k: v for k, v in query.items() if v is not None},
        }
    return _http("GET", "/files", query=query)


def get_file(file_id: str, *, dry_run: bool | None = None) -> dict[str, Any]:
    """GET /v1/files/{id} — metadata for one file."""
    fid = (file_id or "").strip()
    if not fid:
        raise FilesAPIError("file_id is required")
    if _use_dry_run(dry_run) or fid.startswith("file_dry_"):
        return {
            "dry_run": True,
            "id": fid,
            "object": "file",
            "bytes": 0,
            "created_at": int(time.time()),
            "expires_at": None,
            "filename": "dry-run.bin",
            "purpose": DEFAULT_PURPOSE,
        }
    encoded = urllib.parse.quote(fid, safe="")
    return _http("GET", f"/files/{encoded}")


def upload_file(
    path: str | Path,
    *,
    expires_after: int | None = None,
    purpose: str | None = DEFAULT_PURPOSE,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    """POST /v1/files — multipart upload. Returns metadata including ``id``."""
    ttl = validate_expires_after(expires_after)
    src = validate_upload_path(Path(path))
    purpose_s = (purpose or "").strip() or None
    file_bytes = src.read_bytes()
    body, content_type, field_order = encode_multipart(
        file_path=src,
        file_bytes=file_bytes,
        expires_after=ttl,
        purpose=purpose_s,
    )
    if _use_dry_run(dry_run):
        now = int(time.time())
        return {
            "dry_run": True,
            "id": _mock_file_id(),
            "object": "file",
            "bytes": len(file_bytes),
            "created_at": now,
            "expires_at": (now + ttl) if ttl else None,
            "filename": src.name,
            "purpose": purpose_s or "",
            "field_order": list(field_order),
        }
    result = _http("POST", "/files", data=body, content_type=content_type, timeout=180.0)
    result.setdefault("filename", src.name)
    return result


def delete_file(file_id: str, *, dry_run: bool | None = None) -> dict[str, Any]:
    """DELETE /v1/files/{id}."""
    fid = (file_id or "").strip()
    if not fid:
        raise FilesAPIError("file_id is required")
    if _use_dry_run(dry_run) or fid.startswith("file_dry_"):
        return {
            "dry_run": True,
            "id": fid,
            "object": "file",
            "deleted": True,
        }
    encoded = urllib.parse.quote(fid, safe="")
    return _http("DELETE", f"/files/{encoded}")
