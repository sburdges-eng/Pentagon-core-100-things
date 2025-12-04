# Desktop Standalone App Build Guide

This guide explains how to build standalone desktop executables for **Bulling** that work on Windows, Linux, and macOS without requiring Python to be installed.

## 🎯 Overview

The desktop standalone app uses **PyInstaller** to create self-contained executables that:
- ✅ Include all dependencies (Python runtime, PySide6/Qt6)
- ✅ Work on any system (no installation required)
- ✅ Are single executable files (easy distribution)
- ✅ Support Windows, Linux, and macOS

## 📦 What You Get

### Windows
- `Bulling.exe` - Windows executable (~65-70 MB)
- `Bulling-Windows-x64.zip` - Distribution package with README

### Linux
- `Bulling` - Linux executable (~65-70 MB)
- `Bulling-Linux-x64.tar.gz` - Distribution package with README

### macOS (PyInstaller)
- `Bulling` - macOS executable (~65-70 MB)
- `Bulling-macOS-PyInstaller.zip` - Distribution package with README

**Note:** For native macOS .app bundles, use `build_standalone.sh` instead (creates SwiftUI or py2app builds).

## 🚀 Quick Build

### Prerequisites

1. **Python 3.9 or higher**
   ```bash
   python3 --version  # Should be 3.9+
   ```

2. **Install dependencies**
   ```bash
   pip3 install PyInstaller PySide6
   ```

### Build Commands

#### Option 1: Using Shell Script (Recommended)
```bash
./build_desktop_standalone.sh
```

This will:
- Check and install dependencies automatically
- Build the standalone executable
- Create distribution packages

#### Option 2: Using Python Script Directly
```bash
python3 build_desktop_standalone.py
```

This gives you more control and shows detailed output.

## 📋 Build Process Details

### What Happens During Build

1. **Dependency Check**: Verifies Python, PyInstaller, and PySide6 are installed
2. **Analysis**: PyInstaller analyzes `bulling_qt.py` and all dependencies
3. **Collection**: Gathers all required Python modules and Qt libraries
4. **Bundling**: Creates a single executable with embedded Python runtime
5. **Packaging**: Creates platform-specific distribution archives with README

### Build Options

The build script creates a **single-file executable** (`--onefile`) which:
- ✅ Easy to distribute (one file)
- ✅ No installation needed
- ✅ Runs from any location
- ❌ Slightly slower startup (extracts to temp on first run)
- ❌ Larger file size

### Directory Structure After Build

```
Pentagon-core-100-things/
├── dist/                           # Distribution output
│   ├── Bulling                     # Standalone executable
│   ├── Bulling-<Platform>.zip      # Distribution package
│   └── README.txt                  # Distribution instructions
├── build/                          # Build artifacts (can be deleted)
│   └── Bulling/                    # PyInstaller build files
└── Bulling.spec                    # PyInstaller spec file
```

## 🎮 Running the Standalone App

### Windows
1. Extract `Bulling-Windows-x64.zip`
2. Double-click `Bulling.exe`
3. Windows Defender may show a warning (click "More info" → "Run anyway")

### Linux
1. Extract `Bulling-Linux-x64.tar.gz`
   ```bash
   tar -xzf Bulling-Linux-x64.tar.gz
   ```
2. Make executable (if needed):
   ```bash
   chmod +x Bulling
   ```
3. Run:
   ```bash
   ./Bulling
   ```

### macOS
1. Extract `Bulling-macOS-PyInstaller.zip`
2. Right-click `Bulling` → Select "Open"
3. Click "Open" in security dialog
4. Or run from terminal:
   ```bash
   ./Bulling
   ```

## 🔧 Advanced Usage

### Clean Build

To remove previous build artifacts:
```bash
rm -rf build/ dist/ *.spec
python3 build_desktop_standalone.py
```

The script will ask if you want to clean previous builds.

### Custom Build Options

Edit `build_desktop_standalone.py` to customize:

```python
# Change to --onedir for faster startup (but multiple files)
cmd = [
    "pyinstaller",
    "--name", APP_NAME,
    "--onedir",  # Instead of --onefile
    "--windowed",
    # ... other options
]
```

### Adding Custom Icon

To add a custom icon to the executable:

1. **Windows:** Create `bulling.ico`
2. **macOS:** Create `bulling.icns`
3. **Linux:** Icons are typically set by desktop environment

Update the build script:
```python
if IS_WINDOWS:
    cmd.extend(["--icon", "bulling.ico"])
elif IS_MACOS:
    cmd.extend(["--icon", "bulling.icns"])
```

### Debug Mode

For debugging issues, build without `--windowed`:
```bash
pyinstaller --name Bulling \
    --onefile \
    --hidden-import PySide6.QtCore \
    --hidden-import PySide6.QtGui \
    --hidden-import PySide6.QtWidgets \
    bulling_qt.py
```

This will show console output for debugging.

## 🐛 Troubleshooting

### Build Fails - Missing PyInstaller
```bash
pip3 install --upgrade pyinstaller
```

### Build Fails - Missing PySide6
```bash
pip3 install --upgrade PySide6
```

### Executable Won't Run - Missing Libraries (Linux)

Some Linux distributions may need additional system libraries:
```bash
# Ubuntu/Debian
sudo apt-get install libxcb-xinerama0 libxcb-cursor0

# Fedora/RHEL
sudo dnf install libxcb xcb-util-wm
```

### Windows Defender Blocks Executable

This is normal for unsigned executables:
1. Click "More info"
2. Click "Run anyway"

Alternatively, you can sign the executable with a code signing certificate.

### macOS Gatekeeper Blocks App

For unsigned apps on macOS:
1. Right-click the app
2. Select "Open"
3. Click "Open" in the dialog

Or disable Gatekeeper (not recommended):
```bash
sudo spctl --master-disable
```

### Large File Size

The executable includes the entire Python runtime and Qt6 libraries (~65MB). To reduce size:

1. Use `--onedir` instead of `--onefile` (splits into multiple files)
2. Exclude unused Qt modules in the build script
3. Use UPX compression (may cause issues with some antivirus software)

## 📊 Comparison with Other Build Methods

| Method | Platform | File Size | Type | Best For |
|--------|----------|-----------|------|----------|
| **PyInstaller** | Win/Linux/macOS | ~65 MB | Executable | Cross-platform distribution |
| **py2app** | macOS only | ~100 MB | .app bundle | Native macOS apps |
| **Native SwiftUI** | macOS only | ~5 MB | .app bundle | Best macOS experience |
| **pip install** | All platforms | N/A | Python package | Developers |

## 🎯 Distribution Tips

### For End Users

1. **Test on target platform** before distributing
2. **Include README.txt** with installation instructions
3. **Mention system requirements** (minimal)
4. **Explain security warnings** (unsigned app)

### For Developers

1. **Use version control** for the source code
2. **Tag releases** with version numbers
3. **Create GitHub Releases** for downloads
4. **Sign executables** for production (requires certificates)

### Creating Installers

For a more professional distribution:

**Windows:**
- Use Inno Setup or NSIS to create `.exe` installer
- Include shortcuts, uninstaller, etc.

**macOS:**
- Use DMG Canvas or create-dmg to create `.dmg`
- See `create_macos_dmg.sh` for examples

**Linux:**
- Create `.deb` or `.rpm` packages
- Or use AppImage, Flatpak, or Snap

## 📝 License Notice

**PERSONAL USE ONLY** - These standalone builds are for personal, non-commercial use only.

See [LICENSE.txt](../LICENSE.txt) for complete terms and conditions.

## 🔗 Related Documentation

- [Main README](../README.md) - Project overview
- [macOS App Guide](../MACOS_APP_GUIDE.md) - Native macOS builds
- [Distribution Guide](../DISTRIBUTION_GUIDE.md) - All distribution methods
- [Quick Start](../QUICK_START.md) - Getting started

## ❓ FAQ

### Q: Why is the executable so large?
A: It includes Python runtime + Qt6 libraries. This ensures it works on any system without dependencies.

### Q: Can I make it smaller?
A: Yes, use `--onedir` mode and distribute as a folder, or exclude unused Qt modules.

### Q: Do I need Python installed to run the executable?
A: No! The executable is self-contained.

### Q: Can I distribute this to others?
A: Yes, for personal use only (friends/family). No commercial use or app stores.

### Q: Which build method should I use?
A: 
- **Windows/Linux**: Use PyInstaller (this guide)
- **macOS users**: Use native SwiftUI build for best experience
- **Developers**: Use `pip install .` for development

### Q: How do I update the app?
A: Rebuild with the updated source code and distribute the new executable.

## 🎉 Success!

You now have a standalone desktop app that can be distributed to anyone, regardless of whether they have Python installed!

---

**Ready to build?** Run `./build_desktop_standalone.sh` and start distributing! 🚀
