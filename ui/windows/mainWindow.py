# Encoding: utf-8
# Module name: mainWindow
# Description: Main UI window for the application

# Imports (standard)
from __future__ import annotations
import logging


# Imports (third-party)
from PySide6 import QtCore, QtWidgets
from qtawesome import icon as qta_icon

# Imports (local)
from ui.components.tabbedWidget import TabbedWidget
from core.events import EventBus


# Main UI window class
class MainWindow(QtWidgets.QMainWindow):
    """
    Main UI window for the Climact application.
    """

    def __init__(self):
        super().__init__()

        self._init_attr()  # Set behavior and attributes
        self._init_ui()  # Initialize interface components

    # Behavior and attributes
    def _init_attr(self):
        """
        Initialize window attributes and behavior.
        """
        self.setWindowTitle("Climact Main Window")
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_AcceptDrops)

    # Set up UI components
    def _init_ui(self):
        """
        Initialize UI components.
        """

        toolbar = self._create_toolbar()
        sidebar = self._create_sidebar()
        tabview = self._create_tab_widget()
        menubar = self._create_menubar()

        # Add toolbar, menubar, and central widget
        self.addToolBar(QtCore.Qt.ToolBarArea.LeftToolBarArea, toolbar)
        self.setCentralWidget(tabview)
        self.setMenuBar(menubar)

    # Helper method to create a toolbar:
    def _create_toolbar(self) -> QtWidgets.QToolBar:
        """
        Create and configure the main toolbar.
        """
        toolbar = QtWidgets.QToolBar(
            "Toolbar",
            self,
            movable=False,
            floatable=False,
            iconSize=QtCore.QSize(24, 24),
            orientation=QtCore.Qt.Orientation.Vertical,
        )

        toolbar.addAction(qta_icon("ph.layout-fill", color="#efefef"), "Dock")
        toolbar.addAction(qta_icon("mdi.folder", color="#ffcb00"), "Open")
        toolbar.addAction(qta_icon("mdi.content-save", color="lightblue"), "Save")
        toolbar.addAction(qta_icon("mdi.language-python", color="#bd6b73"), "Run")
        toolbar.addAction(qta_icon("mdi.chart-box", color="#899878"), "Run")
        toolbar.setStyleSheet("QToolBar QToolButton { margin: 8px 2px 8px 2px; }")

        return toolbar

    # Helper method to create a tab widget:
    def _create_tab_widget(self) -> TabbedWidget:
        """
        Create and configure the main tab widget.
        """
        tab_widget = TabbedWidget(
            self,
            movable=True,
            tabsClosable=True,
            tabPosition=QtWidgets.QTabWidget.TabPosition.North,
        )

        bus = EventBus.instance()
        bus.instruction.emit(
            {
                "command": "open_in_tab",
                "payload": {
                    "widget": QtWidgets.QLabel("Welcome to Climact!"),
                    "label": "Home",
                    "icon": qta_icon("mdi.home", color="green"),
                },
            }
        )

        return tab_widget

    # Helper method to create a menubar:
    def _create_menubar(self) -> QtWidgets.QMenuBar:
        """
        Create and configure the main menubar.
        """
        menubar = QtWidgets.QMenuBar(self)

        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        view_menu = menubar.addMenu("View")
        help_menu = menubar.addMenu("Help")

        return menubar

    # Helper method to create a sidebar:
    def _create_sidebar(self) -> QtWidgets.QDockWidget:
        """
        Create and configure the main sidebar.
        """
        sidebar = QtWidgets.QDockWidget("Sidebar", self)
        sidebar.setFeatures(
            QtWidgets.QDockWidget.DockWidgetFeature.NoDockWidgetFeatures
        )

        list_widget = QtWidgets.QListWidget()
        list_widget.addItems(["Item 1", "Item 2", "Item 3"])
        sidebar.setWidget(list_widget)

        self.addDockWidget(QtCore.Qt.DockWidgetArea.LeftDockWidgetArea, sidebar)

        return sidebar
