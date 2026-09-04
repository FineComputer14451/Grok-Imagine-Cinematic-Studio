"""Files API client: multipart order, dry-run, size/TTL preflight."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from files_client import (  # noqa: E402
    EXPIRES_AFTER_MAX,
    EXPIRES_AFTER_MIN,
    FilesAPIError,
    create_public_url,
    delete_file,
    encode_multipart,
    get_file,
    list_files,
    revoke_public_url,
    upload_file,
    validate_expires_after,
)


def _tiny_png(tmp_path: Path, name: str = "plate.png") -> Path:
    path = tmp_path / name
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + b"x" * 32)
    return path


def test_multipart_expires_after_before_file(tmp_path: Path) -> None:
    src = _tiny_png(tmp_path)
    body, content_type, names = encode_multipart(
        file_path=src,
        file_bytes=src.read_bytes(),
        expires_after=3600,
        purpose="assistants",
        boundary="testdeadbeef",
    )
    assert names == ("expires_after", "purpose", "file")
    assert names.index("expires_after") < names.index("file")
    text = body.decode("latin1")
    assert text.index('name="expires_after"') < text.index('name="file"')
    assert "filename=\"plate.png\"" in text
    assert content_type.startswith("multipart/form-data; boundary=")
    assert b"XAI_API_KEY" not in body
    assert b"Bearer" not in body


def test_multipart_file_only_when_optional_fields_omitted(tmp_path: Path) -> None:
    src = _tiny_png(tmp_path)
    _body, _ctype, names = encode_multipart(
        file_path=src,
        file_bytes=src.read_bytes(),
    )
    assert names == ("file",)


def test_expires_after_bounds() -> None:
    assert validate_expires_after(None) is None
    assert validate_expires_after(EXPIRES_AFTER_MIN) == EXPIRES_AFTER_MIN
    assert validate_expires_after(EXPIRES_AFTER_MAX) == EXPIRES_AFTER_MAX
    with pytest.raises(FilesAPIError, match="expires_after"):
        validate_expires_after(EXPIRES_AFTER_MIN - 1)
    with pytest.raises(FilesAPIError, match="expires_after"):
        validate_expires_after(EXPIRES_AFTER_MAX + 1)


def test_upload_rejects_missing_and_empty(tmp_path: Path) -> None:
    missing = tmp_path / "nope.png"
    with pytest.raises(FilesAPIError, match="not found"):
        upload_file(missing, dry_run=True)
    empty = tmp_path / "empty.png"
    empty.write_bytes(b"")
    with pytest.raises(FilesAPIError, match="empty"):
        upload_file(empty, dry_run=True)


def test_upload_rejects_over_50mb(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    src = _tiny_png(tmp_path)
    import files_client as fc

    monkeypatch.setattr(fc, "_file_size", lambda _p: fc.MAX_FILE_BYTES + 1)
    with pytest.raises(FilesAPIError, match="50 MB"):
        upload_file(src, dry_run=True)


def test_dry_run_upload_list_get_delete(tmp_path: Path) -> None:
    src = _tiny_png(tmp_path)
    uploaded = upload_file(src, expires_after=86400, dry_run=True)
    assert uploaded["dry_run"] is True
    assert str(uploaded["id"]).startswith("file_dry_")
    assert uploaded["filename"] == "plate.png"
    assert uploaded["bytes"] == src.stat().st_size
    assert uploaded["field_order"][0] == "expires_after"
    assert uploaded["field_order"][-1] == "file"

    listed = list_files(dry_run=True, limit=5)
    assert listed["dry_run"] is True
    assert listed["data"] == []

    meta = get_file(uploaded["id"], dry_run=True)
    assert meta["id"] == uploaded["id"]
    deleted = delete_file(uploaded["id"], dry_run=True)
    assert deleted["deleted"] is True
    assert deleted["id"] == uploaded["id"]


def test_live_upload_sends_multipart_in_order(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import files_client as fc

    captured: dict = {}

    def fake_http(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["data"] = kwargs.get("data")
        captured["content_type"] = kwargs.get("content_type")
        return {"id": "file_live_1", "object": "file", "bytes": 4, "filename": "hero.png"}

    monkeypatch.setattr(fc, "_http", fake_http)
    monkeypatch.setattr(fc, "_use_dry_run", lambda _dry: False)
    src = _tiny_png(tmp_path, "hero.png")
    result = upload_file(src, expires_after=3600, purpose="assistants", dry_run=False)
    assert result["id"] == "file_live_1"
    assert captured["method"] == "POST"
    assert captured["path"] == "/files"
    assert str(captured["content_type"]).startswith("multipart/form-data")
    body = captured["data"].decode("latin1")
    assert body.index('name="expires_after"') < body.index('name="file"')
    assert "hero.png" in body
    assert "bearer" not in body.lower()
    assert "xai_api_key" not in body.lower()


def test_save_inbox_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import files_client as fc

    inbox = tmp_path / "files_inbox"
    monkeypatch.setattr(fc, "FILES_INBOX_DIR", inbox)
    dest = fc.save_inbox_file("hero.png", b"\x89PNG data")
    assert dest.parent == inbox
    assert dest.name == "hero.png"
    assert dest.read_bytes() == b"\x89PNG data"
    with pytest.raises(FilesAPIError, match="empty"):
        fc.save_inbox_file("x.png", b"")
    with pytest.raises(FilesAPIError, match="50 MB"):
        fc.save_inbox_file("big.png", b"x" * (fc.MAX_FILE_BYTES + 1))


def test_create_public_url_posts_json(monkeypatch: pytest.MonkeyPatch) -> None:
    import files_client as fc

    captured: dict = {}

    def fake_http(method, path, **kwargs):
        captured["method"] = method
        captured["path"] = path
        captured["data"] = kwargs.get("data")
        captured["content_type"] = kwargs.get("content_type")
        return {"public_url": "https://files-cdn.x.ai/tok/file_live.png"}

    monkeypatch.setattr(fc, "_http", fake_http)
    monkeypatch.setattr(fc, "_use_dry_run", lambda _dry: False)
    out = create_public_url("file_live", expires_after=3600, dry_run=False)
    assert out["public_url"].startswith("https://files-cdn.x.ai/")
    assert captured["method"] == "POST"
    assert captured["path"].endswith("/public-url")
    assert captured["content_type"] == "application/json"
    assert b"expires_after" in captured["data"]


def test_public_url_dry_run() -> None:
    shared = create_public_url("file_dry_abc", expires_after=86400, dry_run=True)
    assert shared["dry_run"] is True
    assert shared["public_url"].startswith("https://dry-run.x.ai/")
    assert shared["expires_at"]
    revoked = revoke_public_url("file_dry_abc", dry_run=True)
    assert revoked["revoked"] is True
    with pytest.raises(FilesAPIError, match="file_id"):
        create_public_url("  ", dry_run=True)


def test_get_and_delete_require_id() -> None:
    with pytest.raises(FilesAPIError, match="file_id"):
        get_file("  ", dry_run=True)
    with pytest.raises(FilesAPIError, match="file_id"):
        delete_file("", dry_run=True)


def test_cli_files_upload_and_delete_guard(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from cli_helpers import run_cli

    monkeypatch.delenv("XAI_API_KEY", raising=False)
    src = _tiny_png(tmp_path)
    uploaded = run_cli("files", "upload", str(src), "--dry-run", "--json")
    assert uploaded.returncode == 0, uploaded.stderr
    assert "file_dry_" in uploaded.stdout
    assert "xai-" not in uploaded.stdout.lower()

    listed = run_cli("files", "list", "--dry-run", "--json")
    assert listed.returncode == 0, listed.stderr

    blocked = run_cli("files", "delete", "file_dry_abc")
    assert blocked.returncode == 1
    assert "--yes" in blocked.stdout

    gone = run_cli("files", "delete", "file_dry_abc", "--yes", "--dry-run", "--json")
    assert gone.returncode == 0, gone.stderr
    assert "true" in gone.stdout.lower() or "deleted" in gone.stdout.lower()
