#!/usr/bin/env bash
#
# Shared library for Grok Imagine Cinematic Studio meta installer (v3.6.6)
#

CINEMATIC_STUDIO_FALLBACK_VERSION="3.6.6"

CINEMATIC_INSTALLER_SCRIPTS=(
    cinematic_studio.sh
    install_cinematic_studio.sh
    update_cinematic_studio.sh
    verify_cinematic_studio.sh
    required_skills.manifest
)

CINEMATIC_GITHUB_MAIN_URL="https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/archive/refs/heads/main.zip"

cinematic_studio_resolve_root() {
    local script_dir="$1"
    if [[ -f "$script_dir/../VERSION" ]]; then
        cd "$script_dir/.." && pwd
        return 0
    fi
    if [[ -f "$script_dir/../../VERSION" ]]; then
        cd "$script_dir/../.." && pwd
        return 0
    fi
    echo ""
}

cinematic_studio_load_version() {
    local root="$1"
    local remote=""

    if [[ -n "$root" && -f "$root/VERSION" ]]; then
        tr -d '[:space:]' < "$root/VERSION"
        return 0
    fi

    if [[ -n "${CINEMATIC_RAW_BASE:-}" ]]; then
        remote="$(curl -fsSL "$CINEMATIC_RAW_BASE/VERSION" 2>/dev/null | tr -d '[:space:]')" || true
        if [[ -n "$remote" ]]; then
            echo "$remote"
            return 0
        fi
    fi

    echo "$CINEMATIC_STUDIO_FALLBACK_VERSION"
}

cinematic_studio_init_paths() {
    local script_dir="$1"
    CINEMATIC_SCRIPT_DIR="$script_dir"
    CINEMATIC_REPO_ROOT="$(cinematic_studio_resolve_root "$script_dir")"
    CINEMATIC_RAW_BASE="${CINEMATIC_RAW_BASE:-https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main}"
    CINEMATIC_STUDIO_VERSION="$(cinematic_studio_load_version "$CINEMATIC_REPO_ROOT")"
    SKILLS_DIR="${SKILLS_DIR:-$HOME/.grok/skills}"
    PROJECT_DIR="${PROJECT_DIR:-$HOME/Grok-Cinematic-Projects}"
    CINEMATIC_RELEASE_BASE="${CINEMATIC_RELEASE_BASE:-https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/latest/download}"
    CINEMATIC_ZIP_NAME="grok-imagine-cinematic-studio-skills-install-v${CINEMATIC_STUDIO_VERSION}.zip"
    CINEMATIC_MANIFEST="${CINEMATIC_MANIFEST:-$script_dir/required_skills.manifest}"
}

cinematic_studio_bundle_urls() {
    local version="$1"
    local zip_name="grok-imagine-cinematic-studio-skills-install-v${version}.zip"
    printf '%s\n' \
        "$CINEMATIC_RELEASE_BASE/$zip_name" \
        "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/download/v${version}/${zip_name}" \
        "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/download/${version}/${zip_name}"
}

cinematic_studio_ensure_manifest() {
    local manifest="${1:-${CINEMATIC_MANIFEST:-}}"
    [[ -n "$manifest" ]] || return 1
    if [[ -f "$manifest" ]]; then
        return 0
    fi
    mkdir -p "$(dirname "$manifest")"
    curl -fsSL "${CINEMATIC_RAW_BASE:-https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main}/scripts/required_skills.manifest" -o "$manifest"
}

cinematic_studio_read_manifest() {
    local manifest="$1"
    local tier="${2:-all}"
    local -n _skills_out="$3"
    local line=""
    local is_core=false

    _skills_out=()
    cinematic_studio_ensure_manifest "$manifest"

    while IFS= read -r line || [[ -n "$line" ]]; do
        [[ "$line" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue

        is_core=false
        if [[ "$line" == *"# core"* ]]; then
            is_core=true
        fi

        line="${line%%#*}"
        line="$(echo "$line" | xargs)"
        [[ -z "$line" ]] && continue

        if [[ "$tier" == "core" && "$is_core" != true ]]; then
            continue
        fi

        _skills_out+=("$line")
    done < "$manifest"
}

cinematic_studio_download_release_zip() {
    local tmp_zip="$1"
    local url=""

    echo "→ Downloading release bundle ($CINEMATIC_ZIP_NAME)..." >&2
    while IFS= read -r url; do
        [[ -z "$url" ]] && continue
        echo "   trying $url" >&2
        if curl -fsSL "$url" -o "$tmp_zip" \
            && [[ -s "$tmp_zip" ]] \
            && unzip -tq "$tmp_zip" >/dev/null 2>&1; then
            return 0
        fi
        echo "   invalid or empty bundle, trying next..." >&2
        rm -f "$tmp_zip"
    done < <(cinematic_studio_bundle_urls "$CINEMATIC_STUDIO_VERSION")

    return 1
}

cinematic_studio_extract_bundle() {
    local tmp_zip="$1"
    local tmp_extract="$2"
    echo "→ Extracting bundle..." >&2
    rm -rf "$tmp_extract"
    mkdir -p "$tmp_extract"
    unzip -q "$tmp_zip" -d "$tmp_extract"
}

# Resolve bundle root — handles flat zips and nested release folders.
cinematic_studio_bundle_root() {
    local base="$1"
    local child=""

    [[ -d "$base/.grok/skills" ]] && { echo "$base"; return 0; }

    shopt -s nullglob
    for child in "$base"/*; do
        [[ -d "$child/.grok/skills" ]] || continue
        echo "$child"
        shopt -u nullglob
        return 0
    done
    shopt -u nullglob

    return 1
}

cinematic_studio_copy_tools_tree() {
    local tools_src="$1"
    local dest="$PROJECT_DIR/tools"
    local pyfile=""

    [[ -d "$tools_src" ]] || return 1

    mkdir -p "$dest/cli"
    shopt -s nullglob
    for pyfile in "$tools_src"/*.py; do
        cp "$pyfile" "$dest/"
    done
    if [[ -d "$tools_src/cli" ]]; then
        for pyfile in "$tools_src/cli"/*.py; do
            cp "$pyfile" "$dest/cli/"
        done
    fi
    shopt -u nullglob
    return 0
}

cinematic_studio_tools_complete() {
    [[ -f "$PROJECT_DIR/tools/cinematic_studio_cli.py" \
        && -f "$PROJECT_DIR/tools/models.py" \
        && -f "$PROJECT_DIR/tools/cli/models_commands.py" ]]
}

cinematic_studio_resolve_payload_path() {
    local bundle_root="$1"
    local rel="$2"

    if [[ -d "$bundle_root/$rel" || -f "$bundle_root/$rel" ]]; then
        echo "$bundle_root/$rel"
        return 0
    fi
    if [[ -n "${CINEMATIC_REPO_ROOT:-}" ]]; then
        if [[ -d "$CINEMATIC_REPO_ROOT/$rel" || -f "$CINEMATIC_REPO_ROOT/$rel" ]]; then
            echo "$CINEMATIC_REPO_ROOT/$rel"
            return 0
        fi
    fi
    return 1
}

cinematic_studio_install_scripts() {
    local scripts_src="$1"
    local f=""

    [[ -d "$scripts_src" ]] || return 1

    echo "→ Installing meta-installer scripts to $PROJECT_DIR/scripts ..."
    mkdir -p "$PROJECT_DIR/scripts/lib"
    for f in "${CINEMATIC_INSTALLER_SCRIPTS[@]}"; do
        [[ -f "$scripts_src/$f" ]] && cp "$scripts_src/$f" "$PROJECT_DIR/scripts/"
    done
    [[ -f "$scripts_src/lib/cinematic_studio_common.sh" ]] && \
        cp "$scripts_src/lib/cinematic_studio_common.sh" "$PROJECT_DIR/scripts/lib/"
}

cinematic_studio_fetch_github_main() {
    local tmp_zip="$1"
    local tmp_extract="$2"
    local -n _archive_out="$3"

    _archive_out=""

    if ! curl -fsSL "$CINEMATIC_GITHUB_MAIN_URL" -o "$tmp_zip"; then
        return 1
    fi
    if ! unzip -tq "$tmp_zip" >/dev/null 2>&1; then
        rm -f "$tmp_zip"
        return 1
    fi

    rm -rf "$tmp_extract"
    mkdir -p "$tmp_extract"
    unzip -q "$tmp_zip" -d "$tmp_extract"

    _archive_out="$(find "$tmp_extract" -mindepth 1 -maxdepth 1 -type d | head -1)"
    [[ -n "$_archive_out" ]] || return 1
    return 0
}

# Acquire a staging root: extracted bundle dir or local repo root. Prints path on success.
cinematic_studio_acquire_bundle() {
    local tmp_zip="$1"
    local tmp_extract="$2"

    if cinematic_studio_download_release_zip "$tmp_zip"; then
        cinematic_studio_extract_bundle "$tmp_zip" "$tmp_extract"
        if cinematic_studio_bundle_root "$tmp_extract" >/dev/null; then
            echo "$tmp_extract"
            return 0
        fi
        echo "   bundle missing .grok/skills/, trying fallback..." >&2
        rm -rf "$tmp_zip" "$tmp_extract"
    fi

    if [[ -n "$CINEMATIC_REPO_ROOT" && -d "$CINEMATIC_REPO_ROOT/.grok/skills" ]]; then
        echo "→ Using local repository bundle at $CINEMATIC_REPO_ROOT" >&2
        echo "$CINEMATIC_REPO_ROOT"
        return 0
    fi

    echo "❌ Failed to download skills bundle from GitHub releases." >&2
    echo "   Expected asset: $CINEMATIC_ZIP_NAME" >&2
    return 1
}

cinematic_studio_install_tree() {
    local root="$1"
    local normalized=""
    local skills_src=""
    local refs_src=""
    local payload=""
    local doc=""

    normalized="$(cinematic_studio_bundle_root "$root")" || {
        echo "❌ Bundle is missing .grok/skills/"
        return 1
    }
    root="$normalized"
    skills_src="$root/.grok/skills"
    refs_src="$root/references"

    echo "→ Creating directories..."
    mkdir -p "$SKILLS_DIR"
    mkdir -p "$PROJECT_DIR/references"
    mkdir -p "$PROJECT_DIR/tools"
    mkdir -p "$PROJECT_DIR/config"

    echo "→ Installing skills to $SKILLS_DIR ..."
    cp -r "$skills_src/"* "$SKILLS_DIR/"

    if [[ -d "$refs_src" ]]; then
        echo "→ Installing references to $PROJECT_DIR ..."
        cp -r "$refs_src/"* "$PROJECT_DIR/references/"
    fi

    if payload="$(cinematic_studio_resolve_payload_path "$root" "tools")"; then
        echo "→ Installing CLI tools to $PROJECT_DIR/tools ..."
        cinematic_studio_copy_tools_tree "$payload"
    fi

    if payload="$(cinematic_studio_resolve_payload_path "$root" "config")"; then
        echo "→ Installing config templates to $PROJECT_DIR/config ..."
        cp -r "$payload/"* "$PROJECT_DIR/config/"
    fi

    if payload="$(cinematic_studio_resolve_payload_path "$root" "requirements.txt")"; then
        cp "$payload" "$PROJECT_DIR/"
    fi

    if payload="$(cinematic_studio_resolve_payload_path "$root" "scripts")"; then
        cinematic_studio_install_scripts "$payload"
    fi

    for doc in AGENTS.md MASTER_PROMPT_v3.6.md; do
        if payload="$(cinematic_studio_resolve_payload_path "$root" "$doc")"; then
            cp "$payload" "$PROJECT_DIR/"
        fi
    done
}

cinematic_studio_missing_manifest_skills() {
    local -n _missing_out="$1"
    local tier="${2:-all}"
    local -a required=()
    local skill=""

    _missing_out=()
    cinematic_studio_read_manifest "$CINEMATIC_MANIFEST" "$tier" required

    for skill in "${required[@]}"; do
        if [[ ! -d "$SKILLS_DIR/$skill" || ! -f "$SKILLS_DIR/$skill/SKILL.md" ]]; then
            _missing_out+=("$skill")
        fi
    done
}

cinematic_studio_copy_skill() {
    local skill_src="$1"
    local skill="$2"

    [[ -d "$skill_src" && -f "$skill_src/SKILL.md" ]] || return 1
    rm -rf "$SKILLS_DIR/$skill"
    cp -r "$skill_src" "$SKILLS_DIR/"
    return 0
}

cinematic_studio_reconcile_from_archive() {
    local archive_root="$1"
    local needs_tools="$2"
    shift 2
    local skill=""
    local skill_src=""

    for skill in "$@"; do
        [[ -z "$skill" ]] && continue
        skill_src="$archive_root/.grok/skills/$skill"
        if cinematic_studio_copy_skill "$skill_src" "$skill"; then
            echo "   ✓ $skill (GitHub main)"
        fi
    done

    if [[ "$needs_tools" == true ]]; then
        if [[ -d "$archive_root/tools" ]]; then
            cinematic_studio_copy_tools_tree "$archive_root/tools"
            echo "   ✓ tools/ (GitHub main)"
        fi
        if [[ -d "$archive_root/config" ]]; then
            mkdir -p "$PROJECT_DIR/config"
            cp -r "$archive_root/config/"* "$PROJECT_DIR/config/"
            echo "   ✓ config/ (GitHub main)"
        fi
        if [[ -f "$archive_root/requirements.txt" ]]; then
            cp "$archive_root/requirements.txt" "$PROJECT_DIR/"
        fi
    fi
}

cinematic_studio_reconcile_gaps() {
    local -a missing=()
    local -a still_missing=()
    local needs_tools=false
    local skill=""
    local skill_src=""
    local synced=0
    local tmp_zip=""
    local tmp_extract=""
    local archive_root=""

    cinematic_studio_missing_manifest_skills missing "all"
    cinematic_studio_tools_complete || needs_tools=true

    [[ ${#missing[@]} -eq 0 && "$needs_tools" != true ]] && return 0

    if [[ ${#missing[@]} -gt 0 ]]; then
        echo "→ Reconciling ${#missing[@]} missing skill(s)..."
    elif [[ "$needs_tools" == true ]]; then
        echo "→ Reconciling Python CLI tools..."
    fi

    for skill in "${missing[@]}"; do
        if [[ -n "${CINEMATIC_REPO_ROOT:-}" ]]; then
            skill_src="$CINEMATIC_REPO_ROOT/.grok/skills/$skill"
            if cinematic_studio_copy_skill "$skill_src" "$skill"; then
                echo "   ✓ $skill (local repo)"
                synced=$((synced + 1))
                continue
            fi
        fi
        still_missing+=("$skill")
    done

    if [[ "$needs_tools" == true && -n "${CINEMATIC_REPO_ROOT:-}" && -d "$CINEMATIC_REPO_ROOT/tools" ]]; then
        cinematic_studio_copy_tools_tree "$CINEMATIC_REPO_ROOT/tools"
        if [[ -d "$CINEMATIC_REPO_ROOT/config" ]]; then
            mkdir -p "$PROJECT_DIR/config"
            cp -r "$CINEMATIC_REPO_ROOT/config/"* "$PROJECT_DIR/config/"
        fi
        [[ -f "$CINEMATIC_REPO_ROOT/requirements.txt" ]] && \
            cp "$CINEMATIC_REPO_ROOT/requirements.txt" "$PROJECT_DIR/"
        cinematic_studio_tools_complete && needs_tools=false
    fi

    [[ ${#still_missing[@]} -eq 0 && "$needs_tools" != true ]] && return 0

    tmp_zip="/tmp/cinematic-github-main-$$.zip"
    tmp_extract="/tmp/cinematic-github-main-extract-$$"

    if ! cinematic_studio_fetch_github_main "$tmp_zip" "$tmp_extract" archive_root; then
        echo "⚠️  Could not download supplementary assets from GitHub."
        rm -rf "$tmp_zip" "$tmp_extract"
        return 0
    fi

    if [[ ${#still_missing[@]} -gt 0 && ! -d "$archive_root/.grok/skills" ]]; then
        echo "⚠️  GitHub archive is missing .grok/skills/."
        rm -rf "$tmp_zip" "$tmp_extract"
        return 0
    fi

    cinematic_studio_reconcile_from_archive "$archive_root" "$needs_tools" "${still_missing[@]}"

    rm -rf "$tmp_zip" "$tmp_extract"

    if [[ $synced -gt 0 ]]; then
        echo "→ Reconciled $synced skill(s) from local repository."
    fi
}

cinematic_studio_apply_release_bundle() {
    local tmp_zip="/tmp/cinematic-studio-v${CINEMATIC_STUDIO_VERSION}-$$.zip"
    local tmp_extract="/tmp/cinematic-extract-$$"
    local staging=""
    local used_extract=false

    staging="$(cinematic_studio_acquire_bundle "$tmp_zip" "$tmp_extract")" || return 1

    if [[ "$staging" == "$tmp_extract" ]]; then
        used_extract=true
    fi

    cinematic_studio_install_tree "$staging" || return 1

    if [[ "$used_extract" == true ]]; then
        rm -rf "$tmp_zip" "$tmp_extract"
    fi

    cinematic_studio_reconcile_gaps
    return 0
}

cinematic_studio_ensure_tools_local() {
    cinematic_studio_tools_complete && return 0
    [[ -n "${CINEMATIC_REPO_ROOT:-}" && -d "$CINEMATIC_REPO_ROOT/tools" ]] || return 1
    cinematic_studio_copy_tools_tree "$CINEMATIC_REPO_ROOT/tools"
    cinematic_studio_tools_complete
}

cinematic_studio_resolve_plugin_root() {
    local plugins_dir="${GROK_PLUGINS_DIR:-$HOME/.grok/installed-plugins}"
    local candidate=""

    if [[ -n "${CINEMATIC_PLUGIN_ROOT:-}" ]]; then
        if [[ -d "$CINEMATIC_PLUGIN_ROOT/.grok/skills" ]]; then
            echo "$CINEMATIC_PLUGIN_ROOT"
            return 0
        fi
        return 1
    fi

    if [[ -f "$plugins_dir/registry.json" ]] && command -v python3 >/dev/null 2>&1; then
        candidate="$(python3 - "$plugins_dir/registry.json" <<'PY'
import json
import sys
from pathlib import Path

reg = Path(sys.argv[1])
data = json.loads(reg.read_text(encoding="utf-8"))
for repo in data.get("repos", {}).values():
    if "grok-imagine-cinematic-studio" in repo.get("plugins", {}):
        print(repo["path"])
        break
PY
)" || true
        if [[ -n "$candidate" && -d "$candidate/.grok/skills" ]]; then
            echo "$candidate"
            return 0
        fi
    fi

    shopt -s nullglob
    for candidate in "$plugins_dir"/grok-imagine-cinematic-studio-*/; do
        if [[ -d "$candidate/.grok/skills" ]]; then
            echo "${candidate%/}"
            shopt -u nullglob
            return 0
        fi
    done
    shopt -u nullglob

    return 1
}

cinematic_studio_verify_models() {
    local tools_root="${1:-}"
    local cli_py=""

    # Prefer explicit tools_root (plugin checkout) so a stale PROJECT_DIR copy
    # cannot shadow the installed dual-stack registry (v3.6.6+).
    if [[ -n "$tools_root" && -f "$tools_root/tools/cinematic_studio_cli.py" ]]; then
        cli_py="$tools_root/tools/cinematic_studio_cli.py"
    elif [[ -n "${CINEMATIC_REPO_ROOT:-}" && -f "$CINEMATIC_REPO_ROOT/tools/cinematic_studio_cli.py" ]]; then
        cli_py="$CINEMATIC_REPO_ROOT/tools/cinematic_studio_cli.py"
    elif [[ -f "$PROJECT_DIR/tools/cinematic_studio_cli.py" ]]; then
        cli_py="$PROJECT_DIR/tools/cinematic_studio_cli.py"
    fi

    if [[ -z "$cli_py" ]] && cinematic_studio_ensure_tools_local; then
        cli_py="$PROJECT_DIR/tools/cinematic_studio_cli.py"
    fi

    echo "Model compatibility (Grok 4.5 Build + Grok 4.3 cinematic + Imagine):"
    if [[ -z "$cli_py" ]]; then
        echo "⚠️  Skipping model check (CLI tools unavailable — re-run install)"
        echo ""
        return 0
    fi

    if ! command -v python3 >/dev/null 2>&1; then
        echo "⚠️  Skipping model check (python3 not found)"
        echo ""
        return 0
    fi

    if python3 "$cli_py" models verify; then
        echo ""
        return 0
    fi
    echo ""
    return 1
}

cinematic_studio_verify() {
    local tier="${1:-core}"
    local -a required=()
    local missing=0
    local skill=""

    cinematic_studio_read_manifest "$CINEMATIC_MANIFEST" "$tier" required

    if [[ ${#required[@]} -eq 0 ]]; then
        echo "❌ No skills found in manifest: $CINEMATIC_MANIFEST"
        return 1
    fi

    echo "🔍 Verifying Grok Imagine Cinematic Studio v${CINEMATIC_STUDIO_VERSION}"
    echo "================================================"
    echo ""
    echo "Skills directory: $SKILLS_DIR"
    echo "Checking ${#required[@]} skill(s) [$tier tier]"
    echo ""

    for skill in "${required[@]}"; do
        if [[ -d "$SKILLS_DIR/$skill" && -f "$SKILLS_DIR/$skill/SKILL.md" ]]; then
            echo "✅ $skill"
        else
            echo "❌ $skill (missing)"
            missing=$((missing + 1))
        fi
    done

    echo ""
    if ! cinematic_studio_verify_models; then
        missing=$((missing + 1))
    fi

    if [[ $missing -eq 0 ]]; then
        echo "✅ All checked skills are installed correctly!"
        echo ""
        echo "Activate with:"
        echo "  Activate Grok Imagine Cinematic Studio v${CINEMATIC_STUDIO_VERSION}"
        return 0
    fi

    echo "⚠️  $missing issue(s) found. Re-run:"
    echo "  bash <(curl -sL $CINEMATIC_RAW_BASE/scripts/cinematic_studio.sh) install"
    return 1
}

cinematic_studio_verify_plugin() {
    local plugin_root=""
    local skills_dir=""
    local -a required=()
    local -a command_paths=()
    local missing=0
    local skill=""
    local cmd_path=""
    local cmd_name=""

    plugin_root="$(cinematic_studio_resolve_plugin_root)" || {
        echo "❌ Grok plugin install not found."
        echo "   Install: grok plugin install FineComputer14451/Grok-Imagine-Cinematic-Studio --trust"
        echo "   Or set CINEMATIC_PLUGIN_ROOT to the plugin checkout path."
        return 1
    }

    skills_dir="$plugin_root/.grok/skills"
    cinematic_studio_read_manifest "$CINEMATIC_MANIFEST" "all" required

    if [[ ${#required[@]} -eq 0 ]]; then
        echo "❌ No skills found in manifest: $CINEMATIC_MANIFEST"
        return 1
    fi

    echo "🔍 Verifying Grok Imagine Cinematic Studio v${CINEMATIC_STUDIO_VERSION} (plugin)"
    echo "================================================"
    echo ""
    echo "Plugin root: $plugin_root"
    echo "Checking ${#required[@]} skill(s) [plugin tier]"
    echo ""

    for skill in "${required[@]}"; do
        if [[ -d "$skills_dir/$skill" && -f "$skills_dir/$skill/SKILL.md" ]]; then
            echo "✅ $skill"
        else
            echo "❌ $skill (missing)"
            missing=$((missing + 1))
        fi
    done

    echo ""
    echo "Slash commands:"

    if [[ -f "$plugin_root/.grok-plugin/plugin.json" ]] && command -v python3 >/dev/null 2>&1; then
        while IFS= read -r cmd_path; do
            [[ -z "$cmd_path" ]] && continue
            command_paths+=("$cmd_path")
        done < <(python3 - "$plugin_root/.grok-plugin/plugin.json" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for cmd in data.get("commands", []):
    print(cmd)
PY
)
    else
        shopt -s nullglob
        for cmd_path in "$plugin_root"/commands/*.md; do
            [[ "$(basename "$cmd_path")" == _* ]] && continue
            command_paths+=("commands/$(basename "$cmd_path")")
        done
        shopt -u nullglob
    fi

    if [[ ${#command_paths[@]} -eq 0 ]]; then
        echo "❌ commands/ (missing)"
        missing=$((missing + 1))
    else
        for cmd_path in "${command_paths[@]}"; do
            cmd_name="${cmd_path##*/}"
            cmd_name="${cmd_name%.md}"
            if [[ -f "$plugin_root/$cmd_path" ]]; then
                echo "✅ /$cmd_name"
            else
                echo "❌ /$cmd_name (missing: $cmd_path)"
                missing=$((missing + 1))
            fi
        done
    fi

    echo ""
    if command -v grok >/dev/null 2>&1; then
        echo "Grok plugin registry:"
        if grok plugin details grok-imagine-cinematic-studio 2>/dev/null; then
            echo ""
        else
            echo "⚠️  grok plugin details unavailable (on-disk plugin files checked above)"
            echo ""
        fi
    else
        echo "ℹ️  grok CLI not found — skipped registry check (on-disk plugin files checked above)"
        echo ""
    fi

    if ! cinematic_studio_verify_models "$plugin_root"; then
        missing=$((missing + 1))
    fi

    if [[ $missing -eq 0 ]]; then
        echo "✅ Plugin install verified!"
        echo ""
        echo "Refresh Skills in Grok, start a new chat, then:"
        echo "  /cinematic"
        echo "  Activate Grok Imagine Cinematic Studio v${CINEMATIC_STUDIO_VERSION}"
        return 0
    fi

    echo "⚠️  $missing issue(s) found. Re-run:"
    echo "  grok plugin update grok-imagine-cinematic-studio"
    return 1
}

cinematic_studio_print_next_steps() {
    echo ""
    echo "✅ Done!"
    echo ""
    echo "Next steps:"
    echo "1. Refresh the Skills page in Grok"
    echo "2. Start a new chat"
    echo "3. Type: Activate Grok Imagine Cinematic Studio v${CINEMATIC_STUDIO_VERSION}"
    if [[ -f "$PROJECT_DIR/tools/cinematic_studio_cli.py" ]]; then
        echo "4. Optional CLI: pip install -r $PROJECT_DIR/requirements.txt"
        echo "   python $PROJECT_DIR/tools/cinematic_studio_cli.py models verify"
    fi
    if [[ -f "$PROJECT_DIR/config/grok-build.example.toml" ]]; then
        echo "5. Optional Grok Build config: cp $PROJECT_DIR/config/grok-build.example.toml ~/.grok/config.toml"
    fi
    echo ""
    echo "Project folder: $PROJECT_DIR"
    if [[ -f "$PROJECT_DIR/scripts/cinematic_studio.sh" ]]; then
        echo "Verify install: $PROJECT_DIR/scripts/cinematic_studio.sh verify"
    fi
}