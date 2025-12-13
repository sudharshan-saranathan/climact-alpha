# Encoding: utf-8
# Module name: tabview
# Description: A tab-switching widget for the Climact application

# Import(s):
import util
from gui import maps

from PySide6 import QtGui
from PySide6 import QtCore
from PySide6 import QtWidgets

from schematic.canvas import Canvas
from schematic.viewer import Viewer

TAB_VIEW_OPTS = {
    "max-tabs": 8,
}


# Tab switcher class:
class TabView(QtWidgets.QTabWidget):
    """
    A tab-switching widget for the Climact application based on QtWidgets.QTabWidget.

    Feature(s):
        - Create/close/rename tabs.
        - Configurable max-tabs.
        - Auto-creates Viewer instances in new tabs.

    Note:
        - Beeps when max-tabs reached or trying to close the last tab.
    """

    # Default constructor:
    def __init__(self, parent: QtWidgets.QWidget | None = None, **kwargs):
        super().__init__(parent, **kwargs)

        # Connect the tab widget's signals to appropriate slots:
        self.setIconSize(QtCore.QSize(16, 16))
        self.tabCloseRequested.connect(self._on_tab_close)
        self.tabBarClicked.connect(self._on_tab_clicked)

        # Shortcuts:
        QtGui.QShortcut("Ctrl+T", self, self.create_tab)
        QtGui.QShortcut("Ctrl+W", self, self.remove_tab)
        QtGui.QShortcut("Ctrl+R", self, self.rename_tab)

        # Initialize a map:
        viewer = Viewer(
            maps.Scene(),
            renderHints=QtGui.QPainter.RenderHint.Antialiasing,
            backgroundBrush=QtGui.QBrush(QtCore.Qt.GlobalColor.white),
            viewportUpdateMode=QtWidgets.QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate,
            resizeAnchor=QtWidgets.QGraphicsView.ViewportAnchor.NoAnchor,
            dragMode=QtWidgets.QGraphicsView.DragMode.ScrollHandDrag,
        )

        self.create_tab(
            widget=viewer,
            label="Map View",
            icon=util.qta_icon("mdi.map", color="lightblue"),
        )

        # Connect to bus' signals:
        from gui import WidgetBus

        bus = WidgetBus.instance()
        bus.sig_open_widget.connect(self.create_tab)
        bus.sig_open_widget.connect(
            lambda widget: print(f"Opening widget in new tab: {widget}")
        )

    # Create a new tab:
    def create_tab(
        self,
        widget: QtWidgets.QWidget | None = None,
        label: str = str(),
        icon: QtGui.QIcon | None = None,
    ):
        """
        Create a new tab.
        :param widget: The widget to display in the tab.
        :param label: The name of the new tab.
        :param icon: The icon for the new tab.
        :return: None
        """

        # Check if maximum tabs reached:
        if self.count() >= TAB_VIEW_OPTS["max-tabs"]:
            QtWidgets.QApplication.beep()
            return

        count = self.count()
        label = label or f"Tab {count + 1}"

        widget = widget or Viewer(
            Canvas(self),
            sceneRect=QtCore.QRectF(0, 0, 10000, 10000),
            renderHints=QtGui.QPainter.RenderHint.Antialiasing,
            backgroundBrush=QtGui.QBrush(
                QtCore.Qt.GlobalColor.darkGray, QtCore.Qt.BrushStyle.FDiagPattern
            ),
            viewportUpdateMode=QtWidgets.QGraphicsView.ViewportUpdateMode.MinimalViewportUpdate,
            resizeAnchor=QtWidgets.QGraphicsView.ViewportAnchor.NoAnchor,
            dragMode=QtWidgets.QGraphicsView.DragMode.ScrollHandDrag,
        )

        self.addTab(widget, label)
        self.setTabIcon(count, icon or util.qta_icon("mdi.transit-connection-variant"))

    # Remove the current tab:
    def remove_tab(self) -> None:
        """
        Remove the current tab.
        :return:
        """

        # Remove the current tab:
        self._on_tab_close(self.currentIndex())

    # Rename an existing tab:
    def rename_tab(self, index: int = -1, name: str = str()) -> None:
        """
        Rename an existing tab.
        :param index: The index of the tab to rename.
        :param name: The new name for the tab.
        :return: None
        """

        # If no index provided, use the current tab:
        if index == -1:
            index = self.currentIndex()

        # If no name is provided, get name from user:
        name = (
            name
            or QtWidgets.QInputDialog.getText(self, "Tab Rename", "Enter new label:")[0]
        )

        # Rename the tab:
        if 0 <= index < self.count() and name:
            self.setTabText(index, name)

    # Remove the tab at the specified index:
    def _on_tab_close(self, index: int) -> None:
        """
        Remove the current tab.
        :param index: The index of the tab to remove.
        :return: None
        """

        # Remove the tab:
        if self.count() > 1:
            self.removeTab(index)  # Remove the tab if more than one exists.
        else:
            QtWidgets.QApplication.beep()  # Emit a beep if only one tab remains.

    # When the user clicks a tab:
    def _on_tab_clicked(self, index: int) -> None:
        """
        When the user clicks a tab.
        :param index: The index of the clicked tab.
        :return: None
        """

        pass
