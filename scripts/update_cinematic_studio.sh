#!/usr/bin/env bash
#
# Grok Imagine Cinematic Studio v3.11.1 Updater
# Backward-compatible wrapper — delegates to cinematic_studio.sh
#

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/cinematic_studio.sh" update "$@"