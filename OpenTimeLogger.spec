# -*- mode: python ; coding: utf-8 -*-
# onedir build (fast startup, no _MEI temp extraction) with backend excludes


a = Analysis(
    ['session_logger.py'],
    pathex=[],
    binaries=[],
    datas=[('web', 'web')],
    hiddenimports=['webview.platforms.winforms', 'webview.platforms.edgechromium'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'webview.platforms.cef', 'webview.platforms.qt', 'webview.platforms.gtk',
        'webview.platforms.cocoa', 'webview.platforms.mshtml',
        'webview.platforms.android',
        'tkinter', 'PyQt5', 'PyQt6', 'PySide2', 'PySide6',
        'matplotlib', 'numpy', 'scipy', 'pandas',
        'IPython', 'jedi', 'pytest', 'setuptools',
    ],
    noarchive=False,
    optimize=1,  # NOT 2: level 2 strips docstrings, which breaks pycparser
                 # (needed by clr_loader/pythonnet) in frozen boots.
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='OpenTimeLogger',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['app.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='OpenTimeLogger',
)
