#!/usr/bin/env bash
#
# Verify Grok plugin manifest, marketplace catalog, and installed plugin checkout.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "→ Validating plugin manifest..."
grok plugin validate

echo "→ Checking marketplace catalog + plugin-index..."
python3 scripts/generate_plugin_index.py --check

if grok plugin details grok-imagine-cinematic-studio >/dev/null 2>&1; then
    echo "→ Verifying installed plugin checkout..."
    bash scripts/cinematic_studio.sh verify --plugin
else
    echo "ℹ️  grok-imagine-cinematic-studio not installed — skipping verify --plugin"
fi

echo "✅ Plugin verification complete"