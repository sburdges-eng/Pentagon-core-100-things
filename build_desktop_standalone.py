#!/usr/bin/env python3
"""
Build script for creating standalone desktop executables for Bulling
Supports: Windows, Linux, macOS
Uses PyInstaller for cross-platform builds
"""

import sys
import os
import shutil
import subprocess
import platform
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

def print_header():
    """Print build header"""
    print("\n" + "=" * 60)
    print(f"  Building Bulling Standalone Desktop App")
    print(f"  Platform: {SYSTEM}")
    print(f"  Python: {sys.version.split()[0]}")
    print("=" * 60 + "\n")

def check_requirements():
    """Check if required tools are installed"""
    print("Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required")
        sys.exit(1)
    
    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__}")
    except ImportError:
        print("Error: PyInstaller is not installed")
        print("Install with: pip install pyinstaller")
        sys.exit(1)
    
    # Check PySide6
    try:
        import PySide6
        print(f"✓ PySide6 installed")
    except ImportError:
        print("Error: PySide6 is not installed")
        print("Install with: pip install PySide6")
        sys.exit(1)
    
    print("")

def clean_build_dirs():
    """Clean previous build artifacts"""
    print("Cleaning previous builds...")
    for dir_path in [BUILD_DIR, DIST_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed {dir_path}")
    print("")

def build_standalone():
    """Build standalone executable using PyInstaller"""
    print(f"Building standalone executable for {SYSTEM}...")
    
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
    print(f"Running: {' '.join(cmd)}")
    print("")
    result = subprocess.run(cmd, cwd=PROJECT_DIR)
    
    if result.returncode != 0:
        print("\n✗ Build failed!")
        sys.exit(1)
    
    print("\n✓ Build completed successfully!")

def create_distribution_package():
    """Create distribution package"""
    print("\nCreating distribution package...")
    
    # Source executable
    exe_path = DIST_DIR / EXE_NAME
    
    if not exe_path.exists():
        print(f"Error: Executable not found at {exe_path}")
        return
    
    # Get file size
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"  Executable size: {size_mb:.2f} MB")
    
    # Create platform-specific distribution
    if IS_WINDOWS:
        # Create ZIP for Windows
        dist_name = f"{APP_NAME}-Windows-x64"
        zip_path = DIST_DIR / f"{dist_name}.zip"
        
        # Create README
        readme_path = DIST_DIR / "README.txt"
        with open(readme_path, "w") as f:
            f.write(f"""{APP_NAME} - Bowling Scoring Game
Version: 1.0.0
Platform: Windows

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
        print(f"  Created: {dist_name}.zip")
        
    elif IS_LINUX:
        # Create tar.gz for Linux
        dist_name = f"{APP_NAME}-Linux-x64"
        tar_path = DIST_DIR / f"{dist_name}.tar.gz"
        
        # Create README
        readme_path = DIST_DIR / "README.txt"
        with open(readme_path, "w") as f:
            f.write(f"""{APP_NAME} - Bowling Scoring Game
Version: 1.0.0
Platform: Linux

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
        print(f"  Created: {dist_name}.tar.gz")
        
    elif IS_MACOS:
        # Create ZIP for macOS
        dist_name = f"{APP_NAME}-macOS-PyInstaller"
        zip_path = DIST_DIR / f"{dist_name}.zip"
        
        # Create README
        readme_path = DIST_DIR / "README.txt"
        with open(readme_path, "w") as f:
            f.write(f"""{APP_NAME} - Bowling Scoring Game
Version: 1.0.0
Platform: macOS (PyInstaller build)

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
        print(f"  Created: {dist_name}.zip")

def print_summary():
    """Print build summary"""
    print("\n" + "=" * 60)
    print("  Build Complete!")
    print("=" * 60)
    print(f"\nDistribution files in: {DIST_DIR}")
    print("\nFiles created:")
    
    # List distribution files
    for item in DIST_DIR.iterdir():
        if item.is_file() and item.name.startswith(APP_NAME):
            size_mb = item.stat().st_size / (1024 * 1024)
            print(f"  - {item.name} ({size_mb:.2f} MB)")
    
    print("\n" + "=" * 60)
    print("  ⚠️  PERSONAL USE ONLY")
    print("  Do NOT publish to app stores or use commercially")
    print("  See LICENSE.txt for complete terms")
    print("=" * 60 + "\n")

def main():
    """Main build function"""
    print_header()
    check_requirements()
    
    # Ask user if they want to clean previous builds
    response = input("Clean previous builds? (y/N): ").strip().lower()
    if response == 'y':
        clean_build_dirs()
    
    build_standalone()
    create_distribution_package()
    print_summary()

if __name__ == "__main__":
    main()
