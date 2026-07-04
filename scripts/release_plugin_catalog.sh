#!/usr/bin/env bash
#
# Extremely thin shim for release catalog pinning.
# Delegates to the canonical CLI:
#   cinematic-studio plugin catalog pin
#
# Run as the final step before committing a plugin-affecting release.
#

set -euo pipefail

cd "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "→ Pinning marketplace catalog to git HEAD..."

if command -v cinematic-studio >/dev/null 2>&1; then
    cinematic-studio plugin catalog pin
else
    python3 -m tools.cinematic_studio_cli plugin catalog pin
fi

cat <<'EOF'

Next steps:
  1. Stage your feature changes together with:
       .grok-plugin/marketplace.json
       .grok-plugin/plugin-index.json
       .grok-plugin/plugin.json   (if changed)
  2. Commit in a single commit — do not split catalog sha bumps into a follow-up commit.
  3. Before publish/tag: bash scripts/verify_plugins.sh --release
     (or: cinematic-studio plugin catalog check --release)
EOF