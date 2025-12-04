"""
Setup script for creating a macOS application bundle (.app) for Bulling.

This script uses py2app to create a standalone macOS application that can be
double-clicked to run, with no code or terminal commands required.

To build the app:
    python setup.py py2app

The .app bundle will be created in the 'dist' folder.
"""

from setuptools import setup

APP = ['bulling_qt.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': True,
    'iconfile': 'app_icon.icns',  # Will be created
    'plist': {
        'CFBundleName': 'Bulling',
        'CFBundleDisplayName': 'Bulling',
        'CFBundleGetInfoString': 'Bowling Scoring Game - Bull Head Edition',
        'CFBundleIdentifier': 'com.bulling.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHumanReadableCopyright': '© 2025 Bulling',
        'NSHighResolutionCapable': True,
    },
    'packages': ['PySide6'],
    'includes': [],
    'excludes': ['tkinter', 'matplotlib', 'numpy'],
    'strip': True,
    'optimize': 2,
}

setup(
    name='Bulling',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
