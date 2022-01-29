import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize
from package.gui.Main_window import MainWindows
from pathlib import Path

if __name__ == '__main__':
    app = QApplication([])

    # set icon
    app_icon = QIcon()
    app_icon.addFile(os.path.join(Path.cwd(), "src/main/icons/base/16.png"), QSize(16, 16))
    app_icon.addFile(os.path.join(Path.cwd(), "src/main/icons/base/24.png"), QSize(24, 24))
    app_icon.addFile(os.path.join(Path.cwd(), "src/main/icons/base/32.png"), QSize(32, 32))
    app_icon.addFile(os.path.join(Path.cwd(), "src/main/icons/base/48.png"), QSize(48, 48))
    app_icon.addFile(os.path.join(Path.cwd(), "src/main/icons/base/64.png"), QSize(64, 64))
    app_icon.addFile(os.path.join(Path.cwd(), "src/main/icons/Icon.ico"), QSize(256, 256))

    # Create a Qt widget, which will be our window.
    main_window = MainWindows()
    main_window.setWindowIcon(app_icon)
    main_window.show()

    # Start the event loop.
    app.exec()
