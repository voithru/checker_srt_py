import PyInstaller.__main__
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))

if sys.platform.startswith('win'):
    separator = ';'
    add_data_format = '{};.'
else:
    separator = ':'
    add_data_format = '{}:.'

PyInstaller.__main__.run([
    'main.py',
    '--onefile',
    '--windowed',
    '--name', 'SRTChecker',
    '--add-data', add_data_format.format(os.path.join(current_dir, 'settings_manager.py')),
    '--add-data', add_data_format.format(os.path.join(current_dir, 'error_checker.py')),
    '--add-data', add_data_format.format(os.path.join(current_dir, 'srt_processor.py')),
    '--add-data', add_data_format.format(os.path.join(current_dir, 'error_settings_window.py')),
    '--add-data', add_data_format.format(os.path.join(current_dir, 'application.py')),
    '--hidden-import', 'tkinter',
    '--hidden-import', 'tkinter.ttk',
    '--hidden-import', 'tkinter.filedialog',
    '--hidden-import', 'tkinter.messagebox',
    '--hidden-import', 'pyperclip',
    '--collect-submodules', 'pyperclip',
    '--clean',
])