#!/bin/bash
#
# Grok Imagine Cinematic Studio v3.6.4 Installer
# https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio
#

set -e

echo "🎥 Grok Imagine Cinematic Studio v3.6.4 Installer"
echo "================================================"
echo ""

SKILLS_DIR="$HOME/.grok/skills"
PROJECT_DIR="$HOME/Grok-Cinematic-Projects"
ZIP_URL="https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/latest/download/grok-imagine-cinematic-studio-skills-install-v3.6.4.zip"

echo "→ Creating directories..."
mkdir -p "$SKILLS_DIR"
mkdir -p "$PROJECT_DIR/references"

echo "→ Downloading latest release..."
TMP_ZIP="/tmp/cinematic-studio-v3.6.4.zip"
curl -sL "$ZIP_URL" -o "$TMP_ZIP"

if [ ! -f "$TMP_ZIP" ]; then
    echo "❌ Failed to download the zip file."
    exit 1
fi

echo "→ Extracting files..."
TMP_EXTRACT="/tmp/cinematic-extract"
rm -rf "$TMP_EXTRACT"
mkdir -p "$TMP_EXTRACT"
unzip -q "$TMP_ZIP" -d "$TMP_EXTRACT"

echo "→ Installing skills..."
cp -r "$TMP_EXTRACT/.grok/skills/"* "$SKILLS_DIR/"

echo "→ Installing references and prompts..."
cp -r "$TMP_EXTRACT/references/"* "$PROJECT_DIR/references/"
cp "$TMP_EXTRACT/AGENTS.md" "$PROJECT_DIR/" 2>/dev/null || true
cp "$TMP_EXTRACT/MASTER_PROMPT_v3.6.md" "$PROJECT_DIR/" 2>/dev/null || true

rm -rf "$TMP_ZIP" "$TMP_EXTRACT"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Refresh the Skills page in Grok"
echo "2. Start a new chat"
echo "3. Type: Activate Grok Imagine Cinematic Studio v3.6.4"
echo ""
echo "Your projects folder: $PROJECT_DIR"
