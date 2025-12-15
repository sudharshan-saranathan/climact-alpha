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
from core.events import EventBus
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

        print(QtCore.QFile.exists(":/assets/icons/pack-png/caret-down.png"))

        # Add a combobox as the title bar widget
        combobox = ComboBox(
            self, editable=False, items=["Option 1", "Option 2", "Option 3"]
        )
        self.setTitleBarWidget(combobox)

        # Set minimum width
        self.setMinimumWidth(400)
