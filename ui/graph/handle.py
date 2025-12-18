# Encoding: utf-8
# Module name: handle
# Description: Connection end points for vertices.

# Import (standard)
from __future__ import annotations
import enum
from typing import Any

# Import (third party)
from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets


# Import (local)
from qtawesome import icon as qta_icon


# Default options for HandleItem:
HandleOpts = {
    "frame": QtCore.QRectF(-1.5, -1.5, 3, 3),
    "color": 0xB4F7D2,
}


# Enum HandleRole:
class HandleRole(enum.Enum):
    INP = enum.auto()
    OUT = enum.auto()


# Enum HandleConnectivity:
class HandleConnectivity(enum.Enum):
    ONE_TO_ONE = enum.auto()
    MANY_TO_MANY = enum.auto()


# Class Handle:
class HandleItem(QtWidgets.QGraphicsObject):

    # sig_stream_changed = QtCore.Signal(type(Stream))
    sig_handle_clicked = QtCore.Signal(QtWidgets.QGraphicsObject)
    sig_handle_moved = QtCore.Signal(QtWidgets.QGraphicsObject)

    def __init__(
        self,
        role: HandleRole,  # The handle's role (input or output).
        position: QtCore.QPointF,  # The handle's position (w.r.t the parent or scene).
        parent: (
            QtWidgets.QGraphicsObject | QtWidgets.QGraphicsItem | None
        ) = None,  # The parent QGraphicsObject.
        **kwargs,
    ):
        super().__init__(parent)

        # Determine connectivity and snapping behavior:
        self._connectivity = kwargs.get("connectivity", HandleConnectivity.ONE_TO_ONE)
        self._snap = False if parent is None else True

        # Initialize an attribute dictionary for serialization and deserialization.
        # This is simpler and faster than using Qt's property system:
        self.attr = {
            "id": id(self),
            "role": role,
            "xpos": position.x(),
            "name": kwargs.get("name", "Resource"),
            # "flow": kwargs.get("flow", BasicFlows["ItemFlow"]),
            "frame": QtCore.QRectF(kwargs.get("frame", HandleOpts["frame"])),
            "color": QtGui.QColor(kwargs.get("color", HandleOpts["color"])),
            "icon-size": kwargs.get("icon-size", 12),
        }

        # Y-axis boundaries for snapping. Note: The y-axis is inverted in Qt's coordinate systems.
        self.setProperty("ymin", kwargs.get("ymin", -float("inf")))
        self.setProperty("ymax", kwargs.get("ymax", float("inf")))

        # Sub-component initialization:
        self._anim = self._init_anim()
        self._menu = self._init_menu()

        self.connected = False
        self.conjugate = None
        self.connector = None

        # Import:
        from ui.graph.edge import EdgeItem

        self._connections: dict[EdgeItem, HandleItem] = {}

        # If provided, connect to the callback:
        if kwargs.get("callback", None):
            self.sig_handle_clicked.connect(kwargs.get("callback"))

        # Set flags and attribute(s):
        self.setPos(position)
        self.setAcceptHoverEvents(True)
        self.setFlag(
            QtWidgets.QGraphicsObject.GraphicsItemFlag.ItemSendsScenePositionChanges
        )

    # _Reimplement __getitem__(...):
    def __getitem__(self, key: str):
        """
        Method to access dynamic properties using the indexing syntax.
        :param key:
        :return:
        """

        if key in self.dynamicPropertyNames():
            return self.property(key)

        return None

    # Reimplement __setitem__(...):
    def __setitem__(self, key: str, value: Any) -> None:
        """
        Method to set dynamic properties using the indexing syntax.
        :param key:
        :param value:
        :return:
        """

        self.setProperty(key, value)

    # Initialize the context menu for the handle:
    def _init_menu(self) -> QtWidgets.QMenu:

        # Create the context menu:
        self._menu = QtWidgets.QMenu()
        self._flow_submenu = self._menu.addMenu(
            "Stream"
        )  # For easy access, the submenu has to be a class member.

        pencil = self._menu.addAction(qta_icon("mdi.pencil"), "Configure")
        unpair = self._menu.addAction(
            qta_icon("mdi.link-off", color="#ffcb00"), "Unpair", self.free
        )
        self._menu.addSeparator()

        delete = self._menu.addAction(qta_icon("mdi.delete", color="red"), "Delete")

        # Display icons:
        pencil.setIconVisibleInMenu(True)
        unpair.setIconVisibleInMenu(True)
        delete.setIconVisibleInMenu(True)

        return self._menu

    # Initialize the animation for the handle:
    def _init_anim(self) -> QtCore.QPropertyAnimation:

        # Create the animation and set attribute(s):
        animation = QtCore.QPropertyAnimation(self, b"radius")
        animation.setEasingCurve(QtCore.QEasingCurve.Type.OutQuad)
        animation.setDuration(240)

        # Return the animation:
        return animation

    # Reimplement boundingRect(...):
    def boundingRect(self, /):

        frame = self.attr["frame"]
        frame = (
            frame.adjusted(-20, -4, 4, 4)
            if self.attr["role"] == HandleRole.OUT
            else frame.adjusted(-4, -4, 20, 4)
        )
        return frame

    # Reimplement paint(...):
    def paint(self, painter, option, widget=...):

        color = QtGui.QColor(self.attr["color"])
        brush = QtGui.QBrush(color)
        pen = QtGui.QPen(QtCore.Qt.GlobalColor.black, 0.50)

        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawEllipse(self.attr["frame"])

        if self.isUnderMouse():
            frame = self.attr["frame"].adjusted(0.75, 0.75, -0.75, -0.75)
            painter.setBrush(QtCore.Qt.GlobalColor.black)
            painter.setPen(QtCore.Qt.PenStyle.NoPen)
            painter.drawEllipse(frame)

    # Reimplementation of QtWidgets.QGraphicsObject.itemChange():
    def itemChange(self, change, value, /):

        if (
            change
            == QtWidgets.QGraphicsObject.GraphicsItemChange.ItemScenePositionHasChanged
        ):
            self.sig_handle_moved.emit(self)

        if (
            change == QtWidgets.QGraphicsObject.GraphicsItemChange.ItemSceneHasChanged
            and value
        ):
            if hasattr(value, "begin_transient"):
                self.sig_handle_clicked.connect(value.begin_transient)

        return super().itemChange(change, value)

    # Reimplementation of QtWidgets.QGraphicsObject.contextMenuEvent():
    def contextMenuEvent(self, event, /):

        # Clear the flow-menu:
        self._flow_submenu.clear()

        # Reset the movable flag. This is required because triggering the context-menu doesn't invoke the
        # mouseReleaseEvent(...) which would normally reset this flag. Instead, we have to do it here.
        self.setFlag(QtWidgets.QGraphicsObject.GraphicsItemFlag.ItemIsMovable, False)

        event.accept()
        self._menu.exec(event.screenPos())

    # Reimplementation of QtWidgets.QGraphicsObject.hoverEnterEvent():
    def hoverEnterEvent(self, event, /):

        super().hoverEnterEvent(event)
        super().setCursor(QtCore.Qt.CursorShape.ArrowCursor)

        # Start animation:
        self._anim.setStartValue(HandleOpts["frame"].width() / 2)
        self._anim.setEndValue(HandleOpts["frame"].width() / 2 + 0.5)
        self._anim.start()

    # Reimplementation of QtWidgets.QGraphicsObject.hoverLeaveEvent():
    def hoverLeaveEvent(self, event, /):

        super().hoverLeaveEvent(event)
        super().unsetCursor()

        # Start animation:
        self._anim.setStartValue(HandleOpts["frame"].width() / 2 + 0.5)
        self._anim.setEndValue(HandleOpts["frame"].width() / 2)
        self._anim.start()

    # Reimplementation of QtWidgets.QGraphicsObject.mousePressEvent():
    def mousePressEvent(self, event, /):

        # Clear the scene's selection:
        if self.scene():
            self.scene().clearSelection()

        if not self.connected and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.sig_handle_clicked.emit(self)

        else:
            super().setFlag(
                QtWidgets.QGraphicsObject.GraphicsItemFlag.ItemIsMovable, True
            )
            super().mousePressEvent(event)
            event.accept()

    # Reimplementation of QtWidgets.QGraphicsObject.mouseReleaseEvent():
    def mouseReleaseEvent(self, event, /):

        if self.connected:
            xpos = self.attr["xpos"] if self._snap else self.pos().x()
            ymax = self.property("ymax")
            ymin = self.property("ymin")
            ypos = max(min(self.pos().y(), ymax), ymin)

            # Emit the shifted QtCore.Signal:
            self.setPos(QtCore.QPointF(xpos, ypos))

        super().setFlag(QtWidgets.QGraphicsObject.GraphicsItemFlag.ItemIsMovable, False)
        super().mouseReleaseEvent(event)

    # Callback slot when the user selects a stream-type from the context menu:
    def on_set_stream(self) -> None:

        action = self.sender()
        pass

    # When the user connects this handle to another:
    def pair(
        self, connector: QtWidgets.QGraphicsObject, conjugate: "HandleItem"
    ) -> None:
        self.connected = True
        self.connector = connector
        self.conjugate = conjugate

    # When the user disconnects this handle from another:
    def free(self, mirror: bool = True) -> None:

        if mirror and self.connector and self.conjugate:
            self.connector.hide()
            self.conjugate.free(mirror=False)  # Avoids infinite recursion.

        self.connected = False
        self.connector = None
        self.conjugate = None

    # Method to check if the handle can be connected to:
    def is_connectable(self) -> bool:

        if self.connected:
            return True

        else:
            return not len(self._connections)

    # Declare the `radius` property using the `@Property` decorator to register with Qt's metaobject system:
    @QtCore.Property(float)
    def radius(self) -> float:
        return float(self.attr["frame"].width() / 2.0)

    # Setter for the `radius` property:
    @radius.setter
    def radius(self, value: float) -> None:
        self.attr["frame"] = QtCore.QRectF(-value, -value, value * 2, value * 2)
        self.update()
