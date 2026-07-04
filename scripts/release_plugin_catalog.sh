#!/usr/bin/env bash
#
# Pin marketplace catalog to HEAD and verify release-ready plugin artifacts.
# Run as the final step before committing a plugin-affecting release.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

echo "→ Pinning marketplace catalog to git HEAD..."
python3 scripts/generate_plugin_index.py --sync-sha

echo "→ Verifying release-ready catalog state..."
python3 scripts/generate_plugin_index.py --check --release

cat <<'EOF'

Next steps:
  1. Stage your feature changes together with:
       .grok-plugin/marketplace.json
       .grok-plugin/plugin-index.json
       .grok-plugin/plugin.json   (if changed)
  2. Commit in a single commit — do not split catalog sha bumps into a follow-up commit.
  3. Before publish/tag: bash scripts/verify_plugins.sh --release
EOF