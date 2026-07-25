#!/usr/bin/env bash
#
# Install the unified cinematic-studio PATH wrapper + ensure Grok Build CLI binary.
# Expects PROJECT_DIR, CINEMATIC_SCRIPT_DIR, and optionally CINEMATIC_REPO_ROOT.
# Requires bash (not zsh/sh) — version compare uses BASH_REMATCH.
#
# Env:
#   CINEMATIC_SKIP_GROK_CLI=1       — skip Grok Build binary ensure/install
#   CINEMATIC_FORCE_GROK_CLI=1      — reinstall/refresh even if min version is met
#   CINEMATIC_MIN_GROK_CLI=0.2.93   — minimum Grok Build binary version
#   CINEMATIC_GROK_INSTALL_URL=…    — override official install script URL
#

if [[ -z "${BASH_VERSION:-}" ]]; then
    echo "install_cli_wrappers.sh requires bash (got non-bash shell)" >&2
    return 1 2>/dev/null || exit 1
fi


# Official xAI Grok Build CLI installer (stable channel by default).
CINEMATIC_GROK_INSTALL_URL_DEFAULT="https://x.ai/cli/install.sh"
# Keep in sync with tools/models.py → RECOMMENDED_GROK_BUILD_CLI_VERSION
CINEMATIC_MIN_GROK_CLI_DEFAULT="0.2.93"

cinematic_studio_resolve_wrapper_template() {
    local candidate=""
    for candidate in \
        "${CINEMATIC_SCRIPT_DIR:-}/wrappers/cinematic-studio" \
        "${CINEMATIC_REPO_ROOT:-}/scripts/wrappers/cinematic-studio" \
        "${PROJECT_DIR:-}/scripts/wrappers/cinematic-studio"; do
        if [[ -n "$candidate" && -f "$candidate" ]]; then
            printf '%s\n' "$candidate"
            return 0
        fi
    done
    return 1
}

# Return 0 if version $1 >= version $2 (dot-separated numeric, e.g. 0.2.112).
cinematic_studio_version_ge() {
    local installed="${1:-}"
    local minimum="${2:-}"
    [[ -n "$installed" && -n "$minimum" ]] || return 1
    # strip any pre-release / build suffix after first non X.Y.Z token
    installed="${installed%%[!0-9.]*}"
    minimum="${minimum%%[!0-9.]*}"
    [[ "$installed" =~ ^[0-9]+(\.[0-9]+)*$ ]] || return 1
    [[ "$minimum" =~ ^[0-9]+(\.[0-9]+)*$ ]] || return 1
    # sort -V: if the lower of (min, installed) is min, then installed >= min
    [[ "$(printf '%s\n%s\n' "$minimum" "$installed" | sort -V | head -n1)" == "$minimum" ]]
}

# Parse "0.2.112" from `grok --version` style output.
cinematic_studio_parse_grok_version() {
    local blob="${1:-}"
    if [[ "$blob" =~ ([0-9]+\.[0-9]+\.[0-9]+([.-][A-Za-z0-9._]+)?) ]]; then
        # Prefer pure X.Y.Z for comparisons
        if [[ "${BASH_REMATCH[1]}" =~ ^([0-9]+\.[0-9]+\.[0-9]+) ]]; then
            printf '%s\n' "${BASH_REMATCH[1]}"
            return 0
        fi
    fi
    return 1
}

# Locate a grok binary (PATH, then common install dirs). Prints absolute path or empty.
cinematic_studio_find_grok_binary() {
    local candidate=""
    # Prefer user-local official installs over distro/npm shims when multiple exist
    for candidate in \
        "${HOME}/.grok/bin/grok" \
        "${HOME}/.local/bin/grok"; do
        if [[ -x "$candidate" ]]; then
            # Resolve symlink to real path when possible
            if command -v readlink >/dev/null 2>&1; then
                printf '%s\n' "$(readlink -f "$candidate" 2>/dev/null || echo "$candidate")"
            else
                printf '%s\n' "$candidate"
            fi
            return 0
        fi
    done
    if command -v grok >/dev/null 2>&1; then
        command -v grok
        return 0
    fi
    return 1
}

cinematic_studio_grok_version_at() {
    local bin="${1:-}"
    local out=""
    [[ -n "$bin" && -x "$bin" ]] || return 1
    out="$("$bin" --version 2>&1 || true)"
    cinematic_studio_parse_grok_version "$out"
}

# Ensure ~/.grok/bin and ~/.local/bin are early on PATH for this process.
cinematic_studio_prepend_grok_path() {
    local bin_dir="${HOME}/.grok/bin"
    local local_bin="${HOME}/.local/bin"
    mkdir -p "$bin_dir" "$local_bin"
    case ":${PATH}:" in
        *":${bin_dir}:"*) ;;
        *) export PATH="${bin_dir}:${PATH}" ;;
    esac
    case ":${PATH}:" in
        *":${local_bin}:"*) ;;
        *) export PATH="${local_bin}:${PATH}" ;;
    esac
}

# Symlink ~/.local/bin/grok → ~/.grok/bin/grok when the official binary is present.
cinematic_studio_link_grok_binary() {
    local bin_dir="${HOME}/.grok/bin"
    local local_bin="${HOME}/.local/bin"
    local src=""
    mkdir -p "$bin_dir" "$local_bin"

    if [[ -x "${bin_dir}/grok" ]]; then
        src="${bin_dir}/grok"
    else
        # Prefer highest versioned binary if bare `grok` missing (grok-0.2.112, …)
        src="$(ls -1 "${bin_dir}"/grok-[0-9]* 2>/dev/null | sort -V | tail -n1 || true)"
        if [[ -n "$src" && -x "$src" ]]; then
            ln -sfn "$(basename "$src")" "${bin_dir}/grok"
            src="${bin_dir}/grok"
        fi
    fi

    if [[ -n "$src" && -e "$src" ]]; then
        ln -sfn "$src" "${local_bin}/grok"
        return 0
    fi
    return 1
}

# Run official installer (curl | bash) or `grok update` when a binary already exists.
# Soft-fail: prints warnings, returns 0 so studio skill install can continue.
cinematic_studio_install_grok_build_cli() {
    local min_ver="${CINEMATIC_MIN_GROK_CLI:-$CINEMATIC_MIN_GROK_CLI_DEFAULT}"
    local url="${CINEMATIC_GROK_INSTALL_URL:-$CINEMATIC_GROK_INSTALL_URL_DEFAULT}"
    local force="${CINEMATIC_FORCE_GROK_CLI:-0}"
    local existing=""
    local ver=""
    local need_install=0

    cinematic_studio_prepend_grok_path

    existing="$(cinematic_studio_find_grok_binary 2>/dev/null || true)"
    if [[ -n "$existing" ]]; then
        ver="$(cinematic_studio_grok_version_at "$existing" 2>/dev/null || true)"
        if [[ "$force" == "1" || "$force" == "true" || "$force" == "yes" ]]; then
            need_install=1
            echo "→ Grok Build CLI force refresh (CINEMATIC_FORCE_GROK_CLI=1) · found ${ver:-unknown} at $existing"
        elif [[ -n "$ver" ]] && cinematic_studio_version_ge "$ver" "$min_ver"; then
            echo "→ Grok Build CLI OK: $ver ≥ $min_ver ($existing)"
            cinematic_studio_link_grok_binary || true
            return 0
        else
            need_install=1
            echo "→ Grok Build CLI needs upgrade: ${ver:-unparsed} < $min_ver ($existing)"
        fi
    else
        need_install=1
        echo "→ Grok Build CLI not found — installing via $url"
    fi

    if [[ "$need_install" -ne 1 ]]; then
        return 0
    fi

    # Prefer in-place update when a working grok binary already exists
    if [[ -n "$existing" && -x "$existing" ]]; then
        echo "→ Running: $existing update --stable"
        if "$existing" update --stable 2>&1; then
            cinematic_studio_prepend_grok_path
            cinematic_studio_link_grok_binary || true
            existing="$(cinematic_studio_find_grok_binary 2>/dev/null || true)"
            ver="$(cinematic_studio_grok_version_at "$existing" 2>/dev/null || true)"
            if [[ -n "$ver" ]] && cinematic_studio_version_ge "$ver" "$min_ver"; then
                echo "→ Grok Build CLI updated: $ver ($existing)"
                return 0
            fi
            echo "⚠️  grok update finished but version still ${ver:-unknown}; trying official installer"
        else
            echo "⚠️  grok update failed; trying official installer"
        fi
    fi

    if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
        echo "⚠️  Cannot install Grok Build CLI: need curl or wget"
        echo "   Manual: curl -fsSL $url | bash"
        return 0
    fi

    echo "→ Running official Grok Build installer (stable)"
    if command -v curl >/dev/null 2>&1; then
        if ! curl -fsSL "$url" | bash; then
            echo "⚠️  Official Grok Build install failed"
            echo "   Manual: curl -fsSL $url | bash"
            echo "   Then re-run: bash scripts/cinematic_studio.sh install"
            return 0
        fi
    else
        if ! wget -qO- "$url" | bash; then
            echo "⚠️  Official Grok Build install failed"
            echo "   Manual: wget -qO- $url | bash"
            return 0
        fi
    fi

    cinematic_studio_prepend_grok_path
    cinematic_studio_link_grok_binary || true
    existing="$(cinematic_studio_find_grok_binary 2>/dev/null || true)"
    ver="$(cinematic_studio_grok_version_at "$existing" 2>/dev/null || true)"
    if [[ -n "$existing" && -n "$ver" ]]; then
        echo "→ Grok Build CLI installed: $ver ($existing)"
        if ! cinematic_studio_version_ge "$ver" "$min_ver"; then
            echo "⚠️  Installed $ver is still below recommended $min_ver"
        fi
    else
        echo "⚠️  Installer finished but grok not found on PATH"
        echo "   Add ${HOME}/.grok/bin and ${HOME}/.local/bin to PATH, then: grok --version"
    fi
    return 0
}

# Public entry: ensure Grok Build ≥ min (unless skipped).
cinematic_studio_ensure_grok_build_cli() {
    local skip="${CINEMATIC_SKIP_GROK_CLI:-0}"
    if [[ "$skip" == "1" || "$skip" == "true" || "$skip" == "yes" ]]; then
        echo "→ Skipping Grok Build CLI ensure (CINEMATIC_SKIP_GROK_CLI=$skip)"
        return 0
    fi
    cinematic_studio_install_grok_build_cli
}

# Install/update ~/.grok/bin/cinematic-studio from the static template.
# Soft overwrite: skip when identical; backup when replacing a different file.
# Also installs cinematic-studio-install → same dispatcher (back-compat alias).
# Ensures Grok Build CLI binary is present (≥ CINEMATIC_MIN_GROK_CLI) unless skipped.
cinematic_studio_install_cli_wrappers() {
    local bin_dir="${HOME}/.grok/bin"
    local local_bin="${HOME}/.local/bin"
    local dest="${bin_dir}/cinematic-studio"
    local alias_dest="${bin_dir}/cinematic-studio-install"
    local template=""
    local bak=""

    # Grok Build binary first so PATH + doctor see a real `grok` on fresh machines
    cinematic_studio_ensure_grok_build_cli

    if ! template="$(cinematic_studio_resolve_wrapper_template)"; then
        echo "⚠️  wrapper template not found (scripts/wrappers/cinematic-studio); skipping CLI wrapper"
        return 0
    fi

    mkdir -p "$bin_dir" "$local_bin"
    cinematic_studio_prepend_grok_path

    if [[ -f "$dest" ]] && cmp -s "$template" "$dest"; then
        echo "→ CLI wrapper up to date: $dest"
    else
        if [[ -f "$dest" ]]; then
            bak="${dest}.bak.$(date +%Y%m%d%H%M%S)"
            cp "$dest" "$bak"
            echo "→ Updating CLI wrapper (backup: $bak)"
        else
            echo "→ Installing CLI wrapper: $dest"
        fi
        install -m 755 "$template" "$dest"
    fi

    # Back-compat alias: same unified dispatcher
    ln -sfn "$dest" "$alias_dest"
    ln -sfn "$dest" "${local_bin}/cinematic-studio"
    ln -sfn "$dest" "${local_bin}/cinematic-studio-install"

    # Also keep a copy under PROJECT_DIR for reference / offline reinstall
    if [[ -n "${PROJECT_DIR:-}" ]]; then
        mkdir -p "${PROJECT_DIR}/scripts/wrappers"
        if [[ ! -f "${PROJECT_DIR}/scripts/wrappers/cinematic-studio" ]] || \
           ! cmp -s "$template" "${PROJECT_DIR}/scripts/wrappers/cinematic-studio"; then
            install -m 755 "$template" "${PROJECT_DIR}/scripts/wrappers/cinematic-studio"
        fi
    fi


    # Grok Doctor (health check)
    local doctor_src=""
    for doctor_src in \
        "${CINEMATIC_SCRIPT_DIR:-}/grok_doctor.sh" \
        "${CINEMATIC_REPO_ROOT:-}/scripts/grok_doctor.sh" \
        "${PROJECT_DIR:-}/scripts/grok_doctor.sh"; do
        if [[ -n "$doctor_src" && -f "$doctor_src" ]]; then
            install -m 755 "$doctor_src" "${bin_dir}/grok-doctor"
            ln -sfn "${bin_dir}/grok-doctor" "${local_bin}/grok-doctor"
            # Also allow: cinematic-studio doctor (via meta dispatcher)
            echo "→ Grok Doctor: ${bin_dir}/grok-doctor"
            break
        fi
    done

    if ! command -v cinematic-studio >/dev/null 2>&1; then
        echo "   Note: add ${bin_dir} or ${local_bin} to PATH"
        echo "   Absolute: ${dest} models verify"
    fi
}
