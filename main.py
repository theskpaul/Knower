#!/usr/bin/env /home/var0/Projects/Knower/.venv/bin/python3

from default import check_and_make

check_and_make()

import sys

from PySide6.QtWidgets import QApplication

from interface.window import APPWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = APPWindow()
    window.show()

    sys.exit(app.exec())
