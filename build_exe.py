import PyInstaller.__main__
import sys
from pathlib import Path

# Get the Qt plugins directory
import PyQt6
qt_plugins = str(Path(PyQt6.__file__).parent / "Qt6" / "plugins")

# Get absolute path to icon file
icon_path = str(Path(__file__).parent / "icon.ico")

PyInstaller.__main__.run([
    'fotoparadies_launcher.py',  # use our new launcher script
    '--name=fotoparadies',
    '--onefile',
    '--noconsole',  # hide console window since we have a GUI
    '--clean',
    f'--icon={icon_path}',  # use absolute path to icon
    '--add-data=LICENSE;.',
    '--add-data=README.md;.',
    f'--add-data={qt_plugins};Qt6/plugins',
    '--hidden-import=PyQt6.QtCore',
    '--hidden-import=PyQt6.QtGui',
    '--hidden-import=PyQt6.QtWidgets',
    '--hidden-import=fotoparadies.main',
    '--hidden-import=fotoparadies.fotoparadies',
    '--hidden-import=fotoparadies.gui',  # explicitly import gui module
    '--collect-all=PyQt6',
    '--paths=.',
])