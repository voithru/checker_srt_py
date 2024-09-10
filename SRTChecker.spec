# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\myProject\\checker_srt_hybe_win\\settings_manager.py', '.'), ('C:\\myProject\\checker_srt_hybe_win\\error_checker.py', '.'), ('C:\\myProject\\checker_srt_hybe_win\\srt_processor.py', '.'), ('C:\\myProject\\checker_srt_hybe_win\\error_settings_window.py', '.')],
    hiddenimports=['win32api', 'win32con', 'winreg', 'tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='SRTChecker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
