# Encoding: utf-8
# Module name: anchor
# Description: Transparent rails on which input and output handles to a vertex can be anchored.

# PySide6:
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, Property
from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QGraphicsObject, QGraphicsEllipseItem

from schematic.handle import HANDLE_OPTS

# Default config:
AnchorOpts = {
    "frame": QRectF(-1, -18, 2, 32),
    "round": 0,
    "style": {
        "color": QPen(Qt.GlobalColor.transparent),
        "brush": QBrush(QColor(0xFFFFFF), Qt.BrushStyle.SolidPattern),
    },
}


# Class Anchor:
class AnchorItem(QGraphicsObject):

    # Signals:
    sig_anchor_clicked = Signal(QPointF)

    # Class constructor:
    def __init__(self, role: int, parent: QGraphicsObject | None = None, **kwargs):

        # Base-class initialization:
        super().__init__(parent)
        super().setAcceptHoverEvents(True)

        # Set attribute(s):
        self.setProperty("role", role)
        self.setProperty("cpos", kwargs.get("cpos", QPointF(0, 0)))
        self.setProperty("frame", kwargs.get("frame", AnchorOpts["frame"]))
        self.setProperty("round", kwargs.get("round", AnchorOpts["round"]))
        self.setProperty("style", kwargs.get("style", AnchorOpts["style"]))
        self.setProperty("ordinate", None)

        # Position the anchor:
        self.setPos(self.property("cpos"))

        # Initialize handle-hint:
        self._hint = QGraphicsEllipseItem(self)
        self._hint.setRect(HANDLE_OPTS["frame"])
        self._hint.setPen(QPen(QColor(0x000000), 0.50))
        self._hint.setBrush(QBrush(HANDLE_OPTS["color"]))
        self._hint.setVisible(False)

        # Hook onto callbacks:
        if kwargs.get("callback", None):
            self.sig_anchor_clicked.connect(
                kwargs.get("callback"), Qt.ConnectionType.UniqueConnection
            )

    # Reimplementation of QGraphicsObject.boundingRect(...):
    def boundingRect(self):
        return self.property("frame").adjusted(-2, 0, 2, 0)

    # Reimplementation of QGraphicsObject.paint(...):
    def paint(self, painter, option, widget=...):

        # Customize painter:
        painter.setPen(self.property("style")["color"])
        painter.setBrush(self.property("style")["brush"])
        painter.drawRoundedRect(
            self.property("frame").adjusted(0.75, 0.75, -0.75, -0.75),
            self.property("round"),
            self.property("round"),
        )

    # Reimplementation of QGraphicsObject.hoverEnterEvent(...):
    def hoverEnterEvent(self, event, /):

        # Invoke base-class implementation and set the cursor:
        super().hoverEnterEvent(event)
        super().setProperty("ordinate", event.pos().y())
        super().setCursor(Qt.CursorShape.ArrowCursor)

        # Show hint:
        self._hint.show()

    # Reimplementation of QGraphicsObject.hoverMoveEvent(...):
    def hoverMoveEvent(self, event, /):

        # Invoke base-class implementation:
        super().setProperty("ordinate", event.pos().y())
        super().hoverMoveEvent(event)

        # Reposition hint:
        self._hint.setY(event.pos().y())

    # Reimplementation of QGraphicsObject.hoverEnterEvent(...):
    def hoverLeaveEvent(self, event, /):

        # Unset the cursor and invoke base-class implementation:
        super().setProperty("ordinate", None)
        super().unsetCursor()
        super().hoverLeaveEvent(event)

        # Hide hint:
        self._hint.hide()

    # Reimplementation of QGraphicsObject.mousePressEvent(...):
    def mousePressEvent(self, event, /):
        self.sig_anchor_clicked.emit(QPointF(0, event.pos().y()))

    # ----------------
    # Utility methods:
    # ----------------

    # Resize the anchor:
    def resize(self, bottom: float, /):

        rect = self.property("frame")
        rect.setBottom(bottom)
        self.setProperty("frame", rect)

    # ------------------------------------------------------------------------------------------------------------------
    # Property getter(s) and setter(s):

    @Property(int)
    def role(self):
        return self.property("role")

    @role.setter
    def role(self, value):
        pass
