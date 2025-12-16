# Encoding: utf-8
# Module name: toolbar
# Description: A QToolBar-based toolbar for the Climact application with action handling and alignment.

# Imports (standard)
from __future__ import annotations


# Imports (third party)
from PySide6 import QtCore, QtWidgets


# Class Toolbar:
class ToolBar(QtWidgets.QToolBar):

    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent,
            iconSize=kwargs.get("iconSize", QtCore.QSize(16, 16)),
            movable=False,
            floatable=False,
        )

        self._init_actions(kwargs)  # Install the actions specified in `kwargs`

    # Initialize the toolbar's actions:
    def _init_actions(self, kwargs: dict[str, str | tuple[str, str]]) -> None:

        # Alignment:
        align = kwargs.get("align", "right")
        space = QtWidgets.QFrame()
        space.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )

        # Add spacer based on alignment
        if align == "right":
            self.addWidget(space)

        # Add actions
        for icon, text, slot in kwargs.get("actions", []):
            self.addAction(icon, text, slot)

        # Add spacer based on alignment
        if align == "left":
            self.addWidget(space)

        # Set style
        if kwargs.get("style"):
            self.setStyleSheet(kwargs.get("style"))
