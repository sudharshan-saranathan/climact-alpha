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
from ui.sidebar.setting import GlobalSettings


# Sidebar class
class SideBar(QtWidgets.QDockWidget):
    """
    Sidebar component for the Climact application, added to the main window as a docked widget.
    """

    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent,
            floating=False,
            features=QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures,
            dockLocation=kwargs.get(
                "dockLocation", QtCore.Qt.DockWidgetArea.LeftDockWidgetArea
            ),
        )

        # Add a combobox as the title bar widget
        combobox = ComboBox(
            self,
            editable=False,
            items=["Settings", "Assistant", "Schematic", "Geospatial Data"],
        )

        # Initialize a stack widget
        self._stack = self._init_stack()

        self.setTitleBarWidget(combobox)
        self.setWidget(self._stack)

    # Helper method to initialize the stack widget
    def _init_stack(self) -> QtWidgets.QStackedWidget:

        stack = QtWidgets.QStackedWidget(self)
        stack.addWidget(GlobalSettings(self))

        return stack
