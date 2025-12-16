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
from core.events import EventBus
from ui.components.graphicsView import GraphicsView
from ui.components.tabbedWidget import TabbedWidget
from ui.components.toolbar import ToolBar
from ui.sidebar.sidebar import SideBar


# Main UI window class
class MainWindow(QtWidgets.QMainWindow):
    """
    Refactored MainWindow with DI for EventBus, smaller helpers, explicit slots,
    and a public method to open the initial tab (avoids emitting during __init__).
    Note: import your compiled resources module before applying app stylesheet elsewhere.
    """

    def __init__(self, event_bus: EventBus | None = None):
        super().__init__()

        self._logger = logging.getLogger(__name__)
        self._bus = event_bus or EventBus.instance()

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
        toolbar = ToolBar(
            self,
            align="left",
            style="QToolBar QToolButton { margin: 1px 2px 16px 2px;}",
            movable=False,
            floatable=False,
            iconSize=QtCore.QSize(25, 25),
            orientation=QtCore.Qt.Orientation.Vertical,
            actions=[
                (
                    qta_icon("ph.layout-fill", color="#efefef"),
                    "Dock",
                    self.toggle_sidebar,
                ),
                (qta_icon("mdi.folder", color="#ffcb00"), "Open", None),
                (qta_icon("mdi.content-save", color="lightblue"), "Save", None),
                (qta_icon("mdi.language-python", color="#bd6b73"), "Run", None),
                (qta_icon("mdi.chart-box", color="#899878"), "Run", None),
            ],
        )

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
                    "widget": GraphicsView(None),
                    "label": "Home",
                    "icon": QtGui.QIcon(),
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
        traffic_lights = ToolBar(
            self,
            align="right",
            iconSize=QtCore.QSize(18, 18),
            actions=[
                (
                    qta_icon("mdi.plus", color="gray", color_active="white"),
                    "Maximize",
                    self.toggle_maximize,
                ),
                (
                    qta_icon("mdi.minus", color="gray", color_active="white"),
                    "Minimize",
                    self.showMinimized,
                ),
                (
                    qta_icon("mdi.close", color="gray", color_active="white"),
                    "Close",
                    self.close,
                ),
            ],
        )
        traffic_lights.setObjectName("TrafficLights")
        menubar.setCornerWidget(traffic_lights, QtCore.Qt.Corner.TopRightCorner)
        return menubar

    # Helper method to create a sidebar:
    def _create_sidebar(self) -> QtWidgets.QDockWidget:
        """
        Create and configure the main sidebar.
        """
        sidebar = SideBar(self)
        sidebar.setFixedWidth(360)
        sidebar.hide()

        return sidebar

    # Slot to toggle sidebar visibility
    @QtCore.Slot()
    def toggle_sidebar(self):
        """
        Toggle the visibility of the sidebar.
        """
        sidebar = self.findChild(SideBar)
        if sidebar:
            sidebar.setVisible(not sidebar.isVisible())

    @QtCore.Slot()
    def toggle_maximize(self):
        """
        Toggle between maximized and normal window states.
        """
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # Reimplement paint event for custom rendering:
    def paintEvent(self, event):
        """
        Custom paint event for the main window.
        """
        painter = QtGui.QPainter(self)
        painter.save()

        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0x393E41)))
        painter.drawRoundedRect(self.rect(), 8, 8)

        painter.restore()
        super().paintEvent(event)
