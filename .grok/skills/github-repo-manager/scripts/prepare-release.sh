#!/bin/bash
#
# prepare-release.sh
# Part of github-repo-manager skill
#
# Helps prepare a new release for cinematic studio repos
# Usage: ./scripts/prepare-release.sh [patch|minor|major]
#

set -euo pipefail

BUMP_TYPE=${1:-patch}

if [ ! -f "VERSION" ]; then
    echo "❌ No VERSION file found. Create one first (e.g. echo '3.6.5' > VERSION)"
    exit 1
fi

CURRENT_VERSION=$(cat VERSION | tr -d '[:space:]')
echo "📦 Current version: $CURRENT_VERSION"

# Simple semver bump
IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"

case "$BUMP_TYPE" in
    patch) patch=$((patch + 1)) ;;
    minor) minor=$((minor + 1)); patch=0 ;;
    major) major=$((major + 1)); minor=0; patch=0 ;;
    *) echo "Usage: $0 [patch|minor|major]"; exit 1 ;;
esac

NEW_VERSION="$major.$minor.$patch"
echo "🚀 Suggested new version: $NEW_VERSION"

echo ""
echo "Next steps (manual for safety):"
echo "1. Update VERSION file to $NEW_VERSION"
echo "2. Update CHANGELOG.md and RELEASE_NOTES_v${NEW_VERSION}.md"
echo "3. Commit changes"
echo "4. git tag -a v\( {NEW_VERSION} -m \"Release v \){NEW_VERSION}\""
echo "5. git push && git push --tags"
echo ""
echo "Or run with --auto to perform steps 1+3+4 (edit docs first!)"
