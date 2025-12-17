# Encoding: utf-8
# Module name: graphicsScene
# Description: A QGraphicsScene-based canvas for the Climact application

# Import (standard)
from __future__ import annotations
import dataclasses


# Imports (third party)
from PySide6 import QtGui, QtCore, QtWidgets
from PySide6.QtCore import QPointF
from qtawesome import icon as qta_icon


# GraphicsScene class
class GraphicsScene(QtWidgets.QGraphicsScene):
    """
    A QGraphicsScene-based canvas for the Climact application.
    """

    def __init__(self, scene_rect: QtCore.QRectF, **kwargs):
        super().__init__(
            scene_rect,
            backgroundBrush=kwargs.get(
                "backgroundBrush", QtGui.QBrush(QtCore.Qt.GlobalColor.white)
            ),
        )

        self._mpos = QtCore.QPointF()
        self._menu = self._init_menu()

    # Helper method to initialize the context menu
    @staticmethod
    def _init_menu():

        menu = QtWidgets.QMenu()
        subm = menu.addMenu("Add")
        menu.addSeparator()

        menu.addAction(qta_icon("mdi.content-copy", color="#efefef"), "Copy")
        menu.addAction(qta_icon("mdi.content-paste", color="blue"), "Paste")
        return menu

    # Reimplement QGraphicsScene.contextMenuEvent():
    def contextMenuEvent(self, event: QtWidgets.QGraphicsSceneContextMenuEvent) -> None:

        if hasattr(self, "_menu"):
            self._mpos = event.scenePos()
            self._menu.exec(event.screenPos())

    # Public methods
    def create_item(self, item_class: str):

        # Import globals
        _class = globals()[item_class]
