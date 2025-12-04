#!/usr/bin/env python3
"""
Build script for creating standalone desktop executables for Bulling
Supports: Windows, Linux, macOS
Uses PyInstaller for cross-platform builds

Usage:
    python3 build_desktop_standalone.py [OPTIONS]

Options:
    --help, -h          Show this help message and exit
    --clean             Clean previous builds before building
    --no-clean          Don't clean previous builds (default)
    --verbose, -v       Show verbose output
    --version VERSION   Set version number for distribution package
    
Examples:
    python3 build_desktop_standalone.py
    python3 build_desktop_standalone.py --clean
    python3 build_desktop_standalone.py --clean --verbose
"""

import sys
import os
import shutil
import subprocess
import platform
import argparse
from pathlib import Path

# Project paths
PROJECT_DIR = Path(__file__).parent
DIST_DIR = PROJECT_DIR / "dist"
BUILD_DIR = PROJECT_DIR / "build"
ICON_FILE = PROJECT_DIR / "bulling_icon.svg"

# Platform-specific settings
SYSTEM = platform.system()
IS_WINDOWS = SYSTEM == "Windows"
IS_LINUX = SYSTEM == "Linux"
IS_MACOS = SYSTEM == "Darwin"

# App name and executable name
APP_NAME = "Bulling"
if IS_WINDOWS:
    EXE_NAME = f"{APP_NAME}.exe"
else:
    EXE_NAME = APP_NAME

# Color codes for terminal output
class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    
    @staticmethod
    def disable():
        """Disable colors (for Windows or when piping output)"""
        Colors.RESET = ''
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.CYAN = ''
        Colors.BOLD = ''

# Disable colors on Windows unless ANSICON is set
if IS_WINDOWS and not os.environ.get('ANSICON'):
    Colors.disable()

# Global verbose flag
VERBOSE = False

def print_header():
    """Print build header"""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  Building Bulling Standalone Desktop App{Colors.RESET}")
    print(f"{Colors.YELLOW}  Platform: {SYSTEM}{Colors.RESET}")
    print(f"{Colors.YELLOW}  Python: {sys.version.split()[0]}{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}\n")

def check_requirements():
    """Check if required tools are installed"""
    print(f"{Colors.YELLOW}Checking requirements...{Colors.RESET}")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print(f"{Colors.RED}Error: Python 3.9 or higher is required{Colors.RESET}")
        sys.exit(1)
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"{Colors.GREEN}✓ PyInstaller {PyInstaller.__version__}{Colors.RESET}")
    except ImportError:
        print(f"{Colors.RED}Error: PyInstaller is not installed{Colors.RESET}")
        print("Install with: pip install pyinstaller")
        sys.exit(1)
    
    # Check PySide6
    try:
        import PySide6
        print(f"{Colors.GREEN}✓ PySide6 installed{Colors.RESET}")
    except ImportError:
        print(f"{Colors.RED}Error: PySide6 is not installed{Colors.RESET}")
        print("Install with: pip install PySide6")
        sys.exit(1)
    
    print("")

def clean_build_dirs():
    """Clean previous build artifacts"""
    print(f"{Colors.YELLOW}Cleaning previous builds...{Colors.RESET}")
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"{Colors.CYAN}  Removed {dir_path}{Colors.RESET}")
    print("")

def build_standalone():
    """Build standalone executable using PyInstaller"""
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.CYAN}Building standalone executable for {SYSTEM}...{Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 60}{Colors.RESET}\n")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name", APP_NAME,
        "--onefile",  # Single executable file
        "--windowed",  # No console window (GUI app)
        "--clean",
        str(PROJECT_DIR / "bulling_qt.py"),
    ]
    
    # Add platform-specific options
    if IS_WINDOWS:
        # Windows-specific options
        cmd.extend([
            "--icon", "NONE",  # Will add icon support later
        ])
    elif IS_MACOS:
        # macOS-specific options
        cmd.extend([
            "--icon", "NONE",  # Will add icon support later
            "--osx-bundle-identifier", "com.bulling.app",
        ])
    
    # Add hidden imports for PySide6
    cmd.extend([
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui",
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "PySide6.QtSvg",
    ])
    
    # Run PyInstaller
    if VERBOSE:
        print(f"{Colors.YELLOW}Running: {' '.join(cmd)}{Colors.RESET}")
        print("")
    
    result = subprocess.run(cmd, cwd=PROJECT_DIR)
    
    if result.returncode != 0:
        print(f"\n{Colors.RED}✗ Build failed!{Colors.RESET}")
        sys.exit(1)
    
    print(f"\n{Colors.GREEN}✓ Build completed successfully!{Colors.RESET}")

def create_distribution_package(version="1.0.0"):
    """Create distribution package"""
    print(f"\n{Colors.CYAN}Creating distribution package...{Colors.RESET}")
    
    # Source executable
    exe_path = DIST_DIR / EXE_NAME
    
    if not exe_path.exists():
        print(f"{Colors.RED}Error: Executable not found at {exe_path}{Colors.RESET}")
        return
    
    # Get file size
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"{Colors.GREEN}  Executable size: {size_mb:.2f} MB{Colors.RESET}")
    
    # Create platform-specific distribution
    if IS_WINDOWS:
        # Create ZIP for Windows
        dist_name = f"{APP_NAME}-Windows-x64"
        zip_path = DIST_DIR / f"{dist_name}.zip"
        
        # Create README
        readme_path = DIST_DIR / "README.txt"
        with open(readme_path, "w") as f:
            f.write(f"""{APP_NAME} - Bowling Scoring Game
Version: {version}
Platform: Windows

FEATURES:
- Traditional 10-pin bowling rules with authentic scoring
- Real-time bowling scorecard with strikes (X) and spares (/)
- Professional scoreboard display
- 10th frame bonus rules
- Multiple player support

INSTALLATION:
1. Extract this ZIP file to a folder of your choice
2. Double-click {EXE_NAME} to run the app

PERSONAL USE ONLY
This software is for personal, non-commercial use only.
See LICENSE.txt for complete terms.

FIRST RUN:
Windows may show a security warning because the app is not signed.
Click "More info" and then "Run anyway" to proceed.

Enjoy bowling!
""")
        
        # Create ZIP
        shutil.make_archive(str(DIST_DIR / dist_name), 'zip', DIST_DIR, 
                           base_dir=None)
        print(f"{Colors.GREEN}  Created: {dist_name}.zip{Colors.RESET}")
        
    elif IS_LINUX:
        # Create tar.gz for Linux
        dist_name = f"{APP_NAME}-Linux-x64"
        tar_path = DIST_DIR / f"{dist_name}.tar.gz"
        
        # Create README
        readme_path = DIST_DIR / "README.txt"
        with open(readme_path, "w") as f:
            f.write(f"""{APP_NAME} - Bowling Scoring Game
Version: {version}
Platform: Linux

FEATURES:
- Traditional 10-pin bowling rules with authentic scoring
- Real-time bowling scorecard with strikes (X) and spares (/)
- Professional scoreboard display
- 10th frame bonus rules
- Multiple player support

INSTALLATION:
1. Extract this archive to a folder of your choice
2. Make the file executable: chmod +x {EXE_NAME}
3. Run the app: ./{EXE_NAME}

PERSONAL USE ONLY
This software is for personal, non-commercial use only.
See LICENSE.txt for complete terms.

DEPENDENCIES:
This is a standalone build that includes all required libraries.
You may need to install system libraries:
- sudo apt-get install libxcb-xinerama0 libxcb-cursor0  (Ubuntu/Debian)

Enjoy bowling!
""")
        
        # Create tar.gz
        shutil.make_archive(str(DIST_DIR / dist_name), 'gztar', DIST_DIR,
                           base_dir=None)
        print(f"{Colors.GREEN}  Created: {dist_name}.tar.gz{Colors.RESET}")
        
    elif IS_MACOS:
        # Create ZIP for macOS
        dist_name = f"{APP_NAME}-macOS-PyInstaller"
        zip_path = DIST_DIR / f"{dist_name}.zip"
        
        # Create README
        readme_path = DIST_DIR / "README.txt"
        with open(readme_path, "w") as f:
            f.write(f"""{APP_NAME} - Bowling Scoring Game
Version: {version}
Platform: macOS (PyInstaller build)

FEATURES:
- Traditional 10-pin bowling rules with authentic scoring
- Real-time bowling scorecard with strikes (X) and spares (/)
- Professional scoreboard display
- 10th frame bonus rules
- Multiple player support

INSTALLATION:
1. Extract this ZIP file to a folder of your choice
2. Double-click {EXE_NAME} to run the app

PERSONAL USE ONLY
This software is for personal, non-commercial use only.
See LICENSE.txt for complete terms.

FIRST RUN:
Since the app is not signed with an Apple Developer certificate:
1. Right-click (or Control-click) on {EXE_NAME}
2. Select "Open" from the context menu
3. Click "Open" in the security dialog
4. The app will now open normally in the future

NOTE: For a native macOS .app bundle, use the build_standalone.sh script instead.

Enjoy bowling!
""")
        
        # Create ZIP
        shutil.make_archive(str(DIST_DIR / dist_name), 'zip', DIST_DIR,
                           base_dir=None)
        print(f"{Colors.GREEN}  Created: {dist_name}.zip{Colors.RESET}")

def print_summary():
    """Print build summary"""
    print(f"\n{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}  Build Complete!{Colors.RESET}")
    print(f"{Colors.BLUE}{'=' * 60}{Colors.RESET}")
    print(f"\n{Colors.CYAN}Distribution files in: {DIST_DIR}{Colors.RESET}")
    print("\nFiles created:")
    
    # List distribution files
    for item in DIST_DIR.iterdir():
        if item.is_file() and item.name.startswith(APP_NAME):
            size_mb = item.stat().st_size / (1024 * 1024)
            print(f"  {Colors.GREEN}-{Colors.RESET} {item.name} ({size_mb:.2f} MB)")
    
    print(f"\n{Colors.RED}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.YELLOW}  ⚠️  PERSONAL USE ONLY{Colors.RESET}")
    print(f"{Colors.YELLOW}  Do NOT publish to app stores or use commercially{Colors.RESET}")
    print(f"{Colors.YELLOW}  See LICENSE.txt for complete terms{Colors.RESET}")
    print(f"{Colors.RED}{'=' * 60}{Colors.RESET}\n")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Build standalone desktop executables for Bulling',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 build_desktop_standalone.py
  python3 build_desktop_standalone.py --clean
  python3 build_desktop_standalone.py --clean --verbose
  
Features:
  - Traditional 10-pin bowling rules with authentic scoring
  - Real-time bowling scorecard with strikes (X) and spares (/)
  - Professional scoreboard display
  - 10th frame bonus rules
  - Multiple player support
"""
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean previous builds before building'
    )
    
    parser.add_argument(
        '--no-clean',
        action='store_true',
        help='Do not clean previous builds (default)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show verbose output'
    )
    
    parser.add_argument(
        '--version',
        type=str,
        default='1.0.0',
        help='Set version number for distribution package (default: 1.0.0)'
    )
    
    return parser.parse_args()

def main():
    """Main build function"""
    global VERBOSE
    
    # Parse arguments
    args = parse_arguments()
    VERBOSE = args.verbose
    
    print_header()
    check_requirements()
    
    # Handle clean option
    if args.clean:
        clean_build_dirs()
    elif not args.no_clean:
        # Interactive mode (default behavior for backwards compatibility)
        try:
            response = input(f"{Colors.YELLOW}Clean previous builds? (y/N): {Colors.RESET}").strip().lower()
            if response == 'y':
                clean_build_dirs()
        except (KeyboardInterrupt, EOFError):
            print(f"\n{Colors.YELLOW}Skipping clean...{Colors.RESET}")
    
    build_standalone()
    create_distribution_package(version=args.version)
    print_summary()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Build cancelled by user{Colors.RESET}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.RESET}")
        if VERBOSE:
            import traceback
            traceback.print_exc()
        sys.exit(1)
