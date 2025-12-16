# Encoding: utf-8
# Module name: viewer
# Description: A QGraphicsView-based schematic viewer for the Climact application


# Import - standard
from __future__ import annotations
import types
import dataclasses

# Import(s) - third party
from PySide6 import QtGui, QtCore, QtWidgets, QtOpenGLWidgets

from ui.graph.graphicsScene import GraphicsScene


# Dataclass
@dataclasses.dataclass
class ViewerOpts:
    zoom_max: float = 2.0
    zoom_min: float = 0.2
    zoom_exp: float = 1.5


# Class Viewer: A QGraphicsView-based schematic viewer
class GraphicsView(QtWidgets.QGraphicsView):

    # Signal(s):
    sig_zoom_changed = QtCore.Signal(float)

    # Constructor:
    def __init__(self, canvas: QtWidgets.QGraphicsScene | None = None, **kwargs):

        zoom_max = kwargs.pop("zoom_max", ViewerOpts.zoom_max)
        zoom_min = kwargs.pop("zoom_min", ViewerOpts.zoom_min)
        zoom_exp = kwargs.pop("exp", ViewerOpts.zoom_exp)

        super().__init__(
            alignment=QtCore.Qt.AlignmentFlag.AlignCenter,
            renderHints=kwargs.get(
                "renderHints", QtGui.QPainter.RenderHint.Antialiasing
            ),
            backgroundBrush=kwargs.get(
                "backgroundBrush", QtGui.QBrush(QtCore.Qt.GlobalColor.white)
            ),
        )

        # Base-class initialization:
        super().setScene(canvas or GraphicsScene(QtCore.QRectF(0, 0, 10000, 10000)))
        super().setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
        super().setViewportUpdateMode(
            QtWidgets.QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        super().setOptimizationFlag(
            QtWidgets.QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing
        )
        super().setOptimizationFlag(
            QtWidgets.QGraphicsView.OptimizationFlag.DontSavePainterState
        )

        # Initialize zoom and zoom-animation attribute(s):
        self._zoom = types.SimpleNamespace(
            scale=1.0, min=zoom_min, max=zoom_max, exp=zoom_exp
        )

        # Zoom animation:
        self._zoom_anim = QtCore.QPropertyAnimation(self, b"zoom")
        self._zoom_anim.setEasingCurve(QtCore.QEasingCurve.Type.OutExpo)
        self._zoom_anim.setDuration(720)

        # Focus animation:
        self._focus_anim = QtCore.QPropertyAnimation(self, b"center")
        self._focus_anim.setEasingCurve(QtCore.QEasingCurve.Type.InOutCubic)
        self._focus_anim.setDuration(720)

        # Use an OpenGL viewport for hardware acceleration:
        self._format = QtGui.QSurfaceFormat()
        self._format.setSamples(4)
        self._openGL_viewport = QtOpenGLWidgets.QOpenGLWidget(self)
        self._openGL_viewport.setFormat(self._format)
        self.setViewport(self._openGL_viewport)

    # Reimplementation of QGraphicsView.keyPressEvent():
    def keyPressEvent(self, event, /):

        # When the Ctrl key is pressed, switch to selection mode:
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.RubberBandDrag)

        # When the Shift key is pressed, switch to drag-mode:
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier:
            self.setDragMode(QtWidgets.QGraphicsView.DragMode.ScrollHandDrag)
            self.setCursor(QtCore.Qt.CursorShape.OpenHandCursor)

        super().keyPressEvent(event)

    # When the Shift key is released, switch back to hand-drag mode:
    def keyReleaseEvent(self, event, /):

        # Reset to no-drag mode and unset cursor:
        self.setDragMode(QtWidgets.QGraphicsView.DragMode.NoDrag)
        self.unsetCursor()

        super().keyReleaseEvent(event)

    # QWheelEvent:
    def wheelEvent(self, event, /):

        delta = event.angleDelta().y()
        delta = self._zoom.exp ** (delta / 100.0)

        self.execute_zoom(
            delta, event.deviceType() == QtGui.QInputDevice.DeviceType.Mouse
        )

    # Animation property:
    @QtCore.Property(float)
    def zoom(self):
        return self._zoom.scale

    # Set the zoom level:
    @zoom.setter
    def zoom(self, value: float):

        factor = value / self._zoom.scale
        self.scale(factor, factor)
        self._zoom.scale = value

    # Zoom execution:
    def execute_zoom(self, factor, animate=True, /):

        # Stop any ongoing animation:
        if self._zoom_anim.state() == QtCore.QPropertyAnimation.State.Running:
            self._zoom_anim.stop()

        # Calculate the target zoom level:
        target = self._zoom.scale * factor
        target = max(self._zoom.min, min(self._zoom.max, target))

        # Set up and start the animation:
        if animate:
            self._zoom_anim.setStartValue(self._zoom.scale)
            self._zoom_anim.setEndValue(target)
            self._zoom_anim.start()

        else:
            self.zoom = target

    # Focus property:
    @QtCore.Property(QtCore.QPointF)
    def center(self):
        return self.mapToScene(self.viewport().rect().center())

    @center.setter
    def center(self, value: QtCore.QPointF):
        self.centerOn(value)

    # This method implements the centering animation for graphics items:
    def _on_item_focused(self, item: QtWidgets.QGraphicsObject):
        item_pos = item.mapToScene(item.boundingRect().center())
        view_pos = self.mapToScene(self.viewport().rect().center())

        self._focus_anim.stop()
        self._focus_anim.setStartValue(view_pos)
        self._focus_anim.setEndValue(item_pos)
        self._focus_anim.start()

        # Trigger the item's on_focus method if it exists:
        if hasattr(item, "on_focus") and callable(item.on_focus):
            item.on_focus()
