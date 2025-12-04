#!/bin/bash

# =============================================================================
# Bulling Desktop Standalone App Builder (Cross-Platform)
# =============================================================================
# Creates standalone executables for Windows, Linux, and macOS
# Uses PyInstaller for cross-platform builds
#
# Usage:
#   ./build_desktop_standalone.sh [--yes|-y] [--no-clean]
#
#   --yes, -y      Automatically clean previous builds without prompting
#   --no-clean     Skip cleaning previous builds
#
# Prerequisites:
#   - Python 3.9+
#   - PyInstaller: pip install pyinstaller
#   - PySide6: pip install PySide6
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║${NC}     ${CYAN}Bulling Desktop Standalone App Builder${NC}              ${BLUE}║${NC}"
echo -e "${BLUE}║${NC}     ${YELLOW}Cross-Platform - Windows, Linux, macOS${NC}             ${BLUE}║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${YELLOW}Platform: $(uname -s)${NC}"
echo -e "${YELLOW}Python: $(python3 --version)${NC}"
echo ""

# Check if required packages are installed
echo -e "${CYAN}Checking dependencies...${NC}"

if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo -e "${YELLOW}PyInstaller not found. Installing...${NC}"
    pip3 install pyinstaller
fi

if ! python3 -c "import PySide6" 2>/dev/null; then
    echo -e "${YELLOW}PySide6 not found. Installing...${NC}"
    pip3 install PySide6
fi

echo -e "${GREEN}✓ All dependencies installed${NC}"
echo ""

# Run the Python build script with all arguments passed through
python3 build_desktop_standalone.py "$@"

echo ""
echo -e "${GREEN}Done!${NC}"
echo ""
