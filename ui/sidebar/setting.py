# Encoding: utf-8
# Module name: setting
# Description: A global settings widget for the Climact application.


# Imports (standard)
from __future__ import annotations

# Imports (third party)
from PySide6 import QtCore
from PySide6 import QtWidgets


# Imports (local)
from ui.components.widgetLayouts import HLayout


# Global settings widget:
class GlobalSettings(QtWidgets.QWidget):

    # Default constructor:
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)

        # Initialize buttons (apply and reset buttons):
        self._init_buttons()

        # Initialize child-widgets:
        name_edit = QtWidgets.QLineEdit(self)
        text_edit = QtWidgets.QTextEdit()
        combo_box = QtWidgets.QComboBox()
        spin_start = QtWidgets.QSpinBox()
        spin_final = QtWidgets.QSpinBox()
        flow_hub = QtWidgets.QFrame()

        # Initialize form layout and customize behavior:
        self._form = QtWidgets.QFormLayout(self)
        self._form.setFieldGrowthPolicy(
            QtWidgets.QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow
        )
        self._form.setContentsMargins(4, 0, 0, 4)
        self._form.setSpacing(2)

        # Insert widgets:
        self._form.addRow("Project:", name_edit)
        self._form.addRow("Version:", combo_box)
        self._form.addRow("Description:", text_edit)
        self._form.addRow("Start Epoch:", spin_start)
        self._form.addRow("Final Epoch:", spin_final)
        self._form.addRow("Stream Manager:", flow_hub)

        text_edit.setMaximumHeight(160)
        spin_start.setRange(-100, 100)
        spin_final.setRange(-100, 100)
        spin_final.setValue(50)

    # Initialize meta buttons:
    def _init_buttons(self):

        # Buttons layout:
        self._buttons = HLayout(None, spacing=4)
        self._buttons.addStretch(10)
        self._buttons.addWidget(
            reset := QtWidgets.QPushButton("Reset"),
            0,
            QtCore.Qt.AlignmentFlag.AlignRight,
        )
        self._buttons.addWidget(
            apply := QtWidgets.QPushButton("Apply"),
            0,
            QtCore.Qt.AlignmentFlag.AlignRight,
        )

        reset.setObjectName("Reset Button")
        apply.setObjectName("Apply Button")
        apply.pressed.connect(self._on_save_settings)

    # Slot to handle saving settings:
    def _on_save_settings(self):

        apply = self.findChild(QtWidgets.QPushButton, "Apply Button")
        apply.setText("Apply")

    def _on_settings_changed(self):

        apply = self.findChild(QtWidgets.QPushButton, "Apply Button")
        apply.setText("Apply")
