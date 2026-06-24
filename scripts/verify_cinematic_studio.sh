#!/usr/bin/env bash
#
# Verify Grok Imagine Cinematic Studio Installation
# Backward-compatible wrapper — delegates to cinematic_studio.sh
#

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/cinematic_studio.sh" verify "$@"