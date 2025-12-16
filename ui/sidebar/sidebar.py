# Encoding: utf-8
# Module name: sidebar
# Description: Sidebar component added to the main window as a docked widget

# Imports (standard)
from __future__ import annotations
from typing import Dict, Any
import logging
import resources

# Imports (third-party)
from PySide6 import QtGui, QtCore, QtWidgets


# Imports (local)
from ui.components.combobox import ComboBox


# Sidebar class
class SideBar(QtWidgets.QDockWidget):
    """
    Sidebar component for the Climact application, added to the main window as a docked widget.
    """

    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent,
            floating=kwargs.get("floating", False),
            features=kwargs.get(
                "features",
                QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures,
            ),
            dockLocation=kwargs.get(
                "dockLocation", QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            ),
        )

        # Add a combobox as the title bar widget
        combobox = ComboBox(
            self, editable=False, items=["Option 1", "Option 2", "Option 3"]
        )

        self.setTitleBarWidget(combobox)

    # Reimplement paintEvent to customize appearance
    def paintEvent(self, event: QtGui.QPaintEvent) -> None:

        painter = QtGui.QPainter(self)
        painter.save()

        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0x232A2E)))
        # painter.drawRoundedRect(self.rect().adjusted(0, 2, 0, -4), 4, 4)

        painter.restore()
        super().paintEvent(event)
