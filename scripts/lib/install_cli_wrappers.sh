#!/usr/bin/env bash
#
# Install the unified cinematic-studio PATH wrapper (kept out of common.sh).
# Expects PROJECT_DIR, CINEMATIC_SCRIPT_DIR, and optionally CINEMATIC_REPO_ROOT.
#

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

# Install/update ~/.grok/bin/cinematic-studio from the static template.
# Soft overwrite: skip when identical; backup when replacing a different file.
# Also installs cinematic-studio-install → same dispatcher (back-compat alias).
cinematic_studio_install_cli_wrappers() {
    local bin_dir="${HOME}/.grok/bin"
    local local_bin="${HOME}/.local/bin"
    local dest="${bin_dir}/cinematic-studio"
    local alias_dest="${bin_dir}/cinematic-studio-install"
    local template=""
    local bak=""

    if ! template="$(cinematic_studio_resolve_wrapper_template)"; then
        echo "⚠️  wrapper template not found (scripts/wrappers/cinematic-studio); skipping CLI wrapper"
        return 0
    fi

    mkdir -p "$bin_dir" "$local_bin"

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
