#!/bin/bash
#
# Script to build the macOS app and package it into a DMG
# for personal, unsigned distribution (no license/EULA prompts).
#
set -euo pipefail

DIST_DIR="dist"
DMG_NAME="Bulling-macOS-Personal.dmg"
VOLUME_NAME="Bulling (Personal Use)"
STAGING_DIR="${DIST_DIR}/dmg_staging"

echo "================================"
echo "Creating Personal-Use macOS DMG"
echo "================================"
echo ""

# Require macOS because hdiutil is only available there
if [[ "${OSTYPE:-}" != "darwin"* ]]; then
    echo "❌ This script must be run on macOS (hdiutil is required)."
    exit 1
fi

# Ensure the builder script exists
if [ ! -f "build_macos_app.sh" ]; then
    echo "❌ build_macos_app.sh not found"
    exit 1
fi

if [ ! -x "build_macos_app.sh" ]; then
    echo "⚠️  build_macos_app.sh is not executable, making it executable..."
    chmod +x build_macos_app.sh
fi

mkdir -p "${DIST_DIR}"

# Build the app if needed
if [ ! -d "${DIST_DIR}/Bulling.app" ]; then
    echo "🔨 Building macOS application..."
    ./build_macos_app.sh
    echo ""
fi

# Verify build output
if [ ! -d "${DIST_DIR}/Bulling.app" ]; then
    echo "❌ Build failed. Bulling.app not found in dist/"
    exit 1
fi

# Prepare staging folder
echo "📁 Preparing DMG staging area..."
rm -rf "${STAGING_DIR}"
mkdir -p "${STAGING_DIR}"
cp -R "${DIST_DIR}/Bulling.app" "${STAGING_DIR}/"

# Add a note making the distribution intent explicit
cat > "${STAGING_DIR}/PERSONAL_USE_ONLY.txt" <<'NOTE'
Bulling macOS DMG
-----------------

This disk image is unsigned and provided strictly for personal use.
No license agreement is required to open or install the app.

To install:
1) Open the DMG
2) Drag Bulling.app into Applications
3) Control+click the first launch and choose "Open" to bypass the unsigned warning
NOTE

# Create DMG
echo "💿 Creating DMG..."
rm -f "${DIST_DIR}/${DMG_NAME}"
hdiutil create \
    -volname "${VOLUME_NAME}" \
    -srcfolder "${STAGING_DIR}" \
    -ov \
    -format UDZO \
    "${DIST_DIR}/${DMG_NAME}"

echo ""
echo "✅ SUCCESS!"
echo "Distribution file: ${DIST_DIR}/${DMG_NAME}"
echo "(Unsigned, no license prompts — intended for personal use.)"

echo "================================"
