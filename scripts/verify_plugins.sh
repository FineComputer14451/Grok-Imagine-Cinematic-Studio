#!/usr/bin/env bash
#
# Verify Grok plugin manifest, marketplace catalog, and installed plugin checkout.
# Delegates catalog checks to:
#   cinematic-studio plugin catalog check [--release]
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

release_mode=false
if [[ "${1:-}" == "--release" ]]; then
    release_mode=true
fi

echo "→ Validating plugin manifest..."
grok plugin validate

echo "→ Checking marketplace catalog + plugin-index..."
if command -v cinematic-studio >/dev/null 2>&1; then
    if $release_mode; then
        cinematic-studio plugin catalog check --release
    else
        cinematic-studio plugin catalog check
    fi
else
    # Thin fallback to the canonical CLI module
    if $release_mode; then
        python3 -m tools.cinematic_studio_cli plugin catalog check --release
    else
        python3 -m tools.cinematic_studio_cli plugin catalog check
    fi
fi

if grok plugin details grok-imagine-cinematic-studio >/dev/null 2>&1; then
    echo "→ Verifying installed plugin checkout..."
    bash scripts/cinematic_studio.sh verify --plugin
else
    echo "ℹ️  grok-imagine-cinematic-studio not installed — skipping verify --plugin"
fi

echo "✅ Plugin verification complete"
