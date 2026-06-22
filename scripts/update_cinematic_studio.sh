#!/bin/bash
#
# Grok Imagine Cinematic Studio v3.6.4 Updater
#

set -e

echo "🔄 Grok Imagine Cinematic Studio v3.6.4 Updater"
echo "=============================================="
echo ""

SKILLS_DIR="$HOME/.grok/skills"
PROJECT_DIR="$HOME/Grok-Cinematic-Projects"
ZIP_URL="https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/latest/download/grok-imagine-cinematic-studio-skills-install-v3.6.4.zip"

if [ ! -d "$SKILLS_DIR" ]; then
    echo "❌ No existing installation found."
    echo "Please run the installer first."
    exit 1
fi

BACKUP_DIR="$HOME/.grok/skills-backup-$(date +%Y%m%d-%H%M%S)"
echo "→ Creating backup at: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "$SKILLS_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true

echo "→ Downloading latest release..."
TMP_ZIP="/tmp/cinematic-studio-v3.6.4.zip"
curl -sL "$ZIP_URL" -o "$TMP_ZIP"

TMP_EXTRACT="/tmp/cinematic-extract"
rm -rf "$TMP_EXTRACT"
mkdir -p "$TMP_EXTRACT"
unzip -q "$TMP_ZIP" -d "$TMP_EXTRACT"

echo "→ Updating skills..."
cp -r "$TMP_EXTRACT/.grok/skills/"* "$SKILLS_DIR/"

echo "→ Updating references..."
mkdir -p "$PROJECT_DIR/references"
cp -r "$TMP_EXTRACT/references/"* "$PROJECT_DIR/references/"
cp "$TMP_EXTRACT/AGENTS.md" "$PROJECT_DIR/" 2>/dev/null || true
cp "$TMP_EXTRACT/MASTER_PROMPT_v3.6.md" "$PROJECT_DIR/" 2>/dev/null || true

rm -rf "$TMP_ZIP" "$TMP_EXTRACT"

echo ""
echo "✅ Update complete!"
echo "Backup saved to: $BACKUP_DIR"
echo ""
echo "Refresh Skills page and run: Activate Grok Imagine Cinematic Studio v3.6.4"
