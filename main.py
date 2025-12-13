# Encoding: utf-8
# Module name: main
# Description: Main entry point for the application

# Imports (standard)
import os
import sys
import logging
import argparse

# Imports (third-party)
from PySide6 import QtGui, QtCore, QtWidgets

# Imports (local)
import opts
import resources
from ui.windows.main_ui import MainUi


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Main application class (subclass of QtWidgets.QApplication)
class Climact(QtWidgets.QApplication):

    def __init__(self, argv):
        super().__init__(argv)

        # Application metadata
        self.setApplicationName(opts.ClimactMeta.app_name)
        self.setApplicationVersion(opts.ClimactMeta.app_version)
        self.setOrganizationDomain(opts.ClimactMeta.org_domain)
        self.setOrganizationName(opts.ClimactMeta.org_name)

        # Parse command-line arguments
        self._parse_args(argv)

        # Set icon and style
        self._set_icon()
        self._set_style()

        # Instantiate the main window
        self.main_ui = MainUi()
        self.main_ui.showMaximized()

    # Parse command-line arguments
    @staticmethod
    def _parse_args(argv):

        parser = argparse.ArgumentParser(description="Climact Application")
        parser.add_argument(
            "-v", "--version", action="version", version=opts.ClimactMeta.app_version
        )
        parser.add_argument(
            "-a",
            "--enable-assistant",
            action="store_true",
            help="Enable AI assistant",
            default=True,
        )
        parser.add_argument(
            "-s",
            "--enable-solver",
            action="store_true",
            help="Enable solver module",
            default=True,
        )

        flags = parser.parse_args(argv[1:] if len(argv) > 1 else None)
        if flags.enable_assistant:
            opts.global_flags |= opts.ClimactFlags.ENABLE_AGENTS

        if flags.enable_solver:
            opts.global_flags |= opts.ClimactFlags.ENABLE_SOLVER

        return flags

    # Apply custom stylesheet
    def _set_style(self):

        file = QtCore.QFile(":/assets/theme/dark.qss")
        if file.open(
            QtCore.QFile.OpenModeFlag.ReadOnly
            | QtCore.QFile.OpenModeFlag.Text  # type: ignore
        ):

            try:
                qss = QtCore.QTextStream(file)  # Load file as text stream
                qss = qss.readAll()  # Read file contents
                self.setStyleSheet(qss)  # Apply stylesheet

            except Exception as exception:
                logger.error(f"Error applying stylesheet: {exception}")

            file.close()  # Close file after reading

        else:
            logger.error(f"Failed to load stylesheet: {file.fileName()}")

    # Set window icon
    def _set_icon(self):

        icon = QtGui.QIcon(":/assets/icons/logo-padded.png")
        if icon.isNull():
            logger.error(f"Failed to load icon.")
            return

        self.setWindowIcon(icon)


def main():

    app = Climact(sys.argv)
    app.exec()
    sys.exit(0)


if __name__ == "__main__":
    main()
