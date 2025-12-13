# --
# Encoding: utf-8
# Module name: layout
# Description: Layout utilities for the Climact application
# --

# Import(s):
from PySide6 import QtWidgets


# Class GLayout:
class GLayout(QtWidgets.QGridLayout):

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        # Parse margins:
        ml, mt, mr, md = kwargs.get("margins", (0, 0, 0, 0))

        # Set attribute(s):
        self.setSpacing(kwargs.get("spacing", 0))
        self.setContentsMargins(ml, mt, mr, md)


# Class HLayout:
class HLayout(QtWidgets.QHBoxLayout):

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        # Parse margins:
        ml, mt, mr, md = kwargs.get("margins", (0, 0, 0, 0))

        # Set attribute(s):
        self.setSpacing(kwargs.get("spacing", 0))
        self.setContentsMargins(ml, mt, mr, md)

        # If widgets are available, add them:
        for widget in kwargs.get("widgets", []):
            self.addWidget(widget)


# Class VLayout:
class VLayout(QtWidgets.QVBoxLayout):

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent)

        # Parse margins:
        ml, mt, mr, md = kwargs.get("margins", (0, 0, 0, 0))

        # Set attribute(s):
        self.setSpacing(kwargs.get("spacing", 0))
        self.setContentsMargins(ml, mt, mr, md)

        # If widgets are available, add them:
        for widget in kwargs.get("widgets", []):
            self.addWidget(widget)
