import PyInstaller.__main__
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
icon_path = os.path.join(current_dir, 'icon.ico')

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name', 'SRTChecker',
    '--add-data', f'{current_dir}\\settings_manager.py;.',
    '--add-data', f'{current_dir}\\error_checker.py;.',
    '--add-data', f'{current_dir}\\srt_processor.py;.',
    '--add-data', f'{current_dir}\\error_settings_window.py;.',
    '--add-data', f'{current_dir}\\application.py;.',
    '--hidden-import', 'tkinter',
    '--hidden-import', 'tkinter.ttk',
    '--hidden-import', 'tkinter.filedialog',
    '--hidden-import', 'tkinter.messagebox',
    '--clean',
    '--log-level', 'INFO'
])