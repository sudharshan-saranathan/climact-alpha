# Encoding: utf-8
# Module name: graphicsScene
# Description: A QGraphicsScene-based canvas for the Climact application

# Import (standard)
from __future__ import annotations
import dataclasses


# Imports (third party)
from PySide6 import QtGui, QtCore, QtWidgets


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
