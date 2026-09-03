#!/usr/bin/env bash
#
# Shared library for Grok Imagine Cinematic Studio meta installer (v3.11.2)
#

CINEMATIC_STUDIO_FALLBACK_VERSION="3.11.2"

CINEMATIC_INSTALLER_SCRIPTS=(
    cinematic_studio.sh
    install_cinematic_studio.sh
    update_cinematic_studio.sh
    verify_cinematic_studio.sh
    grok_doctor.sh
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

cinematic_studio_strip_bytecode() {
    local dest="${1:-}"
    [[ -n "$dest" && -d "$dest" ]] || return 0
    find "$dest" -type d -name '__pycache__' -prune -exec rm -rf {} + 2>/dev/null || true
}

# Recursive copy of a Python package/tree (merges into dest).
cinematic_studio_copy_package_tree() {
    local src="${1:-}"
    local dest="${2:-}"

    [[ -n "$src" && -d "$src" && -n "$dest" ]] || return 1
    mkdir -p "$dest"
    cp -r "$src"/. "$dest/"
    cinematic_studio_strip_bytecode "$dest"
    return 0
}

cinematic_studio_copy_tools_tree() {
    local tools_src="$1"
    local dest="$PROJECT_DIR/tools"

    [[ -d "$tools_src" ]] || return 1
    # Full tree — includes tools/cli/tui/ (shallow *.py globs dropped that package).
    cinematic_studio_copy_package_tree "$tools_src" "$dest"
}

cinematic_studio_copy_studio_core() {
    local src="${1:-}"
    [[ -d "$src" ]] || return 1
    cinematic_studio_copy_package_tree "$src" "$PROJECT_DIR/studio_core"
}

cinematic_studio_tools_complete() {
    # Fail closed if Method A PROJECT_DIR cannot import the Python CLI.
    # Needs Grok Build management modules, Wave A CLI, TUI package, and studio_core.
    [[ -f "$PROJECT_DIR/tools/cinematic_studio_cli.py" \
        && -f "$PROJECT_DIR/tools/models.py" \
        && -f "$PROJECT_DIR/tools/grok_build_cli.py" \
        && -f "$PROJECT_DIR/tools/cli/models_commands.py" \
        && -f "$PROJECT_DIR/tools/cli/grok_cli_commands.py" \
        && -f "$PROJECT_DIR/tools/cli/wave_a_commands.py" \
        && -f "$PROJECT_DIR/tools/cli/tui/__init__.py" \
        && -f "$PROJECT_DIR/studio_core/services/dashboard.py" ]]
}

# Same interpreter as scripts/wrappers/cinematic-studio (_python).
# Override with CINEMATIC_PYTHON for tests / pinned venvs.
cinematic_studio_resolve_python() {
    local project="${1:-${PROJECT_DIR:-}}"
    local repo="${CINEMATIC_REPO_ROOT:-}"

    if [[ -n "${CINEMATIC_PYTHON:-}" ]]; then
        if [[ -x "${CINEMATIC_PYTHON}" ]] || command -v "${CINEMATIC_PYTHON}" >/dev/null 2>&1; then
            printf '%s\n' "${CINEMATIC_PYTHON}"
            return 0
        fi
    fi
    if [[ -n "$project" && -x "$project/.venv/bin/python" ]]; then
        printf '%s\n' "$project/.venv/bin/python"
        return 0
    fi
    if [[ -n "$repo" && -x "$repo/.venv/bin/python" ]]; then
        printf '%s\n' "$repo/.venv/bin/python"
        return 0
    fi
    if command -v python3 >/dev/null 2>&1; then
        command -v python3
        return 0
    fi
    if command -v python >/dev/null 2>&1; then
        command -v python
        return 0
    fi
    return 1
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
    mkdir -p "$PROJECT_DIR/scripts/lib" "$PROJECT_DIR/scripts/wrappers"
    for f in "${CINEMATIC_INSTALLER_SCRIPTS[@]}"; do
        [[ -f "$scripts_src/$f" ]] && cp "$scripts_src/$f" "$PROJECT_DIR/scripts/"
    done
    for f in cinematic_studio_common.sh install_cli_wrappers.sh; do
        [[ -f "$scripts_src/lib/$f" ]] && cp "$scripts_src/lib/$f" "$PROJECT_DIR/scripts/lib/"
    done
    if [[ -d "$scripts_src/wrappers" ]]; then
        cp -r "$scripts_src/wrappers/." "$PROJECT_DIR/scripts/wrappers/"
        chmod +x "$PROJECT_DIR/scripts/wrappers/"* 2>/dev/null || true
    fi
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
    local archive_root=""

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

    echo "→ Release zip unavailable; fetching GitHub main archive..." >&2
    if cinematic_studio_fetch_github_main "$tmp_zip" "$tmp_extract" archive_root \
        && [[ -n "$archive_root" ]] \
        && cinematic_studio_bundle_root "$archive_root" >/dev/null; then
        echo "→ Using GitHub main archive at $archive_root" >&2
        echo "$archive_root"
        return 0
    fi

    echo "❌ Failed to download skills bundle from GitHub releases." >&2
    echo "   Expected asset: $CINEMATIC_ZIP_NAME" >&2
    echo "   Fallback: GitHub main zip also failed (need a local clone)." >&2
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

    if payload="$(cinematic_studio_resolve_payload_path "$root" "studio_core")"; then
        echo "→ Installing studio_core to $PROJECT_DIR/studio_core ..."
        cinematic_studio_copy_studio_core "$payload"
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

    for doc in AGENTS.md MASTER_PROMPT.md; do
        if payload="$(cinematic_studio_resolve_payload_path "$root" "$doc")"; then
            cp "$payload" "$PROJECT_DIR/"
        fi
    done

    # Installer is the source of truth for project VERSION (CLI reads this file).
    if payload="$(cinematic_studio_resolve_payload_path "$root" "VERSION")" && [[ -f "$payload" ]]; then
        local bundle_ver
        bundle_ver="$(tr -d '[:space:]' <"$payload" 2>/dev/null || true)"
        if [[ -n "$bundle_ver" && "$bundle_ver" != "$CINEMATIC_STUDIO_VERSION" ]]; then
            echo "⚠️  Bundle VERSION ($bundle_ver) differs from installer ($CINEMATIC_STUDIO_VERSION); pinning installer version."
        fi
    fi
    printf '%s\n' "$CINEMATIC_STUDIO_VERSION" >"$PROJECT_DIR/VERSION"

    cinematic_studio_install_cli_wrappers
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
        if [[ -d "$archive_root/studio_core" ]]; then
            cinematic_studio_copy_studio_core "$archive_root/studio_core"
            echo "   ✓ studio_core/ (GitHub main)"
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

    if [[ "$needs_tools" == true && -n "${CINEMATIC_REPO_ROOT:-}" ]]; then
        if [[ -d "$CINEMATIC_REPO_ROOT/tools" ]]; then
            cinematic_studio_copy_tools_tree "$CINEMATIC_REPO_ROOT/tools"
        fi
        if [[ -d "$CINEMATIC_REPO_ROOT/studio_core" ]]; then
            cinematic_studio_copy_studio_core "$CINEMATIC_REPO_ROOT/studio_core"
        fi
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

    staging="$(cinematic_studio_acquire_bundle "$tmp_zip" "$tmp_extract")" || return 1

    local rc=0
    cinematic_studio_install_tree "$staging" || rc=$?

    # Never delete a local clone; always drop download scratch (incl. main-zip nested root).
    rm -f "$tmp_zip"
    if [[ -z "${CINEMATIC_REPO_ROOT:-}" || "$staging" != "$CINEMATIC_REPO_ROOT" ]]; then
        rm -rf "$tmp_extract"
    fi

    [[ "$rc" -eq 0 ]] || return 1

    cinematic_studio_reconcile_gaps
    return 0
}

cinematic_studio_ensure_tools_local() {
    cinematic_studio_tools_complete && return 0
    [[ -n "${CINEMATIC_REPO_ROOT:-}" ]] || return 1
    [[ -d "$CINEMATIC_REPO_ROOT/tools" ]] && cinematic_studio_copy_tools_tree "$CINEMATIC_REPO_ROOT/tools"
    [[ -d "$CINEMATIC_REPO_ROOT/studio_core" ]] && cinematic_studio_copy_studio_core "$CINEMATIC_REPO_ROOT/studio_core"
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
    # cannot shadow the installed Grok 4.5 stack registry (v3.6.6+).
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

    echo "Model compatibility (Grok 4.5 cinematic+Build default · optional 4.3 1M · Imagine):"
    if [[ -z "$cli_py" ]]; then
        echo "⚠️  Skipping model check (CLI tools unavailable — re-run install)"
        echo ""
        return 0
    fi

    local py=""
    if ! py="$(cinematic_studio_resolve_python)"; then
        echo "⚠️  Skipping model check (python3 not found)"
        echo ""
        return 0
    fi

    if "$py" "$cli_py" models verify; then
        echo ""
        return 0
    fi
    echo "   python: $py"
    if [[ ! -x "${PROJECT_DIR:-}/.venv/bin/python" ]]; then
        echo "   Hint: create a venv (Kali: uv venv $PROJECT_DIR/.venv && \\"
        echo "     UV_LINK_MODE=copy uv pip install --python $PROJECT_DIR/.venv/bin/python -r $PROJECT_DIR/requirements.txt)"
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
    echo "3. Type: Activate Grok Imagine Cinematic Studio v${CINEMATIC_STUDIO_VERSION:-$CINEMATIC_STUDIO_FALLBACK_VERSION}"
    if [[ -f "$PROJECT_DIR/tools/cinematic_studio_cli.py" ]]; then
        echo "4. CLI: cinematic-studio models verify"
        echo "   Meta: cinematic-studio verify --plugin | install | update | declutter"
        if [[ -f "$PROJECT_DIR/requirements.txt" ]]; then
            if command -v uv >/dev/null 2>&1; then
                echo "   Deps: uv venv $PROJECT_DIR/.venv && \\"
                echo "     UV_LINK_MODE=copy uv pip install --python $PROJECT_DIR/.venv/bin/python -r $PROJECT_DIR/requirements.txt"
            else
                echo "   Deps: python3 -m venv $PROJECT_DIR/.venv && \\"
                echo "     $PROJECT_DIR/.venv/bin/pip install -r $PROJECT_DIR/requirements.txt"
                echo "   Kali without python3-venv: install uv, or apt install python3-venv"
            fi
            echo "   TUI: cinematic-studio ui  (needs textual from requirements.txt)"
            echo "   Web UI (repo checkout): streamlit run web_ui/app.py"
        fi
    fi
    if [[ -f "$PROJECT_DIR/config/grok-build.example.toml" ]]; then
        if [[ -f "$HOME/.grok/config.toml" ]]; then
            echo "5. Config: ~/.grok/config.toml already exists — leave it."
            echo "   Example: $PROJECT_DIR/config/grok-build.example.toml"
        else
            echo "5. Optional Grok Build config: cp $PROJECT_DIR/config/grok-build.example.toml ~/.grok/config.toml"
        fi
    fi
    echo ""
    echo "Project folder: $PROJECT_DIR"
    if [[ -f "$PROJECT_DIR/scripts/cinematic_studio.sh" ]]; then
        echo "Verify install: cinematic-studio verify   # or $PROJECT_DIR/scripts/cinematic_studio.sh verify"
    fi
}

# CLI wrapper installer lives in install_cli_wrappers.sh (keeps this file smaller).
_cs_self="${BASH_SOURCE[0]:-}"
if [[ -z "$_cs_self" && -n "${0:-}" && "$0" != "bash" && "$0" != "-bash" ]]; then
    _cs_self="$0"
fi
_cs_lib_dir=""
if [[ -n "$_cs_self" && -f "$_cs_self" ]]; then
    _cs_lib_dir="$(cd "$(dirname "$_cs_self")" && pwd)"
fi
if [[ -n "$_cs_lib_dir" && -f "$_cs_lib_dir/install_cli_wrappers.sh" ]]; then
    # shellcheck source=install_cli_wrappers.sh
    source "$_cs_lib_dir/install_cli_wrappers.sh"
elif ! declare -F cinematic_studio_install_cli_wrappers >/dev/null 2>&1; then
    cinematic_studio_install_cli_wrappers() {
        echo "⚠️  install_cli_wrappers.sh not found; skipping CLI wrapper install"
        return 0
    }
fi
unset _cs_self _cs_lib_dir
# ---------------------------------------------------------------------------
# Declutter local install (plugin vs ~/.grok/skills dual-install hygiene)
# ---------------------------------------------------------------------------
# Prefer Method B (plugin) for studio skills when the plugin is installed.
# Keep only user-global skills under ~/.grok/skills/; prune old Method A backups.

cinematic_studio_declutter_usage() {
    cat <<'USAGE'
Usage: cinematic_studio.sh declutter [options]

Remove Method A skill copies that duplicate the installed Grok plugin,
prune old ~/.grok/skills-backup-* directories, and when the full suite plugin
is installed drop overlapping skills from satellite pack installs
(full_suite_wins — never removes skills from the full suite).

Options:
  --dry-run           Show what would be removed (default if DEClutter not forced)
  --apply             Actually delete duplicates and old backups
  --keep-backups N    Keep N most recent skills-backup-* dirs (default: 1)
  --keep-skills-copy  Do not remove studio skills from ~/.grok/skills/
  --prune-backups-only  Only prune skills-backup-* (no skill dir changes)
USAGE
}

cinematic_studio_declutter() {
    local dry_run=1
    local apply=0
    local keep_backups=1
    local keep_skills_copy=0
    local prune_backups_only=0
    local plugin_root=""
    local skill=""
    local removed_skills=0
    local removed_backups=0
    local kept_user=0
    local backup=""
    local -a plugin_skills=()
    local -a to_remove=()
    local -a backups=()
    local -a keep_list=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --dry-run) dry_run=1; apply=0; shift ;;
            --apply) apply=1; dry_run=0; shift ;;
            --keep-backups)
                keep_backups="${2:-1}"
                shift 2
                ;;
            --keep-skills-copy) keep_skills_copy=1; shift ;;
            --prune-backups-only) prune_backups_only=1; shift ;;
            -h|--help|help)
                cinematic_studio_declutter_usage
                return 0
                ;;
            *)
                echo "❌ Unknown declutter option: $1"
                cinematic_studio_declutter_usage
                return 1
                ;;
        esac
    done

    echo "🧹 Cinematic Studio declutter v${CINEMATIC_STUDIO_VERSION}"
    echo "=============================================="
    if [[ $dry_run -eq 1 ]]; then
        echo "Mode: DRY-RUN (pass --apply to execute)"
    else
        echo "Mode: APPLY"
    fi
    echo "Skills dir: $SKILLS_DIR"
    echo ""

    plugin_root="$(cinematic_studio_resolve_plugin_root 2>/dev/null || true)"

    if [[ -n "$plugin_root" ]]; then
        echo "→ Plugin install found: $plugin_root"
        while IFS= read -r skill; do
            [[ -n "$skill" ]] && plugin_skills+=("$skill")
        done < <(find "$plugin_root/.grok/skills" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null | sort)
        echo "  Plugin skills: ${#plugin_skills[@]}"
    else
        echo "→ No grok-imagine-cinematic-studio plugin install detected"
        echo "  Skipping skill de-duplication (nothing to replace Method A copies)."
        keep_skills_copy=1
    fi
    echo ""

    if [[ $prune_backups_only -eq 0 && $keep_skills_copy -eq 0 && ${#plugin_skills[@]} -gt 0 ]]; then
        echo "→ Studio skills duplicated under $SKILLS_DIR (remove; plugin owns these):"
        for skill in "${plugin_skills[@]}"; do
            if [[ -d "$SKILLS_DIR/$skill" ]]; then
                to_remove+=("$skill")
                echo "  - $skill"
            fi
        done
        if [[ ${#to_remove[@]} -eq 0 ]]; then
            echo "  (none — already clean)"
        fi
        echo ""
        echo "→ User-global skills kept under $SKILLS_DIR:"
        if [[ -d "$SKILLS_DIR" ]]; then
            while IFS= read -r skill; do
                [[ -z "$skill" ]] && continue
                local is_plugin=0
                for ps in "${plugin_skills[@]}"; do
                    if [[ "$ps" == "$skill" ]]; then
                        is_plugin=1
                        break
                    fi
                done
                if [[ $is_plugin -eq 0 ]]; then
                    echo "  + $skill"
                    kept_user=$((kept_user + 1))
                fi
            done < <(find "$SKILLS_DIR" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null | sort)
        fi
        if [[ $kept_user -eq 0 ]]; then
            echo "  (none found)"
        fi
        echo ""

        if [[ $apply -eq 1 && ${#to_remove[@]} -gt 0 ]]; then
            for skill in "${to_remove[@]}"; do
                rm -rf "$SKILLS_DIR/$skill"
                removed_skills=$((removed_skills + 1))
            done
            echo "✅ Removed $removed_skills duplicate studio skill(s) from $SKILLS_DIR"
        elif [[ ${#to_remove[@]} -gt 0 ]]; then
            echo "Would remove ${#to_remove[@]} skill(s) (re-run with --apply)"
        fi
        echo ""
    fi

    # Prune old Method A update backups
    shopt -s nullglob
    backups=("$HOME"/.grok/skills-backup-*)
    shopt -u nullglob

    if [[ ${#backups[@]} -eq 0 ]]; then
        echo "→ No skills-backup-* directories found"
    else
        # Sort by name (timestamp suffix) descending = newest first
        mapfile -t backups < <(printf '%s\n' "${backups[@]}" | sort -r)
        echo "→ skills-backup directories: ${#backups[@]} (keeping newest $keep_backups)"
        local i=0
        for backup in "${backups[@]}"; do
            i=$((i + 1))
            if [[ $i -le $keep_backups ]]; then
                keep_list+=("$backup")
                echo "  keep: $backup"
            else
                echo "  drop: $backup"
                if [[ $apply -eq 1 ]]; then
                    rm -rf "$backup"
                    removed_backups=$((removed_backups + 1))
                fi
            fi
        done
        if [[ $apply -eq 0 && ${#backups[@]} -gt $keep_backups ]]; then
            echo "Would remove $((${#backups[@]} - keep_backups)) backup dir(s) (re-run with --apply)"
        elif [[ $apply -eq 1 ]]; then
            echo "✅ Removed $removed_backups old backup dir(s)"
        fi
    fi

    echo ""

    # --- full_suite_wins: satellite skill dups lose when full suite is installed ---
    local plugins_root="${GROK_PLUGINS_DIR:-$HOME/.grok/installed-plugins}"
    local full_install=""
    local sat_install=""
    local satellite_skill=""
    local plugin_name=""
    local plugin_json=""
    local install_dir=""
    local sat_name=""
    local sat_dupes=0
    local removed_sat_skills=0
    local -a sat_roots=()
    local -a sat_names=(
        grok-imagine-cinematic-core
        grok-imagine-camera-image
        grok-imagine-sequence-narrative
        grok-imagine-nsfw
        grok-imagine-delivery-post
    )

    echo "→ full_suite_wins (satellite vs full suite under installed-plugins):"
    if [[ ! -d "$plugins_root" ]]; then
        echo "  (no installed-plugins dir: $plugins_root — skip)"
    else
        while IFS= read -r install_dir; do
            [[ -z "$install_dir" ]] && continue
            plugin_json=""
            if [[ -f "$install_dir/plugin.json" ]]; then
                plugin_json="$install_dir/plugin.json"
            elif [[ -f "$install_dir/.grok-plugin/plugin.json" ]]; then
                plugin_json="$install_dir/.grok-plugin/plugin.json"
            else
                continue
            fi

            plugin_name=""
            if command -v python3 >/dev/null 2>&1; then
                plugin_name="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1], encoding="utf-8")).get("name") or "")' "$plugin_json" 2>/dev/null || true)"
            elif command -v jq >/dev/null 2>&1; then
                plugin_name="$(jq -r '.name // empty' "$plugin_json" 2>/dev/null || true)"
            else
                plugin_name="$(sed -n 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$plugin_json" 2>/dev/null | head -n1 || true)"
            fi
            plugin_name="${plugin_name//$'\r'/}"
            plugin_name="${plugin_name//$'\n'/}"
            [[ -z "${plugin_name:-}" ]] && continue

            if [[ "$plugin_name" == "grok-imagine-cinematic-studio" ]]; then
                if [[ -d "$install_dir/.grok/skills" ]]; then
                    full_install="$install_dir"
                fi
                continue
            fi

            for sat_name in "${sat_names[@]}"; do
                if [[ "$plugin_name" == "$sat_name" ]]; then
                    if [[ -d "$install_dir/.grok/skills" ]]; then
                        sat_roots+=("$install_dir")
                    fi
                    break
                fi
            done
        done < <(find "$plugins_root" -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort)

        if [[ -z "$full_install" && ${#sat_roots[@]} -gt 0 ]]; then
            echo "  satellites only (${#sat_roots[@]}) — skip full_suite_wins (full suite not installed)"
        elif [[ -n "$full_install" && ${#sat_roots[@]} -eq 0 ]]; then
            echo "  full suite present; no satellite installs — nothing to do"
        elif [[ -z "$full_install" ]]; then
            echo "  (no full suite or satellite installs detected)"
        else
            echo "  full: $full_install"
            echo "  satellites: ${#sat_roots[@]}"
            for sat_install in "${sat_roots[@]}"; do
                echo "  satellite: $sat_install"
                while IFS= read -r satellite_skill; do
                    [[ -z "$satellite_skill" ]] && continue
                    if [[ -d "$full_install/.grok/skills/$satellite_skill" ]]; then
                        echo "  - drop satellite skill: $satellite_skill ($sat_install)"
                        sat_dupes=$((sat_dupes + 1))
                        if [[ $apply -eq 1 ]]; then
                            rm -rf "$sat_install/.grok/skills/$satellite_skill"
                            removed_sat_skills=$((removed_sat_skills + 1))
                        fi
                    fi
                done < <(find "$sat_install/.grok/skills" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null | sort)
            done
            if [[ $sat_dupes -eq 0 ]]; then
                echo "  (no overlapping satellite skills)"
            elif [[ $apply -eq 1 ]]; then
                echo "✅ Removed $removed_sat_skills satellite skill duplicate(s) (full suite wins)"
            else
                echo "Would remove $sat_dupes satellite skill(s) (re-run with --apply)"
            fi
        fi
    fi

    echo ""
    echo "Summary"
    echo "-------"
    if [[ $apply -eq 1 ]]; then
        echo "  Skills removed:  $removed_skills"
        echo "  Satellite skill dups removed: $removed_sat_skills"
        echo "  Backups removed: $removed_backups"
        echo "  User skills kept: $kept_user"
        echo ""
        echo "Preferred layout after declutter:"
        echo "  • Studio skills  → plugin (~/.grok/installed-plugins/...)"
        echo "  • User globals   → ~/.grok/skills/ (help, create-skill, docx, …)"
        echo "  • Verify         → bash scripts/cinematic_studio.sh verify --plugin"
    else
        echo "  Dry-run complete. Apply with:"
        echo "    bash scripts/cinematic_studio.sh declutter --apply"
    fi
    echo ""
}
