"""PR9: FastAPI control plane over studio_core."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))


def test_root_index() -> None:
    try:
        import fastapi  # noqa: F401
    except ImportError:
        return
    from fastapi.testclient import TestClient
    from studio_api.app import create_app

    client = TestClient(create_app())
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert body.get("docs") == "/docs"
    assert body.get("health") == "/health"


def test_create_app_and_health() -> None:

    try:
        import fastapi  # noqa: F401
    except ImportError:
        return
    from fastapi.testclient import TestClient
    from studio_api.app import create_app

    client = TestClient(create_app())
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["actions"] >= 10
    assert body["studio_version"]


def test_dashboard_endpoint() -> None:
    try:
        import fastapi  # noqa: F401
    except ImportError:
        return
    from fastapi.testclient import TestClient
    from studio_api.app import create_app

    client = TestClient(create_app())
    r = client.get("/v1/dashboard")
    assert r.status_code == 200
    snap = r.json()
    for key in ("project", "studio", "quota", "production", "studio_version"):
        assert key in snap


def test_bible_guided_endpoints() -> None:
    try:
        import fastapi  # noqa: F401
    except ImportError:
        return
    from fastapi.testclient import TestClient
    from studio_api.app import create_app

    client = TestClient(create_app())
    stages = client.get("/v1/bible/stages")
    assert stages.status_code == 200
    body = stages.json()
    assert body["count"] >= 4
    ids = [s["id"] for s in body["stages"]]
    assert "story" in ids and "review" in ids

    bad = client.post(
        "/v1/bible/validate",
        json={"stage_id": "story", "answers": {}},
    )
    assert bad.status_code == 200
    assert bad.json()["ok"] is False

    ok_val = client.post(
        "/v1/bible/validate",
        json={"stage_id": "story", "answers": {"title": "E2E Rain Code"}},
    )
    assert ok_val.status_code == 200
    assert ok_val.json()["ok"] is True

    gen = client.post(
        "/v1/bible/guided",
        json={
            "answers": {
                "title": "E2E Rain Code",
                "genre": "Sci-Fi",
                "target_duration_seconds": 90,
                "complexity": "Medium",
                "chat_model": "grok-4.5",
                "video_model": "grok-imagine-video",
                "logline": "Neon rain and a rogue AI.",
            },
            "write": False,
        },
    )
    assert gen.status_code == 200, gen.text
    out = gen.json()
    assert out["ok"] is True
    assert out["bible"]["project_title"] == "E2E Rain Code"
    assert out["summary"]


def test_meta_phase2_endpoints() -> None:
    try:
        import fastapi  # noqa: F401
    except ImportError:
        return
    from fastapi.testclient import TestClient
    from studio_api.app import create_app

    client = TestClient(create_app())
    health = client.get("/health")
    assert health.status_code == 200
    assert "xai_api_key_set" in health.json()

    env = client.get("/v1/meta/env")
    assert env.status_code == 200
    assert "xai_api_key_set" in env.json()

    opts = client.get("/v1/meta/production-options")
    assert opts.status_code == 200
    body = opts.json()
    assert "genres" in body and "defaults" in body
    assert "grok-imagine-image-2.0" in body.get("image_models", [])
    assert "xai_responses_tool" in body.get("imagine_surfaces", [])
    assert "video_extend" in body.get("imagine_execution_modes", [])

    agents = client.get("/v1/meta/agents")
    assert agents.status_code == 200
    ar = agents.json()
    assert ar["core_count"] >= 1
    assert ar["groups"]

    cards = client.get("/v1/meta/role-cards")
    assert cards.status_code == 200
    cr = cards.json()
    assert cr["count"] >= 1
    stem = cr["role_cards"][0]["stem"]
    one = client.get(f"/v1/meta/role-cards/{stem}")
    assert one.status_code == 200
    assert one.json().get("content")

    bad = client.get("/v1/meta/role-cards/../etc/passwd")
    assert bad.status_code in {400, 404, 422}


def test_list_and_get_actions() -> None:
    try:
        import fastapi  # noqa: F401
    except ImportError:
        return
    from fastapi.testclient import TestClient
    from studio_api.app import create_app

    client = TestClient(create_app())
    r = client.get("/v1/actions")
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == len(data["actions"])
    ids = {a["id"] for a in data["actions"]}
    assert "status" in ids
    assert "dna_list" in ids

    detail = client.get("/v1/actions/status")
    assert detail.status_code == 200
    assert detail.json()["base_argv"] == ["status"]

    missing = client.get("/v1/actions/nope_not_real")
    assert missing.status_code == 404


def test_execute_status() -> None:
    try:
        import fastapi  # noqa: F401
    except ImportError:
        return
    from fastapi.testclient import TestClient
    from studio_api.app import create_app

    client = TestClient(create_app())
    r = client.post("/v1/actions/status/execute", json={"answers": {}, "mode": "inprocess"})
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is True
    assert body["returncode"] == 0
    assert body["argv"] == ["status"]
    assert body["stdout"] or body["output"]


def test_execute_validation_failure() -> None:
    try:
        import fastapi  # noqa: F401
    except ImportError:
        return
    from fastapi.testclient import TestClient
    from studio_api.app import create_app

    client = TestClient(create_app())
    r = client.post(
        "/v1/actions/bible_create/execute",
        json={"answers": {"title": ""}, "mode": "inprocess"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ok"] is False
    assert body["errors"] or body["returncode"] != 0


def test_api_cli_help() -> None:
    import subprocess

    cli = ROOT / "tools" / "cinematic_studio_cli.py"
    result = subprocess.run(
        [sys.executable, str(cli), "api", "--help"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0
    assert "FastAPI" in result.stdout or "control plane" in result.stdout.lower() or "api" in result.stdout.lower()


def test_main_help_lists_api() -> None:
    import subprocess

    cli = ROOT / "tools" / "cinematic_studio_cli.py"
    result = subprocess.run(
        [sys.executable, str(cli), "--help"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0
    assert "api" in result.stdout


if __name__ == "__main__":
    test_create_app_and_health()
    test_dashboard_endpoint()
    test_list_and_get_actions()
    test_execute_status()
    test_execute_validation_failure()
    test_api_cli_help()
    test_main_help_lists_api()
    print("studio_api tests passed")
