#!/usr/bin/env bash
#
# Build the lightweight meta-installer zip for Grok Imagine Cinematic Studio v3.7.1.
# Ships the bootstrap skill + installer scripts (pulls full suite on install).
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# shellcheck source=lib/cinematic_studio_common.sh
source "$SCRIPT_DIR/lib/cinematic_studio_common.sh"
VERSION="$(tr -d '[:space:]' < "$REPO_ROOT/VERSION")"
SKILL_NAME="cinematic-studio-meta-installer"
ZIP_NAME="grok-imagine-cinematic-studio-meta-installer-v${VERSION}.zip"
OUTPUT="${1:-$REPO_ROOT/$ZIP_NAME}"
if [[ "$OUTPUT" != /* ]]; then
    mkdir -p "$(dirname "$OUTPUT")"
    OUTPUT="$(cd "$(dirname "$OUTPUT")" && pwd)/$(basename "$OUTPUT")"
fi
STAGING="/tmp/cinematic-meta-installer-staging-$$"

META_SKILL_SRC="$REPO_ROOT/.grok/skills/$SKILL_NAME"
META_SKILL_DST="$STAGING/.grok/skills/$SKILL_NAME"

cleanup() {
    rm -rf "$STAGING"
}
trap cleanup EXIT

if [[ ! -f "$META_SKILL_SRC/SKILL.md" ]]; then
    echo "❌ Missing skill: $META_SKILL_SRC/SKILL.md"
    exit 1
fi

mkdir -p "$META_SKILL_DST" "$STAGING/scripts/lib"

echo "→ Staging meta-installer skill..."
cp -r "$META_SKILL_SRC/"* "$META_SKILL_DST/"

echo "→ Staging installer scripts..."
for script in "${CINEMATIC_INSTALLER_SCRIPTS[@]}"; do
    if [[ ! -f "$REPO_ROOT/scripts/$script" ]]; then
        echo "❌ Missing script: scripts/$script"
        exit 1
    fi
    cp "$REPO_ROOT/scripts/$script" "$STAGING/scripts/"
done
cp "$REPO_ROOT/scripts/lib/cinematic_studio_common.sh" "$STAGING/scripts/lib/"

cp "$REPO_ROOT/VERSION" "$STAGING/VERSION"

cat > "$STAGING/bootstrap.sh" <<'BOOT'
#!/usr/bin/env bash
# One-shot bootstrap — install skill into Grok and run full studio install.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILLS_DIR="${SKILLS_DIR:-$HOME/.grok/skills}"
mkdir -p "$SKILLS_DIR"
cp -r "$ROOT/.grok/skills/"* "$SKILLS_DIR/"
exec bash "$ROOT/scripts/cinematic_studio.sh" install
BOOT
chmod +x "$STAGING/bootstrap.sh"
chmod +x "$META_SKILL_DST/scripts/install.sh" 2>/dev/null || true

rm -f "$OUTPUT"
(
    cd "$STAGING"
    zip -qr "$OUTPUT" .
)

echo "✅ Built meta-installer bundle: $OUTPUT"
echo "   Version: v${VERSION}"
echo "   Skill: $SKILL_NAME"
echo ""
echo "Deploy options:"
echo "  1. Skill only:  cp -r .grok/skills/$SKILL_NAME → ~/.grok/skills/"
echo "  2. Full bootstrap: unzip && ./bootstrap.sh"
echo "  3. Install suite:  bash scripts/cinematic_studio.sh install"