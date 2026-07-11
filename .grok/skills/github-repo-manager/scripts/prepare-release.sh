#!/usr/bin/env bash
#
# prepare-release.sh — github-repo-manager (v3.7.1)
# Suggests next semver from VERSION. Does not auto-commit unless --auto (still no push).
# Usage: bash .grok/skills/github-repo-manager/scripts/prepare-release.sh [patch|minor|major] [--auto]
#

set -euo pipefail

# scripts/ → skill/ → skills/ → .grok/ → repo root
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$ROOT"

BUMP_TYPE="${1:-patch}"
AUTO=false
if [[ "${2:-}" == "--auto" ]] || [[ "${1:-}" == "--auto" ]]; then
  AUTO=true
  [[ "${1:-}" == "--auto" ]] && BUMP_TYPE=patch
  [[ "${2:-}" == "--auto" ]] && BUMP_TYPE="${1:-patch}"
fi

if [[ ! -f VERSION ]]; then
  echo "❌ No VERSION file. Create one first (e.g. echo '3.7.1' > VERSION)"
  exit 1
fi

CURRENT_VERSION="$(tr -d '[:space:]' < VERSION)"
echo "📦 Current version: $CURRENT_VERSION"

IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"
if [[ -z "${major:-}" || -z "${minor:-}" || -z "${patch:-}" ]]; then
  echo "❌ VERSION must be semver X.Y.Z (got: $CURRENT_VERSION)"
  exit 1
fi

case "$BUMP_TYPE" in
  patch) patch=$((patch + 1)) ;;
  minor) minor=$((minor + 1)); patch=0 ;;
  major) major=$((major + 1)); minor=0; patch=0 ;;
  *)
    echo "Usage: $0 [patch|minor|major] [--auto]"
    exit 1
    ;;
esac

NEW_VERSION="${major}.${minor}.${patch}"
echo "🚀 Suggested new version: $NEW_VERSION"
echo ""
echo "Next steps (manual for safety):"
echo "1. Update VERSION to $NEW_VERSION"
echo "2. Update CHANGELOG.md and RELEASE_NOTES_v${NEW_VERSION}.md (if used)"
echo "3. Sync AGENTS.md / README skill counts & Model Layer notes if needed"
echo "4. Commit content: git commit -m \"chore(release): prepare v${NEW_VERSION}\""
echo "5. Pin plugin catalog: bash scripts/release_plugin_catalog.sh"
echo "6. Commit only .grok-plugin/: chore(plugins): pin marketplace catalog"
echo "7. Tag: git tag -a v${NEW_VERSION} -m \"Release v${NEW_VERSION}\""
echo "8. Push branch + tags (with approval): git push && git push --tags"
echo "9. Gate: bash scripts/verify_plugins.sh --release"
echo ""

if [[ "$AUTO" == true ]]; then
  echo "⚙️  --auto: writing VERSION only (no commit/tag/push)"
  echo "$NEW_VERSION" > VERSION
  echo "✅ VERSION is now $NEW_VERSION — edit CHANGELOG, then commit yourself."
fi
