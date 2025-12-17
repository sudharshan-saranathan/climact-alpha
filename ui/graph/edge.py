# Encoding: utf-8
# Module name: bundle
# Description: A connection bundle for the Climact application


# Imports (standard)
from __future__ import annotations
from typing import Any
import weakref

# Import (third party):
from PySide6 import QtGui, QtCore, QtWidgets

# Import (local):
import opts

EdgeOpts = {
    "frame": QtCore.QRectF(-2.5, -2.5, 5, 5),  # Default bounding rectangle.
    "slack": 0.40,  # Higher values result in more slacked beziers.
    "radius": 4,  # Radius for rounded corners (only for the angular curve).
    "stroke": {
        "width": 2.0,
        "color": QtGui.QColor(0x363E41),
        "style": QtCore.Qt.PenStyle.SolidLine,
    },
}


# Class Bundle:
class VectorItem(QtWidgets.QGraphicsObject):
    """
    A generic connector that connects two QGraphicsObject items in a QGraphicsScene.
    It supports bezier and angular curves, with customizable appearance and interactive behavior.
    1. Origin and Target: The vector connects two QGraphicsObject items, referred to as 'origin' and 'target'.
    2. Curve Types: Supports 'bezier' and 'angular' curve types for the connection path.
    3. Appearance Customization: Stroke color, width, and style can be customized.
    4. Interactive Behavior: Responds to hover and double-click events for interactivity.
    5. Animation: Smoothly animates stroke width on hover events.
    """

    # Signals sent to the event-bus:
    sig_item_focused = QtCore.Signal(QtWidgets.QGraphicsObject)

    # Default constructor:
    def __init__(self, parent: QtWidgets.QGraphicsObject | None = None, **kwargs):
        super().__init__(parent)
        super().setZValue(-10)  # Ensure vectors are drawn beneath other scene-items.

        # Behavior:
        self.setAcceptHoverEvents(True)
        self.setFlag(QtWidgets.QGraphicsObject.GraphicsItemFlag.ItemIsSelectable, True)

        self._init_attr(kwargs)  # Instance-level attribute(s)
        self._init_anim()  # Initialize animation "after" attributes.

        # Arrow to indicate the flow direction:
        self._arrow = custom.Image(
            opts.CLIMACT_CONFIG["root"] + "/assets/icons/pack-svg/arrow.svg",
            parent=self,
        )

        # Import:
        from schematic import HandleItem

        # The input and output objects must be of the type `Handle` (see schematic/handle.py):
        if isinstance(kwargs.get("origin", None), HandleItem) and isinstance(
            kwargs.get("target", None), HandleItem
        ):
            origin = kwargs.get("origin")
            target = kwargs.get("target")
            self._connect(origin, target)

        # Register this object with the event bus:
        self._register_with_bus()

    # Initialize attribute(s):
    def _init_attr(self, kwargs: dict[str, Any]):

        self.setProperty("curve", "bezier")
        self.setProperty("route", QtGui.QPainterPath())
        self.setProperty("slack", kwargs.get("slack", EdgeOpts["slack"]))
        self.setProperty("frame", kwargs.get("frame", EdgeOpts["frame"]))
        self.setProperty("stroke", kwargs.get("stroke", EdgeOpts["stroke"]))

        self.base_width = EdgeOpts["stroke"]["width"]  # Base width for the stroke.

    # Initialize animation(s):
    def _init_anim(self):

        self._anim = QtCore.QPropertyAnimation(self, b"thickness")
        self._anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutSine)
        self._anim.setDuration(240)

    # Connect the vector to origin and target:
    def _connect(self, origin: "HandleItem", target: "HandleItem") -> None:

        self.origin = weakref.ref(origin)  # Weak reference to the origin handle.
        self.target = weakref.ref(target)  # Weak reference to the target handle.
        self.setProperty("color", origin.attr["flow"].COLOR)

        # Initial path construction:
        self.update_path(origin, target)

        # Pair the origin to the target:
        origin.pair(self, target)
        target.pair(self, origin)
        target.set_stream(origin.attr["flow"].LABEL, mirror=False)

        # Connect signals to monitor endpoint shifts:
        origin.sig_handle_moved.connect(self.on_endpoint_shifted)
        target.sig_handle_moved.connect(self.on_endpoint_shifted)

    # Register this object with the event bus:
    def _register_with_bus(self) -> None:

        from schematic.bus_object import Bus

        bus = Bus.instance()
        self.sig_item_focused.connect(bus.sig_item_focused)

    # Reimplement QGraphicsObject.boundingRect():
    def boundingRect(self) -> QtCore.QRectF:
        return self.property("route").boundingRect().adjusted(-4, -4, 4, 4)

    # Reimplement QGraphicsObject.paint():
    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionGraphicsItem,
        widget: QtWidgets.QWidget | None = None,
    ) -> None:

        color = self.property("stroke")["color"]
        width = self.property("stroke")["width"]
        style = self.property("stroke")["style"]
        color = color if not self.isSelected() else QtGui.QColor(0xFFCB00)
        pen = QtGui.QPen(
            color,
            width,
            style,
            QtCore.Qt.PenCapStyle.RoundCap,
            QtCore.Qt.PenJoinStyle.RoundJoin,
        )
        painter.setPen(pen)
        painter.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        painter.drawPath(self.property("route"))

    # Reimplement QGraphicsObject.shape():
    def shape(self):
        stroker = QtGui.QPainterPathStroker()
        stroker.setWidth(self.property("stroke")["width"] + 12)
        return stroker.createStroke(self.property("route"))

    # Reimplement hoverEnterEvent():
    def hoverEnterEvent(self, event) -> None:

        self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)

        self._anim.stop()
        self._anim.setStartValue(self.base_width)
        self._anim.setEndValue(self.base_width + 2.0)
        self._anim.start()

    # Reimplement hoverLeaveEvent():
    def hoverLeaveEvent(self, event) -> None:

        self.unsetCursor()

        self._anim.stop()
        self._anim.setStartValue(self.base_width + 2.0)
        self._anim.setEndValue(self.base_width)
        self._anim.start()

    # Reimplement mouseDoubleClickEvent(...):
    def mouseDoubleClickEvent(self, event) -> None:

        from gui.config import VectorConfig

        self.sig_item_focused.emit(self)
        cfg_window = VectorConfig(self)
        cfg_window.exec()

        event.accept()
        super().mouseDoubleClickEvent(event)

    # Clear the current path:
    def clear(self) -> None:

        self._arrow.setPos(QtCore.QPointF())
        self.setProperty("route", QtGui.QPainterPath())
        self.prepareGeometryChange()
        self.update()

    # Bezier curve generator:
    def construct_path(self, initial: QtCore.QPointF, final: QtCore.QPointF):
        """
        Constructs the stream path from origin to target.
        :param initial: Origin point of the stream.
        :param final: Target point of the stream.
        :return: QPainterPath: The constructed path from origin to target.
        """

        def _bezier(_slack: float):

            path = QtGui.QPainterPath()
            path.moveTo(initial)

            ctrl_one_x = initial.x() + (final.x() - initial.x()) * _slack
            ctrl_one_y = initial.y() + (final.y() - initial.y()) * 0.25
            ctrl_two_x = initial.x() + (final.x() - initial.x()) * (1 - _slack)
            ctrl_two_y = final.y() - (final.y() - initial.y()) * 0.25

            ctrl_one = QtCore.QPointF(ctrl_one_x, ctrl_one_y)
            ctrl_two = QtCore.QPointF(ctrl_two_x, ctrl_two_y)
            path.cubicTo(ctrl_one, ctrl_two, final)
            return path

        slack = (
            self.property("slack")
            if initial.x() < final.x()
            else -10 * self.property("slack")
        )
        return _bezier(slack)

    # Callback function to update the path:
    def update_path(
        self,
        origin: QtCore.QPointF | QtWidgets.QGraphicsObject,
        target: QtCore.QPointF | QtWidgets.QGraphicsObject,
    ) -> None:

        if isinstance(origin, QtWidgets.QGraphicsObject) and isinstance(
            target, QtWidgets.QGraphicsObject
        ):
            origin = origin.scenePos()
            target = target.scenePos()

        self.setProperty("route", self.construct_path(origin, target))
        self.prepareGeometryChange()
        self.update()

        route = QtGui.QPainterPath(self.property("route"))
        self._arrow.setPos(route.pointAtPercent(0.60))  # Update the arrow's position.
        self._arrow.setRotation(
            -self.property("route").angleAtPercent(0.60)
        )  # Update the arrow's rotation.

    # Callback when the endpoint(s) are shifted:
    def on_endpoint_shifted(self, item) -> None:

        if self.origin and self.target and item in [self.origin(), self.target()]:
            self.update_path(self.origin(), self.target())

    @QtCore.Property(float)
    def thickness(self):
        return self.property("stroke").get("width", 2.0)

    @thickness.setter
    def thickness(self, value: float):
        stroke = self.property("stroke")
        stroke["width"] = float(value)

        self.setProperty("stroke", stroke)
        self.prepareGeometryChange()
        self.update()

    @QtCore.Property(QtGui.QColor)
    def color(self):
        return self.property("stroke").get("color", QtGui.QColor(0x363E41))

    @color.setter
    def color(self, value: str | int | QtGui.QColor):

        stroke = self.property("stroke")
        stroke["color"] = (
            QtGui.QColor(value) if not isinstance(value, QtGui.QColor) else value
        )

        self.setProperty("stroke", stroke)
        self.prepareGeometryChange()
        self.update()
