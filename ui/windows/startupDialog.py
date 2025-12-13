# Encoding: utf-8
# Module name: startup
# Description: A startup widget for the Climact application


# Imports (standard)
from enum import Enum


# Imports (third party)
from PySide6 import QtCore, QtWidgets


# Imports (local)
from ui.components.layouts import VLayout


# Startup finish codes:
class StartupCode(Enum):
    Closed = -1
    Quit = 0
    New = 1
    Import = 2
    Templates = 3


# Class StartupScreen:
class StartupWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        # The `_startup_choice` button group includes the "Template" and "Models" push-buttons.
        # Selecting one of these buttons updates the file table on the right-side panel to show
        # the appropriate files in the relevant subdirectory.
        self._startup_choice = QtWidgets.QButtonGroup(exclusive=True)

        # Additional window settings
        self.setObjectName("startup-dialog")  # DO NOT MODIFY (used in stylesheet)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlag(QtCore.Qt.WindowType.FramelessWindowHint)

        # Set up the UI
        self._init_ui()

    # Set up the UI
    def _init_ui(self):

        container = QtWidgets.QWidget(self)
        vb_layout = VLayout(container)
