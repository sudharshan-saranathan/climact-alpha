# Encoding: utf-8
# Module name: quitConfirm
# Description: Quit confirmation dialog for the Climact application

# Imports (standard)
from __future__ import annotations


# Imports (third party)
from PySide6 import QtGui, QtCore, QtWidgets


# Quit confirmation dialog class
class QuitConfirm(QtWidgets.QDialog):
    """
    A quit confirmation dialog for the Climact application.
    """

    def __init__(self, messages: str, parent: QtWidgets.QGraphicsObject | None = None):
        super().__init__(parent)

        self.setWindowTitle("Confirm Close")
        self.setModal(True)

        # Layout
        layout = QtWidgets.QVBoxLayout()

        # Message
        message = QtWidgets.QLabel("Are you sure you want to close the application?")
        layout.addWidget(message)

        # Buttons
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Yes
            | QtWidgets.QDialogButtonBox.StandardButton.No
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)
