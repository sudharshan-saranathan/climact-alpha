# Encoding: utf-8
# Module name: combobox
# Description: Custom combobox widget for the Climact application


# Imports (third party)
from PySide6 import QtGui, QtCore, QtWidgets
from qtawesome import icon as qta_icon


# Imports (local)
import resources


# Item delegate for a combo box with a fixed height:
class FixedHeightDelegate(QtWidgets.QStyledItemDelegate):

    # Default constructor:
    def __init__(self, height: int, parent=None):
        super().__init__(parent)
        self._height = int(height)

    # Reimplement sizeHint to set fixed height:
    def sizeHint(
        self, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex
    ):
        base = super().sizeHint(option, index)
        return QtCore.QSize(base.width(), self._height)


# Class ComboBox:
class ComboBox(QtWidgets.QComboBox):

    # Default constructor:
    def __init__(self, parent=None, **kwargs):
        super().__init__(
            parent,
            iconSize=kwargs.get("iconSize", QtCore.QSize(16, 16)),
            editable=kwargs.get("editable", False),
        )

        # Set custom view with fixed item height:
        view = QtWidgets.QListView(self)
        view.setItemDelegate(FixedHeightDelegate(24, view))
        view.setSpacing(2)

        # Custom style:
        self.setView(view)
        self.setObjectName("ComboBox")
        self.setStyleSheet(
            "QComboBox {"
            "margin: 0px 0px 0px 0px;"
            "border: 0px solid gray; "
            "border-radius: 4px;"
            "}"
            "QComboBox::down-arrow {"
            "height: 16px;"
            "width: 16px;"
            "image: url(:/assets/icons/pack-png/caret-down.png);"
            "margin-right: 4px;"
            "}"
            "QComboBox QAbstractView {"
            "margin: 4px 0px 4px 0px;"
            "border: 0px solid gray; "
            "border-radius: 4px;"
            "}"
            "QComboBox QAbstractView::item {"
            "width:  80px;"
            "padding: 4px;"
            "}"
            "QComboBox QAbstractView::item:selected {"
            "background-color: #3874F2;"
            "color: white;"
            "}"
        )

        # Add items, if available:
        for item in kwargs.get("items", []):

            if (
                isinstance(item, tuple) and len(item) == 2
            ):  # Items have both icons and labels
                icon, label = item
                self.addItem(qta_icon(icon, color="#efefef"), label)

            else:
                self.addItem(item)  # Only labels
