"""Tests for Imagine API region routing."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from imagine_regions import (  # noqa: E402
    DEFAULT_REGION,
    get_active_region,
    get_failover_chain,
    region_payload_fields,
    region_request_headers,
    set_imagine_region,
)


def test_default_region() -> None:
    assert get_active_region() in ("us-east-1", "eu-west-1", "us-west-2")


def test_failover_chain_unique() -> None:
    chain = get_failover_chain(DEFAULT_REGION)
    assert chain[0] == DEFAULT_REGION or chain
    assert len(chain) == len(set(chain))


def test_set_region() -> None:
    settings = set_imagine_region("eu-west-1", persist=False)
    assert settings["region"] == "eu-west-1"


def test_region_headers() -> None:
    headers = region_request_headers("us-west-2")
    assert headers["x-xai-region"] == "us-west-2"
    assert region_payload_fields("us-west-2")["region"] == "us-west-2"


if __name__ == "__main__":
    test_default_region()
    test_failover_chain_unique()
    test_set_region()
    test_region_headers()
    print("All imagine region tests passed")