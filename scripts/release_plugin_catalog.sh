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

Next steps (pin cannot embed its own commit hash):
  1. Content must already be committed (skills, tools, docs).
  2. This pin wrote the current HEAD as the install SHA.
  3. Commit **only** catalog artifacts:
       git add .grok-plugin/marketplace.json .grok-plugin/plugin-index.json .grok-plugin/plugin.json
       git commit -m "chore(plugins): pin marketplace catalog to HEAD"
  4. Pre-publish gate (still green after the pin-only commit):
       bash scripts/verify_plugins.sh --release
       # or: cinematic-studio plugin catalog check --release
EOF