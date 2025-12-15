# Encoding: utf-8
# Module name: mainWindow
# Description: Main UI window for the application

# Imports (standard)
from __future__ import annotations
import logging


# Imports (third party)
from PySide6 import QtGui, QtCore, QtWidgets
from qtawesome import icon as qta_icon

# Imports (local)
from ui.components.tabbedWidget import TabbedWidget
from core.events import EventBus
from ui.sidebar.sidebar import SideBar


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

        self._toolbar = self._create_toolbar()
        self._sidebar = self._create_sidebar()
        self._tabview = self._create_tab_widget()
        self._menubar = self._create_menubar()

        # Add toolbar, menubar, and central widget
        self.addToolBar(QtCore.Qt.ToolBarArea.LeftToolBarArea, self._toolbar)
        self.setCentralWidget(self._tabview)
        self.setMenuBar(self._menubar)

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
            iconSize=QtCore.QSize(26, 26),
            orientation=QtCore.Qt.Orientation.Vertical,
        )

        toolbar.addAction(qta_icon("ph.layout-fill", color="#efefef"), "Dock", self.toggle_sidebar)
        toolbar.addAction(qta_icon("mdi.folder", color="#ffcb00"), "Open")
        toolbar.addAction(qta_icon("mdi.content-save", color="lightblue"), "Save")
        toolbar.addAction(qta_icon("mdi.language-python", color="#bd6b73"), "Run")
        toolbar.addAction(qta_icon("mdi.chart-box", color="#899878"), "Run")
        toolbar.setStyleSheet("QToolBar QToolButton { margin: 2px 2px 4px 2px; }")

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
        menubar.setNativeMenuBar(False)

        file_menu = menubar.addMenu("File")
        edit_menu = menubar.addMenu("Edit")
        view_menu = menubar.addMenu("View")
        help_menu = menubar.addMenu("Help")

        # Traffic light indicators
        expander = QtWidgets.QFrame(self)
        expander.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Preferred
        )
        traffic_lights_widget = QtWidgets.QToolBar(self, iconSize=QtCore.QSize(16, 16))
        traffic_lights_widget.addWidget(expander)
        traffic_lights_widget.addAction(qta_icon("fa5s.circle", color="green"), "Maximize", self.showMaximized)
        traffic_lights_widget.addAction(qta_icon("fa5s.circle", color="yellow"), "Minimize", self.showMinimized)
        traffic_lights_widget.addAction(qta_icon("fa5s.circle", color="red"), "Close", self.close)
        traffic_lights_widget.setObjectName("TrafficLights")

        menubar.setCornerWidget(traffic_lights_widget, QtCore.Qt.Corner.TopRightCorner)
        return menubar

    # Helper method to create a sidebar:
    def _create_sidebar(self) -> QtWidgets.QDockWidget:
        """
        Create and configure the main sidebar.
        """
        sidebar = SideBar(self)
        sidebar.hide()

        return sidebar

    # Helper method to toggle sidebar visibility:
    def toggle_sidebar(self):
        """
        Toggle the visibility of the sidebar.
        """
        sidebar = self.findChild(SideBar)
        if sidebar:
            sidebar.setVisible(not sidebar.isVisible())

    # Reimplement paint event for custom rendering:
    def paintEvent(self, event):
        """
        Custom paint event for the main window.
        """

        self.rect()

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0x393e41)))
        painter.drawRoundedRect(
            self.rect(),
            8,
            8,
        )

        super().paintEvent(event)
