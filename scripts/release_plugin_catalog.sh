#!/usr/bin/env bash
#
# Extremely thin shim for release catalog pinning.
# Delegates to the canonical CLI:
#   cinematic-studio plugin catalog pin
#
# Run as the final step before committing a plugin-affecting release.
#

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "→ Pinning marketplace catalog to git HEAD..."

# Prefer in-repo CLI so the pin SHA is this clone's HEAD. PATH cinematic-studio
# often defaults to ~/Grok-Cinematic-Projects (install tree, not always a git repo).
if [[ -f "$REPO_ROOT/tools/cinematic_studio_cli.py" ]]; then
    PYTHONPATH="${REPO_ROOT}${PYTHONPATH:+:${PYTHONPATH}}" \
        python3 -m tools.cinematic_studio_cli plugin catalog pin
elif command -v cinematic-studio >/dev/null 2>&1; then
    CINEMATIC_PROJECT_DIR="$REPO_ROOT" \
    CINEMATIC_REPO_ROOT="$REPO_ROOT" \
        cinematic-studio plugin catalog pin
else
    echo "❌ No in-repo tools/cinematic_studio_cli.py and no cinematic-studio on PATH" >&2
    exit 1
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