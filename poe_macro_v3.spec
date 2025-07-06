# -*- mode: python ; coding: utf-8 -*-

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# Collect all necessary data files
datas = [
    ('config/*.yaml', 'config'),
    ('assets/templates/*.png', 'assets/templates'),
    ('data/flasks/*.csv', 'data/flasks'),
]

# Hidden imports for PyQt5 and other libraries
hiddenimports = [
    'PyQt5',
    'PyQt5.QtCore',
    'PyQt5.QtGui',
    'PyQt5.QtWidgets',
    'cv2',
    'numpy',
    'PIL',
    'pynput',
    'pynput.keyboard',
    'pynput.mouse',
    'pyautogui',
    'psutil',
    'mss',
    'pygetwindow',
    'yaml',
    'colorama',
    'requests',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Remove unnecessary files to reduce size
a.binaries = [x for x in a.binaries if not x[0].startswith('opencv_video')]
a.binaries = [x for x in a.binaries if not x[0].startswith('opencv_objdetect')]
a.binaries = [x for x in a.binaries if not x[0].startswith('opencv_dnn')]

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='poe_macro_v3',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon='assets/poe_macro.ico' if os.path.exists('assets/poe_macro.ico') else None
)