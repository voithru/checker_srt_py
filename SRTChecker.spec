# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['tkinter', 'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox', 'pyperclip']
hiddenimports += collect_submodules('pyperclip')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('/Users/p-156/dev/checker_srt_py/settings_manager.py', '.'), ('/Users/p-156/dev/checker_srt_py/error_checker.py', '.'), ('/Users/p-156/dev/checker_srt_py/srt_processor.py', '.'), ('/Users/p-156/dev/checker_srt_py/error_settings_window.py', '.'), ('/Users/p-156/dev/checker_srt_py/application.py', '.')],
    hiddenimports=hiddenimports,
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
    icon=['/Users/p-156/dev/checker_srt_py/icon.icns'],
)
app = BUNDLE(
    exe,
    name='SRTChecker.app',
    icon='/Users/p-156/dev/checker_srt_py/icon.icns',
    bundle_identifier=None,
)
