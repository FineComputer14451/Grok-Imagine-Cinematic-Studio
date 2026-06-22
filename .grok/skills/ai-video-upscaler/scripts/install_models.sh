#!/usr/bin/env bash
# Install Real-ESRGAN and GFPGAN model weights for ai-video-upscaler
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="${SCRIPT_DIR}/../models"
mkdir -p "${MODELS_DIR}"

download() {
    local url="$1"
    local dest="$2"
    if [[ -f "${dest}" ]]; then
        echo "  ✓ Already exists: $(basename "${dest}")"
        return 0
    fi
    echo "  ↓ Downloading $(basename "${dest}")..."
    curl -fL --progress-bar -o "${dest}" "${url}"
    echo "  ✓ Saved: ${dest}"
}

echo "Installing ai-video-upscaler models to ${MODELS_DIR}"
echo ""

echo "Real-ESRGAN models:"
download \
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth" \
    "${MODELS_DIR}/realesrgan-x4plus.pth"

download \
    "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.2.4/RealESRGAN_x4plus_anime_6B.pth" \
    "${MODELS_DIR}/realesrgan-x4plus-anime.pth"

echo ""
echo "GFPGAN face restoration model:"
download \
    "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth" \
    "${MODELS_DIR}/GFPGANv1.4.pth"

echo ""
echo "All models installed."
echo ""
echo "Optional Python dependencies for GPU path:"
echo "  pip install realesrgan basicsr gfpgan opencv-python-headless torch"
echo ""
echo "Pure-Python fallback requires only:"
echo "  pip install pillow"
echo "  apt-get install ffmpeg"