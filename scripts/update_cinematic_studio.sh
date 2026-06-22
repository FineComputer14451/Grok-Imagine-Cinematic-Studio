#!/bin/bash
#
# Grok Imagine Cinematic Studio v3.6.4 Updater
# https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio
#
# This script updates an existing installation to the latest version.
#

set -e

echo "🔄 Grok Imagine Cinematic Studio v3.6.4 Updater"
echo "=============================================="
echo ""

# Configuration
SKILLS_DIR="$HOME/.grok/skills"
PROJECT_DIR="$HOME/Grok-Cinematic-Projects"
REPO="FineComputer14451/Grok-Imagine-Cinematic-Studio"
ZIP_URL="https://github.com/${REPO}/releases/latest/download/grok-imagine-cinematic-studio-skills-install-v3.6.4.zip"

# Check if skills directory exists
if [ ! -d "$SKILLS_DIR" ]; then
    echo "❌ No existing installation found at $SKILLS_DIR"
    echo "Please run the installer first:"
    echo "bash <(curl -sL https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main/scripts/install_cinematic_studio.sh)"
    exit 1
fi

echo "→ Existing installation detected. Preparing update..."

# Create backup of current skills (optional safety)
BACKUP_DIR="$HOME/.grok/skills-backup-$(date +%Y%m%d-%H%M%S)"
echo "→ Creating backup at: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
cp -r "$SKILLS_DIR"/* "$BACKUP_DIR/" 2>/dev/null || true

# Download latest bundle
echo "→ Downloading latest release..."
TMP_ZIP="/tmp/cinematic-studio-v3.6.4.zip"
curl -sL "$ZIP_URL" -o "$TMP_ZIP"

if [ ! -f "$TMP_ZIP" ]; then
    echo "❌ Failed to download the update zip file."
    exit 1
fi

# Extract
echo "→ Extracting update files..."
TMP_EXTRACT="/tmp/cinematic-extract"
rm -rf "$TMP_EXTRACT"
mkdir -p "$TMP_EXTRACT"
unzip -q "$TMP_ZIP" -d "$TMP_EXTRACT"

# Update skills (overwrite)
echo "→ Updating skills in ~/.grok/skills/..."
cp -r "$TMP_EXTRACT/.grok/skills/"* "$SKILLS_DIR/"

# Update references and prompts
echo "→ Updating references and prompts..."
mkdir -p "$PROJECT_DIR/references"
cp -r "$TMP_EXTRACT/references/"* "$PROJECT_DIR/references/"
cp "$TMP_EXTRACT/AGENTS.md" "$PROJECT_DIR/" 2>/dev/null || true
cp "$TMP_EXTRACT/MASTER_PROMPT_v3.6.md" "$PROJECT_DIR/" 2>/dev/null || true

# Cleanup
rm -rf "$TMP_ZIP" "$TMP_EXTRACT"

echo ""
echo "✅ Update complete!"
echo ""
echo "Backup of previous version saved to:"
echo "$BACKUP_DIR"
echo ""
echo "Next steps:"
echo "1. Refresh the Skills page in Grok"
echo "2. Start a new chat"
echo "3. Type: Activate Grok Imagine Cinematic Studio v3.6.4"
echo ""
echo "To verify the update, run:"
echo "./scripts/verify_cinematic_studio.sh"

