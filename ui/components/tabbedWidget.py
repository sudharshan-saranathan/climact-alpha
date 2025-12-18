# Encoding: utf-8
# Module name: tabbedWidget
# Description: Tabbed widget component for the Climact application

# Imports (standard)
from __future__ import annotations
from typing import Dict, Any


# Imports (third-party)
from PySide6 import QtGui, QtCore, QtWidgets


# Imports (local)
from events.widgetEvents import EventBus
from ui.components.graphicsView import GraphicsView, GraphicsScene


# Tabbed widget class
class TabbedWidget(QtWidgets.QTabWidget):
    """
    A tab-switching widget for the Climact application based on QtWidgets.QTabWidget.

    Feature(s):
        - Create/close/rename tabs.
        - Configurable max-tabs.
        - Creates Viewer instances in new tabs, by default.

    Note:
        - Beeps when max-tabs reached or trying to close the last tab.
    """

    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent,
            movable=kwargs.get("movable", True),
            tabsClosable=kwargs.get("tabsClosable", True),
            tabBarAutoHide=kwargs.get("tabBarAutoHide", False),
            tabPosition=kwargs.get(
                "tabPosition", QtWidgets.QTabWidget.TabPosition.North
            ),
        )

        instance = EventBus.instance()  # Get the singleton EventBus instance
        instance.instruction.connect(self._handle_instructions)

    # Override getitem method
    def __getitem__(self, index) -> QtWidgets.QWidget:
        """
        Get the widget at the specified tab index.
        """
        return self.widget(index)

    # Close tab method
    def _close_tab(self, index) -> None:
        """
        Close the tab at the specified index.
        """
        self.removeTab(index)

    # Instructions handler
    def _handle_instructions(self, message: dict) -> None:
        """
        Handle incoming instructions from the EventBus.

        :param message: A dictionary containing the command and payload.
        """
        command: str = message.get("command", "")
        payload: Dict[str, Any] = message.get("payload", {})

        if command == "open_in_tab":

            self.new_tab(
                widget=payload.get("widget", None),
                label=payload.get("label", None),
                icon=payload.get("icon", None),
            )

    # Reimplement paint event
    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """
        Reimplement the paint event to customize tab appearance.
        """

        painter = QtGui.QPainter(self)
        painter.save()

        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0x232A2E)))
        painter.drawRoundedRect(self.rect().adjusted(0, 2, -4, -4), 4, 4)

        painter.restore()
        super().paintEvent(event)

    # New tab method
    def new_tab(
        self,
        widget: QtWidgets.QWidget | None = None,
        label: str | None = None,
        icon: QtGui.QIcon | None = None,
    ):
        """
        Show the provided widget in a new tab if it doesn't already exist.
        """

        count = self.count()
        index = self.indexOf(widget)  # Returns -1 if the widget is not found.

        if index >= 0:
            self.setCurrentIndex(index)  # Switch to the existing tab.
            return  # Exit the method.

        canvas = GraphicsScene(QtCore.QRectF(0, 0, 100, 100))
        widget = widget or GraphicsView(
            canvas,
            sceneRect=QtCore.QRectF(0, 0, 5000, 5000),
            renderHints=QtGui.QPainter.RenderHint.Antialiasing,
            viewportUpdateMode=QtWidgets.QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate,
            backgroundBrush=QtGui.QBrush(QtGui.QColor(0x232A2E)),
        )  # Use a QGraphicsView as the default widget if no widget is provided.

        self.addTab(
            widget,  # Set the provided widget or the default widget.
            icon or QtGui.QIcon(),  # The default icon is empty.
            label or f"Tab {count + 1}",  # Use an updated tab count as the default.
        )  # Display the widget in a new tab
