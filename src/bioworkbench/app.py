from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from bioworkbench.catalog import build_registry
from bioworkbench.ui.main_window import MainWindow


def run() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("BioWorkbench Starter")
    app.setStyle("Fusion")

    window = MainWindow(build_registry())
    window.show()
    return app.exec()

