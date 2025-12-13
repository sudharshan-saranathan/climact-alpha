# Encoding: utf-8
# Module name: mainWindow
# Description: Main UI window for the application


# Imports (third-party)
from PySide6 import QtGui, QtCore, QtWidgets


# Main UI window class
class MainWindow(QtWidgets.QMainWindow):
    """
    Main UI window for the Climact application.
    """

    def __init__(self):
        super().__init__()

        self._init_attr()  # Set behavior and attributes
        self._init_ui()  # Setup UI components

    # Behavior and attributes
    def _init_attr(self):
        """
        Initialize window attributes and behavior.
        """
        self.setWindowTitle("Climact Main Window")
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_AcceptDrops)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

    # Set up UI components
    def _init_ui(self):
        """
        Initialize UI components.
        """

        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel("Welcome to Climact!")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
