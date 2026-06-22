#!/bin/bash
#
# Grok Imagine Cinematic Studio v3.6.4 Installer
# https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio
#

set -e

echo "🎥 Grok Imagine Cinematic Studio v3.6.4 Installer"
echo "================================================"
echo ""

# Configuration
SKILLS_DIR="$HOME/.grok/skills"
PROJECT_DIR="$HOME/Grok-Cinematic-Projects"
REPO="FineComputer14451/Grok-Imagine-Cinematic-Studio"
ZIP_URL="https://github.com/${REPO}/releases/latest/download/grok-imagine-cinematic-studio-skills-install-v3.6.4.zip"

# Create directories
echo "→ Creating directories..."
mkdir -p "$SKILLS_DIR"
mkdir -p "$PROJECT_DIR/references"

# Download latest bundle
echo "→ Downloading latest release..."
TMP_ZIP="/tmp/cinematic-studio-v3.6.4.zip"
curl -sL "$ZIP_URL" -o "$TMP_ZIP"

if [ ! -f "$TMP_ZIP" ]; then
    echo "❌ Failed to download the zip file."
    exit 1
fi

# Extract
echo "→ Extracting files..."
TMP_EXTRACT="/tmp/cinematic-extract"
rm -rf "$TMP_EXTRACT"
mkdir -p "$TMP_EXTRACT"
unzip -q "$TMP_ZIP" -d "$TMP_EXTRACT"

# Install skills
echo "→ Installing skills into ~/.grok/skills/..."
cp -r "$TMP_EXTRACT/.grok/skills/"* "$SKILLS_DIR/"

# Install references and prompts
echo "→ Installing references and prompts..."
cp -r "$TMP_EXTRACT/references/"* "$PROJECT_DIR/references/"
cp "$TMP_EXTRACT/AGENTS.md" "$PROJECT_DIR/"
cp "$TMP_EXTRACT/MASTER_PROMPT_v3.6.md" "$PROJECT_DIR/"

# Cleanup
rm -rf "$TMP_ZIP" "$TMP_EXTRACT"

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Refresh the Skills page in Grok"
echo "2. Start a new chat"
echo "3. Type: Activate Grok Imagine Cinematic Studio v3.6.4"
echo ""
echo "Your cinematic projects folder is at: $PROJECT_DIR"

