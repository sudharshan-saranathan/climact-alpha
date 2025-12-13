# Encoding: utf-8
# Module name: tabbedWidget
# Description: Tabbed widget component for the Climact application

# Imports (third-party)
from PySide6 import QtGui, QtCore, QtWidgets


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
        )

    # Override getitem method
    def __getitem__(self, index):
        """
        Get the widget at the specified tab index.
        """
        return self.widget(index)

    # Close tab method
    def _close_tab(self, index):
        """
        Close the tab at the specified index.
        """
        self.removeTab(index)
