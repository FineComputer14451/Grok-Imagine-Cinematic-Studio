#!/usr/bin/env bash
#
# Shared library for Grok Imagine Cinematic Studio installer (v3.6.4)
#

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
    if [[ -n "$root" && -f "$root/VERSION" ]]; then
        tr -d '[:space:]' < "$root/VERSION"
        return 0
    fi
    echo "3.6.4"
}

cinematic_studio_init_paths() {
    local script_dir="$1"
    CINEMATIC_SCRIPT_DIR="$script_dir"
    CINEMATIC_REPO_ROOT="$(cinematic_studio_resolve_root "$script_dir")"
    CINEMATIC_STUDIO_VERSION="$(cinematic_studio_load_version "$CINEMATIC_REPO_ROOT")"
    SKILLS_DIR="${SKILLS_DIR:-$HOME/.grok/skills}"
    PROJECT_DIR="${PROJECT_DIR:-$HOME/Grok-Cinematic-Projects}"
    CINEMATIC_RAW_BASE="${CINEMATIC_RAW_BASE:-https://raw.githubusercontent.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/main}"
    CINEMATIC_RELEASE_BASE="${CINEMATIC_RELEASE_BASE:-https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/latest/download}"
    CINEMATIC_ZIP_NAME="grok-imagine-cinematic-studio-skills-install-v${CINEMATIC_STUDIO_VERSION}.zip"
    CINEMATIC_ZIP_URL="${CINEMATIC_ZIP_URL:-$CINEMATIC_RELEASE_BASE/$CINEMATIC_ZIP_NAME}"
    CINEMATIC_MANIFEST="${CINEMATIC_MANIFEST:-$script_dir/required_skills.manifest}"
}

cinematic_studio_bundle_urls() {
    local version="$1"
    local zip_name="grok-imagine-cinematic-studio-skills-install-v${version}.zip"
    cat <<EOF
${CINEMATIC_RELEASE_BASE}/${zip_name}
https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/download/${version}/${zip_name}
https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/releases/download/3.6/${zip_name}
EOF
}

cinematic_studio_ensure_manifest() {
    if [[ -f "$CINEMATIC_MANIFEST" ]]; then
        return 0
    fi
    mkdir -p "$(dirname "$CINEMATIC_MANIFEST")"
    curl -fsSL "$CINEMATIC_RAW_BASE/scripts/required_skills.manifest" -o "$CINEMATIC_MANIFEST"
}

cinematic_studio_read_manifest() {
    local manifest="$1"
    local tier="${2:-all}"
    local -n _skills_out="$3"
    local line=""
    local is_core=false

    _skills_out=()
    cinematic_studio_ensure_manifest

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

cinematic_studio_download_bundle() {
    local tmp_zip="$1"
    local url=""
    local tried=0

    if [[ -n "${CINEMATIC_ZIP_URL:-}" ]]; then
        echo "→ Downloading release bundle ($CINEMATIC_ZIP_NAME)..."
        if curl -fsSL "$CINEMATIC_ZIP_URL" -o "$tmp_zip" && [[ -s "$tmp_zip" ]]; then
            return 0
        fi
        tried=1
    fi

    echo "→ Downloading release bundle ($CINEMATIC_ZIP_NAME)..."
    while IFS= read -r url; do
        [[ -z "$url" ]] && continue
        tried=1
        echo "   trying $url"
        if curl -fsSL "$url" -o "$tmp_zip" && [[ -s "$tmp_zip" ]]; then
            return 0
        fi
        rm -f "$tmp_zip"
    done < <(cinematic_studio_bundle_urls "$CINEMATIC_STUDIO_VERSION")

    if [[ -n "$CINEMATIC_REPO_ROOT" && -d "$CINEMATIC_REPO_ROOT/.grok/skills" ]]; then
        echo "→ Using local repository bundle at $CINEMATIC_REPO_ROOT"
        cinematic_studio_install_from_repo "$CINEMATIC_REPO_ROOT"
        return 2
    fi

    if [[ $tried -eq 0 ]]; then
        echo "❌ No download URLs configured."
    else
        echo "❌ Failed to download skills bundle from GitHub releases."
        echo "   Expected asset: $CINEMATIC_ZIP_NAME"
    fi
    return 1
}

cinematic_studio_install_from_repo() {
    local repo_root="$1"
    local skills_src="$repo_root/.grok/skills"
    local refs_src="$repo_root/references"

    echo "→ Creating directories..."
    mkdir -p "$SKILLS_DIR"
    mkdir -p "$PROJECT_DIR/references"

    echo "→ Installing skills from $skills_src ..."
    cp -r "$skills_src/"* "$SKILLS_DIR/"

    if [[ -d "$refs_src" ]]; then
        echo "→ Installing references from $repo_root ..."
        cp -r "$refs_src/"* "$PROJECT_DIR/references/"
    fi

    for doc in AGENTS.md MASTER_PROMPT_v3.6.md; do
        if [[ -f "$repo_root/$doc" ]]; then
            cp "$repo_root/$doc" "$PROJECT_DIR/"
        fi
    done
}

cinematic_studio_extract_bundle() {
    local tmp_zip="$1"
    local tmp_extract="$2"
    echo "→ Extracting bundle..."
    rm -rf "$tmp_extract"
    mkdir -p "$tmp_extract"
    unzip -q "$tmp_zip" -d "$tmp_extract"
}

cinematic_studio_install_from_extract() {
    local tmp_extract="$1"
    local skills_src="$tmp_extract/.grok/skills"
    local refs_src="$tmp_extract/references"

    if [[ ! -d "$skills_src" ]]; then
        echo "❌ Bundle is missing .grok/skills/"
        return 1
    fi

    echo "→ Creating directories..."
    mkdir -p "$SKILLS_DIR"
    mkdir -p "$PROJECT_DIR/references"

    echo "→ Installing skills to $SKILLS_DIR ..."
    cp -r "$skills_src/"* "$SKILLS_DIR/"

    if [[ -d "$refs_src" ]]; then
        echo "→ Installing references to $PROJECT_DIR ..."
        cp -r "$refs_src/"* "$PROJECT_DIR/references/"
    fi

    for doc in AGENTS.md MASTER_PROMPT_v3.6.md; do
        if [[ -f "$tmp_extract/$doc" ]]; then
            cp "$tmp_extract/$doc" "$PROJECT_DIR/"
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

cinematic_studio_sync_repo_extras() {
    local -a missing=()
    local skill=""
    local synced=0

    [[ -n "$CINEMATIC_REPO_ROOT" && -d "$CINEMATIC_REPO_ROOT/.grok/skills" ]] || return 0

    cinematic_studio_missing_manifest_skills missing "all"
    [[ ${#missing[@]} -eq 0 ]] && return 0

    for skill in "${missing[@]}"; do
        if [[ -d "$CINEMATIC_REPO_ROOT/.grok/skills/$skill" ]]; then
            echo "→ Syncing repo-only skill: $skill"
            cp -r "$CINEMATIC_REPO_ROOT/.grok/skills/$skill" "$SKILLS_DIR/"
            synced=$((synced + 1))
        fi
    done

    if [[ $synced -gt 0 ]]; then
        echo "→ Synced $synced skill(s) from local repository."
    fi
}

cinematic_studio_sync_missing_skills() {
    local -a missing=()
    local skill=""
    local tmp_zip=""
    local tmp_extract=""
    local repo_extract=""
    local synced=0

    cinematic_studio_sync_repo_extras

    cinematic_studio_missing_manifest_skills missing "all"
    [[ ${#missing[@]} -eq 0 ]] && return 0

    echo "→ Syncing ${#missing[@]} missing skill(s) from GitHub main branch..."
    tmp_zip="/tmp/cinematic-repo-main-$$.zip"
    tmp_extract="/tmp/cinematic-repo-extract-$$"
    repo_extract="$tmp_extract/Grok-Imagine-Cinematic-Studio-main"

    if ! curl -fsSL "https://github.com/FineComputer14451/Grok-Imagine-Cinematic-Studio/archive/refs/heads/main.zip" -o "$tmp_zip"; then
        echo "⚠️  Could not download supplementary skills from GitHub."
        return 0
    fi

    rm -rf "$tmp_extract"
    mkdir -p "$tmp_extract"
    unzip -q "$tmp_zip" -d "$tmp_extract"

    if [[ ! -d "$repo_extract/.grok/skills" ]]; then
        echo "⚠️  GitHub archive is missing .grok/skills/."
        rm -rf "$tmp_zip" "$tmp_extract"
        return 0
    fi

    for skill in "${missing[@]}"; do
        if [[ -d "$repo_extract/.grok/skills/$skill" ]]; then
            echo "→ Installing $skill from GitHub main branch"
            cp -r "$repo_extract/.grok/skills/$skill" "$SKILLS_DIR/"
            synced=$((synced + 1))
        fi
    done

    rm -rf "$tmp_zip" "$tmp_extract"

    if [[ $synced -gt 0 ]]; then
        echo "→ Synced $synced skill(s) from GitHub main branch."
    fi
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
    if [[ $missing -eq 0 ]]; then
        echo "✅ All checked skills are installed correctly!"
        echo ""
        echo "Activate with:"
        echo "  Activate Grok Imagine Cinematic Studio v${CINEMATIC_STUDIO_VERSION}"
        return 0
    fi

    echo "⚠️  $missing skill(s) missing. Re-run:"
    echo "  bash <(curl -sL $CINEMATIC_RAW_BASE/scripts/cinematic_studio.sh) install"
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
    echo ""
    echo "Project folder: $PROJECT_DIR"
}